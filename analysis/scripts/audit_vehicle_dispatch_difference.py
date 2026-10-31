"""Static paired vehicle-dispatch witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-vehicle-dispatch-comparison', 'range_end': 'exclusive',
              'binaries': {}, 'limits': ['No rendering or target execution.',
              'Field labels are bounded by existing research; no complete vehicle structure claimed.']}
    capture = ROOT/'analysis/captures/modern-differences/vehicle-dispatch'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x4bbba0, 0x4bbcb4 if label == 'original' else 0x4bbce3),
                 (0x4bbad0, 0x4bbb94), (0x422aa0, 0x422ace)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                         'assembly': str(path.relative_to(ROOT)),
                         'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    a, b = [result['binaries'][k]['spans'][1] for k in ('original', 'official_modern')]
    assert a['bytes_sha256'] == b['bytes_sha256']
    result['helper_004bbad0_identical'] = True
    (ROOT/'analysis/evidence/audits/original-modern-vehicle-dispatch.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete dispatcher spans, identical selection helper')


if __name__ == '__main__':
    main()
