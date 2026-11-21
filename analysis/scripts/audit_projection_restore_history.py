"""Date selected projection restore changes153 to160; no target execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    ap='analysis/evidence/audits/language-fallback-history.json';bp='analysis/evidence/audits/official-160-161-baseline.json'
    a=json.loads((ROOT/ap).read_text())['packages']['1.5.3'];b=json.loads((ROOT/bp).read_text())['packages']['1.6.0']
    specs={'1.5.3':(a['archive'],a['archive_sha256'],a['executable_sha256']),
           '1.6.0':(b['archive_path'],b['archive_sha256'],next(r['sha256']for r in b['members']if r['member']=='nfs3.exe'))}
    result={'kind':'static-projection-restore-history','source_manifests':[{'path':p,'sha256':sha((ROOT/p).read_bytes())}for p in [ap,bp]],'versions':{}};bodies=[];camera_regions=[]
    spans=[('type8_restore',0x4213b0,0x421441),('projection_builder',0x4bf260,0x4bf370),('float_consumer',0x41bc90,0x41bf26),('fixed_descriptor_handler',0x4240c0,0x424252),('camera_dispatch_wrapper',0x426450,0x42649a),('type8_handler',0x425060,0x4251ef),('removed_stub_and_padding',0x421480,0x421490)]
    for version,(rel,ah,eh)in specs.items():
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        camera_regions.append(get(0x420000,0x427000))
        bodies.append([get(a,b)for _,a,b in spans])
        if version=='1.6.0':assert get(0x421404,0x421430)==b'\xeb\x2a'+b'\x90'*42
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'camera_dispatch_table':{'start':'004263f0','bytes':96,'hex':get(0x4263f0,0x426450).hex(),'sha256':sha(get(0x4263f0,0x426450))},
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert bodies[0][1:-1]==bodies[1][1:-1]
    assert result['versions']['1.5.3']['camera_dispatch_table']==result['versions']['1.6.0']['camera_dispatch_table']
    result['retained_camera_boundaries']=['Complete402-byte fixed-descriptor handler,74-byte dispatch wrapper,96-byte dispatch table and399-byte type8 handler match153/160.','Their documented original/final changes therefore predate160 in this historical lineage;not newly introduced by this pair.']
    changed=[0x4213b0+i for i,(a,b)in enumerate(zip(bodies[0][0],bodies[1][0]))if a!=b]
    assert len(changed)==75 and all(0x4213d4<=v<0x421430 for v in changed)
    result['restore_changed_bytes']=[f'{v:08x}'for v in changed]
    region_changes=[0x420000+i for i,(a,b)in enumerate(zip(*camera_regions))if a!=b]
    assert len(region_changes)==91 and set(region_changes)==set(changed)|set(range(0x421480,0x421490))
    assert bodies[1][-1]==b'\x90'*16
    assert bodies[0][-1].hex()=='5589e55dc38d80000000008d52008bdb'
    result['complete_camera_region_partition']={'start':'00420000','end_exclusive':'00427000','bytes':28672,'changed_bytes':91,'unchanged_bytes':28581,'sha256':[sha(x)for x in camera_regions],'restore_changed_bytes':75,'stub_padding_changed_bytes':16,'outside_these_two_regions_identical':True,'limits':'Address-bounded region,not every camera function,data,callee or runtime-generated code.'}
    result['retained_float_mapping']={'005e1020':'0056009c','005e1038':'005600a0','005e102c':'005600a4','005e1030':'005600a8'}
    result['removed_legacy_stores']={'005e10a0':'0056443c','005e1034':'00564440','005e1024':'00564434','005e1028':'00564438'}
    result['limits']=['Historical local restore removal,not the complete MP160-003 camera/horizon mechanism.',
        'Float mapping retained but instruction scheduling differs;not all-state equivalence for exceptions,flags or nonordinary values.',
        'Source capture writer/lifetime,computed aliases,camera orientation and rendered horizon remain unresolved.',
        'No target/API/instruction execution,compilation or executable/Ghidra mutations.']
    (ROOT/'analysis/evidence/audits/projection-restore-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:153 to160 removes four legacy integer stores;four float mappings retained;builder and consumer identical')


if __name__=='__main__':main()
