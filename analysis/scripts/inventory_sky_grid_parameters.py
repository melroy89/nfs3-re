"""Inventory labelled cloud settings in installed NFS3 HRZ files, read-only.

Uses only the standard library. This follows asset text labels, not the game's
full positional parser, and does not execute rendering or emulate x87 arithmetic.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def inventory(root):
    root = root.resolve()
    rows = []
    skipped = []
    paths = sorted((root/'GAMEDATA/TRACKS').glob('TRK*/*.HRZ'))
    if not paths:
        raise ValueError('No GAMEDATA/TRACKS/TRK*/*.HRZ files found')
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode('latin1')
        def following(label, count):
            match = re.search(r'/\*[^*]*'+label+r'[^*]*\*/([^/]+)', text, re.I)
            if not match:
                return None
            values = re.findall(r'[+-]?\d+', match.group(1))
            return list(map(int, values[:count])) if len(values) >= count else None
        cloud = following('Cloud bright', 3)
        dome = following('Cloud dome offset', 2)
        relative = path.relative_to(root).as_posix()
        if not cloud or not dome:
            skipped.append(relative)
            continue
        rows.append(dict(path=relative, sha256=hashlib.sha256(raw).hexdigest(),
                         dome_offset=dome[0], dome_height_token=dome[1],
                         brightness=cloud[0], variance=cloud[1], nimbus_percent=cloud[2]))
    return dict(scope='Installed uppercase GAMEDATA/TRACKS/TRK*/*.HRZ files with both cloud-labelled fields; original text labels, not live parser execution.',
                count=len(rows), skipped=skipped, rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(count=result['count'], skipped=len(result['skipped']))))


if __name__ == '__main__':
    main()
