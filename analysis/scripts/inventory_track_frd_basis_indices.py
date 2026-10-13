#!/usr/bin/env python3
"""Inventory installed FRD packed-basis references selected by COLL type 15.

Standard library only. Parses the FRD stream sequentially through the first
per-block pass that reads the packed-basis table at block+0x598, using the
statically documented loader layout. It then follows each COLL type-15
segment ordinal to its FRD descriptor and material records. This is installed
asset evidence, not proof of successful loading or runtime validity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


U32_MAX = 0xffffffff


class AssetFormatError(ValueError):
    """An installed asset does not fit the statically documented layout."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def loader_array_bytes(count, stride, label):
    """Return the x86 DWORD product only when it does not wrap."""
    size = count * stride
    if size > U32_MAX:
        raise AssetFormatError(f'{label}: 32-bit loader size multiplication wraps')
    return size


def parse_frd(path):
    data = path.read_bytes()
    cursor = 0

    def take(size, label):
        nonlocal cursor
        if size < 0 or cursor + size > len(data):
            raise AssetFormatError(
                f'{path}: {label} at 0x{cursor:x} requests {size} bytes '
                f'past file end 0x{len(data):x}')
        start = cursor
        chunk = data[start:start + size]
        cursor += size
        return start, chunk

    # 00419c20 reads an opaque four-byte value, three eight-byte values, then
    # the top-level count. Do not assign semantics to the opaque header fields.
    take(4, 'opaque header field')
    take(8, 'opaque header field')
    take(8, 'opaque header field')
    take(8, 'opaque header field')
    _, raw_top_count = take(4, 'top-level block count')
    top_count = struct.unpack('<I', raw_top_count)[0]
    if top_count >= len(data):
        raise AssetFormatError(f'{path}: implausible top-level block count {top_count}')

    blocks = []
    # The loader loops inclusively, so there are top_count + 1 block records.
    for block_index in range(top_count + 1):
        take(12, 'block+0x78 bytes')
        take(0x30, 'block+0x84 bytes')

        _, raw_count_58 = take(4, 'block+0x58 count')
        count_58 = struct.unpack('<I', raw_count_58)[0]
        take(0x14, 'block+0x5c bytes')
        take(loader_array_bytes(count_58, 12, 'block+0x70 array'),
             'block+0x70 array')
        take(loader_array_bytes(count_58, 4, 'block+0x74 array'),
             'block+0x74 array')
        take(0x4b0, 'block+0xb4 bytes')

        # These eight DWORDs are read in this order by the loader. The +0x584
        # field is the first segment ordinal; the following counts describe
        # the descriptor, material, packed-basis and later tables.
        counts = {}
        for field_offset in (0x584, 0x588, 0x590, 0x598,
                             0x5a0, 0x5a8, 0x5b0, 0x5b8):
            _, raw_count = take(4, f'block+0x{field_offset:x} count')
            counts[field_offset] = struct.unpack('<I', raw_count)[0]

        arrays = {}
        array_offsets = {}
        for field_offset, stride in ((0x588, 8), (0x590, 8), (0x598, 12),
                                     (0x5a0, 20), (0x5a8, 20),
                                     (0x5b0, 16), (0x5b8, 16)):
            array_offsets[field_offset], arrays[field_offset] = take(
                loader_array_bytes(counts[field_offset], stride,
                                   f'block+0x{field_offset:x} array'),
                f'block+0x{field_offset:x} array')

        blocks.append({
            'index': block_index,
            'first_segment': counts[0x584],
            'descriptor_count': counts[0x588],
            'descriptor_table_file_offset': array_offsets[0x588],
            'descriptors': arrays[0x588],
            'material_count': counts[0x590],
            'material_table_file_offset': array_offsets[0x590],
            'materials': arrays[0x590],
            'basis_count': counts[0x598],
            'basis_table_file_offset': array_offsets[0x598],
            'basis_bytes': arrays[0x598],
        })

    return data, top_count, blocks, cursor


def parse_coll(path):
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b'COLL':
        raise AssetFormatError(f'{path}: missing COLL header')
    version, declared_size, block_count = struct.unpack_from('<3I', data, 4)
    directory_end = 16 + 4 * block_count
    if declared_size != len(data) or directory_end > len(data):
        raise AssetFormatError(f'{path}: invalid declared file or directory extent')

    type15 = []
    for directory_index in range(block_count):
        relative_offset = struct.unpack_from('<I', data, 16 + 4 * directory_index)[0]
        offset = 16 + relative_offset
        if offset < directory_end or offset + 8 > len(data):
            raise AssetFormatError(f'{path}: invalid block header at directory index {directory_index}')
        block_size, block_type, record_count = struct.unpack_from('<IHH', data, offset)
        if block_size < 8 or offset + block_size > len(data):
            raise AssetFormatError(f'{path}: invalid block extent at directory index {directory_index}')
        if block_type == 15:
            expected_size = 8 + 36 * record_count
            if block_size != expected_size:
                raise AssetFormatError(
                    f'{path}: type-15 block {directory_index} has {block_size} bytes; '
                    f'expected {expected_size}')
            type15.append({
                'directory_index': directory_index,
                'file_offset': offset,
                'record_count': record_count,
            })
    return data, version, block_count, type15


