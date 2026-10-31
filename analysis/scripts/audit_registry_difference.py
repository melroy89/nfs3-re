"""Hash-pinned static registry-call inventory; never executes target code."""
import hashlib
import json
import struct
import subprocess
from audit_thrash_loader_difference import ROOT, SPECS
import pefile

SPANS = [(0x4a5780, 0x4a587c), (0x4a5880, 0x4a59ba),
         (0x4b6400, 0x4b64b5), (0x4b64c0, 0x4b6513),
         (0x4b6520, 0x4b6588), (0x4bbcc0, 0x4bbd70),
         (0x522250, 0x5222e8), (0x4b5720, 0x4b584e)]
STRINGS = [0x53da94, 0x53daa8, 0x53dab8, 0x53dabc, 0x53dac0,
           0x53dac4, 0x53dac8, 0x53dacc, 0x53fe50, 0x53fe7c,
           0x53fe8c, 0x53fe98, 0x53feb0, 0x53fef4, 0x551928, 0x55193c]


def main():
    out = {'kind': 'static-registry-comparison', 'range_end': 'exclusive',
           'limits': ['Direct CALL encodings in executable sections only; not a reachability proof.',
                      'Indirect aliases, dynamically resolved calls and DLL behavior not covered.',
                      'Retained function bytes do not prove the same callers or runtime inputs.'],
           'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/registry'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        base = pe.OPTIONAL_HEADER.ImageBase
        imports = {i.address: i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT
                   for i in d.imports if i.name in (b'RegCloseKey', b'RegFlushKey', b'RegOpenKeyExA', b'RegQueryValueExA')}
        calls = []
        for section in pe.sections:
            if not section.Characteristics & 0x20000000:
                continue
            data = section.get_data()
            for va, name in imports.items():
                if name not in ('RegOpenKeyExA', 'RegQueryValueExA'):
                    continue
                needle = b'\xff\x15'+struct.pack('<I', va)
                pos = data.find(needle)
                while pos >= 0:
                    site = base+section.VirtualAddress+pos
                    # Retain the optional CS prefix as part of the call address.
                    if pos and data[pos-1] == 0x2e:
                        site -= 1
                    calls.append({'address': f'{site:08x}', 'import': name})
                    pos = data.find(needle, pos+1)
        rows = []
        for start, end in SPANS:
            assembly = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT)
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(assembly)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'bytes_sha256': hashlib.sha256(pe.get_data(start-base, end-start)).hexdigest(),
                         'assembly': str(path.relative_to(ROOT)),
                         'assembly_sha256': hashlib.sha256(assembly).hexdigest()})
        if label == 'official_modern':
            for start, end in SPANS[2:5]:
                assert set(pe.get_data(start-base, end-start)) == {0x90}
        row = {'path': relative, 'sha256': expected,
               'registry_imports': {f'{a:08x}': n for a, n in imports.items()},
               'direct_call_candidates': sorted(calls, key=lambda c: c['address']), 'spans': rows}
        if label == 'original':
            row['strings'] = {f'{a:08x}': pe.get_data(a-base, 200).split(b'\0')[0].decode('ascii') for a in STRINGS}
            row['online_name_table'] = []
            for i in range(4):
                a = struct.unpack('<I', pe.get_data(0x55eca0-base+4*i, 4))[0]
                row['online_name_table'].append({'address': f'{a:08x}',
                    'text': pe.get_data(a-base, 100).split(b'\0')[0].decode('ascii')})
        out['binaries'][label] = row
    a, b = [out['binaries'][k] for k in ('original', 'official_modern')]
    assert len(a['direct_call_candidates']) == 15
    assert len(b['direct_call_candidates']) == 6
    assert a['registry_imports'] == b['registry_imports']
    out['modern_nop_filled_original_helpers'] = ['004b6400', '004b64c0', '004b6520']
    out['identical_complete_spans'] = []
    for i in (0, 1, 6):
        assert a['spans'][i]['bytes_sha256'] == b['spans'][i]['bytes_sha256']
        out['identical_complete_spans'].append(a['spans'][i]['start'])
    target = ROOT/'analysis/evidence/audits/original-modern-registry.json'
    target.write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: baseline hashes, 15/6 direct-call candidates, imports, three retained bodies')


if __name__ == '__main__':
    main()
