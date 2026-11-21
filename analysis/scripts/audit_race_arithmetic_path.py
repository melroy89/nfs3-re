"""Compare bounded race scheduling/physics ranges; static disassembly only."""
import hashlib
import json
import re
import struct

import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble

SPANS = [
    (0x42c400, 0x42c51f, 'InitializeVehicleUpdateCallbacks'),
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
    inventory = json.loads((ROOT / 'analysis/evidence/audits/original-modern-function-diff.json').read_text())
    by_entry = {row['entry']: row for row in inventory['functions']}
    result['integration_direct_helpers'] = []
    for call in result['ranges'][-1]['direct_calls']:
        entry = int(re.search(r'call\s+0x([0-9a-f]+)', call)[1], 16)
        saved = by_entry[f'{entry:08x}']
        chunks = {}
        for baseline, image in images.items():
            chunks[baseline] = b''.join(image.get_data(int(a, 16) - 0x400000, int(b, 16) - int(a, 16))
                                        for a, b in saved['ranges'])
        assert chunks['original'] == chunks['official_modern']
        lines = []
        for a, b in saved['ranges']:
            lines += disassemble(images['original'].get_data(int(a, 16) - 0x400000, int(b, 16) - int(a, 16)), int(a, 16))
        assert not any('(bad)' in line or '.byte' in line for line in lines)
        result['integration_direct_helpers'].append({
            'entry': saved['entry'], 'name': saved['name'], 'ranges': saved['ranges'],
            'identical': True, 'sha256': hashlib.sha256(chunks['original']).hexdigest(),
            'control_instructions': [line for line in lines if re.search(r'\b(finit|fninit|fldcw|fldenv|frstor|fxrstor)\b', line)],
            'integer_conversions': [line for line in lines if re.search(r'\bfist\w*\b', line)],
            'calls': [line for line in lines if re.search(r'\bcall\b', line)],
        })
    assert len(result['integration_direct_helpers']) == 18
    assert not any(row['control_instructions'] for row in result['integration_direct_helpers'])
    constants = {}
    for name, p in images.items():
        raw = p.get_data(0x53dea0 - 0x400000, 4)
        assert raw == bytes.fromhex('0000003d')
        constants[name] = {'address': '0053dea0', 'hex': raw.hex(), 'binary32': struct.unpack('<f', raw)[0]}
    result['scale_constant'] = constants
    result['limits'] = [
        'Names and boundaries reuse the saved inventory; equality is freshly checked against pinned EXEs.',
        'No direct CW instruction in these ranges does not establish inherited CW across delegated/indirect calls.',
        'Initializer assignments are verified; later writers, actual roster and callback publication lifetime remain open.',
        'The18 immediate helpers are compared; their further calls are listed but not transitively qualified.',
        'The selected velocity window has no call; its arithmetic inherits CW at window entry.',
        'No target execution, probes, C translation, compilation or executable/Ghidra changes.',
        'No replay, multiplayer, whole-physics or cross-version behavioral equivalence claim.',
    ]
    out = ROOT / 'analysis/evidence/audits/race-arithmetic-path.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: six race/callback/physics ranges and18 immediate helpers identical; binary32 velocity stores and scale verified')


if __name__ == '__main__':
    main()
