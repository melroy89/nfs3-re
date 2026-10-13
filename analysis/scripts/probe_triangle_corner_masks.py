"""Run the unchanged triangle and segment-clipping code on a finite point grid.

The harness extracts 00485c30..004860a0 from the fingerprinted executable and
calls the original ClipFloatSegmentToRectangle entry for each triangle edge at
its original VA. It then classifies the two no-default corner selectors in
00487a30 using those observed edge masks. This is an isolated native Linux i386
experiment with synthetic triangles, not a Wine/gameplay capture.

Requires pefile, GNU as/ld, and Linux i386 execution support.
"""
import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path
import subprocess
import tempfile

EXPECTED_SHA256 = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"
IMAGE_BASE = 0x400000
CODE_START = 0x485C30
CODE_END_EXCLUSIVE = 0x4860A1
SEGMENT_CLIPPER = 0x485F20
SEGMENT_OFFSET = SEGMENT_CLIPPER - CODE_START
BOUNDS = (0.0, 0.0, 1.0, 1.0)  # yMin, xMin, yMax, xMax
GRID = (-1.0, 0.0, 0.25, 0.5, 0.75, 1.0, 2.0)


def complementary_corner(a, b):
    return any(
        (a & y and b & x) or (b & y and a & x)
        for y in (1, 2)
        for x in (4, 8)
    )


def inside(point):
    return (
        BOUNDS[1] <= point[0] <= BOUNDS[3]
        and BOUNDS[0] <= point[1] <= BOUNDS[2]
    )


