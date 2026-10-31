"""Compare view-offset mode contract, dispatcher and retained arithmetic, offline."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-view-offset-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/view-offset'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x4240c0, 0x424252), (0x421570, 0x4215b7), (0x4dffb0, 0x4dfff3), (0x426450, 0x42655a if label == 'original' else 0x42649a)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        table = struct.unpack('<24I', pe.get_data(0x263f0, 96))
        assert table[0] == (0x426482 if label == 'original' else 0x4240c0)
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'scene_dispatch_table_004263f0': [f'{a:08x}' for a in table], 'constant_00536eac_hex': pe.get_data(0x136eac, 8).hex()}
    out['retained_ranges'] = []
    for start, end in ((0x4240c0, 0x424101), (0x42416b, 0x424252), (0x421570, 0x4215b7), (0x4dffb0, 0x4dfff3)):
        pair = [p.get_data(start-0x400000, end-start) for p in images]
        assert pair[0] == pair[1]
        out['retained_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pair[0]).hexdigest()})
    bodies = [p.get_data(0x240c0, 0x192) for p in images]
    changes = [0x4240c0+i for i, (a,b) in enumerate(zip(*bodies)) if a != b]
    assert len(changes) == 102 and all(0x424101 <= a < 0x42416b for a in changes)
    out['changed_byte_addresses'] = [f'{a:08x}' for a in changes]
    original_table=struct.unpack('<24I',images[0].get_data(0x263f0,96))
    modern_table=struct.unpack('<24I',images[1].get_data(0x263f0,96))
    mappings=[];arms={}
    for selector,(arm,target) in enumerate(zip(original_table,modern_table),1):
        if arm==0x426555:
            assert selector in (15,22) and target==0x426290
            assert images[0].get_data(0x26555,5)==bytes.fromhex('5d5e595bc3')
            assert images[1].get_data(0x26290,1)==b'\xc3'
            original_target=None
        else:
            data=images[0].get_data(arm-0x400000,12)
            assert data[:3]==bytes.fromhex('89c8e8') and data[7:]==bytes.fromhex('5d5e595bc3')
            original_target=arm+7+int.from_bytes(data[3:7],'little',signed=True)
            assert original_target==target
            arms[f'{arm:08x}']=data.hex()
        mappings.append({'selector':selector,'original_arm':f'{arm:08x}',
            'original_callee':f'{original_target:08x}' if original_target is not None else None,
            'modern_callee':f'{target:08x}',
            'classification':'retained target' if original_target is not None else 'epilogue to RET-only stub'})
    assert images[0].get_data(0x26290,5)==bytes.fromhex('5589e55dc3')
    out['complete_scene_dispatch_mapping']={'entries':mappings,'unique_original_call_arms':arms,
        'retained_target_selectors':22,'epilogue_to_stub_selectors':[15,22],
        'original_stub_hex':'5589e55dc3','modern_stub_hex':'c3','limit':'Complete table/arm routing only; same target addresses do not establish unchanged callee bodies/ABI/FP state.'}
    out['limits'] = ['No target instructions or view rendering executed.', 'Same arithmetic bytes do not imply same ambient x87 control, inputs or outputs.', 'Scene/object layouts, dispatch index validity and complete caller census remain bounded.']
    (ROOT/'analysis/evidence/audits/original-modern-view-offset.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: 102 changed policy bytes, added mode contract, retained transform/helpers')


if __name__ == '__main__':
    main()
