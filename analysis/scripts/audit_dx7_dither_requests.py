"""Retain DX7 dithering requests and selected SDK/device correspondence."""
import hashlib,json,re,struct,subprocess,uuid
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    archive='analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.5.0.7z'
    ah='de6cbbbce4b77765f96472aaf8c12a4e245e2abceaf26dd9b84215442b1f4a0f'
    assert sha((ROOT/archive).read_bytes())==ah
    raw=subprocess.check_output(['7z','x','-so',str(ROOT/archive),'drivers/dx7/dx7a.dll']);pe=pefile.PE(data=raw)
    intro=json.loads((ROOT/'analysis/evidence/audits/dx7-package-introduction.json').read_text())
    assert sha(raw)==next(r['sha256']for r in intro['versions']['1.5.0']['members']if r['member'].endswith('.dll'))
    get=lambda a,b:pe.get_data(a-0x60000000,b-a)
    assert pe.get_data(0x15bf8,16)==uuid.UUID('f5049e77-4861-11d2-a407-00a0c90629a8').bytes_le
    assert pe.get_data(0x96ec,13).hex()=='68988d056068f85b016050ff11'
    assert pe.get_data(0x9f97,6).hex()=='689c8d056052'
    assert pe.get_data(0x9fa7,9).hex()=='68e85b016050ff5110'
    assert get(0x6000a6f8,0x6000a707).hex()=='a19c8d05608b106a006a1a50ff5250'
    index=pe.get_data(0x6af1,1)[0];target=struct.unpack('<I',pe.get_data(0x6a34+index*4,4))[0]
    assert(index,target)==(5,0x60004b6e)
    headers=[]
    for name,pin in [('d3dtypes.h','a111ecba9c6d90d3387a6442f7a8d482850b94cef97c8b43743ca3bbeffb6ba2'),
                     ('d3d.h','0912630face1250f3afbbb340c5ff1cda16d23d9a00432ae3358e8595d67809a')]:
        path=f'analysis/captures/modern-differences/dx7-api-headers/{name}';data=(ROOT/path).read_bytes();assert sha(data)==pin
        text=data.decode('utf-8-sig')
        if name=='d3dtypes.h':assert re.search(r'D3DRENDERSTATE_DITHERENABLE\s*=\s*26',text)
        else:
            block=text.split('DECLARE_INTERFACE_(IDirect3DDevice7, IUnknown)',1)[1].split('};',1)[0]
            methods=re.findall(r'STDMETHOD(?:_\([^,]+,\s*|\()([A-Za-z0-9_]+)',block)
            assert methods.index('SetRenderState')==20
        headers.append({'path':path,'sha256':pin,'source':'https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/'+name})
    prefix=disassemble(get(0x6000a490,0x6000a707),0x6000a490)
    branches=[]
    for line in prefix:
        match=re.search(r'^([0-9a-f]+):.*\t(j[a-z]+)\s+0x([0-9a-f]+)$',line)
        if match:
            address,target_address=int(match[1],16),int(match[3],16)
            assert address<target_address<=0x6000a6f8
            branches.append({'address':match[1],'mnemonic':match[2],'target':match[3]})
        assert '\tret' not in line and '\tjmp    DWORD' not in line
    assert len(branches)==7
    assert get(0x60009ec0,0x60009ec5).hex()=='e8cb050000'
    assert get(0x6000a49e,0x6000a4a1).hex()=='ff5114'
    assert get(0x6000aa2a,0x6000aa2d).hex()=='ff5118'
    spans=[('initializer_prefix_to_disable',0x6000a490,0x6000a707),
           ('direct_setup_call',0x60009ec0,0x60009ec5),
           ('initializer_tail',0x6000aa19,0x6000aa3e),('parent_query',0x600096e5,0x60009704),('device_create',0x60009f8a,0x60009fb4),
           ('zero_request',0x6000a6f8,0x6000a707),('selector5_branch',0x60004b6e,0x60004b8d),
           ('raw_state_wrapper',0x60008a10,0x60008a47)]
    result={'kind':'static-dx7-dither-requests','archive':archive,'archive_sha256':ah,'member':'drivers/dx7/dx7a.dll',
        'sha256':sha(raw),'sdk_headers':headers,'selector5_target':f'{target:08x}','initializer_prefix_forward_branches':branches,
        'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
         'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans],
        'verified':['Selected successful factory chain produces IDirect3DDevice7 at60058d9c;SDK SetRenderState slot20 corresponds to+50h.',
                    '6000a6f8..6000a707 requests DITHERENABLE26 with value0 through that object.',
                    'THRASH selector5 targets60004b6e,which selects1/0 based on EBX versus EDX and calls raw state26 wrapper.',
                    'Direct call60009ec0 reaches initializer6000a490;its seven prefix branches are forward and rejoin before the disable request,with no local early RET.',
                    'On normal return from preceding calls,initializer entry reaches the disable request;vtable+14/+18 calls bracket the broader setup sequence.',
                    'This supplies partial code support forMP150-029 without proving permanent/default runtime state.'],
        'limits':['Initializer caller parent/export reachability,whole reset lifecycle,EDX producer for selector branch and all later overrides remain unresolved;callee nonreturn/faults excluded from prefix argument.',
                  'API/device success and visible dithering not observed;request result is not tested in retained zero-request slice.',
                  'No source lineage,original-driver dither policy or all-provider comparison established.',
                  'SDK headers are hashed cached inputs;fresh retrieval may differ and is not silently accepted.',
                  'No DLL/API/target instruction execution,compilation or Ghidra changes.']}
    (ROOT/'analysis/evidence/audits/dx7-dither-requests.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:150 DX7 disable request and selector5 alternative retained;SDK state26 and device slot20 verified')


if __name__=='__main__':main()
