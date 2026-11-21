"""Inspect early DX8 mode filtering and140/150 depth admission; static only."""
import hashlib,json,re,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble
SPECS={
 '1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','dx8.dll','c58ffb6810ca335602766d9179f2fcd8ecf9c9127c98ffa43cd76c0f8fb91e62'),
 '1.4.0':(HISTORY['1.4.0'][0],'drivers/dx8/dx8a.dll','09d3289f5246ec633fdf9f92f9e154a669bb3bf7a33c641c030015f7a0de2e23'),
 '1.5.0':(HISTORY['1.5.0'][0],'drivers/dx8/dx8a.dll','92e352738012fe1098d98e125bdafae089275ceb7d40a9c1aca9c5b31423a1f7')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dx8-mode-admission-history','versions':{}};builders={}
    for version,(ah,member,dh)in SPECS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==dh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        assert any(d.dll.lower()==b'd3d8.dll'and any(i.name==b'Direct3DCreate8'and i.address==0x600180b8 for i in d.imports)for d in pe.DIRECTORY_ENTRY_IMPORT)
        assert get(0x60011244,0x6001124a).hex()=='ff25b8800160'
        assert get(0x60003749,0x60003757).hex()=='6a78e8f4da000085c0a324ed0160'
        assert get(0x6000375f,0x60003764).hex()=='e8ec0d0000'
        assert any(e.name==b'_THRASH_about@0'and e.address==0x1000 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        assert get(0x60001153,0x60001159).hex()=='b8c0280460c3'
        old=version!='1.5.0';threshold=0x600045f3 if old else 0x600045ea
        assert get(threshold,threshold+6).hex()=='81fd80020000'
        assert get(threshold+12,threshold+18).hex()=='81ffe0010000'
        if old:assert get(0x600045de,0x600045e7).hex()=='83f8200f85e8010000'
        else:assert get(0x6000461a,0x60004623).hex()=='83f8100f8502010000'
        depth_index=pe.get_data(0x5447,1)[0];depth_target=struct.unpack('<I',pe.get_data(0x542c+4*depth_index,4))[0]
        token_index=pe.get_data(0x52f7,1)[0];token_target=struct.unpack('<I',pe.get_data(0x52cc+4*token_index,4))[0]
        assert(depth_target,token_target)==(0x600053d8,0x600051f7)
        assert get(depth_target,depth_target+5).hex()=='b810000000'
        assert get(token_target,token_target+6).hex()=='b804000000c3'
        spans=[('about',0x60001000,0x60001159),('factory_publication',0x60003740,0x60003764),
               ('mode_builder',0x60004550,0x600047f2),('depth16_leaf',0x600053d8,0x600053ed),
               ('token4_leaf',0x600051f7,0x600051fd)]
        builders[version]=get(0x60004550,0x600047f2)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,'sha256':dh,
            'format23':{'depth_target':f'{depth_target:08x}','depth':16,'token_target':f'{token_target:08x}','token':4},
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert builders['1.1.0']==builders['1.4.0']
    assert builders['1.4.0'][:0x8e]==builders['1.5.0'][:0x8e]
    assert builders['1.4.0'][0xd3:]==builders['1.5.0'][0xd3:]
    headers=[]
    for name,pin in [('d3d8.h','e93563a03f30a83dae6afe20ad0061558f6a56fe7d101b3d883749b47d1edeef'),
                     ('d3d8types.h','6443383135f69c8199f4c9c1b81717b94ade16ae625f760f198d7c49d864353d')]:
        path=f'analysis/captures/modern-differences/dx8-api-headers/{name}';data=(ROOT/path).read_bytes();assert sha(data)==pin
        text=data.decode()
        if name=='d3d8.h':
            block=text.split('DECLARE_INTERFACE_IID_(IDirect3D8,',1)[1].split('};',1)[0]
            methods=re.findall(r'STDMETHOD(?:_\(\s*[^,]+,\s*|\(\s*)(\w+)\s*\)',block)
            assert methods.index('GetAdapterModeCount')==6 and methods.index('EnumAdapterModes')==7
        else:
            assert re.search(r'D3DFMT_R5G6B5\s*=\s*23\s*,',text)
            block=text.split('typedef struct _D3DDISPLAYMODE {',1)[1].split('}',1)[0]
            assert re.findall(r'(?:UINT|D3DFORMAT)\s+(\w+)\s*;',block)==['Width','Height','RefreshRate','Format']
        headers.append({'path':path,'sha256':pin,'source':'https://raw.githubusercontent.com/mingw-w64/mingw-w64/master/mingw-w64-headers/include/'+name})
    result['header_evidence']=headers
    result['verified']=['Imported Direct3DCreate8 output published6001ed24;mode builder calls count/enum slots18h/1ch with16-byte display-mode output.',
        '110 and140 complete674-byte mode builder identical;both reject unsigned width<640 orheight<480 before record writes.',
        '140->150 removes depth32-only gate,retains nonzero classifier/depth gates,and reserves640x480 depth16 for slot1.',
        'Format23 R5G6B5 maps token4/depth16:old gate rejects it,new selected640x480 path can write slot1 with depth16.',
        'All builder differences are within600045de..60004623;prefix/suffix retained.']
    result['limits']=['Static request/admission evidence,not successful enumeration,mode activation,device/rendering or visible menu output.',
        'EnumAdapterModes return is not checked locally before reading output;valid complete API output is a premise,not a guaranteed success.',
        'Builder starts count2 and clears256 forty-byte records;reserved/unpopulated slots and complete EXE consumers need separate qualification.',
        '110 filter is verified present,not its introduction versus unavailable100;15016-bit admission is not proof every depth is16/32 only.',
        'No original/modern runtime equivalence,full mode ordering or Motor City Online ancestry claim.',
        'No DLL/API/target instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/dx8-mode-admission-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:early DX8 minimum-size filter;140->150 removes32-only gate and admits selected16-bit modes;API outcomes qualified')


if __name__=='__main__':main()
