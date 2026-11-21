"""Compare complete140/150 SoftTri code section and selected callback; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-softtri-mode-fix-history','versions':{}};codes=[];initializers=[]
    for version,pin in [('1.4.0','93a9de899d341eec71a3cf46575d51eb265ef495e12d6e5e56ab5130660ce191'),('1.5.0','2db30c5c38eb9686731d7f309e6f43b580afef73bf0f3e4c18df6a0e2cbaf25c')]:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==HISTORY[version][0]
        member='drivers/softtri/softtria.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==pin
        pe=pefile.PE(data=raw);assert pe.OPTIONAL_HEADER.ImageBase==0x60000000
        section=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.code');code=section.get_data();codes.append(code)
        assert section.VirtualAddress==0x1000 and len(code)==245760
        get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        imports={i.address:i.name.decode()for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name};assert imports[0x6003d200]=='GetSystemInfo'
        assert imports[0x6003d254]=='VirtualAlloc'
        initializers.append(get(0x600026e7,0x600027ac))
        assert get(0x600026ef,0x600026f6).hex()=='2eff1500d20360'
        assert get(0x60002707,0x6000270e).hex()=='2eff1554d20360'
        assert get(0x6000277a,0x6000277f).hex()=='6880240060'
        assert get(0x60002794,0x60002799).hex()=='ba03000000'
        assert get(0x600027a9,0x600027ac).hex()=='ff5220'
        old=version=='1.4.0'
        assert get(0x60002499,0x6000249e).hex()==('be10000000'if old else'eb03909090')
        assert get(0x60002537,0x60002545).hex()==('817b08e00100007cc6eb03909090'if old else'85ed74cb89e0502eff1500d20360')
        assert get(0x60002545,0x60002552).hex()=='b9280000008b44240431d2f7f1'
        ini=subprocess.check_output(['7z','x','-so',str(archive),'drivers/softtri/thrash.ini'])
        result['versions'][version]={'archive':rel,'archive_sha256':HISTORY[version][0],'member':member,'sha256':pin,
            'code':{'rva':'00001000','bytes':len(code),'sha256':sha(code)},'system_info_import':{'iat':'6003d200','name':imports[0x6003d200]},
            'initializer':{'start':'600026e7','end_exclusive':'600027ac','hex':get(0x600026e7,0x600027ac).hex(),'sha256':sha(get(0x600026e7,0x600027ac)),'disassembly':disassemble(get(0x600026e7,0x600027ac),0x600026e7)},'ini':{'sha256':sha(ini),'text':ini.decode()},'callback':{'start':'60002480','end_exclusive':'6000257e','bytes':254,
                'hex':get(0x60002480,0x6000257e).hex(),'sha256':sha(get(0x60002480,0x6000257e)),'disassembly':disassemble(get(0x60002480,0x6000257e),0x60002480)}}
    assert initializers[0]==initializers[1]
    result['allocation_registration_contract']={'initializer_identical140_150':True,'system_info_call':'600026ef','allocation_call':'60002707','allocation_import':'VirtualAlloc','allocation_size':'SYSTEM_INFO local+4,page size','published_pointer':'60040050','initial_count':3,'context_pointer':'6004004c','callback_push':'6000277a','callback':'60002480','dispatch_call':'600027a9 vtable+20h','capacity_argument':'For successful allocationP and matching callback page sizeP,3<=count<floor(P/40) selects recordcount;40*(count+1)<=P.','limits':'Requires successful allocation,consistent page size/count,ordinary pointers and no aliased/intervening mutations;not universal safety.'}
    changed=[0x60001000+i for i,(a,b)in enumerate(zip(*codes))if a!=b]
    assert changed==list(range(0x60002499,0x6000249e))+list(range(0x60002537,0x60002545))
    result['complete_code_partition']={'changed_bytes':19,'unchanged_bytes':245741,'ranges_exclusive':[['60002499','6000249e'],['60002537','60002545']],'scope':'Complete file-backed code section;not complete PE files or transitive runtime behavior.'}
    result['api_layout_sources']=['https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsysteminfo','https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-system_info']
    result['findings']=['150 calls GetSystemInfo with ESP before reading local+4 and unsigned dividing by40 for count bound;32-bit SYSTEM_INFO+4 is dwPageSize.',
        '140 instead tests signed input height>=480 at that location,without the local API-buffer initialization in this callback.',
        'Other changed block removes MOV ESI,16 after preceding input-depth==16 admission;its local assigned value is redundant.',
        'INI removes LightBeams=0;File,Type and DirectDrawLagFix retained.']
    result['limits']=['Selected mode callback/system-info mechanism,not proven complete advertised symptom or successful resolution enumeration.',
        'Selected allocation request/registration linked;full lifetime,page-size values,classifier transitive writes,all API outcomes or actual UI modes established.',
        'BSS has raw pointer0;no file-offset0 bytes interpreted as its runtime initial contents.',
        'No DLL/API/target instruction execution or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/softtri-mode-fix-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:all19 code-byte changes confined to callback;150 adds GetSystemInfo before local bound read;runtime untested')


if __name__=='__main__':main()
