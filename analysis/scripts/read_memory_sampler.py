# Read-only sampler for the documented NFS3 executable and fixed address map.
# Rediscover the PID each run; no process suspension or memory writes.
from pathlib import Path
import argparse
import json
import os
import struct
import signal
import time

p = argparse.ArgumentParser()
p.add_argument('pid', type=int)
p.add_argument('--seconds', type=float, default=900)
p.add_argument('--output', required=True)
p.add_argument('--reset-only', action='store_true', help='Omit physics profiles and spike records for focused reset capture')
p.add_argument('--spike-only', action='store_true', help='Capture strip and wheel geometry without repeated physics profile reads')
p.add_argument('--interval', type=float, default=0.02)
a = p.parse_args()
if a.reset_only and a.spike_only:
    p.error('--reset-only and --spike-only are mutually exclusive')
if not 0.01 <= a.interval <= 10:
    p.error('--interval must be between 0.01 and 10 seconds')
signal.signal(signal.SIGINT, lambda *_: exit(0))
proc = f'/proc/{a.pid}'
if open(proc + '/comm').read().strip().lower() != 'nfs3.exe':
    raise SystemExit('Target is not nfs3.exe')
fd = os.open(proc + '/mem', os.O_RDONLY)
def read(addr, size):
    b = os.pread(fd, size, addr)
    if len(b) != size:
        raise OSError('Short memory read')
    return b
def u(b, o=0): return struct.unpack_from('<I', b, o)[0]
def i(b, o=0): return struct.unpack_from('<i', b, o)[0]
def f(b, o=0): return struct.unpack_from('<f', b, o)[0]
if read(0x400000, 2) != b'MZ':
    raise SystemExit('Expected PE image missing')
