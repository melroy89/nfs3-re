"""Inventory selected installed language labels without loading game code."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-dir', type=Path, required=True)
    args = parser.parse_args()
    root = args.game_dir
    rows = []
    for folder in ('FEDATA/TEXT', 'fedata_org/text'):
        for path in sorted((root/folder).iterdir()):
            if path.suffix.lower() not in ('.eng', '.ger', '.fre', '.spa', '.ita', '.swe'):
                continue
            raw = path.read_bytes()
            labels = []
            for index in (0x15a, 0x15b):
                assert len(raw) >= index*4+4
                offset = struct.unpack_from('<I', raw, index*4)[0]
                assert offset < len(raw)
                end = raw.find(b'\0', offset)
                assert end >= offset
                labels.append({'id': index, 'offset': offset, 'bytes_hex': raw[offset:end].hex(),
                               'byte_length': end-offset, 'text_ascii': raw[offset:end].decode('ascii')})
            rows.append({'path': str(path.relative_to(root)), 'size': len(raw),
                         'sha256': hashlib.sha256(raw).hexdigest(), 'labels': labels})
    assert len(rows) == 18
    assert all([v['byte_length'] for v in r['labels']] == [1, 1] for r in rows)
    result = {'kind': 'installed-numeric-scale-label-inventory', 'files': rows,
              'limits': ['Installed and locally named backup files; no authenticated retail provenance.',
                         'No claim these files were selected at runtime or supplied by the official patch archive.',
                         'Selected offsets/NUL bounds only, not complete language-format validation.'],
              'positive_count_concat_bytes_including_nul': {
                  str(n): 3+sum(len(str(i)) for i in range(1, n+1)) for n in range(1, 13)}}
    out = Path(__file__).resolve().parents[1]/'evidence/inventories/installed-numeric-scale-labels.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: 18 file hashes, selected offset/NUL bounds and one-byte labels')


if __name__ == '__main__':
    main()
