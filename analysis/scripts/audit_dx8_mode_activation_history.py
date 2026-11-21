"""Compare DX8 activation contracts beyond enumerated mode admission; static only."""
import hashlib,json,re,subprocess,struct
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx8_mode_admission_history import SPECS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior=ROOT/'analysis/evidence/audits/dx8-mode-admission-history.json'
    result={'kind':'static-dx8-mode-activation-history','prior_admission_evidence_sha256':sha(prior.read_bytes()),'versions':{}};paired=[]
    spans=[('mode_export',0x600038b0,0x600039fe),('activation_worker',0x60003b80,0x60004001),
           ('windowed_adjustment',0x60004010,0x6000413b),('format_preference',0x60004140,0x6000420b),('depth_stencil_search',0x600043e0,0x60004521)]
    for version in ('1.4.0','1.5.0'):
        ah,member,dh=SPECS[version];rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member]);assert sha(raw)==dh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        assert any(e.name==b'_THRASH_setvideomode@12'and e.address==0x38b0 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        assert get(0x600038be,0x600038c6).hex()=='3b3dfc2804607d10'
        assert get(0x600038cf,0x600038db).hex()=='f644c110017505bf01000000'
        assert get(0x600039a7,0x600039ac).hex()=='e8d4010000'
        assert get(0x60003cc5,0x60003cd1).hex()=='c705a80f026017000000eb0f'
        assert get(0x60003cd6,0x60003ce0).hex()=='c705a80f026016000000'
        assert get(0x60003d4c,0x60003d4f).hex()=='ff513c'
        assert get(0x60003d5e,0x60003d61).hex()=='ff5138'
        imports={i.address:(d.dll.decode(),i.name.decode())for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x600180b0][1]=='PostMessageA'
        assert imports[0x6001808c][1]=='GetDC'and imports[0x60018000][1]=='GetDeviceCaps'
        assert get(0x6000403b,0x60004040).hex()=='6a0856ffd7'
        assert get(0x60004040,0x60004047).hex()=='6a0a568be8ffd7'
        assert get(0x600040c8,0x600040cc).hex()=='85c07526'
        assert get(0x600040e4,0x600040e8).hex()=='85c0740a'
        assert get(0x60004144,0x60004152).hex()=='b816000000558944241489442408'
        assert get(0x60004159,0x60004168).hex()=='b9170000005657894c2418894c2414'
        assert get(0x60004524,0x6000454c).hex()=='0a450060dc440060e9440060dc4400600a450060dc4400600a450060dc4400600a450060d2440060'
        blobs=[get(a,b)for _,a,b in spans];paired.append(blobs)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,'sha256':dh,
            'bodies':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','bytes':b-a,'sha256':sha(get(a,b))}for n,a,b in spans],
            'message_import':{'iat':'600180b0','dll':imports[0x600180b0][0],'name':'PostMessageA'}}
    assert paired[0]==paired[1]
    jump_targets=struct.unpack('<10I',get(0x60004524,0x6000454c))
    assert jump_targets==(0x6000450a,0x600044dc,0x600044e9,0x600044dc,0x6000450a,0x600044dc,0x6000450a,0x600044dc,0x6000450a,0x600044d2)
    result['shared_body_witnesses']=[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
        'hex':blob.hex(),'disassembly':disassemble(blob,a)}for(n,a,b),blob in zip(spans,paired[0])]
    headers=[]
    for name,pin in [('d3d8.h','e93563a03f30a83dae6afe20ad0061558f6a56fe7d101b3d883749b47d1edeef'),
                     ('d3d8types.h','6443383135f69c8199f4c9c1b81717b94ade16ae625f760f198d7c49d864353d'),
                     ('wingdi.h','db2faa700bab930bab000bf1ed6282abbacda608c8c9140f60cacca0ffe6aaac')]:
        path=f'analysis/captures/modern-differences/dx8-api-headers/{name}';raw=(ROOT/path).read_bytes();assert sha(raw)==pin;text=raw.decode()
        if name=='d3d8.h':
            for interface,method,index in [('IDirect3D8','CheckDeviceType',9),('IDirect3D8','CheckDeviceFormat',10),('IDirect3D8','CheckDepthStencilMatch',12),('IDirect3D8','CreateDevice',15),('IDirect3DDevice8','Reset',14)]:
                block=text.split(f'DECLARE_INTERFACE_IID_({interface},',1)[1].split('};',1)[0]
                methods=re.findall(r'STDMETHOD(?:_\(\s*[^,]+,\s*|\(\s*)(\w+)\s*\)',block);assert methods.index(method)==index
        elif name=='d3d8types.h':
            assert re.search(r'D3DFMT_R5G6B5\s*=\s*23\s*,',text)and re.search(r'D3DFMT_X8R8G8B8\s*=\s*22\s*,',text)
            for fmt,value in [('D32',71),('D15S1',73),('D24S8',75),('D24X8',77),('D24X4S4',79),('D16',80)]:
                assert re.search(r'D3DFMT_'+fmt+r'\s*=\s*'+str(value)+r'\s*,',text)
            block=text.split('typedef struct _D3DPRESENT_PARAMETERS_ {',1)[1].split('}',1)[0]
            fields=re.findall(r'^\s*\w+\s+(\w+)\s*;',block,re.M)
            assert fields[:3]==['BackBufferWidth','BackBufferHeight','BackBufferFormat']and len(fields)==13
        else:
            for constant,value in [('HORZRES',8),('VERTRES',10),('BITSPIXEL',12)]:
                assert re.search(r'#define\s+'+constant+r'\s+'+str(value)+r'\b',text)
        headers.append({'path':path,'sha256':pin,'source':'https://raw.githubusercontent.com/mingw-w64/mingw-w64/master/mingw-w64-headers/include/'+name})
    result['header_evidence']=headers
    result['adjustment_contract']={'windowed':{'entry':'60004010','gdi_indices':[8,10,12],
        'required_reported_depths':[16,32],'minimum_reported_width':640,'dimensions':'Signed clamp each requested dimension down to the corresponding GDI cap.',
        'depth':'On admitted return writes GDI-reported16/32,not necessarily incoming selected depth.',
        'quirk':'Nonzero CheckDeviceFormat result skips CheckDeviceType;zero first result requires zero second result before continuing to43e0.'},
        'other_path':{'entry':'60004140','requested32_candidate_formats':[22,23],'other_requested_depth_candidate_formats':[23,22],
        'admission':'Each candidate requires zero CheckDeviceType and CheckDeviceFormat results,then nonzero43e0 result.',
        'writeback':'Chosen23 writes16,chosen22 writes32;no successful candidate returns0.'},
        'depth_stencil_search':{'entry':'600043e0','selector_global':'6001eed0','selector16_candidates':[80,71,75,77,79,73],'selector32_candidates':[71,75,77,79,80,73],'other_selector':'Returns1 without writing output locally.','candidate_admission':'Zero CheckDeviceFormat and CheckDepthStencilMatch results.','exhaustion':'Writes output0 and returns0.','selected':'Writes chosen format;71/75/77/79 write selector32;73 writes selector16 and global6002022c=1;80 writes selector16.','jump_table':{'start':'60004524','targets':[f'{v:08x}'for v in jump_targets]}},
        'shared_unresolved':'Selector/flag initialization and later mutations,complete caller/callback/device lifetime remain separately unverified.'}
    result['verified']=['Complete334-byte mode export and1153-byte worker are byte-identical140/150.',
        'Export checks signed index bounds and active flag,otherwise substitutes index1 without rechecking that row there.',
        'Worker reads admitted row width/height/depth;inactive row fallback is640x480x16 before adjustment helpers.',
        'After helper adjustment,depth16 maps present-parameter format23 R5G6B5;depth32 maps22 X8R8G8B8.',
        'Parameters60020fa0 reach selected CreateDevice slot3ch or Reset slot38h,with local result handling and retries.',
        '16-bit activation request branch predates150 admission expansion;32-only old catalog is not an all-path32-only activation guarantee.',
        'Both adjustment helpers also match140/150;windowed admitted output adopts GDI depth while other path uses two-candidate format preference/fallback.']
    result['limits']=['Selected4010/4140 adjustment and43e0 depth/stencil search established;selector/flag lifetime,actual API outcomes and full device lifetime unresolved.',
        'Export can post message464h and wait on cross-thread path;no actual delivery/synchronization/device acceptance observed.',
        'No all-input index/table safety,all reset/fallback errors,actual display depth or rendered success established.',
        'No DLL/API/target instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/dx8-mode-activation-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:DX8 mode export/worker retained140/150;16/32-bit parameter branches pre-exist admission expansion,device outcomes untested')


if __name__=='__main__':main()
