"""Execute unchanged NFS3 power/helper bytes in a freestanding Linux i386 ELF.

Requires pefile, GNU as/ld/objdump, Linux i386 support. The exception dispatcher
is replaced by a selector recorder returning a quiet NaN; callbacks are untested.
"""
import argparse
import hashlib
import json
import math
import pathlib
import random
import re
import struct
import subprocess
import tempfile

EXPECTED_SHA256 = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
RANGES = [('power', 0x523332, 0x523488), ('exponential', 0x4f80b6, 0x4f8116),
          ('division', 0x5269d4, 0x526baf), ('exception', 0x52b523, 0x52b5aa),
          ('bounds', 0x56716c, 0x56717c), ('flag', 0x567858, 0x567859),
          ('constants', 0x56ccc0, 0x56cd1c)]
SENTINEL = 0x7ff800000000cafe


def bits(value):
    return struct.unpack('<Q', struct.pack('<d', value))[0]


def value(raw):
    return struct.unpack('<d', struct.pack('<Q', raw))[0]


def ordered(raw):
    return (~raw & ((1 << 64)-1)) if raw >> 63 else raw | (1 << 63)


def main():
    import pefile
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    original = args.binary.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit('Unexpected executable fingerprint; revalidate addresses first')
    pe = pefile.PE(data=original)
    cases = []

    def add(name, base, exponent):
        cases.append((name, bits(base), bits(exponent)))

    for exponent in range(3, 19):
        add(f'fog_2_to_{exponent}', 2., exponent)
    for base in [0.99999, 1.00001, -0.99999, -1.00001]:
        for exponent in [-65537, -65536, -65535, 65535, 65536, 65537]:
            add(f'integer_boundary_{base}_{exponent}', base, exponent)
    for base in [-2., -1., -0.5]:
        for exponent in [-4., -3., -0.5, 0., 0.5, 3., 4.]:
            add(f'negative_{base}_{exponent}', base, exponent)
    for base in [0., -0.]:
        for exponent in [-3., -2., -0.5, 0., 0.5, 2., 3.]:
            add(f'zero_{bits(base):016x}_{exponent}', base, exponent)
    for base in [0.25, 0.5, 1., 2., 10.]:
        for exponent in [-3.5, -0.5, 0., 0.5, 3.5]:
            add(f'fractional_{base}_{exponent}', base, exponent)
    special = [bits(0.), bits(-0.), bits(0.5), bits(1.), bits(-1.), bits(2.),
               bits(-2.), bits(math.inf), bits(-math.inf), 0x7ff8000000001234,
               0x7ff0000000001234]
    for i, base in enumerate(special):
        for j, exponent in enumerate(special):
            cases.append((f'special_{i}_{j}', base, exponent))
    for base, exponent in [(2., 1023.), (2., 1024.), (2., -1022.), (2., -1074.),
                            (2., -1075.), (0.5, -1024.), (1e308, 2.),
                            (1e-308, 2.), (-1e308, 3.), (-1e308, -3.),
                            (10., 308.5), (10., -323.5), (2., 65536.), (2., -65536.)]:
        add(f'extreme_{base}_{exponent}', base, exponent)
    rng = random.Random(0x523332)
    for i in range(256):
        add(f'ordinary_{i}', 2**rng.uniform(-8, 8), rng.uniform(-16, 16))
    controls = [0x037f, 0x027f, 0x077f, 0x0b7f, 0x0f7f]
    vectors = [(name, base, exponent, cw, flag) for name, base, exponent in cases
               for cw in controls for flag in [0, 1]]
    audit = []
    with tempfile.TemporaryDirectory(prefix='nfs3-power-') as temp:
        work = pathlib.Path(temp)
        for name, start, end in RANGES:
            data = pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase, end-start)
            assert len(data) == end-start
            path = work/f'{name}.bin'
            path.write_bytes(data)
            record = dict(name=name, start=f'{start:08x}', end_inclusive=f'{end-1:08x}',
                          sha256=hashlib.sha256(data).hexdigest())
            if name in ['power', 'exponential', 'division', 'exception']:
                dis = subprocess.run(['objdump', '-D', '-b', 'binary', '-mi386', '-Mintel',
                                      f'--adjust-vma={start}', str(path)], capture_output=True,
                                     text=True, check=True).stdout
                record['direct_calls'] = re.findall(r'^\s*([0-9a-f]+):.*\bcall\s+(0x[0-9a-f]+)', dis, re.M)
            audit.append(record)
        (work/'vectors.bin').write_bytes(b''.join(struct.pack('<QQII', b, e, cw, f)
                                                for _, b, e, cw, f in vectors))
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
 mov eax,[edi+20]
 mov [flag],al
 mov dword ptr [selector],0
 mov dword ptr [dispatch_count],0
 mov [saved_esp],esp
 fld qword ptr [edi+8]
 fld qword ptr [edi]
 call power
 fnstsw word ptr [esi+16]
 fnstcw word ptr [esi+18]
 fstp qword ptr [esi]
 mov eax,[selector]
 mov [esi+8],eax
 mov eax,[dispatch_count]
 mov [esi+12],eax
 mov eax,esp
 sub eax,[saved_esp]
 mov [esi+20],eax
 add edi,24
 add esi,24
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
.section .dispatcher,"ax"
 mov [selector],eax
 inc dword ptr [dispatch_count]
 fld qword ptr [sentinel]
 ret
.section .unexpected,"ax"
 ud2
