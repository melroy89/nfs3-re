"""Inventory exact indexed camera-state operands and retained slot contract."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'projection-indexed-camera-state', 'binaries': {}}
    patterns = {
        0x5e1010: [(0x422d78, '893cdd10105e00', 'clear'),
                   (0x423928, '8914dd10105e00', 'set1'),
                   (0x423938, '8934dd10105e00', 'clear'),
                   (0x4239e7, '8904dd10105e00', 'set1'),
                   (0x4239f7, '8914dd10105e00', 'clear'),
                   (0x42460c, '833cc510105e0000', 'read'),
                   (0x424aca, '833cc510105e0000', 'read')],
        0x5e1014: [(0x422d86, '893cdd14105e00', 'clear'),
                   (0x4247af, '833cc514105e0020', 'read'),
                   (0x4263bf, 'ff04d514105e00', 'increment'),
                   (0x4263ca, '8934d514105e00', 'clear')]}
    paired = []
    for role, (path, expected, _) in SPECS.items():
        raw = (ROOT/path).read_bytes()
        assert sha(raw) == expected
        pe = pefile.PE(data=raw)
        row = {'path': path, 'sha256': expected, 'references': [], 'captures': []}
        for base, sites in patterns.items():
            literal_offsets = []
            position = 0
            while True:
                position = raw.find(struct.pack('<I', base), position)
                if position < 0:
                    break
                literal_offsets.append(position)
                position += 1
            expected_offsets = []
            for address, encoding, meaning in sites:
                body = bytes.fromhex(encoding)
                assert pe.get_data(address-0x400000, len(body)) == body
                offset = pe.get_offset_from_rva(address-0x400000)+body.index(struct.pack('<I', base))
                expected_offsets.append(offset)
                row['references'].append({'base': f'{base:08x}', 'instruction_va': f'{address:08x}',
                    'encoding': encoding, 'literal_file_offset': offset, 'operation': meaning})
            assert sorted(literal_offsets) == sorted(expected_offsets)
        spans = [(0x4238b0, 0x423959, 'primary-selector'),
                 (0x423960, 0x423a18, 'secondary-selector'),
                 (0x426370, 0x4263ef, 'preparer'),
                 (0x4247a9, 0x4247b9, 'bounded-signed-counter-consumer'),
                 (0x420bf0, 0x420d56, 'track-test-envelope-including-unreachable-zero')]
        bodies = []
        for start, end, label in spans:
            body = pe.get_data(start-0x400000, end-start)
            bodies.append(body)
            row['captures'].append({'label': label, 'start_va': f'{start:08x}',
                'end_va_exclusive': f'{end:08x}', 'sha256': sha(body),
                'disassembly': disassemble(body, start)})
        assert pe.get_data(0x247b7, 2).hex() == '7e13'
        helper = bodies[-1]
        assert helper[:7].hex() == '535152565589e5'
        epilogue = bytes.fromhex('89ec5d5e5a595bc21000')
        assert helper.count(epilogue) == 5 and helper.count(bytes.fromhex('c21000')) == 5
        assert pe.get_data(0x23921, 5).hex() == 'ba01000000'
        assert pe.get_data(0x23931, 2).hex() == '31f6'
        assert pe.get_data(0x239e0, 5).hex() == 'b801000000'
        assert pe.get_data(0x239f5, 2).hex() == '31d2'
        assert pe.get_data(0x263c8, 2).hex() == '31f6'
        paired.append(bodies)
        result['binaries'][role] = row
    assert paired[0] == paired[1]
    targets = [0x5e1020, 0x5e102c, 0x5e1030, 0x5e1038]
    result['wrapped_alias_indices'] = []
    for base in patterns:
        for target in targets:
            delta = (target-base) & 0xffffffff
            indices = [] if delta % 8 else [(delta//8+i*0x20000000) & 0xffffffff for i in range(8)]
            assert all((base+8*i) & 0xffffffff == target for i in indices)
            result['wrapped_alias_indices'].append({'base': f'{base:08x}', 'target': f'{target:08x}',
                'indices': [f'{i:08x}' for i in indices]})
    result['ordinary_slot_destinations'] = {'005e1010': ['005e1010', '005e1018'],
                                           '005e1014': ['005e1014', '005e101c']}
    result['limits'] = [
        'Complete literal inventory for these two exact bases, not every computed alias/bulk writer.',
        'Slot0/1 is an ordinary caller/initialization domain, not validation supplied by these helpers.',
        'Track-test EDX preservation is ordinary return through verified epilogues, not exception or corrupted-stack proof.',
        'Full helper transitive writes and every source-cell producer remain unresolved.',
        'Alias residues are arithmetic possibilities, not observed slot values or corruption.',
        'No new executable difference found in the four captured envelopes; changed surrounding dispatcher contract remains separate.',
        'No target instructions, game/API calls or Ghidra database writes.']
    (ROOT/'analysis/evidence/audits/projection-indexed-camera-state.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:11 exact-base indexed references per EXE; eight writer sites; five retained envelopes; five EDX-restoring RET16 epilogues')


if __name__ == '__main__':
    main()
