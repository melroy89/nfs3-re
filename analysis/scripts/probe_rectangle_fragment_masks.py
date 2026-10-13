"""Exercise all rectangle-fragment dispatch masks in unchanged NFS3 code.

The script extracts BuildRectangleOutsideFragmentsWithPairedCoordinates and
its absolute jump table from the fingerprinted PE, then calls the original
bytes at their original virtual addresses in a freestanding Linux i386 process.
It checks all 16 positive-overlap masks, mapped paired coordinates, partition
area, disjoint input, and edge-only contact. Synthetic inputs only; this is not
a Wine/gameplay test.

Requires pefile, GNU as/ld, and Linux i386 execution support.
"""
import argparse
import hashlib
import json
import math
import struct
import subprocess
import tempfile
from pathlib import Path

EXPECTED_SHA256 = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"
IMAGE_BASE = 0x400000
TABLE_START = 0x4862F8
TABLE_END = 0x486338
FUNCTION_START = 0x486340
FUNCTION_END_EXCLUSIVE = 0x486DE5
CASE_STRIDE = 184
COUNT_OFFSET = 48
STATUS_OFFSET = 52
RECT_OUTPUT_OFFSET = 56
PAIRED_OUTPUT_OFFSET = 120
SENTINEL = 0xDEADBEEF


def get_bytes(pe, start, end):
    data = pe.get_data(start - IMAGE_BASE, end - start)
    if len(data) != end - start:
        raise SystemExit(f"Could not extract complete range {start:#x}..{end:#x}")
    return data


def build_case(name, mask, clip):
    source = (0.0, 0.0, 10.0, 10.0)
    paired = (100.0, 200.0, 300.0, 400.0)
    record = bytearray(CASE_STRIDE)
    struct.pack_into("<4f", record, 0, *source)
    struct.pack_into("<4f", record, 16, *clip)
    struct.pack_into("<4f", record, 32, *paired)
    struct.pack_into("<I", record, COUNT_OFFSET, 0xFEEDFACE)
    struct.pack_into("<I", record, STATUS_OFFSET, SENTINEL)
    for offset in (RECT_OUTPUT_OFFSET, PAIRED_OUTPUT_OFFSET):
        for i in range(16):
            struct.pack_into("<I", record, offset + i * 4, SENTINEL)
    return {"name": name, "mask": mask, "source": source, "clip": clip,
            "paired_source": paired, "record": record}


def unpack_rects(data, offset, count):
    return [list(struct.unpack_from("<4f", data, offset + i * 16)) for i in range(count)]


def area(rect):
    return (rect[2] - rect[0]) * (rect[3] - rect[1])


