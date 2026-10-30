"""Retain static witnesses for NFS3 endpoint/default-port changes.

Requires pefile/GNU objdump. Never executes target code or changes Ghidra.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON = [(0x49e5f0, 0x49e7f2), (0x49e9d0, 0x49ead3), (0x4f5050, 0x4f5066),
          (0x43f760, 0x43f7d0), (0x43fe50, 0x43fee0)]


def main():
    capture = ROOT/'analysis/captures/modern-differences/network-port'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-endpoint-port-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['No transport/provider or socket execution.',
            'Port agreement does not establish simulation/replay compatibility.',
            'Provider method +0x38 implementation and byte-order encoding not inspected here.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        spans = list(COMMON)
        if label == 'official_modern':
            spans += [(0x43fd10, 0x43fda0), (0x4a2f50, 0x4a2f8d)]
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
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    assert result['binaries']['original']['spans'][2]['bytes_sha256'] == result['binaries']['official_modern']['spans'][2]['bytes_sha256']
    output = ROOT/'analysis/evidence/audits/original-modern-network-port.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: input hashes, captures and unchanged provider-dispatch wrapper')


if __name__ == '__main__':
    main()
