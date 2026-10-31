"""Retain moved numeric-scale counterpart and caller witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-numeric-scale-comparison', 'range_end': 'exclusive',
              'counterparts': {'original': '00489b30', 'official_modern': '00489ab0'},
              'binaries': {}, 'limits': ['No UI rendering or target execution.',
                                        'Invalid inputs and localized asset lengths not validated.']}
    capture = ROOT/'analysis/captures/modern-differences/numeric-scale'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x489b30, 0x489c40)] if label == 'original' else [(0x489ab0, 0x489bd9), (0x4f939c, 0x4f93c5), (0x4d1430, 0x4d1450)]
        spans += [(0x4d10e0,0x4d1116 if label=='original' else 0x4d1114),(0x45adba, 0x45ae2c), (0x45aef0, 0x45af63), (0x4839eb, 0x483a67)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                         'assembly': str(path.relative_to(ROOT)),
                         'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        target = 0x489b30 if label == 'original' else 0x489ab0
        for site in (0x45ae27, 0x45af5e, 0x483a62):
            data = pe.get_data(site-0x400000, 5)
            assert data[0] == 0xe8
            assert site+5+int.from_bytes(data[1:], 'little', signed=True) == target
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    images = [pefile.PE(str(ROOT/SPECS[k][0])) for k in ('original', 'official_modern')]
    old,new=images
    assert old.get_data(0xd10e0,0x2f)==new.get_data(0xd10e0,0x2f)
    assert old.get_data(0xd110f,2)==bytes.fromhex('ddd8')
    assert new.get_data(0x89bd1,2)==bytes.fromhex('ddd8')
    assert old.get_data(0xd1115,1)==b'\xc3'
    assert new.get_data(0xd1113,1)==b'\xc3'
    result['right_anchor_return_contract']={'entry':'004d10e0','original_end_exclusive':'004d1116','modern_end_exclusive':'004d1114','shared_prefix_end_exclusive':'004d110f','original':'FSTP ST(0) discards draw return before RET','modern':'Leaves draw x87 return; numeric-scale caller pops it at00489bd1','limits':['Static local stack effect; not a complete ABI audit of all callers.','Identical CALL targets do not establish identical helper implementations.']}
    result['caller_setup_only_retargets'] = []
    for start, end, call in ((0x45adba, 0x45ae2c, 0x45ae27), (0x45aef0, 0x45af63, 0x45af5e), (0x4839eb, 0x483a67, 0x483a62)):
        bodies = [p.get_data(start-0x400000, end-start) for p in images]
        changes = [start+i for i, (a, b) in enumerate(zip(*bodies)) if a != b]
        assert all(call+1 <= a < call+5 for a in changes)
        result['caller_setup_only_retargets'].append({'start': f'{start:08x}', 'end': f'{end:08x}',
                                                     'changed_addresses': [f'{a:08x}' for a in changes]})
    (ROOT/'analysis/evidence/audits/original-modern-numeric-scale.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, moved counterpart spans and three redirected callers')


if __name__ == '__main__':
    main()
