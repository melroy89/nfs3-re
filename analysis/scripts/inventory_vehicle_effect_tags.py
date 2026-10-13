"""Inventory archived FCE effect positions/tags used by NFS3's effect dispatcher.

Standard library only; installed assets are read only. Header offsets follow
verified004b8740 accesses. File evidence does not prove live model admission.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct


def inventory(root):
    root = root.resolve()
    archives = sorted(p for p in (root/'GAMEDATA/CARMODEL').rglob('*')
                      if p.is_file() and p.suffix.lower() == '.viv')
    if not archives:
        raise ValueError('No installed GAMEDATA/CARMODEL VIV archives found')
    rows = []
    total_tags = Counter()
    for path in archives:
        archive = path.read_bytes()
        if len(archive) < 16 or archive[:4] != b'BIGF':
            raise ValueError(f'Not BIGF: {path}')
        declared, count, header = struct.unpack_from('>III', archive, 4)
        if declared != len(archive) or not 16 <= header <= len(archive):
            raise ValueError(f'Invalid BIGF header extent: {path}')
        at = 16
        for _ in range(count):
            if at+8 > header:
                raise ValueError(f'Invalid directory entry: {path}')
            offset, size = struct.unpack_from('>II', archive, at)
            end = archive.index(b'\0', at+8, header)
            name = archive[at+8:end].decode('ascii')
            at = end+1
            if offset < header or offset+size > len(archive):
                raise ValueError(f'Invalid member extent: {path}:{name}')
            if not name.lower().endswith('.fce'):
                continue
            data = archive[offset:offset+size]
            if len(data) < 0x38:
                raise ValueError(f'Short FCE header: {path}:{name}')
            effects = struct.unpack_from('<I', data, 0x34)[0]
            if 0x38+effects*12 > len(data) or 0xa04+effects*64 > len(data):
                raise ValueError(f'Invalid effect array extent: {path}:{name}')
            entries = []
            for index in range(effects):
                raw = data[0xa04+64*index:0xa04+64*(index+1)]
                terminator = raw.find(b'\0')
                tag = raw[:terminator if terminator >= 0 else 64].decode('ascii')
                position = struct.unpack_from('<3f', data, 0x38+12*index)
                if not all(math.isfinite(x) for x in position):
                    raise ValueError(f'Nonfinite effect position: {path}:{name}:{index}')
                second = tag[1:2]
                entries.append(dict(index=index, tag=tag, nul_terminated=terminator >= 0,
                                    position=list(position), second_byte_r_or_f=second in ('R', 'F'),
                                    independent_s_branch=tag.startswith('S'),
                                    fifth_byte_n=raw[4:5] == b'N'))
                total_tags[tag] += 1
            if len(data) < 0x1f04:
                raise ValueError(f'Short FCE render header: {path}:{name}')
            part_count = struct.unpack_from('<i', data, 0xf8)[0]
            if part_count < 0 or 0x4fc+4*part_count > len(data):
                raise ValueError(f'Invalid part metadata extent: {path}:{name}')
            vertex_base = 0x1f04+struct.unpack_from('<I', data, 0x1c)[0]
            clear_ranges = []
            for index in range(part_count):
                first = struct.unpack_from('<I', data, 0x3fc+4*index)[0]
                vertices = struct.unpack_from('<i', data, 0x4fc+4*index)[0]
                start = vertex_base+32*first
                end = start+32*vertices
                if vertices < 0 or not 0x1f04 <= start <= end <= len(data):
                    raise ValueError(f'Invalid part vertex extent: {path}:{name}:{index}')
                clear_ranges.append(dict(part=index, first_vertex=first, vertex_count=vertices,
                                         vertex_start=start, vertex_end_exclusive=end,
                                         clear_first=start+0x14 if vertices else None,
                                         clear_last_end_exclusive=end-8 if vertices else None))
            preparation = dict(part_count=part_count, vertex_base=vertex_base,
                               effect_positions_end=0x38+12*effects, effect_tags_end=0xa04+64*effects,
                               effects_before_render_data=(0x38+12*effects <= 0x1f04 and 0xa04+64*effects <= 0x1e04),
                               builder_vertex_clear_ranges=clear_ranges)
            rows.append(dict(archive=path.relative_to(root).as_posix(),
                             archive_sha256=hashlib.sha256(archive).hexdigest(), member=name,
                             member_offset=offset, member_bytes=size,
                             member_sha256=hashlib.sha256(data).hexdigest(),
                             effect_count=effects, preparation_extents=preparation, entries=entries))
    return dict(scope='FCE members in installed GAMEDATA/CARMODEL/**/*.viv archives (case-insensitive extension); no loose FCE or modified/live model coverage.',
                layout_basis='004b8740: count+0x34, float3 positions+0x38 stride12, tag bytes+0xa04 stride64.',
                member_count=len(rows), entry_count=sum(r['effect_count'] for r in rows),
                tag_counts=dict(sorted(total_tags.items())), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('member_count', 'entry_count', 'tag_counts')}))


if __name__ == '__main__':
    main()
