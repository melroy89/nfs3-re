"""Retain static instruction witnesses for the two hash-pinned THRASH loaders.

Does not execute target instructions or change an executable/Ghidra database.
Requires pefile and GNU objdump. Modern's export table is data, not code.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / 'analysis/captures/modern-differences/thrash-loader'
SPECS = {
    'original': ('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3_org.exe',
                 'b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b',
                 [(0x4f8390, 0x4f8793)]),
    'official_modern': ('analysis/captures/modern-differences/upstream/package/nfs3.exe',
                        '240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6',
                        [(0x4f84a8, 0x4f853b), (0x4b5844, 0x4b5a3c)]),
}


def main():
    import pefile
    CAPTURE.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-dual-binary-instruction-witness', 'binaries': {},
              'limits': ['No target execution or renderer DLL validation.',
                         'Release-to-release introduction dates not verified.',
                         'Modern export-table addresses are data, not instructions.']}
    for label, (relative, expected, spans) in SPECS.items():
        path = ROOT / relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected, relative
        pe = pefile.PE(data=raw)
        base = pe.OPTIONAL_HEADER.ImageBase
        captures = []
        for start, end in spans:
            data = pe.get_data(start-base, end-start)
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                    f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = CAPTURE / f'{label}-{start:08x}.asm'
            output.write_text(text)
            captures.append({'start': f'{start:08x}', 'exclusive_end': f'{end:08x}',
                             'bytes_sha256': hashlib.sha256(data).hexdigest(),
                             'assembly': str(output.relative_to(ROOT)),
                             'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'ranges': captures}
        if label == 'official_modern':
            table = []
            for va in range(0x4f8390, 0x4f84a0, 8):
                name, slot = struct.unpack('<II', pe.get_data(va-base, 8))
                value = pe.get_data(name-base, 96).split(b'\0')[0].decode('ascii')
                assert value.startswith('_THRASH_')
                table.append({'table_va': f'{va:08x}', 'export': value,
                              'name_va': f'{name:08x}', 'slot_va': f'{slot:08x}'})
            assert pe.get_data(0x4f84a0-base, 4) == b'\0'*4
            result['modern_export_table'] = table
        else:
            # Track each explicit name PUSH to its following GetProcAddress,
            # then the EAX store. Reject incomplete/duplicate recovered bindings.
            text = (CAPTURE/'original-004f8390.asm').read_text()
            pending = None
            resolved = None
            bindings = []
            for line in text.splitlines():
                match = re.search(r'push\s+0x([0-9a-f]+)', line)
                if match:
                    va = int(match[1], 16)
                    if 0x54d3a4 <= va <= 0x54d664:
                        pending = pe.get_data(va-base, 96).split(b'\0')[0].decode('ascii')
                if 'call' in line and '0x534558' in line:
                    assert pending is not None
                    resolved, pending = pending, None
                match = re.search(r'mov\s+(?:DWORD PTR )?ds:0x([0-9a-f]+),eax', line)
                if match and resolved:
                    bindings.append({'export': resolved, 'slot_va': f'{int(match[1],16):08x}'})
                    resolved = None
            assert len(bindings) == 34 and len({b['export'] for b in bindings}) == 34
            result['original_explicit_bindings'] = bindings
    old = {b['export']: b['slot_va'] for b in result['original_explicit_bindings']}
    new = {b['export']: b['slot_va'] for b in result['modern_export_table']}
    result['all_34_export_names_and_slots_match'] = old == new
    assert old == new
    output = ROOT/'analysis/evidence/audits/original-modern-thrash-loader.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: input hashes, 34 identical name/slot bindings, instruction captures')


if __name__ == '__main__':
    main()