def apply_finite_swaps(coords):
    points = [[coords[i], coords[i + 1]] for i in (0, 2, 4)]
    membership = [inside(point) for point in points]
    if not membership[0] and membership[1]:
        points[0], points[1] = points[1], points[0]
    if not membership[1] and membership[2]:
        points[1], points[2] = points[2], points[1]
    if not membership[0] and membership[1]:
        points[0], points[1] = points[1], points[0]
    return points, membership


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import pefile

    original = args.binary.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("Unexpected executable fingerprint; revalidate addresses first")
    pe = pefile.PE(data=original)
    if pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.ImageBase != IMAGE_BASE:
        raise SystemExit("Unexpected PE architecture or image base; revalidate addresses first")
    code = pe.get_data(CODE_START - IMAGE_BASE, CODE_END_EXCLUSIVE - CODE_START)
    if len(code) != CODE_END_EXCLUSIVE - CODE_START:
        raise SystemExit("Could not extract the complete helper/clipper range")
    if code[SEGMENT_CLIPPER - CODE_START] != 0x56:
        raise SystemExit("Unexpected segment-clipper entry byte")

    triangles = list(itertools.product(GRID, repeat=6))
    edge_vectors = bytearray()
    for coords in triangles:
        # Model the finite-value swaps that precede the actual edge snapshots.
        vertices, _membership = apply_finite_swaps(coords)
        for start, end in ((vertices[0], vertices[1]), (vertices[1], vertices[2]), (vertices[2], vertices[0])):
            edge_vectors.extend(struct.pack("<4f", *start, *end))

    with tempfile.TemporaryDirectory(prefix="nfs3-triangle-mask-") as temp:
        work = Path(temp)
        (work / "function.bin").write_bytes(code)
        (work / "vectors.bin").write_bytes(edge_vectors)
        edge_count = len(triangles) * 3
        result_bytes = edge_count * 8
        assembly = f""".intel_syntax noprefix
.section .text
.global _start
_start:
 cld
 mov esi,offset vectors
 mov edi,offset results
 mov dword ptr [remaining],{edge_count}
edge_loop:
 fninit
 mov eax,esi
 mov edx,offset bounds
 mov ebx,offset out_buffer
 lea ecx,[edi+4]
 call segment_clipper
 mov [edi],eax
 add esi,16
 add edi,8
 dec dword ptr [remaining]
 jnz edge_loop
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,{result_bytes}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80

.section .data
remaining: .long 0
vectors: .incbin "{work/'vectors.bin'}"
results: .space {result_bytes},0
.section .bounds,"aw"
bounds: .float 0.0,0.0,1.0,1.0
out_buffer: .space 16,0
.section .scratch,"aw"
.space 0x20,0
.section .functions,"ax"
.global segment_clipper
.incbin "{work/'function.bin'}",0,{SEGMENT_OFFSET}
segment_clipper:
.incbin "{work/'function.bin'}",{SEGMENT_OFFSET},{CODE_END_EXCLUSIVE - CODE_START - SEGMENT_OFFSET}
"""
        (work / "probe.s").write_text(assembly)
        subprocess.run(["as", "--32", "-o", str(work / "probe.o"), str(work / "probe.s")], check=True)
        subprocess.run(
            [
                "ld", "-m", "elf_i386", "-Ttext=0x100000", "-Tdata=0xc00000",
                "--section-start=.bounds=0x1800000",
                "--section-start=.scratch=0x791c08",
                "--section-start=.functions=0x485c30",
                "-o", str(work / "probe"), str(work / "probe.o"),
            ],
            check=True,
        )
        output = subprocess.run([str(work / "probe")], capture_output=True, check=True, timeout=30).stdout

    if len(output) != result_bytes:
        raise RuntimeError("Incomplete clipper output")
    observations = []
    corner_tests = 0
    unmatched_count = 0
    selector_counts = {"P0_P1_inside": 0, "P0_inside_P1_outside": 0}
    unmatched_by_selector = {"P0_P1_inside": 0, "P0_inside_P1_outside": 0}
    for i in range(len(triangles)):
        values = [struct.unpack_from("<II", output, (i * 3 + e) * 8) for e in range(3)]
        masks = [item[1] & 0x0F for item in values]
        returns = [item[0] for item in values]
        if all(code != 0 for code in returns):
            continue
        vertices, inside_flags = apply_finite_swaps(triangles[i])
        selector = None
        pair = None
        if inside_flags[0] and inside_flags[1] and masks[1] != masks[2]:
            selector, pair = "P0_P1_inside", (masks[1], masks[2])
        elif inside_flags[0] and not inside_flags[1] and masks[0] != masks[2] and masks[1] == 0:
            selector, pair = "P0_inside_P1_outside", (masks[0], masks[2])
        if selector is not None:
            selector_counts[selector] += 1
            corner_tests += 1
            matched = complementary_corner(*pair)
            if not matched:
                unmatched_count += 1
                unmatched_by_selector[selector] += 1
            if not matched and not any(item["selector"] == selector for item in observations):
                observations.append({
                    "selector": selector,
                    "points_after_swaps": vertices,
                    "inside_before_swaps": inside_flags,
                    "edge_return_values": returns,
                    "edge_masks": masks,
                })

    report = {
        "sha256": digest,
        "method": "Unchanged helper and segment-clipper PE instructions executed at original VAs in a freestanding Linux i386 harness; finite synthetic triangles only.",
        "function_range": [f"0x{CODE_START:08x}", f"0x{CODE_END_EXCLUSIVE - 1:08x}"],
        "range_sha256": hashlib.sha256(code).hexdigest(),
        "rectangle_ymin_xmin_ymax_xmax": list(BOUNDS),
        "grid_coordinate_values": list(GRID),
        "triangle_count": len(triangles),
        "edge_calls": edge_count,
        "tested_corner_consumers": corner_tests,
        "selector_counts": selector_counts,
        "unmatched_count": unmatched_count,
        "unmatched_by_selector": unmatched_by_selector,
        "unmatched_corner_witnesses": observations,
        "limitations": [
            "This grid establishes reachability only for its listed finite coordinates, not the full IEEE-754 domain.",
            "The caller's input swaps are modeled for ordinary finite, non-aliased values; the helper's x87 exceptional behavior is not tested here.",
            "No game callsite admission, Wine rendering, shared-scratch concurrency, or downstream batch capacity is covered.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "sha256": digest,
        "triangles": len(triangles),
        "edge_calls": edge_count,
        "unmatched_witnesses": len(observations),
        "output": str(args.output),
    }))


if __name__ == "__main__":
    main()
