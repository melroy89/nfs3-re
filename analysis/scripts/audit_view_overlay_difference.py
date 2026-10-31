"""Compare complete viewport overlay envelopes and new fixed-colour helper."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-view-overlay-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/view-overlay'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x489240, 0x48962d),(0x488c6e,0x488d41),(0x488b8c,0x488c33),(0x4d4ae0,0x4d5030)]
        if label == 'official_modern': spans += [(0x4900c8, 0x490134), (0x4900b0, 0x4900c5), (0x4f9390, 0x4f9399)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'constants_0053b76c_to_0053b78c_hex': pe.get_data(0x13b76c, 32).hex()}
    data = [p.get_data(0x89240, 0x3ed) for p in images]
    builders=[p.get_data(0xd4ae0,0x550) for p in images]
    assert builders[0]==builders[1]
    out['retained_dashboard_tile_builder']={'span':'004d4ae0..004d5030','bytes':1360,
        'bytes_identical':True,'sha256':hashlib.sha256(builders[0]).hexdigest(),
        'boundary':'Complete retained builder includes RET8 at004d502d; equality is not transitive equivalence of conversion/upload helpers.',
        'limits':'No new local tile-padding algorithm in this envelope; source assets, conversion helpers, descriptor data and caller arguments can still differ.'}
    tile_constants={}
    for address,expected in ((0x53b76c,256.0),(0x53b774,1/640),(0x53b77c,1/480)):
        pairs=[p.get_data(address-0x400000,8) for p in images]
        assert pairs[0]==pairs[1] and struct.unpack('<d',pairs[0])[0]==expected
        tile_constants[f'{address:08x}']={'binary64':expected,'hex':pairs[0].hex()}
    out['primary_tile_coordinates']={'retained_constants':tile_constants,
        'normal_math':'stepX=256*extentW/640; stepY=256*extentH/480, with actual x87 order/binary32 spills retained.',
        'bounds':'Right/bottom candidates clamped against origin+extent before vertex submission004894af.',
        'index':'Incremented once per innerY submission; same44-byte descriptor table, no local per-submit capacity comparison established.',
        'limits':'Coordinate-space construction, not physical rasterized pixel coverage; malformed extents, nonfinite values, origin rounding and callback contracts unqualified.'}
    gear_setup=[p.get_data(0x88c6e,0xd3) for p in images]
    dash_setup=[p.get_data(0x88b8c,0xa7) for p in images]
    assert dash_setup[0]==dash_setup[1]
    for p in images:
        assert p.get_string_at_rva(0x13b6ec)==b'dash.qfs'
        assert p.get_string_at_rva(0x13b6fc)==b'0001'
        assert p.get_string_at_rva(0x13b704)==b'0000'
    out['primary_tile_resource_binding']={'paired_setup':'00488b8c..00488c33','bytes_identical':True,
        'sha256':hashlib.sha256(dash_setup[0]).hexdigest(),
        'resource':'dash.qfs at0053b6ec; shapes0000/0001 passed to004d4ae0.',
        'destinations':'ECX00791d70; return published to primary gate007922fc.',
        'consumer':'00489447..0048948f reads indexed record fields at00791d70+4/+8/.../+24.',
        'limits':'Dashboard/cabin association inferred from named asset and record linkage; actual image contents and loader/renderer success not validated.'}
    assert gear_setup[0]==gear_setup[1]
    bindings=[]
    for index,name in enumerate(['geaR','geaN','gea1','gea2','gea3','gea4','gea5','gea6']):
        destination=0x791c10+44*index;name_address=0x53b70c+8*index
        for p,body in zip(images,gear_setup):
            assert p.get_string_at_rva(name_address-0x400000).decode()==name
            assert b'\xb9'+struct.pack('<I',destination) in body
            assert b'\xba'+struct.pack('<I',name_address) in body
        bindings.append({'index':index,'destination':f'{destination:08x}','shape_name':name,'name_address':f'{name_address:08x}'})
    out['optional_overlay_shape_bindings']={'paired_setup':'00488c6e..00488d41','bytes_identical':True,
        'sha256':hashlib.sha256(gear_setup[0]).hexdigest(),'bindings':bindings,
        'consumer':'0048954f/004895a2 index the same44-byte records using vehicle byte+50b.',
        'limits':'Gear association inferred from shape labels and R/N/1..6 ordering; actual image identity and accepted vehicle index domain not validated.'}
    changes = [0x489240+i for i,(a,b) in enumerate(zip(*data)) if a != b]
    assert len(changes) == 143
    out['envelope_changed_byte_addresses'] = [f'{a:08x}' for a in changes]
    out['modern_function_range_changed_bytes'] = sum(not 0x489614 <= a < 0x489619 for a in changes)
    assert out['modern_function_range_changed_bytes'] == 138
    assert images[1].get_data(0x89614, 5) == bytes([0x90])*5
    assert images[0].get_data(0x89613, 6) == bytes.fromhex('ff154cf99e00')
    out['retained_ranges'] = []
    for start, end in ((0x489240,0x48928c),(0x4892dd,0x4894f8),(0x489510,0x4895a2),(0x489619,0x48962d)):
        pair = [p.get_data(start-0x400000,end-start) for p in images]; assert pair[0] == pair[1]
        out['retained_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pair[0]).hexdigest()})
    site = 0x48960d; call = images[1].get_data(site-0x400000,5)
    assert call[0] == 0xe8 and site+5+int.from_bytes(call[1:],'little',signed=True) == 0x4900c8
    out['limits'] = ['No rendering, target execution or visual acceptance.', 'Complete address envelope includes Modern padding and original call bytes; Modern function ranges alone exclude part of that original instruction.', 'Rectangle/global producers, callback slot identity and complete asset/descriptor bounds remain separate.']
    (ROOT/'analysis/evidence/audits/original-modern-view-overlay.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 143 envelope deltas / 138 Modern-range deltas; retained blocks and new quad helper')


if __name__ == '__main__':
    main()
