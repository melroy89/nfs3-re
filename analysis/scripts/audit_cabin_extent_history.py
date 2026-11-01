"""Static early fixed versus later resolution-dependent overlay correction."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    history=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']
    specs={
        '1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac',
                 '59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72',0x4be874,0x4be898),
        '1.5.3':('0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64',
                 history['1.5.3']['executable_sha256'],0x4be850,0x4be874),
        '1.6.0':('9e1bb8f034026f6f2641417d59f46203f787771394767ca4c6ae4474e4324bb8',
                 '9fd80c4cdc9827f190698f28aa93f1182218d7c557898fb2653abfc4148c7a72',0x4be85c,0x4be89c)}
    result={'kind':'static-cabin-overlay-extent-history','versions':{}}
    helpers={};setters={}
    for version,(archive_hash,exe_hash,start,setter) in specs.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/relative;assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_hash
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        end=start+(63 if version=='1.6.0' else 36)
        body=get(start,end);helpers[version]=body
        store=get(setter,setter+12);setters[version]=store
        assert store.hex()=='8907895f04894f0889570cc3'
        prefix=bytes.fromhex('a188db7c008b1d8cdb7c008b0d90db7c008b1594db7c00')
        if version!='1.6.0':
            assert body[:23]==prefix and body[23:30].hex()=='4142bf50277a00'
            assert body[-1]==0xc3
        else:
            assert body[:1]==b'\x60' and body[1:24]==prefix
            assert body[24:51].hex()=='89ce29c631ff81ee800200007e0347ebf501f96bff03c1ef0201fa'
            assert body[-2:]==b'\x61\xc3'
        call=body.find(b'\xe8',len(body)-8)
        assert call>=0 and start+call+5+int.from_bytes(body[call+1:call+5],'little',signed=True)==setter
        row={'archive':relative,'archive_sha256':archive_hash,'member':'nfs3.exe','sha256':exe_hash,'captures':[]}
        for a,b in [(start,end),(setter,setter+12)]:
            data=get(a,b);row['captures'].append({'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                'sha256':sha(data),'hex':data.hex(),'disassembly':disassemble(data,a)})
        calls=[]
        for section in pe.sections:
            if not section.Characteristics&0x20000000:continue
            code=section.get_data();base=0x400000+section.VirtualAddress
            for i in range(len(code)-4):
                if code[i]==0xe8 and base+i+5+struct.unpack_from('<i',code,i+1)[0]==start:
                    calls.append(f'{base+i:08x}')
        row['direct_e8_candidates']=calls
        result['versions'][version]=row
    assert helpers['1.1.0']==helpers['1.5.3']
    assert len(set(setters.values()))==1
    rel,digest,_=SPECS['official_modern'];raw=(ROOT/rel).read_bytes();assert sha(raw)==digest
    final=pefile.PE(data=raw)
    assert final.get_data(0xbe85c,63)==helpers['1.6.0']
    result['final_retention']={'path':rel,'sha256':digest,'helper_004be85c_identical_to_160':True}
    result['ordinary_derived_examples']=[{'X':0,'W':w,'early_delta_width':1,'early_delta_height':1,
        '160_delta_width':(w-1)//640,'160_delta_height':3*((w-1)//640)//4} for w in [640,1280,1920,2560,3840]]
    result['limits']=['No game, render API or extracted instruction execution; examples are arithmetic derivations.',
        'Existing paired dash.qfs loader/draw evidence supplies cabin association; historical assets/complete consumers not revalidated here.',
        'Direct E8 encoding census is a candidate inventory, not complete decoded caller or reachability proof.',
        'No1.0.0 artifact examined;1.1.0 proves early presence, not introduction date.',
        'Later formula assumes ordinary positive nonoverflowing W-X; actual code uses wrapping32-bit arithmetic and signed branch flags.',
        'Extent units do not establish physical pixel coverage, texture seams or provider success.',
        'Fixed helper exposes working registers/flags;1.6.0 PUSHAD/POPAD preserves general registers but not flags.']
    (ROOT/'analysis/evidence/audits/cabin-extent-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: early/153 complete fixed helpers identical;160 resolution-dependent helper retained in final')


if __name__=='__main__':main()
