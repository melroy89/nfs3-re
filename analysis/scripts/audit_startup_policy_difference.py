"""Static witnesses for NFS3 startup options, error mode, affinity and RAM pool policy.

Requires pefile/GNU objdump. Does not execute target code or change Ghidra.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

KEYS = [0x53f5f4, 0x53f608, 0x53f630, 0x53f63c, 0x53f64c,
        0x53f65c, 0x53f670, 0x53f680, 0x53f694, 0x53f6a4,
        0x53f6b8, 0x53f6cc, 0x53f6d0, 0x53f6e4, 0x53f78c, 0x53f79c]


def main():
    capture = ROOT/'analysis/captures/modern-differences/startup-policy'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-startup-policy-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['No OS policy change or target execution.',
            'Original callsite witnesses are not a complete original startup CFG.',
            'Current option defaults do not prove historical release defaults.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        spans = [(0x4a3ad9, 0x4a3b3a), (0x4f7900, 0x4f79ed),
                 (0x4f9270, 0x4f92df), (0x4f8930, 0x4f8a7d)]
        if label == 'official_modern':
            spans += [(0x4b5580, 0x4b5709), (0x4f1ea0, 0x4f1ed2),
                      (0x4a3e49, 0x4a3e7e), (0x4b5c00, 0x4b5c62)]
            assert set(pe.get_data(0xa3ad9, 0x61)) == {0x90}
        rows = []
        for start, end in spans:
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = capture/f'{label}-{start:08x}.asm'
            output.write_text(text)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        row = {'path': relative, 'sha256': expected, 'spans': rows}
        if label == 'official_modern':
            row['strings'] = {f'{va:08x}': pe.get_data(va-0x400000,100).split(b'\0')[0].decode('ascii') for va in KEYS}
            row['resolved_static_imports'] = {f'{i.address:08x}': i.name.decode()
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                if i.address in (0x5345e4, 0x534504, 0x53454c, 0x53458c, 0x534558)}
        result['binaries'][label] = row
    old, new = [result['binaries'][k]['spans'][1]['bytes_sha256'] for k in ('original','official_modern')]
    assert old == new
    result['allocator_004f7900_bytes_identical'] = True
    output = ROOT/'analysis/evidence/audits/original-modern-startup-policy.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: input hashes, removed original call span, Modern options/import witnesses')


if __name__ == '__main__':
    main()
