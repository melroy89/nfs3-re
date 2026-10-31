"""Compare sentinel-scanned static menu callback rows in pinned PEs, offline."""
import hashlib
import json
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-menu-callback-table-comparison', 'binaries': {}}
    tables = []
    binders = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        for index in range(256):
            address = 0x555c48 + index * 24
            data = pe.get_data(address-0x400000, 24)
            words = struct.unpack('<6I', data)
            if words[0] == 0:
                break
            name = pe.get_data(words[0]-0x400000, 128).split(b'\0')[0].decode('ascii')
            rows.append({'index': index, 'address': f'{address:08x}', 'name': name, 'words': [f'{v:08x}' for v in words]})
        else:
            raise AssertionError('No sentinel within inspection bound')
        assert len(rows) == 57 and address == 0x5561a0
        tables.append(rows)
        binders.append(pe.get_data(0x42b10, 0x4c))
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'rows': rows,
            'sentinel_address': f'{address:08x}', 'sentinel_hex': data.hex(),
            'table_through_sentinel_sha256': hashlib.sha256(pe.get_data(0x155c48, 58*24)).hexdigest(),
            'binder_00442b10_to_00442b5c_sha256': hashlib.sha256(binders[-1]).hexdigest()}
    assert binders[0] == binders[1]
    deltas = []
    for old, new in zip(*tables):
        assert old['name'] == new['name'] and old['address'] == new['address']
        for word_index, (a, b) in enumerate(zip(old['words'], new['words'])):
            if a != b:
                assert word_index > 0
                deltas.append({'row_index': old['index'], 'row_address': old['address'], 'name': old['name'], 'row_offset': f'{word_index*4:02x}', 'descriptor_offset': f'{(word_index-1)*4:02x}', 'original': a, 'official_modern': b})
    assert len(deltas) == 12 and len({d['row_index'] for d in deltas}) == 9
    assert sum(d['official_modern'] == '00000000' for d in deltas) == 8
    result['changed_fields'] = deltas
    result['limits'] = ['No callback execution or universal lifecycle interpretation.', 'Same pointer does not prove same target bytes; relocated pointer does not prove different semantics.', 'Only the binder-selected sentinel-scanned table is covered; duplicated PE bytes are not silently treated as alternate live tables.']
    (ROOT / 'analysis/evidence/audits/original-modern-menu-callback-table.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 57 matching names; nine changed rows, 12 fields (eight null, four redirected)')


if __name__ == '__main__':
    main()
