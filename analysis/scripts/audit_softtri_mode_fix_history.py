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
    refrel='analysis/captures/modern-differences/upstream/history/nfs3_orig.7z'
    assert sha((ROOT/refrel).read_bytes())=='374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'
    reference=subprocess.check_output(['7z','x','-so',str(ROOT/refrel),'softtria.dll'])
    assert sha(reference)=='8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02'
    rp=pefile.PE(data=reference);assert rp.sections[0].VirtualAddress==0x1000 and rp.sections[0].SizeOfRawData==245760
    refcode=rp.get_data(0x1000,245760)
    refdelta=[{'address':f'{0x60001000+i:08x}','reference':a,'150':b}for i,(a,b)in enumerate(zip(refcode,codes[1]))if a!=b]
    assert len(refdelta)==8 and all(0x60002480<=int(r['address'],16)<0x6000257e for r in refdelta)
    exports=lambda p:[(e.name.decode()if e.name else None,e.ordinal,e.address,e.forwarder)for e in p.DIRECTORY_ENTRY_EXPORT.symbols]
    assert exports(rp)==exports(pe) and len(exports(rp))==34
    refcallback=rp.get_data(0x2480,254)
    assert refcallback[0xb7:0xc5].hex()=='85ed749b89e0502eff1500d20360'
    result['original_reference']={'archive':refrel,'archive_sha256':sha((ROOT/refrel).read_bytes()),'member':'softtria.dll','sha256':sha(reference),'code_sha256':sha(refcode),'code_bytes':len(refcode),'reference_to150_changed_bytes':refdelta,'matched_exports':34,'callback':{'start':'60002480','end_exclusive':'6000257e','hex':refcallback.hex(),'sha256':sha(refcallback),'disassembly':disassemble(refcallback,0x60002480)},'provenance':'Author-hosted reference bundle;not authenticated pristine retail or independently paired to supplied original EXE.'}
    finalrel='analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z';assert sha((ROOT/finalrel).read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    finalraw=subprocess.check_output(['7z','x','-so',str(ROOT/finalrel),'drivers/softtri/softtria.dll']);assert sha(finalraw)=='9479203471f4dd615788769bac365043d903505af370c48df69e5d6a1e6f8732'
    finalcode=pefile.PE(data=finalraw).get_data(0x1000,245760)
    later=[{'address':f'{0x60001000+i:08x}','150':a,'final':b}for i,(a,b)in enumerate(zip(codes[1],finalcode))if a!=b];assert len(later)==36
    result['later_final_boundary']={'archive':finalrel,'archive_sha256':sha((ROOT/finalrel).read_bytes()),'member_sha256':sha(finalraw),'code_sha256':sha(finalcode),'150_to_final_changed_code_bytes':later,'semantics':'Pending;150 callback repair does not establish complete final correspondence.'}
    fp=pefile.PE(data=finalraw)
    assert fp.get_data(0x31ac,6).hex()=='76d290909090'
    assert pe.get_data(0x31ac,6).hex()=='0f8639ffffff'
    assert fp.get_data(0x362f,6).hex()=='0f858c000000'
    assert fp.get_data(0x36c1,15).hex()=='6a00ff15b4000460e982feffff9090'
    assert fp.get_data(0x37bb,11).hex()=='5b5e5f6a00ff15b4000460'
    assert fp.get_data(0x37dc,2).hex()=='ebe0'
    witness_spans=[('state_selector_prefix',0x600030c0,0x600031bb),('lock_and_failure_trampoline',0x60003530,0x600036d0),('pageflip_selected_paths',0x60003750,0x600037de)]
    result['later_final_boundary']['classified_witnesses']={label:[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':image.get_data(a-0x60000000,b-a).hex(),'sha256':sha(image.get_data(a-0x60000000,b-a)),'disassembly':disassemble(image.get_data(a-0x60000000,b-a),a)}for n,a,b in witness_spans]for label,image in [('150',pe),('final',fp)]}
    assert all(any(a<=int(r['address'],16)<b for _,a,b in witness_spans)for r in later)
    result['later_final_boundary']['semantics']='All36 byte differences assigned to selector15h result retarget,lock-failure callback0 trampoline,and pageflip cleanup/callback order;callback ABI and runtime outcomes unresolved.'
    assert sum(a!=b for a,b in zip(refcode,finalcode))==44
    result['reference_to_final_code_summary']={'bytes':245760,'changed_bytes':44,'unchanged_bytes':245716,'scope':'Complete code section only;8 reference-to150 plus36 disjoint later deltas,all locally classified.'}
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
