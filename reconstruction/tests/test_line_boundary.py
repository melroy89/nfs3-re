"""Differentially exercise the maintained line-boundary routine vs NFS3 bytes.

Requires Python 3, pefile, GCC with i386 support, GNU as/ld, and Linux i386
execution support. All build products and raw captures stay under analysis/tmp.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "analysis/scripts/probe_line_boundary_helper.py"
SOURCE = ROOT / "reconstruction/line_boundary.c"
HEADER = ROOT / "reconstruction/line_boundary.h"
EXE = ROOT / "nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe"
EXE_SHA256 = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"
FUNCTION_SHA256 = "3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f"
ENTRY, END, ORIGINAL_SCRATCH = 0x485C30, 0x485F1B, 0x791C08
CANARY = 0xC0FFEE71
CW = 0x037F
INITIAL_MASK = 0xA0


def load_probe():
    spec = importlib.util.spec_from_file_location("line_boundary_probe_fixtures", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def executable_bytes():
    import pefile
    data = EXE.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXE_SHA256:
        raise AssertionError("NFS3 executable fingerprint changed")
    pe = pefile.PE(data=data)
    if pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.ImageBase != 0x400000:
        raise AssertionError("Unexpected executable architecture or image base")
    body = pe.get_data(ENTRY - 0x400000, END - ENTRY)
    if len(body) != END - ENTRY or body[-3:] != b"\xc2\x04\x00":
        raise AssertionError("Unexpected original function range/return")
    if hashlib.sha256(body).hexdigest() != FUNCTION_SHA256:
        raise AssertionError("Original function byte fingerprint changed")
    return data, body


def make_rows(probe):
    rows = []
    cases = list(probe.CASES) + [
        ("noninteger_left_edge", (-4.0, 0.0, -4.0, 0.0, 2.0, 1.0)),
        ("noninteger_right_edge", (5.0, 0.0, 5.0, 0.0, -1.0, 1.0)),
        ("noninteger_lower_edge", (0.0, -3.0, 0.0, -3.0, 3.0, 2.0)),
        ("noninteger_upper_edge", (0.0, 5.0, 0.0, 5.0, 3.0, -2.0)),
    ]
    rng = random.Random(0x485C30)
    for index in range(128):
        values = tuple(probe.f32(rng.uniform(-8.0, 8.0)) for _ in range(6))
        while values[2] == values[4]:
            values = values[:2] + tuple(probe.f32(rng.uniform(-8.0, 8.0)) for _ in range(4))
        cases.append((f"seeded_finite_{index:03d}", values))
    for name, values in cases:
        for policy in probe.POLICIES:
            rows.append({"case": name, "policy": policy,
                         "values": tuple(probe.f32(x) for x in values),
                         "bounds": probe.RECTANGLE,
                         "mask": probe.INITIAL_MASK, "cw": probe.CONTROL_WORD})
    return rows


def record(row):
    # Two identical writable snapshots. Each region has independent guard words.
    floats = row["values"] + row["bounds"]
    data = bytearray(88)
    for offset in (0, 12, 16, 36, 40, 60, 80, 84):
        struct.pack_into("<I", data, offset, CANARY)
    struct.pack_into("<2f", data, 4, *floats[:2])
    struct.pack_into("<4f", data, 20, *floats[2:6])
    struct.pack_into("<4f", data, 44, *floats[6:10])
    data[64:68] = b"\x5a\x5a\x5a\xa7"
    data[69] = 0xA7
    struct.pack_into("<B", data, 68, row["mask"])
    struct.pack_into("<I", data, 72, row["policy"])
    struct.pack_into("<H", data, 76, row["cw"])
    return bytes(data)


def harness_asm(original_path: Path, rows: list[dict]) -> str:
    count = len(rows)
    # Per-implementation snapshot: candidate @4, line @20, bounds @44,
    # mask @68, policy @72, CW @76, trailing guards @80/@84.
    return f'''.intel_syntax noprefix
.section .text
.global _start
_start:
 mov dword ptr [{ORIGINAL_SCRATCH:#x}],0
 mov dword ptr [{ORIGINAL_SCRATCH+4:#x}],0
 mov dword ptr [gLineBoundaryCandidate_00791c08],0
 mov dword ptr [gLineBoundaryCandidate_00791c08+4],0
 mov esi,offset inputs
 mov [input_ptr],esi
 mov dword ptr [out_ptr],offset output
 mov dword ptr [remaining],{count}
loop_rows:
 mov esi,[input_ptr]
 mov ecx,22
 mov edi,offset original_snapshot
 rep movsd
 mov esi,[input_ptr]
 mov ecx,22
 mov edi,offset c_snapshot
 rep movsd
 mov eax,[input_ptr]
 mov [row_ptr],eax
 add eax,88
 mov [input_ptr],eax
 mov edi,[out_ptr]
 fninit
 fldcw word ptr [original_snapshot+76]
 mov eax,offset original_snapshot+4
 lea edx,[original_snapshot+20]
 lea ebx,[original_snapshot+44]
 mov ecx,[original_snapshot+72]
 push offset original_snapshot+68
 call original_fn
 mov edi,[out_ptr]
 mov ebp,eax
 xor eax,eax
 test ebp,ebp
 jz 2f
 mov eax,1
 cmp ebp,{ORIGINAL_SCRATCH:#x}
 je 2f
 mov eax,2
2:
 mov [edi],eax
 mov eax,dword ptr [{ORIGINAL_SCRATCH:#x}]
 mov [edi+4],eax
 mov eax,dword ptr [{ORIGINAL_SCRATCH+4:#x}]
 mov [edi+8],eax
 movzx eax,byte ptr [original_snapshot+68]
 mov [edi+12],eax
 call check_original_guards
 mov [edi+16],eax
 call check_original_inputs
 mov [edi+20],eax
 fnstcw word ptr [edi+24]
 fnstsw ax
 mov [edi+26],ax
 fninit
 fldcw word ptr [c_snapshot+76]
 push offset c_snapshot+68
 push dword ptr [c_snapshot+72]
 lea eax,[c_snapshot+44]
 push eax
 lea eax,[c_snapshot+20]
 push eax
 lea eax,[c_snapshot+4]
 push eax
 call _Z_placeholder
 add esp,20
 mov edi,[out_ptr]
 mov ebp,eax
 xor eax,eax
 test ebp,ebp
 jz 3f
 mov eax,1
 cmp ebp,offset gLineBoundaryCandidate_00791c08
 je 3f
 mov eax,2
3:
 mov [edi+28],eax
 mov eax,dword ptr [gLineBoundaryCandidate_00791c08]
 mov [edi+32],eax
 mov eax,dword ptr [gLineBoundaryCandidate_00791c08+4]
 mov [edi+36],eax
 movzx eax,byte ptr [c_snapshot+68]
 mov [edi+40],eax
 call check_c_guards
 mov [edi+44],eax
 call check_c_inputs
 mov [edi+48],eax
 fnstcw word ptr [edi+52]
 fnstsw ax
 mov [edi+54],ax
 add dword ptr [out_ptr],56
 dec dword ptr [remaining]
 jnz loop_rows
 mov eax,4
 mov ebx,1
 mov ecx,offset output
 mov edx,{count*56}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80

check_original_guards:
 xor eax,eax
 cmp dword ptr [original_snapshot],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+12],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+16],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+36],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+40],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+60],{CANARY:#x}
 jne 1f
 cmp byte ptr [original_snapshot+64],0x5a
 jne 1f
 cmp byte ptr [original_snapshot+65],0x5a
 jne 1f
 cmp byte ptr [original_snapshot+66],0x5a
 jne 1f
 cmp byte ptr [original_snapshot+67],0xa7
 jne 1f
 cmp byte ptr [original_snapshot+69],0xa7
 jne 1f
 cmp dword ptr [original_snapshot+80],{CANARY:#x}
 jne 1f
 cmp dword ptr [original_snapshot+84],{CANARY:#x}
 jne 1f
 mov eax,1
1: ret
check_c_guards:
 xor eax,eax
 cmp dword ptr [c_snapshot],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+12],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+16],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+36],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+40],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+60],{CANARY:#x}
 jne 1f
 cmp byte ptr [c_snapshot+64],0x5a
 jne 1f
 cmp byte ptr [c_snapshot+65],0x5a
 jne 1f
 cmp byte ptr [c_snapshot+66],0x5a
 jne 1f
 cmp byte ptr [c_snapshot+67],0xa7
 jne 1f
 cmp byte ptr [c_snapshot+69],0xa7
 jne 1f
 cmp dword ptr [c_snapshot+80],{CANARY:#x}
 jne 1f
 cmp dword ptr [c_snapshot+84],{CANARY:#x}
 jne 1f
 mov eax,1
1: ret
check_original_inputs:
 mov eax,1
 mov esi,[row_ptr]
.set input_offset,4
.rept 2
 mov ebx,[original_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 2f
 .set input_offset,input_offset+4
.endr
.set input_offset,20
.rept 4
 mov ebx,[original_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 2f
 .set input_offset,input_offset+4
.endr
.set input_offset,44
.rept 4
 mov ebx,[original_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 2f
 .set input_offset,input_offset+4
.endr
 ret
2: xor eax,eax
 ret
check_c_inputs:
 mov eax,1
 mov esi,[row_ptr]
.set input_offset,4
.rept 2
 mov ebx,[c_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 3f
 .set input_offset,input_offset+4
.endr
.set input_offset,20
.rept 4
 mov ebx,[c_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 3f
 .set input_offset,input_offset+4
.endr
.set input_offset,44
.rept 4
 mov ebx,[c_snapshot+input_offset]
 cmp ebx,[esi+input_offset]
 jne 3f
 .set input_offset,input_offset+4
.endr
 ret
3: xor eax,eax
 ret

.section .data
remaining: .long 0
input_ptr: .long 0
row_ptr: .long 0
out_ptr: .long 0
inputs: .incbin "INPUTS_PATH"
original_snapshot: .space 88
c_snapshot: .space 88
output: .space {count*56},0
.section .intersection,"ax"
.global original_fn
original_fn: .incbin "{original_path}"
.section .scratch,"aw"
.space 8,0
.section .note.GNU-stack,"",@progbits
'''


class LineBoundaryDifferential(unittest.TestCase):
    def test_original_vs_maintained(self):
        for tool in ("gcc", "as", "ld"):
            self.assertIsNotNone(shutil.which(tool), f"required tool missing: {tool}")
        self.assertTrue(SOURCE.is_file(), f"maintained source missing: {SOURCE}")
        self.assertTrue(HEADER.is_file(), f"maintained header missing: {HEADER}")
        original_binary, body = executable_bytes()
        probe = load_probe()
        rows = make_rows(probe)
        (ROOT / "analysis/tmp").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="line-boundary-diff-", dir=ROOT / "analysis/tmp") as tmp:
            work = Path(tmp)
            fn_path, inputs_path = work / "original.bin", work / "inputs.bin"
            fn_path.write_bytes(body)
            inputs_path.write_bytes(b"".join(record(row) for row in rows))
            source = SOURCE
            obj = work / "maintained.o"
            subprocess.run(["gcc", "-m32", "-std=c11", "-O0", "-mfpmath=387", "-fno-fast-math",
                            "-ffp-contract=off", "-frounding-math", "-fexcess-precision=standard",
                            "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-fno-pic",
                            "-fno-stack-protector", "-fno-asynchronous-unwind-tables", "-c",
                            str(source), "-o", str(obj)], cwd=ROOT, check=True)
            asm = harness_asm(fn_path, rows).replace("INPUTS_PATH", str(inputs_path))
            # Resolve the C symbol through GCC's object symbol table, without a runtime library.
            symbols = subprocess.run(["nm", "-g", str(obj)], text=True, capture_output=True, check=True).stdout
            symbol = next((line.split()[-1] for line in symbols.splitlines()
                           if line.rstrip().endswith(" T Nfs3LineBoundaryCandidate_00485c30")), None)
            self.assertIsNotNone(symbol, f"C function symbol missing from object: {symbols}")
            asm = asm.replace("_Z_placeholder", symbol)
            asm_path, asm_obj, elf = work / "harness.s", work / "harness.o", work / "differential"
            asm_path.write_text(asm)
            subprocess.run(["as", "--32", "-o", str(asm_obj), str(asm_path)], check=True)
            subprocess.run(["ld", "-m", "elf_i386", "-Ttext=0x100000", "-Tdata=0x200000",
                            f"--section-start=.intersection={ENTRY:#x}",
                            f"--section-start=.scratch={ORIGINAL_SCRATCH:#x}",
                            "-o", str(elf), str(asm_obj), str(obj)], check=True)
            raw = subprocess.run([str(elf)], capture_output=True, check=True, timeout=10).stdout
            self.assertEqual(len(raw), len(rows) * 56)
        evidence = {"executable_sha256": hashlib.sha256(original_binary).hexdigest(),
                    "original_function_sha256": hashlib.sha256(body).hexdigest(),
                    "function_va": f"0x{ENTRY:08x}", "row_count": len(rows),
                    "functional_equivalence_fields": ["return_class", "scratch_bits", "mask", "guards_intact", "inputs_unchanged"],
                    "fpu_state_equivalence_claimed": False, "rows": []}
        cw_differences, sw_differences = [], []
        for index, row in enumerate(rows):
            vals = struct.unpack_from("<IIIIIIHHIIIIIIHH", raw, index * 56)
            (orig_status, orig0, orig1, origmask, origguards, orig_unchanged, origcw, origsw,
             c_status, c0, c1, cmask, cguards, c_unchanged, ccw, csw) = vals
            input_bits = [f"0x{struct.unpack('<I', struct.pack('<f', value))[0]:08x}"
                          for value in row["values"] + row["bounds"]]
            result = {"case": row["case"], "policy": row["policy"],
                      "candidate_line_bounds_input_bits": input_bits,
                      "original": {"return_class": orig_status, "accepted": orig_status != 0, "scratch_bits": [f"0x{orig0:08x}", f"0x{orig1:08x}"],
                                   "mask": origmask, "guards_intact": bool(origguards), "inputs_unchanged": bool(orig_unchanged),
                                   "cw": f"0x{origcw:04x}", "sw": f"0x{origsw:04x}"},
                      "maintained": {"return_class": c_status, "accepted": c_status != 0, "scratch_bits": [f"0x{c0:08x}", f"0x{c1:08x}"],
                                     "mask": cmask, "guards_intact": bool(cguards), "inputs_unchanged": bool(c_unchanged),
                                     "cw": f"0x{ccw:04x}", "sw": f"0x{csw:04x}"}}
            evidence["rows"].append(result)
            self.assertEqual(orig_status, c_status, row)
            self.assertEqual((orig0, orig1), (c0, c1), row)
            self.assertEqual(origmask, cmask, row)
            self.assertTrue(origguards and cguards, row)
            self.assertTrue(orig_unchanged, ("original inputs changed", row))
            self.assertTrue(c_unchanged, ("maintained inputs changed", row))
            if origcw != ccw:
                cw_differences.append({"case": row["case"], "policy": row["policy"],
                                       "original": f"0x{origcw:04x}", "maintained": f"0x{ccw:04x}"})
            if origsw != csw:
                sw_differences.append({"case": row["case"], "policy": row["policy"],
                                       "original": f"0x{origsw:04x}", "maintained": f"0x{csw:04x}"})
        evidence["cw_differences"] = cw_differences
        evidence["sw_differences"] = sw_differences
        outdir = ROOT / "analysis/tmp"
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "line-boundary-differential.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    unittest.main()
