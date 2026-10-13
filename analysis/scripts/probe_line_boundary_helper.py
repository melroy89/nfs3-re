"""Execute the unchanged NFS III line-boundary helper in a native i386 harness.

The probe exercises only 00485c30 with synthetic pointers and inputs. It does
not start Wine/gameplay or alter the executable. Requires pefile, GNU as/ld and
Linux i386 execution support.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile

EXPECTED_SHA256 = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
ENTRY = 0x485c30
END = 0x485f1b  # Includes the RET 4 immediate.
SCRATCH = 0x791c08
RECTANGLE = (-1.0, -2.0, 3.0, 4.0)  # yMin, xMin, yMax, xMax
CASES = [
    ('horizontal_left_cross', (-4.0, 0.0, -4.0, 0.0, 2.0, 0.0)),
    ('horizontal_right_cross', (5.0, 0.0, 5.0, 0.0, 0.0, 0.0)),
    ('vertical_lower_cross', (0.0, -3.0, 0.0, -3.0, 0.0, 2.0)),
    ('vertical_upper_cross', (0.0, 4.0, 0.0, 4.0, 0.0, 0.0)),
    ('diagonal_hits_lower_corner', (-4.0, -3.0, -4.0, -3.0, 2.0, 3.0)),
    ('diagonal_intersects_left_edge', (-4.0, -2.0, -4.0, -2.0, 2.0, 4.0)),
    ('diagonal_enters_left_edge', (-4.0, 1.0, -4.0, 1.0, 2.0, -2.0)),
    ('diagonal_enters_lower_edge', (-4.0, -5.0, -4.0, -5.0, 2.0, 1.0)),
    ('diagonal_enters_upper_edge', (-4.0, 5.0, -4.0, 5.0, 2.0, 2.0)),
    ('extension_intersection_beyond_segment', (-5.0, 0.0, -5.0, 0.0, -4.0, 1.0)),
    ('parallel_line_outside_y_bounds', (-4.0, 5.0, -4.0, 5.0, 4.0, 5.0)),
    ('vertical_segment_on_x_midline', (0.0, -4.0, 0.0, -4.0, 0.0, 4.0)),
    ('vertical_positive_zero_delta', (0.0, -3.0, 0.0, -3.0, -0.0, 2.0)),
    ('endpoint_exactly_on_left_edge', (-2.0, 0.0, -2.0, 0.0, 2.0, 0.0)),
    ('endpoint_exactly_on_lower_edge', (0.0, -1.0, 0.0, -1.0, 0.0, 2.0)),
    ('horizontal_segment_on_y_midline', (-4.0, 1.0, -4.0, 1.0, 4.0, 1.0)),
    ('point_on_left_boundary', (-2.0, 0.0, -2.0, 0.0, -2.0, 0.0)),
    ('zero_length_outside', (-5.0, 5.0, -5.0, 5.0, -5.0, 5.0)),
    ('nan_candidate_x', (float('nan'), 0.0, float('nan'), 0.0, 1.0, 1.0)),
    ('nan_candidate_y', (0.0, float('nan'), 0.0, float('nan'), 1.0, 1.0)),
]
POLICIES = (0, 1)
INITIAL_MASK = 0xA0
CONTROL_WORD = 0x037F
CASE_BYTES = 52
RESULT_BYTES = 20
EXPECTED = {
    'horizontal_left_cross': ((-2.0, 0.0), 0x04),
    'horizontal_right_cross': ((4.0, 0.0), 0x08),
    'vertical_lower_cross': ((0.0, -1.0), 0x01),
    'vertical_upper_cross': ((0.0, 3.0), 0x02),
    'diagonal_hits_lower_corner': ((-2.0, -1.0), 0x04),
    'diagonal_enters_lower_edge': ((0.0, -1.0), 0x01),
    'diagonal_enters_upper_edge': ((0.0, 3.0), 0x02),
}


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def json_number(value):
    if math.isnan(value):
        return 'NaN'
    if math.isinf(value):
        return '-Infinity' if value < 0 else 'Infinity'
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    import pefile
    original = args.binary.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit('Unexpected executable fingerprint; revalidate addresses first')
    pe = pefile.PE(data=original)
    if pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.ImageBase != 0x400000:
        raise SystemExit('Unexpected PE architecture or image base; revalidate addresses first')
    code = pe.get_data(ENTRY - pe.OPTIONAL_HEADER.ImageBase, END - ENTRY)
    if len(code) != END - ENTRY or code[-3:] != b'\xc2\x04\x00':
        raise SystemExit('Unexpected function extent or return instruction')

    rows = []
    for name, values in CASES:
        point = values[:2]
        line = values[2:]
        for policy in POLICIES:
            rows.append((name, tuple(f32(x) for x in point + line), policy))

    vectors = bytearray()
    metadata = []
    for name, values, policy in rows:
        floats = values + RECTANGLE
        vectors.extend(struct.pack('<10fIII', *floats, policy, INITIAL_MASK, CONTROL_WORD))
        metadata.append({
            'case': name,
            'policy': policy,
            'point': [json_number(x) for x in values[:2]],
            'line': [json_number(x) for x in values[2:]],
            'bounds_ymin_xmin_ymax_xmax': list(RECTANGLE),
            'initial_mask': INITIAL_MASK,
            'control_word': CONTROL_WORD,
        })

    with tempfile.TemporaryDirectory(prefix='nfs3-line-boundary-') as temp:
        work = Path(temp)
        (work / 'function.bin').write_bytes(code)
        (work / 'vectors.bin').write_bytes(vectors)
        assembly = f'''.intel_syntax noprefix
.section .text
.global _start
_start:
 mov esi,offset vectors
 mov edi,offset results
 mov ecx,{len(rows)}
case_loop:
 fninit
 fldcw word ptr [esi+48]
 mov eax,[esi+44]
 mov [mask_byte],al
 mov eax,esi
 lea edx,[esi+8]
 lea ebx,[esi+24]
 mov ecx,[esi+40]
 push offset mask_byte
 call intersection
 mov [edi],eax
 mov eax,dword ptr [{SCRATCH:#x}]
 mov [edi+4],eax
 mov eax,dword ptr [{SCRATCH+4:#x}]
 mov [edi+8],eax
 movzx eax,byte ptr [mask_byte]
 mov [edi+12],eax
 fnstcw word ptr [edi+16]
 fnstsw ax
 mov [edi+18],ax
 add esi,{CASE_BYTES}
 add edi,{RESULT_BYTES}
 dec dword ptr [remaining]
 jnz case_loop
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,{len(rows)*RESULT_BYTES}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80

.section .data
remaining: .long {len(rows)}
mask_byte: .byte 0
.align 4
vectors: .incbin "{work/'vectors.bin'}"
results: .space {len(rows)*RESULT_BYTES},0

.section .intersection,"ax"
.global intersection
intersection: .incbin "{work/'function.bin'}"

.section .scratch,"aw"
.space 0x20,0
'''
        (work / 'probe.s').write_text(assembly)
        subprocess.run(['as', '--32', '-o', str(work / 'probe.o'), str(work / 'probe.s')], check=True)
        command = [
            'ld', '-m', 'elf_i386', '-Ttext=0x100000', '-Tdata=0x200000',
            f'--section-start=.intersection={ENTRY:#x}',
            f'--section-start=.scratch={SCRATCH:#x}',
        ]
        subprocess.run(command + ['-o', str(work / 'probe'), str(work / 'probe.o')], check=True)
        output = subprocess.run([str(work / 'probe')], capture_output=True, check=True, timeout=10).stdout

    if len(output) != len(rows) * RESULT_BYTES:
        raise RuntimeError('Incomplete helper output')
    results = []
    for index, meta in enumerate(metadata):
        returned, c0_bits, c1_bits, mask, cw, sw = struct.unpack_from('<IIIIHH', output, index * RESULT_BYTES)
        c0, c1 = struct.unpack('<ff', struct.pack('<II', c0_bits, c1_bits))
        if meta['policy'] == 0 and returned != SCRATCH:
            raise AssertionError(f"Policy-zero call unexpectedly returned null: {meta['case']}")
        if mask & INITIAL_MASK != INITIAL_MASK:
            raise AssertionError(f"Incoming mask bits were not preserved: {meta['case']}")
        if mask & ~0xAF:
            raise AssertionError(f"Unexpected mask bits: {meta['case']}")
        if meta['case'] in EXPECTED:
            expected_components, expected_bits = EXPECTED[meta['case']]
            if meta['policy'] == 1:
                if returned != SCRATCH or (c0, c1) != expected_components or (mask & 0x0F) != expected_bits:
                    raise AssertionError(f"Unexpected finite boundary result for {meta['case']}")
        results.append({
            **meta,
            'return_pointer': f'0x{returned:08x}',
            'accepted_pointer': returned != 0,
            'candidate_components': [json_number(c0), json_number(c1)],
            'candidate_bits': [f'0x{c0_bits:08x}', f'0x{c1_bits:08x}'],
            'mask_after': f'0x{mask:02x}',
            'control_word_after': f'0x{cw:04x}',
            'status_word_after': f'0x{sw:04x}',
        })
    report = {
        'sha256': digest,
        'method': 'Native Linux i386 execution of unchanged PE bytes for 00485c30; synthetic inputs; no stubs, Wine, or gameplay.',
        'function_va': f'0x{ENTRY:08x}',
        'function_bytes': len(code),
        'function_sha256': hashlib.sha256(code).hexdigest(),
        'function_end_exclusive': f'0x{END:08x}',
        'cases': results,
        'limitations': [
            'Only the helper is executed; wrapper and callers are not run.',
            'Pointers and bounds are valid synthetic data; aliasing and caller reachability are not tested.',
            'The single masked x87 control word does not establish unmasked-exception behavior or all rounding modes.',
            'Returned candidate values are observations, not proof of canonical clipping or visual correctness.',
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'sha256': digest, 'cases': len(results), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
