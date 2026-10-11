"""Offline reconstruction of retained samples; does not access the running game.

Uses Python double intermediates and explicit binary32 stores matching the
observed stages. It is not an x87 emulator or an atomic instruction trace.
"""
import json
import struct
from pathlib import Path

BASE = Path(__file__).resolve().parent

def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]

def transform(m, p):
    return [f32(sum(m[3*k+c]*p[c] for c in range(3))) for k in range(3)]

def clip(poly, axis, sign):
    out = []
    if not poly:
        return out
    prev = poly[-1]
    dp = sign*prev[axis] - 0.5
    for cur in poly:
        dc = sign*cur[axis] - 0.5
        if (dc <= 0) != (dp <= 0):
            t = dp/(dp-dc)
            out.append([prev[k]+t*(cur[k]-prev[k]) for k in range(3)])
        if dc <= 0:
            out.append(cur)
        prev, dp = cur, dc
    return out

results = []
for name, target in [('spike-contact-and-recovery', 1), ('spike-contact-and-arrest', 3)]:
    rows = json.loads((BASE/'runtime'/f'{name}.json').read_text())['samples']
    first = next(i for i,r in enumerate(rows) if r['vehicles'][target]['contact_mask'])
    row = rows[first]
    v = row['vehicles'][target]
    prior = next(r for r in reversed(rows[:first]) if r['timed_events'][0][0])
    raw = prior['timed_events'][0]
    vertices = [struct.unpack('<3f', struct.pack('<3I', *raw[1+3*j:4+3*j])) for j in range(4)]
    m = v['rotation_matrix']
    wheels = []
    mask = 0
    for j, fixed in enumerate(v['wheel_positions_fixed']):
        negative = transform(m, [-f32(x/65536) for x in fixed])
        transformed = [[f32(a+b) for a,b in zip(transform(m,p), negative)] for p in vertices]
        codes = []
        for p in transformed:
            code = 0
            for x,lo,hi in zip(p,[1,4,16],[2,8,32]):
                if x > .5: code |= hi
                if x < -.5: code |= lo
            codes.append(code)
        accepted = (codes[0]&codes[1]&codes[2]&codes[3]) == 0
        if accepted: mask |= 1 << j
        polygon = transformed
        for axis in range(3):
            for sign in (-1,1):
                polygon = clip(polygon,axis,sign)
        # Independent XZ separating-axis certificate, with a positive gap
        # proving separation even if rounded vertices are slightly nonplanar.
        a, b = transformed[:2]
        nx, nz = a[2]-b[2], b[0]-a[0]
        length = (nx*nx+nz*nz)**0.5
        gap = None
        if length:
            nx, nz = nx/length, nz/length
            values = [nx*p[0]+nz*p[2] for p in transformed]
            support = (abs(nx)+abs(nz))*.5
            gap = max(min(values)-support, -max(values)-support)
        wheels.append({'index':j,'transformed_vertices':transformed,'outcodes':codes,
                       'candidate':accepted,'xz_separation_gap':gap,'clipped_polygon':polygon,
                       'quad_intersects_cube_at_sampled_pose':bool(polygon)})
    results.append({'capture':name,'geometry_tick':prior['tick'],'vehicle_tick':row['tick'],
                    'observed_mask':v['contact_mask'],'reconstructed_mask':mask,'wheels':wheels})
output = {'limitations':['Asynchronous sample poses, not exact contact instruction inputs.',
                         'Double intermediates with explicit float stores, not full x87 emulation.',
                         'Polygon clipping concerns the sampled quad/cube, not physical tyre geometry.'],
          'results':results}
(BASE/'spike-contact-reconstruction.json').write_text(json.dumps(output,indent=2)+'\n')
for r in results:
    print(r['capture'], 'observed/reconstructed', r['observed_mask'], r['reconstructed_mask'],
          'intersections', [w['quad_intersects_cube_at_sampled_pose'] for w in r['wheels']])
