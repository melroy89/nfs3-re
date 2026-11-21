"""Compare bounded race scheduling/physics ranges; static disassembly only."""
import hashlib
import json
import re
import struct

import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble

SPANS = [
    (0x4c48d0, 0x4c4abc, 'AdvanceRaceSimulationTick'),
    (0x42c830, 0x42c94e, 'RegisterVehicleUpdateCallbacks'),
    (0x4be3a0, 0x4be3cc, 'DispatchCallbackList'),
    (0x4ae4c1, 0x4ae5c2, 'UpdateVehiclePhysicsDispatch'),
    (0x4ad7a3, 0x4ae4c1, 'IntegrateVehicleFourWheelResponses'),
]


def main():
    result = {'kind': 'bounded-static-race-arithmetic-path', 'baselines': {}, 'ranges': []}
    images = {}
    for name, (path, expected, _) in SPECS.items():
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        images[name] = pefile.PE(data=raw)
        result['baselines'][name] = {'path': path, 'sha256': expected}
    for start, end, name in SPANS:
        bodies = {k: p.get_data(start - 0x400000, end - start) for k, p in images.items()}
        assert bodies['original'] == bodies['official_modern']
        lines = disassemble(bodies['original'], start)
        assert not any('(bad)' in line or '.byte' in line for line in lines)
        result['ranges'].append({
            'start': f'{start:08x}', 'end_exclusive': f'{end:08x}', 'name': name,
            'bytes': end - start, 'identical': True,
            'sha256': hashlib.sha256(bodies['original']).hexdigest(),
            'disassembly': lines,
            'control_or_integer_conversion_instructions': [line for line in lines if re.search(
                r'\b(finit|fninit|fldcw|fstcw|fnstcw|fldenv|frstor|fxrstor|fist\w*)\b', line)],
            'direct_calls': [line for line in lines if re.search(r'\bcall\s+0x', line)],
            'indirect_calls': [line for line in lines if 'call' in line and 'PTR' in line],
        })
    assert all(not row['control_or_integer_conversion_instructions'] for row in result['ranges'])
    physics = result['ranges'][-1]['disassembly']
    result['velocity_update_window'] = [line for line in physics if 0x4ae185 <= int(line.split(':')[0], 16) < 0x4ae1df]
    assert len(result['velocity_update_window']) == 18
    constants = {}
    for name, p in images.items():
        raw = p.get_data(0x53dea0 - 0x400000, 4)
        assert raw == bytes.fromhex('0000003d')
        constants[name] = {'address': '0053dea0', 'hex': raw.hex(), 'binary32': struct.unpack('<f', raw)[0]}
    result['scale_constant'] = constants
    result['limits'] = [
        'Names and boundaries reuse the saved inventory; equality is freshly checked against pinned EXEs.',
        'No direct CW instruction in these ranges does not establish inherited CW across delegated/indirect calls.',
        'Registration reads vehicle callback fields; full constructor/roster binding is not proven by these ranges.',
        'The selected velocity window has no call; its arithmetic inherits CW at window entry.',
        'No target execution, probes, C translation, compilation or executable/Ghidra changes.',
        'No replay, multiplayer, whole-physics or cross-version behavioral equivalence claim.',
    ]
    out = ROOT / 'analysis/evidence/audits/race-arithmetic-path.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: five race/callback/physics ranges identical; binary32 velocity stores and scale verified')


if __name__ == '__main__':
    main()
