"""Hash-pinned static hook-filter spans; no target execution or database writes."""
import hashlib
import json
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-keyboard-hook-filter-comparison', 'end_addresses': 'exclusive',
              'binaries': {}, 'limits': ['Static inspection only; no OS hook behavior observed.',
              'Original startup supplies a null callback; all possible indirect/alias writes and intermediate releases remain unqualified.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        imports = {i.address: i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT
                   for i in d.imports if i.name}
        assert imports[0x534738] == 'GetAsyncKeyState'
        spans = [(0x4ccc70, 0x4ccd5a), (0x4cdc90, 0x4cdccc),
                 (0x4b6165, 0x4b617d)] if label == 'original' else [
            (0x4ccb84, 0x4ccc3f), (0x4ccc40, 0x4ccca4), (0x4f1fd0, 0x4f1ff0)]
        rows = []
        for start, end in spans:
            raw = pe.get_data(start - 0x400000, end - start)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': raw.hex()})
        if label == 'original':
            assert pe.get_data(0x4b6165-0x400000, 24) == bytes.fromhex(
                'b88000000031d2a3d8435600b80100000031dbe8137b0100')
            assert pe.get_data(0x4cdc94-0x400000, 6) == bytes.fromhex('891588125600')
            assert pe.get_data(0x4ccd1a-0x400000, 9) == bytes.fromhex('833d8812560000740d')
            assert pe.get_data(0x4ccd28-0x400000, 6) == bytes.fromhex('ff1588125600')
        else:
            assert pe.get_data(0x4ccbf3-0x400000, 15) == bytes.fromhex('80fb5b743980fb5c743480fb5d742f')
            assert pe.get_data(0x4ccc31-0x400000, 5) == bytes.fromhex('b801000000')
            assert pe.get_data(0x4ccc40-0x400000, 16) == bytes.fromhex('31c003058412560003058812560085c0')
            assert pe.get_data(0x4f1fd0-0x400000, 6) == bytes.fromhex('b011eb02b012')
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    out = ROOT / 'analysis/evidence/audits/keyboard-hook-filter-difference.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: baseline identities, complete filter spans, callback/handling and raw-sum witnesses')


if __name__ == '__main__':
    main()
