"""Bounded, read-only HUD capture; does not suspend or modify the game."""
import argparse
import json
import os
import struct
import time

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('pid', type=int)
p.add_argument('--seconds', type=float, default=300)
a = p.parse_args()
if not 0 < a.seconds <= 600:
    p.error('duration must be between zero and 600 seconds')
if open(f'/proc/{a.pid}/comm').read().strip().lower() != 'nfs3.exe':
    raise SystemExit('Target is not nfs3.exe')
fd = os.open(f'/proc/{a.pid}/mem', os.O_RDONLY)
def read(address, size):
    if not 0x400000 <= address <= 0xa20000-size:
        raise ValueError('Address outside expected image range')
    data = os.pread(fd, size, address)
    if len(data) != size:
        raise ValueError('Short read')
    return data
def u(address):
    return struct.unpack('<I', read(address, 4))[0]
def entry(index):
    if not 0 <= index < 2000:
        return {'invalid_index': index}
    address = 0x604ee0 + index*0xbc
    b = read(address, 0xbc)
    kind = struct.unpack_from('<I', b)[0]
    if kind != 31:
        return {'address': hex(address), 'type': kind,
                'flags': struct.unpack_from('<H', b, 4)[0]}
    return {'address': hex(address), 'type': struct.unpack_from('<I', b)[0],
            'flags': struct.unpack_from('<H', b, 4)[0],
            'item': struct.unpack_from('<i', b, 0x3c)[0],
            'xy': struct.unpack_from('<2h', b, 6),
            'right_bottom': struct.unpack_from('<2i', b, 0x60),
            'normalized_words': struct.unpack_from('<4h', b, 0x1a),
            'rectangle': struct.unpack_from('<4f', b, 0x40),
            'status_link_mode': struct.unpack_from('<3I', b, 0x70),
            'mouse_keyboard': struct.unpack_from('<2h', b, 0x7c)}
try:
    if read(0x400000, 2) != b'MZ':
        raise SystemExit('Expected image missing')
    print(json.dumps({'ready': True, 'pid': a.pid,
                      'method': 'O_RDONLY pread; no suspension; non-atomic samples'}), flush=True)
    start = time.monotonic()
    while time.monotonic()-start < a.seconds:
        try:
            menu = u(0x559230)
            b = read(menu, 0x24)
            first, selected = struct.unpack_from('<2h', b, 0x18)
            name = read(struct.unpack_from('<I', b, 0x14)[0], 64).split(b'\0')[0].decode('ascii', 'replace')
            row = {'t': time.monotonic()-start, 'unix_time': time.time(), 'menu': name,
                   'session': u(0x6fd3b0), 'first': first, 'selected': selected,
                   'viewport': struct.unpack('<2i', read(0x7cdac8, 8)),
                   'split_bounds': struct.unpack('<2i', read(0x677e10, 8))}
            if selected != 100:
                row['entry'] = entry(first+selected)
            if name.startswith('ps2p') and 0 <= first < 2000:
                row['target23'] = None
                for index in range(first, min(first+100, 2000)):
                    candidate = entry(index)
                    if candidate['type'] == 0:
                        break
                    if candidate['type'] == 31 and candidate['item'] == 23:
                        row['target23'] = candidate
                        break
            print(json.dumps(row), flush=True)
        except (OSError, ValueError, struct.error) as exc:
            print(json.dumps({'error': str(exc)}), flush=True)
        time.sleep(0.2)
finally:
    os.close(fd)
