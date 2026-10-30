"""Hash-pinned static texture-extent witnesses; no driver/game execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON = [(0x41db67, 0x41db8c), (0x4b7d30, 0x4b7d7d),
          (0x4d4120, 0x4d4194), (0x4d41a0, 0x4d43db),
          (0x49d1b2, 0x49d1c5), (0x49d3d0, 0x49d3e3)]


def main():
    capture = ROOT/'analysis/captures/modern-differences/texture-extents'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-texture-extent-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['No asset, driver or target execution.',
            'Original helper has a dimension-pass-through branch, not a universal 256 cap.',
            'Renderer descriptor values and allocation/upload success unverified.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        spans = list(COMMON)
        spans += [(0x49cea0, 0x49cf91 if label == 'original' else 0x49cedd)]
        if label == 'official_modern':
            spans += [(0x4b56d5, 0x4b56f6), (0x4b5bd6, 0x4b5bfb)]
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
    for idx in (2, 3, 4, 5):
        assert result['binaries']['original']['spans'][idx]['bytes_sha256'] == result['binaries']['official_modern']['spans'][idx]['bytes_sha256']
    output = ROOT/'analysis/evidence/audits/original-modern-texture-extents.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: input identities, retained limit helpers/callsites and texture instruction spans')


if __name__ == '__main__':
    main()
