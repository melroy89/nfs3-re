"""Static original/Modern mouse cursor callback and registration witnesses."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'mouse-cursor-callback-comparison', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/mouse-cursor-callback'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        imports = {i.address: i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534780] == 'SetCursor'
        assert imports[0x534794] == 'ShowCursor'
        rows = []
        blobs[label] = []
        for a, b in [(0x436930, 0x43697f), (0x4351a0, 0x4351eb), (0x4cd2d0, 0x4cd348)]:
            data = pe.get_data(a - 0x400000, b - a)
            blobs[label].append(data)
            path = capture / f'{label}-{a:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={a}', f'--stop-address={b}', relative], cwd=ROOT))
            rows.append({'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    old, new = blobs['original'], blobs['official_modern']
    assert old[0][:0x2d] == new[0][:0x2d]
    assert old[1:] == new[1:]
    assert old[0][0x2d:0x44] == bytes.fromhex('6a002eff15804753006a002eff1594475300b801000000')
    assert new[0][0x2d:0x48] == bytes.fromhex('31db66837d240175106a00ff158047530043c745280100000089d8')
    result['changed_callback_bytes_in_79_byte_envelope'] = sum(a != b for a, b in zip(old[0], new[0]))
    result['limits'] = ['No cursor or window execution.',
        'Prior callback output, global ShowCursor balance and callback lifetime are separate contracts.']
    (ROOT / 'analysis/evidence/audits/mouse-cursor-callback.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: callback changes; identical forwarding prefix, registration witness and 120-byte dispatcher')


if __name__ == '__main__':
    main()
