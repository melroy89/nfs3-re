"""Read installed credits-range offsets and lengths; no game execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--game-dir', type=Path, required=True)
    root = parser.parse_args().game_dir
    rows = []
    for folder in ('FEDATA/TEXT', 'fedata_org/text'):
        for path in sorted((root/folder).iterdir()):
            if path.suffix.lower() not in ('.eng','.ger','.fre','.spa','.ita','.swe'): continue
            raw = path.read_bytes(); entries = []
            for index in range(0x46a, 0x476):
                offset = struct.unpack_from('<I',raw,index*4)[0]
                assert offset < len(raw)
                end = raw.find(b'\0',offset); assert end >= offset
                entries.append({'id': index, 'offset': offset, 'byte_length': end-offset,
                                'sha256': hashlib.sha256(raw[offset:end]).hexdigest()})
            assert entries[5]['id'] == 0x46f and entries[5]['byte_length'] == 0
            rows.append({'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(raw).hexdigest(),
                         'size': len(raw), 'entries': entries})
    assert len(rows) == 18
    result = {'kind':'installed-credits-range-inventory','files':rows,
              'limits':['Installed and locally named backup files, not authenticated retail provenance.',
                        'Selected offsets and NUL bounds only; no runtime language selection or rendering.']}
    output = Path(__file__).resolve().parents[1]/'evidence/inventories/installed-credits-text-range.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 18 language files, twelve bounded entries each, empty separator ID1135')


if __name__ == '__main__': main()
