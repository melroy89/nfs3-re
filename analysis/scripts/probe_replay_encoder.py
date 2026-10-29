"""Run unchanged replay encoder bytes in a freestanding Linux i386 harness.

No Wine/game execution or input executable modification. Requires GNU as/ld
and host i386 execution support. Synthetic rows do not prove gameplay admission.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile


EXPECTED = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"


def encode_model(source):
    output = bytearray()
    position = 0
    while position < 32:
        if position == 31:
            output.extend((255, source[position]))
            break
        end = position + 1
        if source[position] == source[end]:
            end += 1
            while end < 32 and source[end] == source[position]:
                end += 1
            output.extend((end - position, source[position]))
            position = end
        else:
            while end < 32 and source[end - 1] != source[end]:
                end += 1
            count = end - position - 1
            output.append((-count) & 255)
            output.extend(source[position:position + count])
            position += count
    return bytes(output)


def extract_code(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    base = struct.unpack_from("<I", data, optional + 28)[0]
    for index in range(count):
        offset = optional + optional_size + 40 * index
        _, rva, size, raw = struct.unpack_from("<IIII", data, offset + 8)
        delta = 0x4BC9B0 - base - rva
        length = 0x4BCA7F - 0x4BC9B0
        if 0 <= delta and delta + length <= size:
            return data[raw + delta:raw + delta + length]
    raise ValueError("encoder range missing from raw PE sections")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = args.binary.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        parser.error("unexpected executable fingerprint")
    code = extract_code(data)
    cases = [
        ("constant_zero", bytes(32)),
        ("constant_ff", bytes([255] * 32)),
        ("distinct", bytes(range(32))),
        ("maximum44", bytes([0, 1, 1] * 10 + [0, 2])),
        ("maximum44_handbrake", bytes([0, 4, 4] * 10 + [0, 2])),
        ("intermediate8_analog", bytes([1] * 10 + [2] * 10 + [3] * 11 + [4])),
        ("intermediate8_action", bytes([0] * 10 + [4] * 10 + [0] * 11 + [4])),
        ("intermediate15", bytes([100, 101] + [10] * 6 + [20] * 6 + [30] * 6 + [40] * 6 + [50] * 5 + [60])),
    ]
    rng = random.Random(0x4BC9B0)
    for alphabet in (2, 3, 16, 256):
        for index in range(128):
            cases.append((f"alphabet{alphabet}_{index}", bytes(rng.randrange(alphabet) for _ in range(32))))
    assert all(len(source) == 32 for _, source in cases)
    with tempfile.TemporaryDirectory(prefix="nfs3-replay-encoder-") as temporary:
        directory = Path(temporary)
        (directory / "encoder.bin").write_bytes(code)
        (directory / "vectors.bin").write_bytes(b"".join(source for _, source in cases))
        assembly = f'''.intel_syntax noprefix
.section .text
.global _start
_start:
 cld
 mov esi,offset vectors
 mov edi,offset results
 mov ebp,{len(cases)}
next_case:
 mov eax,esi
 mov edx,edi
 call encoder
 push esi
 mov esi,eax
 add edi,4
 mov ecx,64
 rep movsb
 pop esi
 add esi,32
 dec ebp
 jnz next_case
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,{68 * len(cases)}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80
.section .encoder,"ax"
encoder:
.incbin "{directory / 'encoder.bin'}"
.section .scratch,"aw"
.space 128
.section .data
vectors: .incbin "{directory / 'vectors.bin'}"
results: .space {68 * len(cases)}
'''
        (directory / "probe.s").write_text(assembly)
        subprocess.run(["as", "--32", "-o", str(directory / "probe.o"), str(directory / "probe.s")], check=True)
        subprocess.run(["ld", "-m", "elf_i386", "-Ttext=0x100000", "-Tdata=0x200000",
                        "--section-start=.encoder=0x4bc9b0", "--section-start=.scratch=0x7a3d90",
                        "-o", str(directory / "probe"), str(directory / "probe.o")], check=True)
        result = subprocess.run([str(directory / "probe")], capture_output=True, check=True, timeout=10)
    if len(result.stdout) != 68 * len(cases):
        raise ValueError("short harness output")
    rows = []
    for index, (name, source) in enumerate(cases):
        offset = index * 68
        length = struct.unpack_from("<I", result.stdout, offset)[0]
        if length > 64:
            raise ValueError("encoder exceeded retained output window")
        encoded = result.stdout[offset + 4:offset + 4 + length]
        rows.append({"name": name, "source_hex": source.hex(), "length": length,
                     "encoded_hex": encoded.hex(), "matches_model": encoded == encode_model(source)})
    if not all(row["matches_model"] for row in rows):
        raise ValueError("original-byte result differs from branch model")
    directed = {row["name"]: row for row in rows if not row["name"].startswith("alphabet")}
    assert directed["maximum44"]["length"] == 44
    assert directed["maximum44_handbrake"]["length"] == 44
    assert directed["intermediate15"]["length"] == 15
    cursor = 697 * (4 * directed["maximum44"]["length"])
    cursor += (directed["intermediate8_analog"]["length"] + directed["intermediate8_action"]["length"]
               + directed["intermediate15"]["length"] + directed["distinct"]["length"])
    end = cursor + 4 * directed["maximum44"]["length"]
    report = {"target_sha256": EXPECTED, "code_range": "004bc9b0..004bca7e",
              "code_sha256": hashlib.sha256(code).hexdigest(),
              "method": "Unchanged extracted encoder bytes at original VA in freestanding Linux i386 ELF; synthetic source rows and isolated scratch",
              "case_count": len(rows), "all_match_model": True,
              "maximum_observed_length": max(row["length"] for row in rows),
              "recorder_boundary_arithmetic": {"cursor": cursor, "guard_cursor_plus128": cursor + 128,
                                               "capacity": 0x1E000, "guard_passes": cursor + 128 < 0x1E000,
                                               "end": end, "bytes_beyond": end - 0x1E000},
              "cases": rows,
              "limits": "Encoder only executed; recorder boundary is arithmetic checked against static caller. No game/Wine, active bindings, actual recording, full input-space exhaustiveness or runtime overwrite evidence."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"cases": len(rows), "all_match_model": True,
                      "maximum_observed_length": report["maximum_observed_length"],
                      "boundary": report["recorder_boundary_arithmetic"]}))


if __name__ == "__main__":
    main()
