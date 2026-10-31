"""Retain corresponding graphics menu init/transition bodies; static only."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-graphics-menu-transition-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/graphics-menu-transition'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x448440, 0x4484d7), (0x4484e0, 0x448561)] if label == 'original' else [(0x448440, 0x4484ba), (0x4484bc, 0x448553), (0x43778c, 0x4377c1), (0x448348, 0x448368), (0x44837c, 0x448392), (0x448394, 0x4483fd), (0x448400, 0x448425), (0x4377c4, 0x437801), (0x437801, 0x43781d), (0x448639, 0x448647), (0x44d2a0, 0x44d2c5)]
        rows = []
        for start, end in spans:
            data = pe.get_data(start-0x400000, end-start)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        table = pe.get_data(0x156068, 24)
        cancel = pe.get_data(0x138d84, 40).split(b'\0')[0].decode()
        assert cancel == 'CANCEL_GRAPHICS_OPTIONS'
        expected_callback = 0x4484e0 if label == 'original' else 0x4484bc
        assert int.from_bytes(table[16:20], 'little') == expected_callback
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'graphics_registration_row_00556068_hex': table.hex(), 'cancel_token_00538d84': cancel, 'string_at_00538d7c': pe.get_data(0x138d7c, 32).split(b'\0')[0].decode()}
        if label == 'official_modern':
            out['binaries'][label]['fog_control_tokens'] = {f'{a:08x}': pe.get_data(a-0x400000, 32).split(b'\0')[0].decode() for a in (0x538a20, 0x538a2c)}
            sites = (0x448458, 0x448642, 0x44d2c0)
            for site in sites:
                data = pe.get_data(site-0x400000, 5)
                assert data[0] == 0xe8 and site+5+int.from_bytes(data[1:], 'little', signed=True) == 0x4377c4
            out['binaries'][label]['inspected_fog_gate_direct_calls'] = [f'{site:08x}' for site in sites]
    intensity = {}
    for label,(relative,expected,_) in SPECS.items():
        pe=pefile.PE(str(ROOT/relative))
        body=pe.get_data(0x48728,0x3d)
        assert pe.get_string_at_rva(0x138e3c)==b'SFX_INTENSITY'
        assert pe.get_data(0x48738,7)==bytes.fromhex('f605583a7a00')+bytes([0x40 if label=='original' else 0x50])
        intensity[label]={'start':'00448728','end_exclusive':'00448765',
            'hex':body.hex(),'sha256':hashlib.sha256(body).hexdigest(),
            'admission_mask':0x40 if label=='original' else 0x50}
    a,b=[bytes.fromhex(intensity[label]['hex']) for label in SPECS]
    assert [i for i,(x,y) in enumerate(zip(a,b)) if x!=y]==[0x16]
    out['sfx_intensity_admission']={'baselines':intensity,'token':'SFX_INTENSITY',
        'token_va':'00538e3c','state_byte':'007a3a58',
        'limit':'Local control setup admission only; renderer bit identities, final enabled state, input and visual effect untested.'}
    sfx_dependencies=[]
    for start,end,role in [(0x46cac0,0x46cac8,'Store EDX callback at item+78h'),
                           (0x448570,0x448598,'Admitted slider callback stores getter result to006fbc38'),
                           (0x46c9b0,0x46c9f3,'Slider getter dispatch and binary32 spill/reload')]:
        paired={label:pefile.PE(str(ROOT/spec[0])).get_data(start-0x400000,end-start)
                for label,spec in SPECS.items()}
        assert paired['original']==paired['official_modern']
        data=paired['original']
        sfx_dependencies.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
            'role':role,'hex':data.hex(),'sha256':hashlib.sha256(data).hexdigest()})
    out['sfx_retained_dependencies']={'bodies':sfx_dependencies,
        'limit':'Callback registration and writeback verified; getter leaf semantics, callback invocation/lifetime, final enabled state and rendering remain unqualified.'}
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    def parse(data):
        sections=[];current=None
        for line in data.decode('latin1').splitlines():
            if line.startswith('['):
                current={'section':line.strip('[]'),'fields':{}};sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);current['fields'][key]=value
        return sections
    assets={}
    for label,relative in [
        ('official_modern','analysis/captures/modern-differences/upstream/package/fedata/menus/advgrph.mnu'),
        ('uppercase_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/ADVGRPH.MNU')]:
        data=(ROOT/relative).read_bytes()
        if label=='official_modern':
            assert data==subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/advgrph.mnu'])
        selected=[s for s in parse(data) if s['fields'].get('listname')=='fog']
        assert len(selected)==(2 if label=='official_modern' else 0)
        assets[label]={'path':relative,'sha256':hashlib.sha256(data).hexdigest(),
            'fog_items':selected,'provenance':'Pinned official archive member' if label=='official_modern' else 'Local backup; not authenticated as retail or paired with supplied original EXE'}
    graphics=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/graphics.mnu'])
    routes=[s for s in parse(graphics) if s['fields'].get('nextmenu')=='advgrph']
    assert len(routes)==1
    assets['official_graphics_route']={'member':'fedata/menus/graphics.mnu',
        'sha256':hashlib.sha256(graphics).hexdigest(),'entry':routes[0]}
    pe=pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    descriptor=struct.unpack('<5I',pe.get_data(0x556924-0x400000,20))
    assert descriptor==(0x53a87c,0x5561be,0,0,0x6fd1d4)
    assert pe.get_data(0x53a87c-0x400000,4)==b'fog\0'
    words=struct.unpack('<3H',pe.get_data(0x5561be-0x400000,6));assert words==(229,228,0)
    out['fog_menu_assets']=assets
    out['modern_fog_list_binding']={'descriptor':'00556924','words':[f'{x:08x}' for x in descriptor],
        'name':'fog','selection_cell':'006fd1d4','list_words':list(words)}
    out['limits'] = ['No display or callback execution.', 'Mode-list nonempty and valid descriptor/item/backup prerequisites are not proved.', 'Changed field meanings and helper dependencies prevent inferring whole-menu equivalence.']
    (ROOT / 'analysis/evidence/audits/original-modern-graphics-menu-transition.json').write_text(json.dumps(out, indent=2) + '\n')
    print('PASS: pinned graphics registration, counterpart bodies and Modern helper witnesses')


if __name__ == '__main__':
    main()
