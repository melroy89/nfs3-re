"""Bound the type1 initializer's computed/bulk destinations without target execution."""
import json
import struct

import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'projection-type1-initializer-bulk-boundary', 'binaries': {}, 'destinations': []}
    bodies = []
    for role, (path, expected, _) in SPECS.items():
        raw = (ROOT/path).read_bytes()
        assert sha(raw) == expected
        pe = pefile.PE(data=raw)
        body = pe.get_data(0x22da2, 0x422f11-0x422da2)
        bodies.append(body)
        rows = [struct.unpack('<2I', pe.get_data(0x152ec8+8*mode, 8)) for mode in range(1, 25)]
        assert rows[0] == (0x5e0dd8, 0x5e0ef4)
        assert max(pointer for row in rows for pointer in row) == rows[0][1]
        table = pe.get_data(0x22c88, 24*4)
        assert struct.unpack('<I', table[:4])[0] == 0x422ebb
        assert pe.get_data(0x22dd3, 5).hex() == 'b91e000000'
        assert pe.get_data(0x22ddd, 8).hex() == '8d787489580cf3a5'
        assert pe.get_data(0x22df2, 5).hex() == 'b909000000'
        assert pe.get_data(0x22df7, 11).hex() == '8d782c8db6c0000000f3a5'
        assert pe.get_data(0x22e53, 3).hex() == '83f919'
        assert pe.get_data(0x22eab, 3).hex() == '83f917'
        assert pe.get_data(0x22eb4, 7).hex() == 'ff248d882c4200'
        assert pe.get_data(0x22ecf, 10).hex() == 'c78018010000000080bf'
        asm = disassemble(body, 0x422da2)
        assert not any('\tcall' in line or ' call ' in line for line in asm)
        result['binaries'][role] = {'path': path, 'sha256': expected,
            'start_va': '00422da2', 'end_va_exclusive': '00422f11', 'body_sha256': sha(body),
            'disassembly': asm, 'mode1_pointers': [f'{v:08x}' for v in rows[0]],
            'mode_table_sha256': sha(pe.get_data(0x152ed0, 24*8)),
            'type_case_table_sha256': sha(table), 'type1_case': '00422ebb'}
    assert bodies[0] == bodies[1]
    sources = {0x5e1020, 0x5e102c, 0x5e1030, 0x5e1038}
    ranges = [(0x2c, 0x50, 'matrix-copy9DWORD'), (0x58, 0x71, 'byte-clear25'),
              (0x74, 0xec, 'template-copy30DWORD')]
    fields = [0, 4, 8, 0xc, 0x10, 0x14, 0x18, 0x1c, 0x20, 0x24, 0x28,
              0x50, 0x54, 0xec, 0xf0, 0xf4, 0xf8, 0xfc, 0x104, 0x108, 0x10c, 0x110, 0x114, 0x118]
    for slot, base in enumerate((0x5e0dd8, 0x5e0ef4)):
        local = [(base+lo, base+hi, label) for lo, hi, label in ranges]
        local += [(base+offset, base+offset+4, 'scalar-DWORD') for offset in fields]
        # The extra mode1 byte at69h is inside the already represented clear interval.
        assert all(not any(lo < source+4 and source < hi for source in sources) for lo, hi, _ in local)
        assert max(hi for _, hi, _ in local) == base+0x11c
        result['destinations'].append({'slot': slot, 'base': f'{base:08x}',
            'max_end_exclusive': f'{base+0x11c:08x}',
            'ranges': [{'start': f'{lo:08x}', 'end_exclusive': f'{hi:08x}', 'mechanism': label} for lo, hi, label in local]})
    result['source_cells'] = [f'{v:08x}' for v in sorted(sources)]
    result['limits'] = [
        'Conditional on initialized mode1 table, ordinary slot0/1 dispatch and forward string direction.',
        'Explicit destination enumeration from retained instructions, not automatic whole-program alias analysis.',
        'No structure size is inferred solely from pair spacing; this bounds these initializer writes.',
        'Other type cases, out-of-domain indices, later handlers, external writers and earlier callees are not excluded.',
        'No projection-source writer recovered and no horizon/render/runtime claim established.',
        'No target instructions, Ghidra mutations, reconstruction or compilation.']
    (ROOT/'analysis/evidence/audits/projection-initializer-bulk-boundary.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: retained type1 initializer/dispatch; explicit slot0/1 bulk/scalar destinations end at005e1010 and exclude four projection sources')


if __name__ == '__main__':
    main()
