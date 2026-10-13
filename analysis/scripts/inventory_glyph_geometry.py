"""Inventory installed TEST.GFX using the verified cached glyph-loader layout.

Standard library only; reads assets without running the game. Does not validate
generated glyph topology, lighting state, resource resolution or live rendering.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def inventory(root):
    path = root.resolve() / 'GAMEDATA/RENDER/PC/TEST.GFX'
    data = path.read_bytes()
    if len(data) < 0x2010:
        raise ValueError('Truncated glyph header')
    first, count = data[:2]
    if first + count > 256:
        raise ValueError('Glyph range exceeds cached directory')
    cursor = 0x2010
    rows = []
    for code in range(first, first + count):
        record = 0x10 + code * 32
        flat_triangles, base_vertices = data[record], data[record + 2]
        triangles, vertices = data[record + 1], data[record + 3]
        index_start = cursor + vertices * 24
        end = index_start + triangles * 15
        if end > len(data):
            raise ValueError(f'Truncated glyph payload: {code}')
        indices = data[index_start:index_start + triangles * 3]
        positions_and_normals = struct.unpack_from(f'<{vertices * 6}f', data, cursor)
        face_normals = struct.unpack_from(f'<{triangles * 3}f', data, index_start + triangles * 3)
        paired_faces = 2 * flat_triangles <= triangles and all(
            tuple(indices[(flat_triangles+i)*3:(flat_triangles+i)*3+3]) ==
            tuple(j + base_vertices for j in reversed(indices[i*3:i*3+3]))
            for i in range(flat_triangles))
        fixed_face_normals = 2 * flat_triangles <= triangles and all(
            face_normals[i*3:i*3+3] == (0.0, 0.0, -1.0)
            and face_normals[(flat_triangles+i)*3:(flat_triangles+i)*3+3] == (0.0, 0.0, 1.0)
            for i in range(flat_triangles))
        vertex_normals = positions_and_normals[vertices * 3:]
        normal_lengths = [math.sqrt(sum(v*v for v in values[i:i+3]))
                          for values in (vertex_normals, face_normals)
                          for i in range(0, len(values), 3)]
        zero_area = None
        orientation_counts = dict(positive=0, negative=0, zero=0)
        orientation_cosines = []
        if all(i < vertices for i in indices):
            zero_area = 0
            for i in range(0, len(indices), 3):
                a, b, c = [positions_and_normals[j*3:j*3+3] for j in indices[i:i+3]]
                u = [b[k]-a[k] for k in range(3)]
                v = [c[k]-a[k] for k in range(3)]
                cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
                zero_area += all(x == 0 for x in cross)
                normal = face_normals[i:i+3]
                dot = sum(cross[k]*normal[k] for k in range(3))
                orientation_counts['positive' if dot > 0 else 'negative' if dot < 0 else 'zero'] += 1
                denominator = math.sqrt(sum(x*x for x in cross) * sum(x*x for x in normal))
                if denominator:
                    orientation_cosines.append(dot / denominator)
        rows.append(dict(code=code, character=chr(code), vertices=vertices,
                         base_vertices=base_vertices, flat_triangles=flat_triangles,
                         reversed_offset_back_faces=paired_faces,
                         fixed_front_back_normals=fixed_face_normals,
                         paired_vertex_count=vertices == 2 * base_vertices,
                         paired_xy_and_unit_depth=vertices == 2 * base_vertices and all(
                             positions_and_normals[k*3:k*3+2] == positions_and_normals[(k+base_vertices)*3:(k+base_vertices)*3+2]
                             and positions_and_normals[k*3+2] == 0
                             and positions_and_normals[(k+base_vertices)*3+2] == 1
                             for k in range(base_vertices)),
                         flat_triangle_count_within_total=flat_triangles <= triangles,
                         flat_indices_within_base=flat_triangles <= triangles and all(i < base_vertices for i in indices[:flat_triangles * 3]),
                         triangles=triangles, payload_start=cursor, payload_end=end,
                         maximum_index=max(indices, default=None),
                         indices_in_range=all(i < vertices for i in indices),
                         zero_area_triangles=zero_area,
                         winding_normal_dot_counts=orientation_counts,
                         minimum_winding_normal_cosine=min(orientation_cosines, default=None),
                         maximum_winding_normal_cosine=max(orientation_cosines, default=None),
                         zero_normals=sum(x == 0 for x in normal_lengths),
                         minimum_normal_length=min(normal_lengths, default=None),
                         maximum_normal_length=max(normal_lengths, default=None),
                         finite_vectors=all(math.isfinite(v) for v in positions_and_normals + face_normals)))
        cursor = end
    return dict(path='GAMEDATA/RENDER/PC/TEST.GFX',
                sha256=hashlib.sha256(data).hexdigest(), file_bytes=len(data),
                method='Static installed-asset inventory; cached loader00475240 uses absolute character-indexed32-byte records and packed payload at0x2010. Not runtime evidence.',
                first_code=first, glyph_count=count, payload_end=cursor,
                exact_payload_extent=cursor == len(data), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(glyph_count=report['glyph_count'], exact_payload_extent=report['exact_payload_extent'])))


if __name__ == '__main__':
    main()
