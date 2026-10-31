"""Compare complete viewport overlay envelopes and new fixed-colour helper."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-view-overlay-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/view-overlay'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x489240, 0x48962d)]
        if label == 'official_modern': spans += [(0x4900c8, 0x490134), (0x4900b0, 0x4900c5), (0x4f9390, 0x4f9399)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'constants_0053b76c_to_0053b78c_hex': pe.get_data(0x13b76c, 32).hex()}
    data = [p.get_data(0x89240, 0x3ed) for p in images]
    changes = [0x489240+i for i,(a,b) in enumerate(zip(*data)) if a != b]
    assert len(changes) == 143
    out['envelope_changed_byte_addresses'] = [f'{a:08x}' for a in changes]
    out['modern_function_range_changed_bytes'] = sum(not 0x489614 <= a < 0x489619 for a in changes)
    assert out['modern_function_range_changed_bytes'] == 138
    assert images[1].get_data(0x89614, 5) == bytes([0x90])*5
    assert images[0].get_data(0x89613, 6) == bytes.fromhex('ff154cf99e00')
    out['retained_ranges'] = []
    for start, end in ((0x489240,0x48928c),(0x4892dd,0x4894f8),(0x489510,0x4895a2),(0x489619,0x48962d)):
        pair = [p.get_data(start-0x400000,end-start) for p in images]; assert pair[0] == pair[1]
        out['retained_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pair[0]).hexdigest()})
    site = 0x48960d; call = images[1].get_data(site-0x400000,5)
    assert call[0] == 0xe8 and site+5+int.from_bytes(call[1:],'little',signed=True) == 0x4900c8
    out['limits'] = ['No rendering, target execution or visual acceptance.', 'Complete address envelope includes Modern padding and original call bytes; Modern function ranges alone exclude part of that original instruction.', 'Rectangle/global producers, callback slot identity and complete asset/descriptor bounds remain separate.']
    (ROOT/'analysis/evidence/audits/original-modern-view-overlay.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 143 envelope deltas / 138 Modern-range deltas; retained blocks and new quad helper')


if __name__ == '__main__':
    main()
