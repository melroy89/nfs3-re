"""Retain moved race-now-entry counterpart and caller witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-race-now-entry-comparison', 'range_end': 'exclusive',
              'binaries': {}, 'limits': ['Modern helper is not a same-address original counterpart.',
              'Original capture is a partial credits gate inside a larger routine.', 'No menu or target execution.']}
    capture = ROOT/'analysis/captures/modern-differences/race-now-entry'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x437600, 0x43762c)] if label == 'original' else [(0x437614, 0x4376fb)]
        spans += [(0x442a40, 0x442a95), (0x4cf090, 0x4cf11e)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                         'assembly': str(path.relative_to(ROOT)),
                         'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'tokens': {f'{a:08x}': pe.get_data(a-0x400000, 40).split(b'\0')[0].decode('ascii')
                       for a in (0x53a998, 0x53a990, 0x53714c, 0x537494)}}
    images = [pefile.PE(str(ROOT/SPECS[k][0])) for k in ('original', 'official_modern')]
    result['identical_helpers'] = []
    for start, end in ((0x442a40, 0x442a95), (0x4cf090, 0x4cf11e)):
        bodies = [p.get_data(start-0x400000, end-start) for p in images]
        assert bodies[0] == bodies[1]
        result['identical_helpers'].append(f'{start:08x}')
    (ROOT/'analysis/evidence/audits/original-modern-race-now-entry.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, Modern helper, original credits gate and exact tokens')


if __name__ == '__main__':
    main()
