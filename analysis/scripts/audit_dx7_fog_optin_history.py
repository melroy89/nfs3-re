"""Bound API107 fog claim by DX7 artifact/config identity and EXE reader."""
import configparser,hashlib,io,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    specs={'1.5.1':('c7b66da29ef8cd58c56e27a403bd2889d8a4f0f7cac0873c28a1b4b5a09723de','4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17',0x4b58e8),
           '1.5.2':('23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd','d532b0252610d9de2e826efc399d4d733d84d4758e47b5fadc94bf5c1d4449bb',0x4b58f8)}
    result={'kind':'static-dx7-fog-optin-history','versions':{}};bodies={};inis={};dlls=[]
    for v,(ah,eh,start)in specs.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{v}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        members={name:subprocess.check_output(['7z','x','-so',str(archive),name])for name in ['nfs3.exe','drivers/dx7/dx7a.dll','drivers/dx7/thrash.ini']}
        assert sha(members['nfs3.exe'])==eh
        dll=members['drivers/dx7/dx7a.dll'];assert sha(dll)=='8f3ed9676611d65f40b5dde537aab5813d2e2a854c08fdf3b08b7d19a7a25d5e';dlls.append(dll)
        cp=configparser.ConfigParser();cp.read_file(io.StringIO(members['drivers/dx7/thrash.ini'].decode('utf-8-sig')))
        inis[v]=dict(cp['THRASH']);assert inis[v]['fogsupport']==('0'if v=='1.5.1'else'1')
        pe=pefile.PE(data=members['nfs3.exe']);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        body=get(start,start+35);assert body[:7].hex()=='6830397a006a00'
        assert body[7]==body[12]==0x68
        for offset,value in [(8,b'FogSupport'),(13,b'THRASH')]:
            ptr=int.from_bytes(body[offset:offset+4],'little');assert pe.get_string_at_rva(ptr-0x400000)==value
        assert body[17:].hex()=='ff156c46530085c0740331c040a3543a7a00'
        imported=next((d.dll.decode(),i.name.decode())for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address==0x53466c)
        assert imported[1]=='GetPrivateProfileIntA'
        spans=[('fog_reader',start,start+35),('cached_state_dispatch',0x431900,0x431a99),
               ('environment_state15',0x470aa0,0x470ac1),('environment_state14',0x470ad0,0x470b1e)]
        bodies[v]=[get(a,b)for name,a,b in spans[1:]]
        result['versions'][v]={'archive':rel,'archive_sha256':ah,'members':[{'member':k,'sha256':sha(raw),'bytes':len(raw)}for k,raw in members.items()],
            'dx7_thrash_options':inis[v],'profile_import':{'dll':imported[0],'name':imported[1],'iat':'0053466c'},
            'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                         'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    assert dlls[0]==dlls[1]and bodies['1.5.1']==bodies['1.5.2']
    assert {k:v for k,v in inis['1.5.1'].items()if k!='fogsupport'}=={k:v for k,v in inis['1.5.2'].items()if k!='fogsupport'}
    result['verified']=['Whole packaged DX7 DLL is identical151/152,not a new DX7 implementation in these snapshots.',
        'THRASH/FogSupport changes0->1;all other parsed THRASH values match.',
        'Both historical EXE readers use default0 and normalize nonzero profile return to1 at007a3a54.',
        'Complete cached-state dispatcher and selected environment14/15 bodies remain identical in these two EXEs.']
    result['limits']=['Static package/config/selected code comparison;no driver,INI API,game,instruction probe,compiler or Ghidra writes.',
        'This establishes packaged opt-in,not effective installed settings or visible DX7 fog.',
        'Full API107 adapter/version contract and other EXE/provider changes remain unresolved;checked equal spans are not whole-interface equivalence.',
        'Do not assign early effective gate007a3a64 the same meaning as support flag007a3a54 without producer evidence.',
        'MP152-002 has partial configuration support only;broader compatibility and rendered-fog clauses remain unverified.']
    (ROOT/'analysis/evidence/audits/dx7-fog-optin-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:DX7 DLL identical151/152;FogSupport0->1;paired readers and selected unchanged state bodies')


if __name__=='__main__':main()
