"""Pin author-reference/final Voodoo2 providers and inventory shared-section differences."""
import hashlib,json,subprocess,struct
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import intervals,disassemble
from audit_screenshot_counter_history import PINS
from audit_endpoint_comma_history import HISTORY


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
            'complete_about':{'start':'60001bb0','end_exclusive':'60001d4d','bytes':413,'sha256':sha(pe.get_data(0x1bb0,413)),'hex':pe.get_data(0x1bb0,413).hex(),'disassembly':disassemble(pe.get_data(0x1bb0,413),0x60001bb0)},'about_prefix':{'start':'60001bb0','end_exclusive':'60001cb4','bytes':260,'sha256':sha(about),'hex':about.hex(),'disassembly':disassemble(about,0x60001bb0)}}
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
    historical={};historical_bodies=[]
    for version,ah,member,pin in [('1.3.1',PINS['1.3.1'][0],'drivers/dgvoodoo/voodoo2.dll','de501a929c31cd0d878e162c2b06b34088637bfd1871f7992d2af93f7983311a'),('1.4.0',HISTORY['1.4.0'][0],'drivers/glide3x/voodoo2a.dll','67764a56917fd93fffb847968f2cf90cff7c0fd8ab812d99403bfa88ef0208d3')]:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        blob=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member]);assert sha(blob)==pin
        hp=pefile.PE(data=blob);body=hp.get_data(0x1bb0,413);historical_bodies.append(body)
        assert hp.get_data(0x1c24,10).hex()=='be10000000bf00300160'
        targets={}
        for call in [0x60001d11,0x60001d2d,0x60001d3e]:
            op=hp.get_data(call-0x60000000,5);assert op[0]==0xe8;targets[f'{call:08x}']=f'{call+5+struct.unpack("<i",op[1:])[0]:08x}'
        producer_start,producer_end=(0x600012f0,0x60001545)if version=='1.3.1'else(0x600018d8,0x60001b5a)
        producer=hp.get_data(producer_start-0x60000000,producer_end-producer_start)
        query_slot=0x600128c0 if version=='1.3.1'else 0x600127c0;query_binding=None
        for table_index in range(128):
            name_address,destination=struct.unpack('<II',hp.get_data(0x1120+8*table_index,8))
            if not name_address:break
            if destination==query_slot:query_binding=hp.get_string_at_rva(name_address-0x60000000).decode()
        assert query_binding=='_grQueryResolutions@8'
        if version=='1.3.1':
            assert hp.get_data(0x1352,14).hex()=='c7463c1000000089f0e8e0050000'
            assert hp.get_data(0x1373,17).hex()=='bed4fd0060bf00300160b9b4000000f3a5'
        else:
            assert hp.get_data(0x1a63,8).hex()=='8d45e4e87df8ffff'
            assert hp.get_data(0x1aaa,16).hex()=='c745d0ffffffffc745d4ffffffffebb1'
        historical[version]={'archive':rel,'archive_sha256':ah,'member':member,'sha256':pin,'about_start':'60001bb0','about_end_exclusive':'60001d4d','about_sha256':sha(body),'about_hex':body.hex(),'disassembly':disassemble(body,0x60001bb0),'direct_targets':targets,'mode_producer':{'start':f'{producer_start:08x}','end_exclusive':f'{producer_end:08x}','bytes':len(producer),'sha256':sha(producer),'hex':producer.hex(),'disassembly':disassemble(producer,producer_start),'query_slot':f'{query_slot:08x}','query_binding':query_binding}}
    hd=[0x60001bb0+i for i,(x,y)in enumerate(zip(*historical_bodies))if x!=y]
    assert hd==[0x60001d12,0x60001d13,0x60001d2e,0x60001d3f,0x60001d40]
    assert historical['1.3.1']['direct_targets']=={'60001d11':'600012f0','60001d2d':'6000110c','60001d3e':'600012f0'}
    assert historical['1.4.0']['direct_targets']=={'60001d11':'600018d8','60001d2d':'60001108','60001d3e':'600018d8'}
    result['historical_about']={'versions':historical,'changed_bytes':[f'{v:08x}'for v in hd],'scope':'Complete413-byte about bodies differ only in three call operands;both publish initial16/table60013000;target semantics/lifetime separate.'}
    result['limits']=['Author-hosted reference is distinct from the earlier local VOODOO2A candidate;retail/source provenance not authenticated.',
        'Shared-section raw inventory and about publication,not complete semantic assignment of3307 code bytes or all PE/header/resource changes.',
        'Import-name changes are static dependencies,not successful calls;raw import differences are not function-change counts.',
        'BSS raw pointer0 omitted from file-data hashing;declared extents do not establish runtime allocation/lifetime.',
        'No DLL/API/target instruction execution or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/voodoo-reference-final.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:34 matched Voodoo exports;3307 changed code bytes in{len(comparisons[0]["changed_intervals"])} intervals;about count/table publication mapped')


if __name__=='__main__':main()
