"""Pin author-reference/final Voodoo2 providers and inventory shared-section differences."""
import hashlib,json,subprocess,struct
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import intervals,disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    specs=[('reference','analysis/captures/modern-differences/upstream/history/nfs3_orig.7z','374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127','voodoo2a.dll','99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b'),
        ('final','analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z','c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3','drivers/glide3x/voodoo2a.dll','f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b')]
    result={'kind':'static-voodoo-reference-final','binaries':{}};images=[];imports=[]
    for role,rel,ah,member,pin in specs:
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member]);assert sha(raw)==pin
        pe=pefile.PE(data=raw);images.append(pe);assert pe.OPTIONAL_HEADER.ImageBase==0x60000000
        entries=sorted((d.dll.decode().lower(),i.name.decode()if i.name else'#'+str(i.ordinal))for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports);imports.append(set(entries))
        sections=[{'name':s.Name.rstrip(b'\0').decode(),'rva':f'{s.VirtualAddress:08x}','raw_pointer':s.PointerToRawData,'raw_size':s.SizeOfRawData,'virtual_size':s.Misc_VirtualSize,'file_sha256':sha(s.get_data())if s.PointerToRawData else None}for s in pe.sections]
        about=pe.get_data(0x1bb0,260)
        result['binaries'][role]={'archive':rel,'archive_sha256':ah,'member':member,'sha256':pin,'file_bytes':len(raw),'sections':sections,'imports':[{'dll':d,'name_or_ordinal':n}for d,n in entries],
            'about_prefix':{'start':'60001bb0','end_exclusive':'60001cb4','bytes':260,'sha256':sha(about),'hex':about.hex(),'disassembly':disassemble(about,0x60001bb0)}}
    a,b=images
    exports=lambda p:[(e.name.decode()if e.name else None,e.ordinal,e.address,e.forwarder)for e in p.DIRECTORY_ENTRY_EXPORT.symbols]
    assert exports(a)==exports(b)and len(exports(a))==34
    result['matched_exports']=34
    comparisons=[]
    for name,rva,size in [('code',0x1000,51712),('imports',0xe000,2048),('file_backed_data',0xf000,7680)]:
        x,y=[p.get_data(rva,size)for p in images];delta=intervals(x,y,0x60000000+rva)
        comparisons.append({'name':name,'rva':f'{rva:08x}','bytes':size,'reference_sha256':sha(x),'final_sha256':sha(y),'changed_bytes':sum(u!=v for u,v in zip(x,y)),'changed_intervals':delta})
    assert [x['changed_bytes']for x in comparisons]==[3307,1218,363]
    result['shared_section_comparisons']=comparisons
    x,y=[p.get_data(0x1bb0,260)for p in images];changed=[0x60001bb0+i for i,(u,v)in enumerate(zip(x,y))if u!=v]
    assert changed==[0x60001c25,0x60001c2a,0x60001c2b,0x60001c2c]
    assert a.get_data(0x1c24,10).hex()=='be10000000bfd4fd0060'
    assert b.get_data(0x1c24,10).hex()=='be00000000bf00300160'
    result['about_publication']={'descriptor':'6000fd10','count_cell':'6000fd4c','table_pointer_cell':'6000fd50','initial_count_reference':16,'initial_count_final':0,'table_reference':'6000fdd4','table_final':'60013000','scope':'260-byte prefix only;subordinate enumeration and full lifecycle not inferred.'}
    result['normalized_import_changes']={'removed':[{'dll':d,'name_or_ordinal':n}for d,n in sorted(imports[0]-imports[1])],'added':[{'dll':d,'name_or_ordinal':n}for d,n in sorted(imports[1]-imports[0])]}
    result['limits']=['Author-hosted reference is distinct from the earlier local VOODOO2A candidate;retail/source provenance not authenticated.',
        'Shared-section raw inventory and about publication,not complete semantic assignment of3307 code bytes or all PE/header/resource changes.',
        'Import-name changes are static dependencies,not successful calls;raw import differences are not function-change counts.',
        'BSS raw pointer0 omitted from file-data hashing;declared extents do not establish runtime allocation/lifetime.',
        'No DLL/API/target instruction execution or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/voodoo-reference-final.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:34 matched Voodoo exports;3307 changed code bytes in{len(comparisons[0]["changed_intervals"])} intervals;about count/table publication mapped')


if __name__=='__main__':main()
