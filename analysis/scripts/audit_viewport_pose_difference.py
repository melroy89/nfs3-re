"""Static viewport camera-selection comparison; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-viewport-pose-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No camera/game execution.', 'Normal-return restoration only; no synchronization proved.']}
    capture = ROOT/'analysis/captures/modern-differences/viewport-pose'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x4228e0, 0x4229bb if label == 'original' else 0x4229b9), (0x422850, 0x4228df)]
        spans += [(0x42387c, 0x4238a5), (0x421708, 0x42172c)]
        spans += [(0x4223c0, 0x422512), (0x422520, 0x422604)]
        if label == 'original':
            spans += [(0x42649c, 0x4264be), (0x4264c0, 0x4264ec)]
        if label == 'official_modern':
            spans += [(0x42649c, 0x4264be), (0x4264c0, 0x4264ec),
                      (0x472298, 0x4722ab), (0x45da2d, 0x45da37)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}',
                f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    assert result['binaries']['original']['spans'][1]['bytes_sha256'] == result['binaries']['official_modern']['spans'][1]['bytes_sha256']
    result['pose_finalizer_identical'] = True
    modern = pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    result['snapshot_call_targets'] = {}
    for site, target in ((0x42389a, 0x42649c), (0x421718, 0x4264c0)):
        data = modern.get_data(site-0x400000, 5)
        assert data[0] == 0xe8 and site+5+int.from_bytes(data[1:], 'little', signed=True) == target
        result['snapshot_call_targets'][f'{site:08x}'] = f'{target:08x}'
    result['identical_pose_callees'] = []
    for index in (4, 5):
        pair = [result['binaries'][k]['spans'][index] for k in ('original', 'official_modern')]
        assert pair[0]['bytes_sha256'] == pair[1]['bytes_sha256']
        result['identical_pose_callees'].append(pair[0]['start'])
    (ROOT/'analysis/evidence/audits/original-modern-viewport-pose.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete wrapper bodies and identical pose finalizer')


if __name__ == '__main__':
    main()
