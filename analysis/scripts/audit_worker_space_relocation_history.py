"""Verify120->130 block relocation that frees space for the input worker."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    specs = {
        '1.2.0': ('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b',
                  '4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003', 0x41d7c8),
        '1.3.0': ('93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
                  'deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146', 0x40fed0),
    }
    result = {'kind': 'static-worker-space-relocation-history', 'versions': {}}
    blocks = []
    for version, (archive_hash, exe_hash, start) in specs.items():
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT / relative).read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(ROOT / relative), 'nfs3.exe'])
        assert sha(raw) == exe_hash
        pe = pefile.PE(data=raw)
        body = pe.get_data(start - 0x400000, 150)
        blocks.append(body)
        pointer = struct.unpack('<I', pe.get_data(0x41ca4, 4))[0]
        assert pointer == start
        result['versions'][version] = {
            'archive': relative, 'archive_sha256': archive_hash, 'member': 'nfs3.exe',
            'sha256': exe_hash, 'start': f'{start:08x}', 'end_exclusive': f'{start+150:08x}',
            'block_sha256': sha(body), 'hex': body.hex(), 'disassembly': disassemble(body, start),
            'stored_target_address': '00441ca4', 'stored_target': f'{pointer:08x}',
        }
    old_start, new_start = 0x41d7c8, 0x40fed0
    normalized = bytearray(blocks[0])
    transfers = []
    for line in result['versions']['1.2.0']['disassembly']:
        address = int(line.split(':', 1)[0], 16)
        offset = address - old_start
        opcode = blocks[0][offset]
        if opcode in (0xe8, 0xe9):
            operand_offset, length = 1, 5
        elif opcode == 0x0f and 0x80 <= blocks[0][offset+1] <= 0x8f:
            operand_offset, length = 2, 6
        else:
            continue
        displacement = struct.unpack_from('<i', blocks[0], offset+operand_offset)[0]
        target = address + length + displacement
        struct.pack_into('<i', normalized, offset+operand_offset, target-(new_start+offset+length))
        transfers.append({'old_instruction': f'{address:08x}',
                          'new_instruction': f'{new_start+offset:08x}', 'unchanged_target': f'{target:08x}'})
    assert bytes(normalized) == blocks[1]
    assert transfers[-1]['unchanged_target'] == '004421b8'
    result['relative_transfers'] = transfers
    result['all_other_bytes_equal'] = True
    result['limits'] = [
        'Complete150-byte block comparison, not complete parent-frame/dispatch reconstruction.',
        'Stored target correspondence and normalized relative operands establish relocation, not a new music feature.',
        'Return/instruction addresses differ; no whole-machine, stack-address or exceptional equivalence claim.',
        'Final function names/roles at these addresses must not be transferred to historical binaries.',
        'No target/API/instruction execution, binary edits or Ghidra changes.',
    ]
    (ROOT / 'analysis/evidence/audits/worker-space-relocation-history.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS:150-byte block relocates41d7c8->40fed0 with{len(transfers)} unchanged relative targets;stored target retargeted')


if __name__ == '__main__':
    main()
