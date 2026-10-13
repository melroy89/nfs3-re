"""Read installed COLL type15 segment blocks and derive track-map sampling counts.

Standard library only. Does not run the game or prove loader success/runtime
state. Checks file extents before reading; does not replace the game's loader.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def inventory(root):
    root = root.resolve()
    paths = sorted((root/'GAMEDATA/TRACKS').glob('TRK*/*.COL'))
    if not paths:
        raise ValueError('No GAMEDATA/TRACKS/TRK*/*.COL files found')
    rows = []
    for path in paths:
        data = path.read_bytes()
        if len(data) < 16 or data[:4] != b'COLL':
            raise ValueError(f'Unsupported COLL header: {path}')
        version, declared_size, block_count = struct.unpack_from('<3I', data, 4)
        if declared_size != len(data) or 16+4*block_count > len(data):
            raise ValueError(f'Invalid declared file/directory extent: {path}')
        segments = []
        for index in range(block_count):
            offset = 16+struct.unpack_from('<I', data, 16+4*index)[0]
            if offset < 16+4*block_count or offset+8 > len(data):
                raise ValueError(f'Invalid block header extent: {path}')
            size, tag, count = struct.unpack_from('<IHH', data, offset)
            if size < 8 or offset+size > len(data):
                raise ValueError(f'Invalid declared block extent: {path}')
            if tag != 15:
                continue
            required = 8+36*count
            step = count//128
            samples = (count+step-1)//step if step else None
            segments.append(dict(index=index, offset=offset, declared_bytes=size,
                                 required_segment_bytes=required,
                                 exact_record_extent=size == required,
                                 segment_count=count, step=step,
                                 points_including_closure=samples+1 if samples is not None else None,
                                 initialized_u16_count=True,
                                 avoids_zero_step=count >= 128,
                                 fits_256_pair_sampling_bound=samples is not None and samples+1 <= 256))
        if not segments:
            raise ValueError(f'No type15 segment block: {path}')
        rows.append(dict(path=path.relative_to(root).as_posix(),
                         sha256=hashlib.sha256(data).hexdigest(), version=version,
                         file_bytes=len(data), block_count=block_count, segment_blocks=segments))
    return dict(scope='Installed uppercase GAMEDATA/TRACKS/TRK*/*.COL files. COLL directory offsets are relative to the payload after the16-byte file header; type15 blocks use8-byte header and36-byte segment records.',
                method='Read-only file inventory and integer sampling arithmetic from0048cdb0; not live loading/rendering evidence.',
                file_count=len(rows), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(file_count=report['file_count'])))


if __name__ == '__main__':
    main()