start = time.monotonic()
Path(a.output).parent.mkdir(parents=True, exist_ok=True)
with open(a.output, 'w', buffering=1) as out:
    out.write(json.dumps({'kind':'metadata','pid':a.pid,'method':'pread O_RDONLY; no suspension; samples are not atomic','reset_only':a.reset_only,'spike_only':a.spike_only,'interval':a.interval,'maps':open(proc+'/maps').read()})+'\n')
    print('Sampler ready; read-only memory access verified', flush=True)
    while time.monotonic()-start < a.seconds:
        try:
            n = i(read(0x5efd9c,4))
            row = {'t':time.monotonic()-start, 'count':n, 'tick':u(read(0x7d3684,4)),
                   'stop_limit':i(read(0x6fd4bc,4)),
                   'session':i(read(0x6fd3b0,4)), 'race_mode':i(read(0x6fd3b8,4)),
                   'override_flags':u(read(0x6fd4fc,4)), 'override_selector':i(read(0x6fd500,4)),
                   'track':i(read(0x6fd4ac,4)),
                   'copassist':i(read(0x6fd4a8,4)), 'reverse':i(read(0x6fd4c0,4)),
                   'race_started':i(read(0x7d3680,4)), 'input_bits':read(0x79c4ab,1)[0],
                   'segment_count':i(read(0x5dd940,4)), 'reset_offset':i(read(0x5efdcc,4)),
                   'participant_count':i(read(0x5efda0,4)),
                   'local':i(read(0x6fd4f4,4)), 'skill':i(read(0x6fd4f0,4)), 'vehicles':[],
                   'timed_events':[list(struct.unpack('<20I',read(0x7dd850+idx*80,80))) for idx in range(8)] if not a.reset_only else []}
            pn=row['participant_count']
            if 0 <= pn <= 16:
                row['participant_pointers']=list(struct.unpack('<'+str(pn)+'I',read(0x5efc48,pn*4)))
            if 0 < n <= 16:
                ptrs = read(0x5efac8,n*4)
                for idx in range(n):
                    addr = u(ptrs,idx*4)
                    if not 0x5e1120 <= addr < 0x5eabe0 or (addr-0x5e1120)%0x9ac:
                        row['vehicles'].append({'pointer_rejected':addr}); continue
                    b=read(addr,0x9ac)
                    v={'address':addr,'master':i(b,0x1f0),'resource':b[0x1e4:0x1f0].split(b'\0')[0].decode('ascii','replace'),
                       'category':u(b,0x200),'active':b[0x89],'alternate':b[0x8a],
                       'upright_raw':i(b,0x10c),'upright':f(b,0x10c),'rpm':i(b,0x590),
                       'control_callback':u(b,0x600),'physics_callback':u(b,0x608),
                       'velocity':list(struct.unpack_from('<3f',b,0xa4)), 'profile':u(b,0x528),
                       'position':list(struct.unpack_from('<3f',b,0x98)),
                       'reset_cooldown':i(b,0x524),'reset_state_174':i(b,0x174),
                       'recovery_countdown_8a0':i(b,0x8a0),'impact_counter_8d4':i(b,0x8d4),
                       'recovery_gate_88':b[0x88],'recovery_input_504':b[0x504],
                       'recovery_field_20':i(b,0x20),'recovery_field_24':i(b,0x24),
                       'recovery_motion_b8':f(b,0xb8),
                       'recovery_attempts_2c0':i(b,0x2c0),'recovery_material_18c':i(b,0x18c),
                       'recovery_raw_15c':i(b,0x15c),
                       'recovery_vector_130':list(struct.unpack_from('<3f',b,0x130)),
                       'recovery_vector_cc':list(struct.unpack_from('<3f',b,0xcc)),
                       'reset_blocker_184':i(b,0x184),'ordering_2bc':i(b,0x2bc),
                       'lane_matches':i(b,0x2dc),'lane_misses':i(b,0x2e0),'cones_hit':i(b,0x2d8),
                       'racer_state':i(b,0x2c4),'stops':i(b,0x2c8),'police_stops':i(b,0x2cc),
                       'police_state':i(b,0x70c),'police_flags':u(b,0x710),
                       'target':u(b,0x624),'group':u(b,0x628),'observed_target':u(b,0x730),
                       'stop_link':u(b,0x9a4),'cooldown_until':u(b,0x634),'gear':b[0x50b],
                       'throttle':f(b,0x5f0),'speed_scalar':f(b,0x4f4),
                       'direction_state_5f4':i(b,0x5f4),
                       'state_164':struct.unpack_from('<h',b,0x164)[0],
                       'shift_state_510':struct.unpack_from('<h',b,0x510)[0],
                       'desired_speed_7b0':f(b,0x7b0),
                       'signed_motion_7c0':f(b,0x7c0),'motion_7c4':f(b,0x7c4),
                       'event_input':b[0x512],'event_latch':b[0x513],'police_index':i(b,0x714),
                       'segment':i(b,0x1c),'lane':i(b,0x638),'pursuit_raw':u(b,0x6f0),
                       'wheel_state_bytes':b[0x508:0x514].hex(),'contact_mask':u(b,0x99c),
                       'flags_620':u(b,0x620),
                       'derived_gear_factors':list(struct.unpack_from('<8f',b,0x56c)),
                       'drag_factor':f(b,0x58c)}
                    if a.spike_only:
                        v['rotation_matrix']=list(struct.unpack_from('<9f',b,0xc0))
                        v['wheel_positions_fixed']=[list(struct.unpack_from('<3i',b,0x304+j*0x78)) for j in range(4)]
                        v['strip_effect_counter']=i(b,0x9a0)
                        v['controller_state']=i(b,0x6e0)
                        v['pull_over_deadline']=i(b,0x6ec)
                        v['assignment_pointer']=u(b,0x7ac)
                        if v['category'] & 0x20 and v['assignment_pointer']:
                            try: v['assignment_bytes']=read(v['assignment_pointer'],8).hex()
                            except OSError as e: v['assignment_error']=str(e)
                    if v['group']:
                        try: v['group_dwords']=list(struct.unpack('<24I',read(v['group'],96)))
                        except OSError as e: v['group_error']=str(e)
                    if a.reset_only or a.spike_only:
                        v.pop('derived_gear_factors',None)
                        v.pop('drag_factor',None)
                        row['vehicles'].append(v)
                        continue
                    try:
                        profile=read(v['profile'],0x4ac)
                        v['torque']=list(struct.unpack_from('<41f',profile,0x114))
                        v['active_gear_count']=i(profile,8)
                        v['velocity_to_rpm']=list(struct.unpack_from('<8f',profile,0x94))
                        v['gear_efficiency']=list(struct.unpack_from('<8f',profile,0xd4))
                        v['idle_rpm']=i(profile,0x1c0)
                        v['redline_rpm']=i(profile,0x1c4)
                        v['max_velocity']=f(profile,0x1c8)
                        v['post_torque_dwords']=list(struct.unpack_from('<20I',profile,0x1b8))
                        cfg=read(u(b,0x220),0x6c)
                        v['model']=i(cfg,0x14)
                        v['transmission']=i(cfg,0x1c)
                        v['tuning']=list(struct.unpack_from('<7f',cfg,0x40))
                    except OSError as e: v['profile_error']=str(e)
                    row['vehicles'].append(v)
            out.write(json.dumps(row,allow_nan=True)+'\n')
            time.sleep(a.interval)
        except (OSError,ProcessLookupError) as e:
            out.write(json.dumps({'t':time.monotonic()-start,'error':str(e)})+'\n')
            break
os.close(fd)
