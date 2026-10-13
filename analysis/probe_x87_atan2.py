"""Probe unchanged NFS3 atan2 bytes in a freestanding native Linux i386 ELF.

Requires pefile, GNU as/ld, and Linux i386 support. No Wine or game launch.
The original executable is read only; the temporary harness is removed on exit.
"""
import argparse
import hashlib
import json
import math
import pathlib
import random
import struct
import subprocess
import tempfile

EXPECTED_SHA256 = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'


def bits(value):
    return struct.unpack('<Q', struct.pack('<d', value))[0]


def is_nan(value):
    return value & 0x7ff0000000000000 == 0x7ff0000000000000 and bool(value & 0xfffffffffffff)


def main():
    import pefile
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit('Unexpected executable fingerprint; revalidate addresses first')
    pe = pefile.PE(str(args.binary))
    cases = []
    for x in [0.5, 1.0, 2.0]:
        for sx in [1, -1]:
            for sy in [1, -1]:
                cases.append((f'quadrant_x{x}_{sx}_{sy}', bits(sx*x), bits(sy)))
    for k in range(16):
        boundary = (k + 0.5)/16
        for label, y in [('below', math.nextafter(boundary, 0)), ('tie', boundary),
                         ('above', math.nextafter(boundary, 1))]:
            cases.append((f'grid_{k}_{label}', bits(1.0), bits(y)))
    special = [bits(0.0), bits(-0.0), bits(1.0), bits(-1.0), bits(math.inf),
               bits(-math.inf), 0x7ff8000000001234, 0x7ff0000000001234]
    for i, x in enumerate(special):
        for j, y in enumerate(special):
            cases.append((f'special_{i}_{j}', x, y))
    for i, x in enumerate([1, 0x0010000000000000, 0x7fefffffffffffff]):
        for j, y in enumerate([1, 0x0010000000000000, 0x7fefffffffffffff]):
            for sign in [0, 1 << 63]:
                cases.append((f'extreme_{i}_{j}_{sign >> 63}', x, y | sign))
    rng = random.Random(0x51f320)
    for i in range(1024):
        def operand():
            return (rng.getrandbits(1) << 63) | (rng.randrange(1, 2047) << 52) | rng.getrandbits(52)
        cases.append((f'random_{i}', operand(), operand()))
    controls = [0x037f, 0x027f, 0x077f, 0x0b7f, 0x0f7f]
    vectors = [(name, x, y, cw) for name, x, y in cases for cw in controls]
    with tempfile.TemporaryDirectory(prefix='nfs3-atan2-') as temp:
        work = pathlib.Path(temp)
        for name, start, end in [('angle', 0x51f320, 0x51f520),
                                 ('division', 0x5269d4, 0x526baf),
                                 ('constants', 0x56cb28, 0x56cd1c)]:
            (work/f'{name}.bin').write_bytes(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase, end-start))
        (work/'vectors.bin').write_bytes(b''.join(struct.pack('<QQI', x, y, cw) for _, x, y, cw in vectors))
        assembly = '''.intel_syntax noprefix
.section .text
.global _start
_start:
 mov edi,offset vectors
 mov esi,offset results
 mov ebp,COUNT
case_loop:
 fninit
 fldcw word ptr [edi+16]
 fnstcw word ptr [esi+16]
 fld qword ptr [edi+8]
 fld qword ptr [edi]
 mov eax,0x12345678
 mov ecx,0x23456789
 mov edx,0x3456789a
 mov ebx,0x456789ab
 mov [saved_esp],esp
 mov [saved_esi],esi
 mov [saved_edi],edi
 mov [saved_ebp],ebp
 call angle
 pushad
 mov esi,[saved_esi]
 mov edi,[saved_edi]
 mov ebp,[saved_ebp]
 mov dword ptr [esi+20],0
 cmp dword ptr [esp+28],0x12345678
 je eax_ok
 or dword ptr [esi+20],1
eax_ok:
 cmp dword ptr [esp+24],0x23456789
 je ecx_ok
 or dword ptr [esi+20],2
ecx_ok:
 cmp dword ptr [esp+20],0x3456789a
 je edx_ok
 or dword ptr [esi+20],4
edx_ok:
 cmp dword ptr [esp+16],0x456789ab
 je ebx_ok
 or dword ptr [esi+20],8
ebx_ok:
 cmp [esp+4],esi
 je esi_ok
 or dword ptr [esi+20],16
esi_ok:
 cmp [esp],edi
 je edi_ok
 or dword ptr [esi+20],32
edi_ok:
 cmp [esp+8],ebp
 je ebp_ok
 or dword ptr [esi+20],64
ebp_ok:
 mov eax,[saved_esp]
 cmp [esp+12],eax
 je esp_ok
 or dword ptr [esi+20],128
esp_ok:
 add esp,32
 fnstcw word ptr [esi+18]
 fnstsw word ptr [esi+24]
 fstp qword ptr [esi]
 fninit
 fldcw word ptr [edi+16]
 fld qword ptr [edi+8]
 fld qword ptr [edi]
 fpatan
 fnstsw word ptr [esi+26]
 fstp qword ptr [esi+8]
 add edi,20
 add esi,32
 dec ebp
 jnz case_loop
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,RESULT_SIZE
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80
.section .angle,"ax"
angle: .incbin "ANGLE"
.section .division,"ax"
.incbin "DIVISION"
.section .constants,"a"
.incbin "CONSTANTS"
.section .data
saved_esp: .long 0
saved_esi: .long 0
saved_edi: .long 0
saved_ebp: .long 0
vectors: .incbin "VECTORS"
results: .space RESULT_SIZE
'''
        for key, value in [('COUNT', str(len(vectors))), ('RESULT_SIZE', str(32*len(vectors))),
                           *[(n.upper(), str(work/f'{n}.bin')) for n in ['angle', 'division', 'constants', 'vectors']]]:
            assembly = assembly.replace(key, value)
        (work/'probe.s').write_text(assembly)
        subprocess.run(['as', '--32', '-o', str(work/'probe.o'), str(work/'probe.s')], check=True)
        subprocess.run(['ld', '-m', 'elf_i386', '-Ttext=0x100000', '-Tdata=0x200000',
                        '--section-start=.angle=0x51f320', '--section-start=.division=0x5269d4',
                        '--section-start=.constants=0x56cb28', '-o', str(work/'probe'), str(work/'probe.o')], check=True)
        output = subprocess.run([str(work/'probe')], capture_output=True, timeout=10, check=True).stdout
    if len(output) != len(vectors)*32:
        raise RuntimeError('Incomplete harness output')
    rows = []
    for i, (name, x, y, cw) in enumerate(vectors):
        actual, reference, before, after, registers, status, refstatus = struct.unpack_from('<QQHHIHH', output, 32*i)
        equal = actual == reference
        both_nan = is_nan(actual) and is_nan(reference)
        rows.append(dict(case=name, x=f'{x:016x}', y=f'{y:016x}', control=f'{cw:04x}',
                         actual=f'{actual:016x}', fpatan=f'{reference:016x}', bit_equal=equal,
                         both_nan=both_nan, ulp_distance=None if both_nan else abs(actual-reference),
                         control_preserved=before == after == cw, register_failure_mask=registers,
                         status=f'{status:04x}', fpatan_status=f'{refstatus:04x}'))
    mismatches = [r for r in rows if not r['bit_equal'] and not r['both_nan']]
    digest_after = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    if digest_after != digest:
        raise RuntimeError('Input executable changed during the probe')
    report = dict(sha256=digest, method='Native Linux i386 ELF; unchanged extracted routine, division helper, and constants at original virtual addresses; synthetic binary64 inputs; independent hardware FPATAN instruction reference under same caller control word; both results stored to binary64.',
                  source_sha256_after=digest_after,
                  code_ranges=['0051f320..0051f51f', '005269d4..00526bae'], constants_range='0056cb28..0056cd1b',
                  control_words=[f'{cw:04x}' for cw in controls], case_count=len(rows),
                  input_pair_count=len(cases), non_nan_bit_mismatch_count=len(mismatches),
                  maximum_observed_ulp_distance=max((r['ulp_distance'] for r in mismatches), default=0),
                  control_failure_count=sum(not r['control_preserved'] for r in rows),
                  register_failure_count=sum(bool(r['register_failure_mask']) for r in rows),
                  register_mask_bits='0:EAX,1:ECX,2:EDX,3:EBX,4:ESI,5:EDI,6:EBP,7:ESP',
                  nan_bit_mismatch_count=sum(r['both_nan'] and not r['bit_equal'] for r in rows),
                  mismatches=mismatches, directed_cases=[r for r in rows if not r['case'].startswith('random_')],
                  limits='Sampled local native arithmetic evidence, not gameplay/Wine evidence or exhaustive accuracy proof. FPATAN is a hardware comparison, not a correctly-rounded mathematical oracle. Binary64 inputs are loaded into x87 first, so subnormal doubles become normal extended values and signaling NaNs may be quieted before entry. No raw extended subnormal, unsupported encoding, unmasked exception, extra live x87 stack, or raw 80-bit result comparison. Status words recorded before final double stores but not asserted equal. ULP distance is meaningful for these same-sign finite result pairs; signed zero and NaN are retained as raw bits.')
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ['case_count', 'non_nan_bit_mismatch_count', 'maximum_observed_ulp_distance', 'control_failure_count', 'register_failure_count', 'nan_bit_mismatch_count']}))


if __name__ == '__main__':
    main()
