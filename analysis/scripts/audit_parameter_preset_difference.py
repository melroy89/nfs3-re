"""Hash-pinned preset selection/data comparison; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-parameter-preset-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No preset/game execution.', 'Record field meanings and selector admission remain bounded.']}
    capture = ROOT/'analysis/captures/modern-differences/parameter-preset'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        end = 0x41d863 if label == 'original' else 0x41d6e4
        path = capture/f'{label}-0041d620.asm'
        path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', '--start-address=0x41d620',
            f'--stop-address={end}', relative], cwd=ROOT))
        row = {'path': relative, 'sha256': expected, 'start': '0041d620', 'end': f'{end:08x}',
               'bytes_sha256': hashlib.sha256(pe.get_data(0x1d620, end-0x41d620)).hexdigest(),
               'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'conversion_scale_hex': pe.get_data(0x136ce4, 8).hex()}
        if label == 'official_modern':
            data = pe.get_data(0x1d6e4, 256)
            row['preset_table'] = {'address': '0041d6e4', 'size': 256,
                'sha256': hashlib.sha256(data).hexdigest(),
                'words_by_preset_and_16_byte_block': [[list(struct.unpack_from('<8H', data, i*64+j*16))
                                                      for j in range(4)] for i in range(4)]}
        else:
            row['original_scale_tables_hex'] = pe.get_data(0x1a8b0, 24).hex()
            factors = struct.unpack('<6i', pe.get_data(0x1a8b0,24))
            assert factors == (49152,26869,19660,65536,36044,26214)
            pattern = bytes.fromhex('f7eac1e210c1e81011d0')
            body = pe.get_data(0x1d620,end-0x41d620)
            sites = [0x41d620+i for i in range(len(body)) if body.startswith(pattern,i)]
            assert sites == [0x41d66b,0x41d688,0x41d6a5,0x41d6bf,0x41d6d7,0x41d6ef,
                             0x41d722,0x41d73f,0x41d75c,0x41d776,0x41d78e,0x41d7a6]
            constants = [(0x41d662,440),(0x41d683,60),(0x41d6a0,92),
                         (0x41d6b6,500),(0x41d6d2,110),(0x41d6ea,150),
                         (0x41d719,440),(0x41d73a,60),(0x41d757,92),
                         (0x41d76d,500),(0x41d789,110),(0x41d7a1,150)]
            for va,n in constants:
                assert pe.get_data(va-0x400000,5) == b'\xb8'+struct.pack('<I',n<<16)
            row['original_exact_integer_arithmetic'] = {
                'multiply_sequence_sites': [f'{x:08x}' for x in sites],
                'factors_nonzero_006fd4c8': list(factors[:3]),
                'factors_zero_006fd4c8': list(factors[3:]),
                'formula': 'wrap32(N * signed_factor); N=440,60,92 for mode1, otherwise500,110,150',
                'derivation': 'All constants=N<<16; signed64 product low16=0, so SHR carry bit15=0; joined high/low halves equal low32(product arithmetic-shift16).',
                'scope': 'Mathematical consequence of asserted instructions; not original-instruction execution.'}

        assert struct.unpack('<5I',pe.get_data(0x156460,20))==(0x537e64,0x5561be,0,0,0x6fd4c8)
        assert pe.get_string_at_rva(0x137e64)==b'night'
        assert struct.unpack('<3H',pe.get_data(0x1561be,6))==(229,228,0)
        assert pe.get_string_at_rva(0x137d10)==b'mainsplt'
        assert pe.get_data(0x555ef4-0x400000,4)==struct.pack('<I',0x45d360)
        assert pe.get_data(0x45d36a-0x400000,10)==bytes.fromhex('c705b0d36f0001000000')
        descriptor=struct.unpack('<5I',pe.get_data(0x156730,20))
        assert descriptor==(0x537fc8,0x556252,0,0,0x6fbc28)
        assert pe.get_string_at_rva(0x137fc8)==b'viewlevel'
        assert struct.unpack('<5H',pe.get_data(0x156252,10))==(184,183,182,181,0)
        row['viewlevel_descriptor']={'address':'00556730','words':[f'{x:08x}' for x in descriptor],
                                     'name':'viewlevel','choice_ids':[184,183,182,181]}
        row['caller_and_selector_witnesses'] = []
        for a,b in [(0x41d610,0x41d61a),(0x41d870,0x41d89d),
                    (0x41aaf0,0x41ab02),(0x41d9fa,0x41da0b),
                    (0x41deb0,0x41def9),(0x41df10,0x41e069),
                    (0x41d9a3,0x41da06),(0x41defc,0x41df0c),
                    (0x41d310,0x41d349),(0x41ae90,0x41b2f4),
                    (0x41b300,0x41b63c),(0x45d360,0x45d374),
                    (0x555ee8,0x555ef8)]:
            value=pe.get_data(a-0x400000,b-a)
            row['caller_and_selector_witnesses'].append({'start':f'{a:08x}',
                'exclusive_end':f'{b:08x}','bytes':value.hex(),
                'sha256':hashlib.sha256(value).hexdigest()})
        for call in (0x41aaf6,0x41d894,0x41da01):
            assert pe.get_data(call-0x400000,5)==b'\xe8'+struct.pack('<i',0x41d620-call-5)
        for start,values in [(0x41df6d,(500,500,110,150)),
                             (0x41df99,(400,440,60,92)),(0x41dfe0,(150,100,40,80))]:
            for i,(offset,n) in enumerate(zip((0x24,0x28,0x38,0x3c),values)):
                assert pe.get_data(start+i*7-0x400000,7)==bytes((0xc7,0x40,offset))+struct.pack('<I',n<<16)
        assert struct.unpack('<4I',pe.get_data(0x41defc-0x400000,16)) == (0x41df6d,0x41df99,0x41df99,0x41dfe0)
        assert pe.get_data(0x41af7a-0x400000,25)==bytes.fromhex(
            'a130d85d00d94108d85830dfe09e76098345f80ee9f9020000')
        assert pe.get_data(0x41b3bf-0x400000,24)==bytes.fromhex(
            'a130d85d00d94608d85830dfe09e760883c10ee90e020000')
        assert pe.get_data(0x41debb-0x400000,14)==bytes.fromhex('31c98915d8d05d00890ddcd05d00')
        assert pe.get_data(0x41e057-0x400000,14)==bytes.fromhex('a1dcd05d008d50018915dcd05d00')
        assert pe.get_data(0x41d610-0x400000,10)==bytes.fromhex('5589e5a328bc6f005dc3')
        assert pe.get_data(0x41d875-0x400000,31)==bytes.fromhex(
            '8b1528bc6f0042b904000000891528bc6f0089d0c1fa1ff7f9891528bc6f00')
        result['binaries'][label] = row
    assert result['binaries']['original']['conversion_scale_hex'] == result['binaries']['official_modern']['conversion_scale_hex']
    assert result['binaries']['original']['caller_and_selector_witnesses'] == result['binaries']['official_modern']['caller_and_selector_witnesses']
    old_factors = result['binaries']['original']['original_exact_integer_arithmetic']
    table = result['binaries']['official_modern']['preset_table']['words_by_preset_and_16_byte_block']
    table_bytes = b''.join(struct.pack('<8H',*block) for preset in table for block in preset)
    comparisons=[]
    for selector in range(4):
        for alternate in (False,True):
            factors = old_factors['factors_nonzero_006fd4c8' if alternate else 'factors_zero_006fd4c8']
            factor=factors[max(0,selector-1)]
            for mode1 in (False,True):
                constants=(440,60,92) if mode1 else (500,110,150)
                known=[(n*factor)&0xffffffff for n in constants]
                if selector==0: known=[known[0]]*3
                for aux in range(4):
                    start=selector*64+(32 if alternate else 0)+(16 if mode1 else 0)
                    advance=0 if mode1 else min(aux,max(0,3-selector))*64
                    sources=[start,start+8+advance]
                    new=[list(struct.unpack_from('<4H',table_bytes,x)) for x in sources]
                    comparisons.append({'selector':selector,'nonzero_006fd4c8':alternate,
                        'mode_equals1':mode1,'auxiliary_006fd1d8':aux,
                        'original_known_fields_28_38_3c': [known,known if mode1 else None],
                        'modern_source_offsets':sources,
                        'modern_words_24_28_38_3c':new,
                        'known_field_differences':sum(a != (b<<16) for i,record in enumerate(new)
                            if i==0 or mode1 for a,b in zip(known,record[1:]))})
    for case in comparisons:
        mode1=case['mode_equals1']
        old24=400 if mode1 else 500
        first=[old24<<16]+case['original_known_fields_28_38_3c'][0]
        second=([400<<16]+case['original_known_fields_28_38_3c'][1]) if mode1 else [n<<16 for n in (150,100,40,80)]
        case['original_after_inspected_initialization_24_28_38_3c']=[first,second]
        case['initialization_qualified_field_differences']=sum(a!=(b<<16) for x,y in zip([first,second],case['modern_words_24_28_38_3c']) for a,b in zip(x,y))
    result['derived_integer_comparisons'] = {
        'kind':'mathematical evaluation of asserted static formulas and table; no target execution',
        'scope':'selectors0..3, both flag/mode branches, auxiliary representatives0..3; original untouched fields are null, not zero',
        'initialization_comparison_precondition':'reset establishes count0; mode remains stable; two shown insertions occupy records0/1; no intervening alias mutation of compared fields',
        'cases':comparisons,
        'cases_with_known_field_differences':sum(x['known_field_differences']>0 for x in comparisons)}

    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_sha=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    member='fedata/text/text.eng'
    data=subprocess.check_output(['7z','x','-so',str(archive),member])
    extent=struct.unpack_from('<I',data)[0]; assert extent%4==0 and extent<=len(data)
    labels=[]
    for ident,expected in [(184,b'Full'),(183,b'Far'),(182,b'Medium'),(181,b'Close'),(229,b'Off'),(228,b'On')]:
        assert ident*4<extent
        offset=struct.unpack_from('<I',data,ident*4)[0];assert extent<=offset<len(data)
        value=data[offset:data.index(b'\0',offset)];assert value==expected
        labels.append({'id':ident,'offset':offset,'text':value.decode()})
    assets=[]
    for name in ['fedata/menus/graphics.mnu','fedata/menus/psgraph.mnu','fedata/menus/setup.mnu']:
        raw=subprocess.check_output(['7z','x','-so',str(archive),name])
        fields=[{'line':i,'text':line} for i,line in enumerate(raw.decode('latin1').splitlines(),1)
                if line in ('listname=viewlevel','nextmenu=mainsplt','codelink=SETUP_TWOPLAYERBUTTON')]
        assert fields
        assets.append({'member':name,'sha256':hashlib.sha256(raw).hexdigest(),'viewlevel_fields':fields})
    result['view_distance_binding']={'archive_sha256':archive_sha,
        'english_member':member,'english_sha256':hashlib.sha256(data).hexdigest(),
        'labels':labels,'menu_assets':assets,
        'night_binding':{'descriptor':'00556460','global':'006fd4c8','name':'night','choice_ids':[229,228]},
        'split_binding':{'menu':'mainsplt','row':'00555ee8','callback_slot':'00555ef4','callback':'0045d360','store':'0045d36a','global':'006fd3b0','value':1},
        'limits':['Official asset bindings and identical executable descriptors; runtime menu/language selection not observed.']}
    assert len(comparisons)==64
    assert result['derived_integer_comparisons']['cases_with_known_field_differences']==48
    (ROOT/'analysis/evidence/audits/original-modern-parameter-preset.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete preset bodies, table bytes and retained conversion scale')


if __name__ == '__main__':
    main()
