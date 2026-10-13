"""Measure stored signed-byte basis vectors in installed COLL type-15 records.

Standard library only. This is an offline asset diagnostic; it does not run
the game, identify the selected basis branch, or validate runtime transforms.
"""
import argparse
import hashlib
import json
from pathlib import Path
import math
import struct


VECTOR_OFFSETS = (0x10, 0x14, 0x18)
RECORD_BYTES = 36


def signed_byte(value):
    return value - 256 if value >= 128 else value


def inventory(root):
    root = root.resolve()
    paths = sorted((root / 'GAMEDATA/TRACKS').glob('TRK*/*.COL'))
    if not paths:
        raise ValueError('No GAMEDATA/TRACKS/TRK*/*.COL files found')

    files = []
    vector_lengths = []
    pairwise_abs_dots = []
    zero_vectors = 0
    records_total = 0
    for path in paths:
        raw = path.read_bytes()
        if len(raw) < 16 or raw[:4] != b'COLL':
            raise ValueError(f'Unsupported COLL header: {path}')
        version, declared_size, block_count = struct.unpack_from('<3I', raw, 4)
        directory_end = 16 + 4 * block_count
        if declared_size != len(raw) or directory_end > len(raw):
            raise ValueError(f'Invalid declared file/directory extent: {path}')

        blocks = []
        for index in range(block_count):
            offset = 16 + struct.unpack_from('<I', raw, 16 + 4 * index)[0]
            if offset < directory_end or offset + 8 > len(raw):
                raise ValueError(f'Invalid block header extent: {path}')
            size, tag, count = struct.unpack_from('<IHH', raw, offset)
            if size < 8 or offset + size > len(raw):
                raise ValueError(f'Invalid declared block extent: {path}')
            if tag != 15:
                continue
            expected = 8 + RECORD_BYTES * count
            if size != expected:
                raise ValueError(f'Unexpected type-15 record extent: {path} block {index}')

            lengths = []
            dots = []
            for record_index in range(count):
                base = offset + 8 + RECORD_BYTES * record_index
                vectors = []
                for field_offset in VECTOR_OFFSETS:
                    xyz = tuple(signed_byte(raw[base + field_offset + axis]) / 128.0
                                for axis in range(3))
                    vectors.append(xyz)
                    length = math.sqrt(sum(component * component for component in xyz))
                    lengths.append(length)
                    vector_lengths.append(length)
                    zero_vectors += length == 0.0
                for left in range(3):
                    for right in range(left + 1, 3):
                        dot = sum(vectors[left][axis] * vectors[right][axis]
                                  for axis in range(3))
                        dots.append(abs(dot))
                        pairwise_abs_dots.append(abs(dot))
            records_total += count
            blocks.append(dict(index=index, offset=offset, segment_count=count,
                               record_bytes=RECORD_BYTES,
                               basis_vector_offsets=[f'0x{x:02x}' for x in VECTOR_OFFSETS],
                               basis_vector_count=3,
                               vector_length_min=min(lengths) if lengths else None,
                               vector_length_max=max(lengths) if lengths else None,
                               maximum_pairwise_absolute_dot=max(dots) if dots else None))

        if not blocks:
            raise ValueError(f'No type-15 segment block: {path}')
        files.append(dict(path=path.relative_to(root).as_posix(),
                          sha256=hashlib.sha256(raw).hexdigest(), version=version,
                          file_bytes=len(raw), type15_blocks=blocks))

    return dict(
        scope='Installed uppercase GAMEDATA/TRACKS/TRK*/*.COL files; all segment records in each COLL type-15 block.',
        method=('For each type-15 36-byte segment record, interpret three signed-byte XYZ vectors at offsets 0x10, 0x14 and 0x18, divide each component by 128.0, then compute host binary64 Euclidean lengths and absolute pairwise dot products within that record. This follows the statically identified fallback-basis byte reads; it does not establish that every record uses this fallback.'),
        limitations=('Installed-file evidence only. No loader execution, FRD packed-basis inventory, branch-admission check, coordinate transform, normalization emulation, or runtime geometry validation. Length/dot ranges are diagnostics, not proof that the basis is invalid.'),
        file_count=len(files), segment_record_count=records_total,
        basis_vector_count=len(vector_lengths), zero_vector_count=zero_vectors,
        vector_length_min=min(vector_lengths) if vector_lengths else None,
        vector_length_max=max(vector_lengths) if vector_lengths else None,
        maximum_pairwise_absolute_dot=max(pairwise_abs_dots) if pairwise_abs_dots else None,
        files=files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in
                      ('file_count', 'segment_record_count', 'zero_vector_count',
                       'vector_length_min', 'vector_length_max',
                       'maximum_pairwise_absolute_dot')}))


if __name__ == '__main__':
    main()
