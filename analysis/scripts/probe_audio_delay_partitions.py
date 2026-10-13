"""Execute unchanged NFS3 delay initialization in a freestanding Linux i386 ELF.

Needs pefile, GNU as/ld and Linux i386 execution support. Does not run Wine or
modify the game. Only initialization is executed, not delay processing/audio.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

EXPECTED_SHA256 = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
WORKSPACE_START = 0xa0d2b4
WORKSPACE_BYTES = 0xaf00
RECORD_BYTES = 100


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
    rates = [0, 11025, 16000, 22050, 32000, 44100, 65535]
    controls = [0x037f, 0x027f, 0x077f, 0x0b7f, 0x0f7f]
    cases = [(rate, control) for rate in rates for control in controls]
    ranges = [('initializer', 0x523200, 0x523302),
              ('truncate', 0x4dfd56, 0x4dfd6d),
              ('multiplier', 0x551b00, 0x551b08),
              ('coefficients', 0x56ae00, 0x56ae70)]
    with tempfile.TemporaryDirectory(prefix='nfs3-audio-partitions-') as temp:
        work = Path(temp)
        for name, start, end in ranges:
            (work/f'{name}.bin').write_bytes(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase, end-start))
        (work/'vectors.bin').write_bytes(b''.join(struct.pack('<II', *case) for case in cases))
        assembly = f'''.intel_syntax noprefix
.section .text
.global _start
_start:
 mov esi,offset vectors
 mov edi,offset results
 mov dword ptr [remaining],{len(cases)}
case_loop:
 pushad
 mov edi,{WORKSPACE_START}
 mov ecx,{WORKSPACE_BYTES//4}
 mov eax,0xa5a5a5a5
 rep stosd
 popad
 fninit
 fldcw word ptr [esi+4]
 mov eax,[esi]
 mov [edi],eax
 mov eax,[esi+4]
 mov [edi+4],eax
 mov eax,[esi]
 call initializer+0x5c
 mov [edi+8],eax
 fnstcw word ptr [edi+12]
'''
        arrays = [0xa181d4, 0xa181b4, 0xa0d2a4, 0xa181f4, 0xa181e4]
        for stage in range(4):
            for field, base in enumerate(arrays):
                assembly += f' mov eax,dword ptr [{base+stage*4}]\n mov [edi+{16+stage*20+field*4}],eax\n'
        assembly += f''' pushad
 mov esi,{WORKSPACE_START}
 mov ecx,{WORKSPACE_BYTES//4}
 xor eax,eax
check_zero:
 or eax,dword ptr [esi]
 add esi,4
 loop check_zero
 mov [edi+96],eax
 popad
 add esi,8
 add edi,{RECORD_BYTES}
 dec dword ptr [remaining]
 jnz case_loop
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,{len(cases)*RECORD_BYTES}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80
.section .data
remaining: .long 0
vectors: .incbin "{work/'vectors.bin'}"
results: .space {len(cases)*RECORD_BYTES},0
.section .workspace,"aw",@nobits
.space 0xc000
'''
        for name, _, _ in ranges:
            assembly += f'.section .{name},"awx"\n{name}: .incbin "{work/(name+".bin")}"\n'
        (work/'probe.s').write_text(assembly)
        subprocess.run(['as', '--32', '-o', str(work/'probe.o'), str(work/'probe.s')], check=True)
        command = ['ld', '-m', 'elf_i386', '-Ttext=0x100000', '-Tdata=0x200000',
                   '--section-start=.workspace=0xa0d000']
        command += [f'--section-start=.{name}={start:#x}' for name, start, _ in ranges]
        subprocess.run(command+['-o', str(work/'probe'), str(work/'probe.o')], check=True)
        output = subprocess.run([str(work/'probe')], capture_output=True, check=True, timeout=10).stdout
    if len(output) != len(cases)*RECORD_BYTES:
        raise RuntimeError('Incomplete initializer output')
    rows = []
    for index, (rate, control) in enumerate(cases):
        record = struct.unpack_from('<25I', output, index*RECORD_BYTES)
        assert record[:3] == (rate, control, 0)
        assert record[3] == control and record[24] == 0
        stages = []
        for stage in range(4):
            base, read, write, limit, feedback = record[4+5*stage:9+5*stage]
            size = (limit-base+4)//4
            assert read == base and write == limit and feedback == 0 and size >= 2
            if stage == 0:
                assert base == WORKSPACE_START
            else:
                assert base == stages[-1]['limit']+4
            stages.append(dict(base=base, read=read, write=write, limit=limit,
                               prime_samples=size, cached_feedback_bits=feedback))
        total = sum(stage['prime_samples'] for stage in stages)*4
        rows.append(dict(rate=rate, control_word=f'{control:04x}',
                         recognized_rate=rate in rates[1:-1], stages=stages,
                         partition_bytes=total, cleared_workspace_bytes=WORKSPACE_BYTES,
                         spare_bytes=WORKSPACE_BYTES-total,
                         fits_cleared_workspace=total <= WORKSPACE_BYTES,
                         control_preserved=True, cleared_workspace_zero=True))
    recognized = [r for r in rows if r['recognized_rate']]
    assert all(r['fits_cleared_workspace'] for r in recognized)
    assert hashlib.sha256(args.binary.read_bytes()).hexdigest() == digest
    report = dict(sha256=digest, method='Unchanged original initializer/prime/truncation instructions in native i386 harness; no stubs; no delay processing',
                  code_ranges=[f'{start:08x}..{end-1:08x}' for _, start, end in ranges],
                  workspace_start=WORKSPACE_START, case_count=len(rows),
                  minimum_recognized_spare_bytes=min(r['spare_bytes'] for r in recognized),
                  limits=['Recognized-rate producer values tested; startup ordering and indirect writes remain unproven.',
                          'Rates0/65535 are synthetic controls, not demonstrated game settings.',
                          'Five masked-exception control words; broader x87 state not covered.',
                          'Initialized pointers only; no processor samples, audio callbacks, concurrency or acoustic effects tested.'],
                  cases=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(case_count=len(rows), minimum_recognized_spare_bytes=report['minimum_recognized_spare_bytes'])))


if __name__ == '__main__':
    main()