def positive_overlap(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def union_area(rectangles):
    xs = sorted({edge for rect in rectangles for edge in (rect[0], rect[2])})
    result = 0.0
    for left, right in zip(xs, xs[1:]):
        if right <= left:
            continue
        intervals = sorted((rect[1], rect[3]) for rect in rectangles
                           if rect[0] < right and rect[2] > left)
        covered = 0.0
        if intervals:
            low, high = intervals[0]
            for next_low, next_high in intervals[1:]:
                if next_low > high:
                    covered += high - low
                    low, high = next_low, next_high
                else:
                    high = max(high, next_high)
            covered += high - low
        result += (right - left) * covered
    return result


def close(a, b):
    return math.isclose(a, b, rel_tol=2e-6, abs_tol=2e-5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import pefile

    binary = args.binary.read_bytes()
    digest = hashlib.sha256(binary).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("Unexpected executable fingerprint; revalidate addresses first")
    pe = pefile.PE(data=binary)
    if pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.ImageBase != IMAGE_BASE:
        raise SystemExit("Unexpected PE architecture or image base; revalidate addresses first")
    jump_table = get_bytes(pe, TABLE_START, TABLE_END)
    targets = struct.unpack("<16I", jump_table)
    if any(not FUNCTION_START <= target < FUNCTION_END_EXCLUSIVE for target in targets):
        raise SystemExit("Jump table target falls outside the verified function body")
    function = get_bytes(pe, FUNCTION_START, FUNCTION_END_EXCLUSIVE)

    cases = []
    for mask in range(16):
        xmin = 2.0 if mask & 8 else 0.0
        ymin = 2.0 if mask & 2 else 0.0
        xmax = 8.0 if mask & 4 else 10.0
        ymax = 8.0 if mask & 1 else 10.0
        cases.append(build_case(f"mask_{mask:02x}", mask, (xmin, ymin, xmax, ymax)))
    cases.append(build_case("disjoint", None, (20.0, 20.0, 30.0, 30.0)))
    cases.append(build_case("edge_contact_x", None, (10.0, 0.0, 20.0, 10.0)))
    cases.append(build_case("edge_contact_y", None, (0.0, 10.0, 10.0, 20.0)))
    initial_records = b"".join(case["record"] for case in cases)
    case_count = len(cases)
    output_size = len(initial_records)

    with tempfile.TemporaryDirectory(prefix="nfs3-rect-fragment-") as temp:
        work = Path(temp)
        (work / "function.bin").write_bytes(function)
        (work / "jump-table.bin").write_bytes(jump_table)
        (work / "cases.bin").write_bytes(initial_records)
        assembly = f""".intel_syntax noprefix
.section .text
.global _start
_start:
 cld
 mov ebp,{case_count}
 mov esi,offset cases
case_loop:
 fninit
 mov eax,esi
 lea ebx,[esi+16]
 lea edx,[esi+32]
 lea ecx,[esi+{COUNT_OFFSET}]
 lea edi,[esi+{PAIRED_OUTPUT_OFFSET}]
 push edi
 lea edi,[esi+{RECT_OUTPUT_OFFSET}]
 push edi
 call rectangle_helper
 mov dword ptr [esi+{STATUS_OFFSET}],eax
 add esi,{CASE_STRIDE}
 dec ebp
 jnz case_loop
 mov eax,4
 mov ebx,1
 mov ecx,offset cases
 mov edx,{output_size}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80

.section .cases,"aw"
cases:
.incbin "{work/'cases.bin'}"
.section .jump_table,"a"
.incbin "{work/'jump-table.bin'}"
.section .function,"ax"
.global rectangle_helper
rectangle_helper:
.incbin "{work/'function.bin'}"
"""
        (work / "probe.s").write_text(assembly)
        subprocess.run(["as", "--32", "-o", str(work / "probe.o"), str(work / "probe.s")], check=True)
        subprocess.run([
            "ld", "-m", "elf_i386", "-Ttext=0x100000", "--section-start=.cases=0xc00000",
            f"--section-start=.jump_table={TABLE_START:#x}",
            f"--section-start=.function={FUNCTION_START:#x}",
            "-o", str(work / "probe"), str(work / "probe.o")
        ], check=True)
        output = subprocess.run([str(work / "probe")], capture_output=True, check=True, timeout=30).stdout

    if len(output) != output_size:
        raise RuntimeError(f"Expected {output_size} bytes of results, got {len(output)}")

    observations = []
    for i, case in enumerate(cases):
        offset = i * CASE_STRIDE
        count = struct.unpack_from("<I", output, offset + COUNT_OFFSET)[0]
        status = struct.unpack_from("<I", output, offset + STATUS_OFFSET)[0]
        mask = case["mask"]
        if mask is None:
            unchanged = count == 0xFEEDFACE and all(
                struct.unpack_from("<I", output, offset + out + j * 4)[0] == SENTINEL
                for out in (RECT_OUTPUT_OFFSET, PAIRED_OUTPUT_OFFSET) for j in range(16)
            )
            if status != 0 or not unchanged:
                raise AssertionError(f"{case['name']}: rejection did not preserve outputs/count")
            observations.append({"name": case["name"], "return": status, "outputs_untouched": unchanged})
            continue

        expected_count = mask.bit_count()
        if status != 1 or count != expected_count:
            raise AssertionError(f"mask {mask:#x}: return/count {status}/{count}, expected 1/{expected_count}")
        rects = unpack_rects(output, offset + RECT_OUTPUT_OFFSET, count)
        paired_rects = unpack_rects(output, offset + PAIRED_OUTPUT_OFFSET, count)
        xmin, ymin, xmax, ymax = case["clip"]
        intersection = [max(0.0, xmin), max(0.0, ymin), min(10.0, xmax), min(10.0, ymax)]
        expected_area = 100.0 - area(intersection)
        measured_area = sum(area(rect) for rect in rects)
        overlapping_pairs = []
        for left in range(len(rects)):
            rect = rects[left]
            if not (0 <= rect[0] < rect[2] <= 10 and 0 <= rect[1] < rect[3] <= 10):
                raise AssertionError(f"mask {mask:#x}: invalid fragment {rect}")
            for right in range(left + 1, len(rects)):
                if positive_overlap(rect, rects[right]):
                    intersection = [max(rect[0], rects[right][0]), max(rect[1], rects[right][1]),
                                    min(rect[2], rects[right][2]), min(rect[3], rects[right][3])]
                    overlapping_pairs.append({"fragment_indices": [left, right], "intersection": intersection,
                                              "area": area(intersection)})
            uv = paired_rects[left]
            expected_uv = [100 + rect[0] * 20, 200 + rect[1] * 20,
                           100 + rect[2] * 20, 200 + rect[3] * 20]
            if not all(close(actual, expected) for actual, expected in zip(uv, expected_uv)):
                raise AssertionError(f"mask {mask:#x}: paired coordinates {uv} != {expected_uv}")
        covered_area = union_area(rects)
        if not close(covered_area, expected_area):
            raise AssertionError(f"mask {mask:#x}: union area {covered_area} != {expected_area}")
        observations.append({
            "mask": mask,
            "clipped_source_boundaries": [name for bit, name in ((1, "yMax"), (2, "yMin"), (4, "xMax"), (8, "xMin")) if mask & bit],
            "return": status,
            "fragment_count": count,
            "rectangles_xyxy": rects,
            "paired_coordinates_uvuv": paired_rects,
            "area_sum": measured_area,
            "union_area": covered_area,
            "overlap_area_excess": measured_area - covered_area,
            "overlapping_fragment_pairs": overlapping_pairs,
            "expected_area": expected_area
        })

    report = {
        "target_sha256": digest,
        "method": "Original helper and 16-entry absolute jump table extracted from the fingerprinted PE and executed at their original VAs in a freestanding Linux i386 process; synthetic finite rectangles only.",
        "function": "BuildRectangleOutsideFragmentsWithPairedCoordinates",
        "function_range": [f"0x{FUNCTION_START:08x}", f"0x{FUNCTION_END_EXCLUSIVE - 1:08x}"],
        "jump_table_range": [f"0x{TABLE_START:08x}", f"0x{TABLE_END - 1:08x}"],
        "jump_targets": [f"0x{target:08x}" for target in targets],
        "source_rectangle_xyxy": [0.0, 0.0, 10.0, 10.0],
        "paired_source_coordinates_uvuv": [100.0, 200.0, 300.0, 400.0],
        "overlap_masks_tested": 16,
        "cases": observations,
        "limitations": [
            "This finite grid validates the listed masks and paired linear mapping, not all IEEE-754 values or arbitrary x87 control words.",
            "It does not exercise the caller loop, runtime exclusion counts, output-array capacity, aliasing, concurrent mutation, or renderer behavior.",
            "The paired coordinates are an affine synthetic mapping; they do not identify a specific game texture or prove caller data admission."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"sha256": digest, "masks": 16, "cases": len(cases), "output": str(args.output)}))


if __name__ == "__main__":
    main()