def inventory(game_root):
    game_root = game_root.resolve()
    track_root = game_root / 'GAMEDATA' / 'TRACKS'
    frd_paths = sorted(track_root.glob('TRK*/*.FRD'))
    if not frd_paths:
        raise AssetFormatError(f'no uppercase GAMEDATA/TRACKS/TRK*/*.FRD files under {game_root}')

    rows = []
    for frd_path in frd_paths:
        relative_frd = frd_path.relative_to(game_root).as_posix()
        coll_path = frd_path.with_suffix('.COL')
        if not coll_path.is_file():
            raise AssetFormatError(f'{relative_frd}: matching COLL file is missing')
        frd_data, top_count, blocks, parsed_end = parse_frd(frd_path)
        coll_data, coll_version, coll_block_count, type15 = parse_coll(coll_path)
        relative_coll = coll_path.relative_to(game_root).as_posix()
        if len(type15) != 1:
            raise AssetFormatError(
                f'{relative_coll}: expected one type-15 block, found {len(type15)}')

        segment_count = type15[0]['record_count']
        used_by_block = [[] for _ in blocks]
        mapping_errors = []
        material_table_index_errors = []

        # COLL type-15 records are the active segment records. The statically
        # verified binder chooses an FRD block by segment>>3, then descriptor
        # index = segment - the DWORD at that block's +0x584.
        for segment in range(segment_count):
            block_index = segment >> 3
            if block_index >= len(blocks):
                mapping_errors.append({'segment': segment, 'reason': 'FRD block missing'})
                continue
            block = blocks[block_index]
            descriptor_index = segment - block['first_segment']
            if not 0 <= descriptor_index < block['descriptor_count']:
                mapping_errors.append({
                    'segment': segment,
                    'block': block_index,
                    'first_segment': block['first_segment'],
                    'descriptor_count': block['descriptor_count'],
                    'descriptor_index': descriptor_index,
                })
                continue

            descriptor_offset = descriptor_index * 8
            descriptor = block['descriptors'][descriptor_offset:descriptor_offset + 8]
            if len(descriptor) != 8:
                mapping_errors.append({'segment': segment, 'reason': 'short descriptor record'})
                continue
            material_base = struct.unpack_from('<H', descriptor, 0)[0]
            strip_count = descriptor[2]
            for strip in range(strip_count):
                material_index = material_base + strip
                if material_index >= block['material_count']:
                    material_table_index_errors.append({
                        'segment': segment,
                        'block': block_index,
                        'descriptor_index': descriptor_index,
                        'material_index': material_index,
                        'material_count': block['material_count'],
                    })
                    continue
                entry_offset = material_index * 8
                material = block['materials'][entry_offset:entry_offset + 8]
                if len(material) != 8:
                    material_table_index_errors.append({
                        'segment': segment,
                        'block': block_index,
                        'material_index': material_index,
                        'reason': 'short material record',
                    })
                    continue
                used_by_block[block_index].append((material_index, material[0]))

        if mapping_errors or material_table_index_errors:
            raise AssetFormatError(
                f'{relative_frd}: segment/material mapping failed: '
                f'{len(mapping_errors)} descriptor errors, '
                f'{len(material_table_index_errors)} material table errors')

        invalid_references = []
        block_rows = []
        for block, refs in zip(blocks, used_by_block):
            selected_indices = [basis_index for _, basis_index in refs]
            for material_index, basis_index in refs:
                if basis_index >= block['basis_count']:
                    invalid_references.append({
                        'block': block['index'],
                        'material_index': material_index,
                        'basis_index': basis_index,
                        'basis_count': block['basis_count'],
                    })
            block_rows.append({
                'index': block['index'],
                'first_segment': block['first_segment'],
                'descriptor_count': block['descriptor_count'],
                'descriptor_table_file_offset': block['descriptor_table_file_offset'],
                'material_count': block['material_count'],
                'material_table_file_offset': block['material_table_file_offset'],
                'basis_count': block['basis_count'],
                'basis_table_file_offset': block['basis_table_file_offset'],
                'selected_material_entry_references': len(refs),
                'selected_basis_index_min': min(selected_indices) if selected_indices else None,
                'selected_basis_index_max': max(selected_indices) if selected_indices else None,
                'out_of_range_basis_references': sum(
                    basis_index >= block['basis_count'] for basis_index in selected_indices),
            })

        if invalid_references:
            # Retain a bounded sample for diagnosis while preserving the total.
            invalid_sample = invalid_references[:16]
        else:
            invalid_sample = []

        all_refs = [ref for refs in used_by_block for ref in refs]
        all_basis_indices = [basis_index for _, basis_index in all_refs]
        basis_counts = [block['basis_count'] for block in blocks]
        material_entry_count = sum(block['material_count'] for block in blocks)
        selected_unique_entries = sum(
            len(set(material_index for material_index, _ in refs)) for refs in used_by_block)

        rows.append({
            'track': frd_path.parent.name,
            'frd': {
                'path': relative_frd,
                'bytes': len(frd_data),
                'sha256': sha256(frd_data),
                'top_level_count_field': top_count,
                'block_count': len(blocks),
                'bytes_consumed_through_first_pass': parsed_end,
                'bytes_left_for_later_loader_passes': len(frd_data) - parsed_end,
                'basis_count_min': min(basis_counts),
                'basis_count_max': max(basis_counts),
                'zero_basis_count_blocks': sum(value == 0 for value in basis_counts),
                'descriptor_count_total': sum(block['descriptor_count'] for block in blocks),
                'material_table_entry_count_total': material_entry_count,
                'blocks': block_rows,
            },
            'coll': {
                'path': relative_coll,
                'bytes': len(coll_data),
                'sha256': sha256(coll_data),
                'version': coll_version,
                'block_count': coll_block_count,
                'type15_block_count': len(type15),
                'type15_segment_record_count': segment_count,
            },
            'selected_material_entry_references': len(all_refs),
            'unique_selected_material_entries': selected_unique_entries,
            'selected_basis_index_min': min(all_basis_indices) if all_basis_indices else None,
            'selected_basis_index_max': max(all_basis_indices) if all_basis_indices else None,
            'out_of_range_basis_reference_count': len(invalid_references),
            'out_of_range_basis_reference_examples': invalid_sample,
            'descriptor_mapping_error_count': len(mapping_errors),
            'material_table_index_error_count': len(material_table_index_errors),
            'every_type15_segment_mapped': len(mapping_errors) == 0,
            'every_material_table_entry_selected': selected_unique_entries == material_entry_count,
        })

    all_basis_counts = [
        block['basis_count']
        for row in rows
        for block in row['frd']['blocks']
    ]
    all_indices = [
        value
        for row in rows
        for block in row['frd']['blocks']
        for value in (block['selected_basis_index_min'], block['selected_basis_index_max'])
        if value is not None
    ]
    return {
        'scope': 'Installed uppercase GAMEDATA/TRACKS/TRK*/*.FRD files paired with their matching .COL files.',
        'method': (
            'Sequentially follows the first per-block read pass in LoadTrackFrdResourceStructures '
            '(00419c20), including preceding fixed and count-sized arrays, through each table at '
            'block+0x598. For each COLL type-15 segment ordinal, follows the statically verified '
            'FRD group/descriptor mapping (segment>>3; descriptor index = segment - block+0x584), '
            'then enumerates every strip material entry at descriptor WORD+0 plus strip ordinal. '
            'Compares the unsigned material entry byte0 against the matching block+0x598 DWORD count.'
        ),
        'limitations': (
            'Asset parsing only. The parser stops after the loader first-pass per-block arrays and '
            'does not parse later FRD passes, emulate arena allocation/cursor failure, or execute the '
            'game. All descriptor strips are included, even entries a runtime search may reject. '
            'A zero out-of-range count does not establish successful runtime loading or behavior.'
        ),
        'totals': {
            'frd_file_count': len(rows),
            'coll_file_count': len(rows),
            'frd_block_count': sum(row['frd']['block_count'] for row in rows),
            'coll_type15_segment_record_count': sum(
                row['coll']['type15_segment_record_count'] for row in rows),
            'selected_material_entry_reference_count': sum(
                row['selected_material_entry_references'] for row in rows),
            'unique_selected_material_entry_count': sum(
                row['unique_selected_material_entries'] for row in rows),
            'descriptor_mapping_error_count': sum(
                row['descriptor_mapping_error_count'] for row in rows),
            'material_table_index_error_count': sum(
                row['material_table_index_error_count'] for row in rows),
            'out_of_range_basis_reference_count': sum(
                row['out_of_range_basis_reference_count'] for row in rows),
            'basis_count_min': min(all_basis_counts),
            'basis_count_max': max(all_basis_counts),
            'zero_basis_count_blocks': sum(value == 0 for value in all_basis_counts),
            'selected_basis_index_min': min(all_indices) if all_indices else None,
            'selected_basis_index_max': max(all_indices) if all_indices else None,
        },
        'files': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path,
                        help='complete installed NFS III directory containing GAMEDATA/')
    parser.add_argument('--output', type=Path, required=True,
                        help='JSON report path')
    args = parser.parse_args()
    try:
        report = inventory(args.game_root)
    except (OSError, AssetFormatError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['totals'], sort_keys=True))


if __name__ == '__main__':
    main()
