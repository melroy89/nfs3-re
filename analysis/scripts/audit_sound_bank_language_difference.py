"""Compare complete sound-bank function envelopes, including removed switch code."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = [(0x40a010, 0x40a32c), (0x413750, 0x4138d9), (0x413bc0, 0x4147f8)]
READS = [0x40a1a6, 0x413794, 0x414294, 0x414320, 0x414684]


def main():
    result = {'kind': 'sound-bank-language-selection', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/sound-bank-language'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        blobs[label] = []
        for a, b in SPANS + [(0x4a6ec4, 0x4a6f2e)]:
            data = pe.get_data(a - 0x400000, b - a)
            blobs[label].append(data)
            path = capture / f'{label}-{a:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={a}', f'--stop-address={b}', relative], cwd=ROOT))
            rows.append({'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        selector = 0x6fbb4c if label == 'original' else 0x7a2764
        for a in READS:
            assert pe.get_data(a - 0x400000, 5) == b'\xa1' + struct.pack('<I', selector)
        if label == 'original':
            assert struct.unpack('<6I', pe.get_data(0x13ba8, 24)) == (0x413bf4, 0x413bfb, 0x413c02, 0x413c09, 0x413c10, 0x413bf4)
        else:
            assert pe.get_data(0x13be3, 7) == bytes.fromhex('be342b7a00eb2b')
            assert pe.get_data(0x13bea, 43) == b'\x90' * 43
            assert pe.get_data(0xa6f26, 6) == bytes.fromhex('890d64277a00')
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    result['functions'] = []
    for index, (a, b) in enumerate(SPANS):
        old, new = blobs['original'][index], blobs['official_modern'][index]
        changed = [a + i for i, (x, y) in enumerate(zip(old, new)) if x != y]
        allowed = {r + j for r in READS for j in (1, 2, 3)}
        if index == 2:
            allowed.update(range(0x413be1, 0x413c15))
        assert set(changed) <= allowed
        assert len(changed) == [3, 3, 61][index]
        result['functions'].append({'entry': f'{a:08x}', 'envelope_bytes': b-a,
            'changed_bytes': len(changed), 'changed_addresses': [f'{v:08x}' for v in changed]})
    result['limits'] = ['No game or audio execution; no asset availability validation.',
        'Modern initializer helper contracts and all selector writers are not proved here.']
    (ROOT / 'analysis/evidence/audits/sound-bank-language-difference.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: five selector retargets and removed switch; complete envelopes 796/393/3128 bytes')


if __name__ == '__main__':
    main()
