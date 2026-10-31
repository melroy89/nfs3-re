"""Check wide-angle caller ABI adjustment and relocated scaling constants."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'projection-caller-followup', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/projection-callers'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        blobs[label] = []
        for start, end in [(0x495190, 0x495223), (0x4dbda0, 0x4dbddf),
                           (0x4dece0,0x4dedea),(0x4dedf0,0x4dee71),
                           (0x4dbde0,0x4dbee6)]:
            data = pe.get_data(start - 0x400000, end - start)
            blobs[label].append(data)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        constants = []
        for address in ([0x53be28, 0x53be2c] if label == 'original' else [0x53bdd4, 0x53bdd8]):
            data = pe.get_data(address - 0x400000, 4)
            constants.append({'address': f'{address:08x}', 'bytes_hex': data.hex(),
                'binary32_value': struct.unpack('<f', data)[0]})
        assert [c['bytes_hex'] for c in constants] == ['cdcccc3a', '8988083b']
        assert pe.get_data(0x14972c,8)==struct.pack('<d',1.34834)
        section=pe.sections[0]; base=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
        code=pe.get_data(section.VirtualAddress,section.SizeOfRawData)
        sites=[base+i for i in range(len(code)-4) if code[i]==0xe8 and base+i+5+int.from_bytes(code[i+1:i+5],'little',signed=True)==0x4dbda0]
        assert sites==[0x4ded7a,0x4dee36]
        result.setdefault('wide_angle_direct_call_candidates',{})[label]={
            'sites':[f'{x:08x}' for x in sites],
            'method':'Every-byte E8/rel32 target scan over first code section; sites corroborated in retained full caller envelopes.',
            'limits':'Excludes indirect calls, jumps, other sections and runtime-generated code.'}
        result['binaries'][label] = {'path': relative, 'sha256': expected,
            'spans': rows, 'scaling_constants': constants,
            'ordinary_projection_override_constant':{'address':'0054972c','bytes_hex':pe.get_data(0x14972c,8).hex(),'binary64_value':1.34834}}
    old, new = blobs['original'], blobs['official_modern']
    assert old[2:4]==new[2:4]
    result['weather_caller_envelopes_identical']=True
    ordinary_changes=[0x4dbde0+i for i,(a,b) in enumerate(zip(old[4],new[4])) if a!=b]
    assert ordinary_changes==[0x4dbe00,0x4dbe25,0x4dbe42]
    for label,body in [('original',old[4]),('official_modern',new[4])]:
        target=0x4dbcc0 if label=='original' else 0x4dbc94
        for call in (0x4dbdff,0x4dbe24,0x4dbe41):
            off=call-0x4dbde0
            assert body[off:off+5]==b'\xe8'+struct.pack('<i',target-call-5)
    result['ordinary_projection_selector']={'entry':'004dbde0','exclusive_end':'004dbee6',
        'changed_operand_addresses':[f'{x:08x}' for x in ordinary_changes],
        'changes':'Three angle-chooser calls retarget original004dbcc0 to Modern004dbc94; all other body bytes identical.',
        'centre_override_in_tail':False,
        'limit':'This body retains rectangle dispatch and scale override; upstream data/chooser effects and active state are not equivalent.'}

    assert [i for i, (a, b) in enumerate(zip(old[0], new[0])) if a != b] == [0x34, 0x35, 0x47, 0x48]
    assert old[0][0x32:0x38] == bytes.fromhex('d80d28be5300')
    assert new[0][0x32:0x38] == bytes.fromhex('d80dd4bd5300')
    for offset in (0x12, 0x27):
        assert old[1][offset:offset+4] == struct.pack('<I', 120)
        assert new[1][offset:offset+4] == struct.pack('<f', 120.0)
    assert [i for i, (a, b) in enumerate(zip(old[1], new[1])) if a != b] == [0x12, 0x14, 0x15, 0x27, 0x29, 0x2a]
    result['limits'] = ['Static bytes only; no rendered output or x87 state equivalence.',
        'Callee interface correspondence relies on the linked projection comparison.']
    (ROOT / 'analysis/evidence/audits/projection-callers-followup.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: identical relocated float constants and integer-120 to binary32-120 caller adjustment')


if __name__ == '__main__':
    main()
