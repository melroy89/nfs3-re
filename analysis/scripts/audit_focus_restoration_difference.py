"""Static comparison of the window-thread loop's removed restoration tail."""
import hashlib
import json
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    rows = {}
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        imports = {i.address: i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT
                   for i in d.imports if i.name}
        assert imports[0x534788] == 'SetForegroundWindow'
        assert imports[0x53475c] == 'IsIconic'
        assert imports[0x534794] == 'ShowCursor'
        end = 0x4cd6b7 if label == 'original' else 0x4cd663
        body = pe.get_data(0x4cd4e0-0x400000, end-0x4cd4e0)
        rows[label] = {'path': relative, 'sha256': expected, 'start': '004cd4e0',
                       'exclusive_end': f'{end:08x}', 'body_sha256': hashlib.sha256(body).hexdigest(),
                       'body_bytes': body.hex()}
    old, new = images['original'], images['official_modern']
    get = lambda p, a, n: p.get_data(a-0x400000, n)
    differences = [0x4cd4e0+i for i, (a,b) in enumerate(zip(
        get(old,0x4cd4e0,0x175),get(new,0x4cd4e0,0x175))) if a != b]
    # Only the exit branch displacement changes before the removed tail.
    assert differences == [0x4cd58a, 0x4cd58b]
    assert get(old,0x4cd58a,4) == bytes.fromhex('20010000')
    assert get(new,0x4cd58a,4) == bytes.fromhex('cc000000')
    assert get(new,0x4cd655,5) == bytes.fromhex('e928ffffff')
    assert get(new,0x4cd663,0x54) == b'\x90'*0x54
    assert get(old,0x4cd68c,7) == bytes.fromhex('2eff155c475300')
    assert get(old,0x4cd6a2,7) == bytes.fromhex('2eff1588475300')
    assert get(old,0x4cd6ae,9) == get(new,0x4cd65a,9)
    result = {'kind': 'static-window-loop-restoration-difference', 'binaries': rows,
              'shared_prefix_differing_addresses': [f'{a:08x}' for a in differences],
              'limits': ['No target execution or OS focus behavior observed.',
                         'Removed local retry is not proof all foreground requests were removed.',
                         'Original predicate callees and all dynamic API resolution are not covered.']}
    (ROOT/'analysis/evidence/audits/focus-restoration-difference.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print('PASS: pinned loop bodies, sole prefix displacement, removed retry and retained epilogue')


if __name__ == '__main__':
    main()
