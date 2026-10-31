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
                 (0x4bbad0, 0x4bbb94), (0x422aa0, 0x422ace),
                 (0x4bb4c0, 0x4bb5ce), (0x4b90e0, 0x4b913f),
                 (0x4bae00, 0x4bb10f), (0x4bb200, 0x4bb495)]
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
    result['identical_render_bodies'] = []
    for index in (3, 5, 6):
        pair = [result['binaries'][k]['spans'][index] for k in ('original', 'official_modern')]
        assert pair[0]['bytes_sha256'] == pair[1]['bytes_sha256']
        result['identical_render_bodies'].append(pair[0]['start'])
    images = [pefile.PE(str(ROOT/SPECS[k][0])) for k in ('original', 'official_modern')]
    bodies = [p.get_data(0x4b90e0-0x400000, 0x5f) for p in images]
    differences = [{'address': f'{0x4b90e0+i:08x}', 'original': f'{a:02x}', 'modern': f'{b:02x}'}
                   for i, (a, b) in enumerate(zip(*bodies)) if a != b]
    assert [d['address'] for d in differences] == ['004b90e8', '004b90e9', '004b90ea', '004b90eb']
    result['randomizer_changed_bytes'] = differences
    tables = [p.get_data(0x4bb498-0x400000, 32) for p in images]
    assert tables[0] == tables[1]
    result['identical_dispatch_tables_004bb498'] = tables[0].hex()
    (ROOT/'analysis/evidence/audits/original-modern-vehicle-dispatch.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete dispatcher spans, identical selection helper')


if __name__ == '__main__':
    main()
