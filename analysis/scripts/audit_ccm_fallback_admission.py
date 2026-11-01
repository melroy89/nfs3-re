"""Static CCM admission contracts; no selector or helper instructions executed."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'ccm-fallback-admission-static', 'binaries': {}, 'installed_loose_assets': []}
    spans = [(0x423d90, 0x423faa, 'complete-selector'),
             (0x4251f0, 0x425232, 'bounded-fallback-caller'),
             (0x4e0000, 0x4e0043, 'vector-subtract'),
             (0x4e01c0, 0x4e01ea, 'vector-normalize'),
             (0x4e06a0, 0x4e06c4, 'vector-length'),
             (0x4b7590, 0x4b767e, 'quaternion-to-matrix'),
             (0x4b79c0, 0x4b7a0a, 'basis-row-transform'),
             (0x4e0210, 0x4e0243, 'vector-dot-array')]
    pairs = []
    for role, (path, expected, _) in SPECS.items():
        raw = (ROOT/path).read_bytes()
        assert sha(raw) == expected
        pe = pefile.PE(data=raw)
        captures = []
        bodies = []
        for start, end, label in spans:
            body = pe.get_data(start-0x400000, end-start)
            bodies.append(body)
            captures.append({'label': label, 'start_va': f'{start:08x}', 'end_va_exclusive': f'{end:08x}',
                'sha256': sha(body), 'disassembly': disassemble(body, start)})
        assert struct.unpack('<d', pe.get_data(0x136e8c, 8))[0] == 1/65536
        assert pe.get_data(0x23f91, 9).hex() == '817deccdcccc3e7e05'
        assert pe.get_data(0x23f9a, 5).hex() == 'beffffffff'
        assert pe.get_data(0x23da2, 5).hex() == 'beffffffff'
        assert pe.get_data(0x23d9d, 5).hex() == 'ba1e000000'
        assert pe.get_data(0x23e85, 5).hex() == '3b45f47d05'
        assert pe.get_data(0x23f87, 5).hex() == 'b801000000'
        assert pe.get_data(0xe0237, 3).hex() == 'd959fc'
        pairs.append(bodies)
        result['binaries'][role] = {'path': path, 'sha256': expected, 'captures': captures,
            'position_quaternion_scale_double_hex': pe.get_data(0x136e8c, 8).hex()}
    assert pairs[0] == pairs[1]
    inventory_path = ROOT/'analysis/evidence/inventories/installed-ccm-extents.json'
    inventory = json.loads(inventory_path.read_text())
    root = ROOT/'nfs3_decomp.rep/Electronic Arts/Need For Speed III'
    for row in inventory['files']:
        path = root/row['path']
        raw = path.read_bytes()
        assert sha(raw) == row['sha256']
        magic, count = struct.unpack('<2i', raw[:8])
        assert magic == 1 and count == row['count'] and len(raw) == 8+28*count
        result['installed_loose_assets'].append({'path': str(path.relative_to(ROOT)),
            'sha256': sha(raw), 'count': count, 'bytes': len(raw)})
    assert len(result['installed_loose_assets']) == 8
    actual = {str(p.relative_to(ROOT)) for p in (root/'GAMEDATA/TRACKS').rglob('*')
              if p.is_file() and p.suffix.casefold() == '.ccm'}
    assert actual == {row['path'] for row in result['installed_loose_assets']}
    result['existing_inventory_sha256'] = sha(inventory_path.read_bytes())
    result['raw_comparison_derivations'] = []
    for name, bits in [('equal-threshold', 0x3ecccccd), ('one-bit-above', 0x3eccccce),
                       ('positive-zero', 0), ('negative-zero', 0x80000000),
                       ('positive-infinity', 0x7f800000), ('negative-infinity', 0xff800000),
                       ('positive-quiet-NaN', 0x7fc00000), ('negative-quiet-NaN', 0xffc00000)]:
        signed = bits if bits < 0x80000000 else bits-0x100000000
        result['raw_comparison_derivations'].append({'name': name, 'bits': f'{bits:08x}',
            'signed_int32': signed, 'rejects': signed > 0x3ecccccd,
            'scope': 'Integer branch derivation only; not generated dot results or instruction probes.'})
    result['limits'] = [
        'Positive installed counts do not establish distance/orientation admission or live file selection.',
        'Loaded keys are recomputed by the loader; file count/extent does not establish geometric coverage.',
        'Raw-comparison examples describe machine-branch semantics, not reachable exceptional inputs.',
        'All captured instruction bytes are retained; ambient x87 state and inputs can still differ.',
        'Projection-source producer/lifetime and visible horizon remain unresolved.',
        'No target execution, game/API calls, reconstruction, compilation or saved Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/ccm-fallback-admission.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:8 retained selector/helper envelopes;8 installed CCM identities; signed raw-bit gate and conditional fallback contract')


if __name__ == '__main__':
    main()