.section .data
selector: .long 0
dispatch_count: .long 0
saved_esp: .long 0
sentinel: .quad 0x7ff800000000cafe
vectors: .incbin "VECTORS"
results: .space RESULT_SIZE
'''
        for name, _, _ in RANGES:
            attrs = 'aw' if name == 'flag' else 'ax' if name in ['power', 'exponential', 'division', 'exception'] else 'a'
            assembly += f'.section .{name},"{attrs}"\n{name}: .incbin "{work}/{name}.bin"\n'
        assembly = assembly.replace('COUNT', str(len(vectors))).replace('RESULT_SIZE', str(24*len(vectors))).replace('VECTORS', str(work/'vectors.bin'))
        (work/'probe.s').write_text(assembly)
        subprocess.run(['as', '--32', '-o', str(work/'probe.o'), str(work/'probe.s')], check=True)
        subprocess.run(['ld', '-m', 'elf_i386', '-Ttext=0x100000', '-Tdata=0x200000',
                        '--section-start=.dispatcher=0x5243b1', '--section-start=.unexpected=0x51655c',
                        *[f'--section-start=.{n}={a:#x}' for n, a, _ in RANGES],
                        '-o', str(work/'probe'), str(work/'probe.o')], check=True)
        output = subprocess.run([str(work/'probe')], capture_output=True, timeout=30, check=True).stdout
    if len(output) != len(vectors)*24:
        raise RuntimeError('Incomplete harness output')
    rows = []
    for i, (name, base, exponent, cw, flag) in enumerate(vectors):
        actual, selector, calls, status, after, esp_delta = struct.unpack_from('<QIIHHi', output, i*24)
        ref = None
        ulp = None
        # Host math.pow is only a bounded ordinary finite comparison, not an oracle.
        b, e, a = value(base), value(exponent), value(actual)
        eligible = math.isfinite(b) and math.isfinite(e) and b != 0 and abs(e) <= 65537
        if eligible:
            try:
                reference = math.pow(b, e)
                if math.isfinite(reference) and reference != 0 and math.isfinite(a) and not calls:
                    ref = bits(reference)
                    ulp = abs(ordered(ref)-ordered(actual))
            except (ValueError, OverflowError):
                pass
        rows.append(dict(case=name, base=f'{base:016x}', exponent=f'{exponent:016x}',
                         control=f'{cw:04x}', division_flag=flag, actual=f'{actual:016x}',
                         actual_display=repr(a), dispatcher_selector=f'{selector:08x}' if calls else None,
                         dispatcher_calls=calls, status=f'{status:04x}',
                         control_preserved=after == cw, esp_delta=esp_delta,
                         math_pow=f'{ref:016x}' if ref is not None else None, ulp_distance=ulp))
    after_digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    if after_digest != digest:
        raise RuntimeError('Original executable changed during probe')
    compared = [r for r in rows if r['ulp_distance'] is not None and r['control'] == '037f']
    fog_rows = [r for r in rows if r['case'].startswith('fog_')]
    fog_failures = sum(r['actual'] != f'{bits(2. ** value(int(r["exponent"], 16))):016x}'
                       or r['dispatcher_calls'] != 0 for r in fog_rows)
    selectors = sorted({r['dispatcher_selector'] for r in rows if r['dispatcher_calls']})
    flag_differences = sum(rows[i]['actual'] != rows[i+1]['actual'] or
                           rows[i]['dispatcher_selector'] != rows[i+1]['dispatcher_selector']
                           for i in range(0, len(rows), 2))
    report = dict(sha256=digest, source_sha256_after=after_digest,
                  method='Native Linux i386 ELF. Extracted code/data linked at original VAs. ST0=base, ST1=exponent, binary64 input/output. Only the division feature flag is varied in the temporary data copy; original code bytes are unchanged. Dispatcher stub records EAX and FLDs 7ff800000000cafe; unexpected exponential callback 0051655c traps with UD2.',
                  extraction_audit=audit, case_count=len(rows), input_pair_count=len(cases),
                  control_words=[f'{cw:04x}' for cw in controls], division_flags=[0, 1],
                  fog_case_count=len(fog_rows), fog_exact_result_failure_count=fog_failures,
                  dispatcher_selectors=selectors, dispatcher_case_count=sum(bool(r['dispatcher_calls']) for r in rows),
                  flag_result_or_selector_difference_count=flag_differences,
                  control_failure_count=sum(not r['control_preserved'] for r in rows),
                  stack_pointer_failure_count=sum(r['esp_delta'] != 0 for r in rows),
                  nearest_extended_math_pow_comparison_count=len(compared),
                  nearest_extended_maximum_ulp_distance=max(r['ulp_distance'] for r in compared),
                  limits='Sampled local native arithmetic evidence only; no gameplay/Wine/caller execution, callback results, errno, exception policy, or exhaustive accuracy proof. math.pow is host libm, not a correctly rounded oracle; comparison limited to nonzero finite results with finite nonzero bases and bounded exponents. Other control modes are recorded against default host math.pow only for inspection. Binary64 loads can quiet signaling NaNs before entry. No raw extended inputs/results, live extra x87 stack values, or unmasked exceptions. General registers are not asserted. Successful completion verifies the guarded 0051655c callback was not reached for sampled cases. Dispatch sentinels are synthetic, not original game results.',
                  cases=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['cases', 'extraction_audit', 'limits', 'method']}))


if __name__ == '__main__':
    main()
