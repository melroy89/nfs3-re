"""Static early required-directory checker versus final two-stage preparation."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    ah='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac';assert sha(archive.read_bytes())==ah
    early=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    eh='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72';assert sha(early)==eh
    rel,digest,_=SPECS['official_modern'];raw=(ROOT/rel).read_bytes();assert sha(raw)==digest
    result={'kind':'static-install-directory-history','archive':str(archive.relative_to(ROOT)),'archive_sha256':ah,'binaries':{}}
    for label,data,expected in [('1.1.0',early,eh),('official_final',raw,digest)]:
        pe=pefile.PE(data=data)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        imports={e.address:e.name.decode()for dll in pe.DIRECTORY_ENTRY_IMPORT for e in dll.imports if e.name}
        assert imports[0x534520]=='GetFileAttributesA'
        if label=='1.1.0':
            pointers=struct.unpack('<5I',get(0x4a3998,0x4a39ac));assert pointers[-1]==0
            paths=[pe.get_string_at_rva(a-0x400000).decode()for a in pointers[:-1]]
            assert paths==['.\\GameData\\Tracks\\','.\\GameData\\CarModel\\','.\\FeData\\Art\\','.\\FeData\\Text\\']
            assert get(0x4a3974,0x4a3995).hex()=='515257ff152045530083f8ff740ea9100000007407b801000000eb0231c05a59c3'
            spans=[(0x4a3974,0x4a3995),(0x4a39ac,0x4a39d2)]
            tables={'required_static_strings':paths}
        else:
            assert imports[0x534490]=='CreateDirectoryA'
            assert get(0x4f9214,0x4f9229).hex()=='5389c3e850ffffff85c0750789d8e8ddffffff5bc3'
            tables={}
            for a,n,key in [(0x4a3938,13,'required_slots'),(0x4a3970,4,'create_slots')]:
                pointers=struct.unpack('<'+'I'*(n+1),get(a,a+4*(n+1)));assert pointers[-1]==0
                assert all((v-0x7a27b4)%128==0 and 0<=v-0x7a27b4<22*128 for v in pointers[:-1])
                tables[key]=[f'{v:08x}'for v in pointers[:-1]]
            spans=[(0x4a3984,0x4a39c6),(0x4f915e,0x4f916a),(0x4f916c,0x4f9184),
                   (0x4f9204,0x4f9212),(0x4f9214,0x4f9229)]
        result['binaries'][label]={'sha256':expected,'tables':tables,'captures':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
             'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    result['limits']=['No game, file/directory/API calls or extracted instructions executed; no directory created.',
        'Early/final boundary only; no1.0.0 introduction or precise intermediate expansion date.',
        'Final slot strings/initialization and startup error caller are linked prior evidence, not revalidated as live buffers.',
        'Attribute success and directory bit do not prove asset contents, access rights, complete installation or later I/O success.',
        'Paths and CWD can change between checks/use; no atomicity, concurrency or lifecycle safety claim.',
        'Create helper returns its API result after a failed existence test, without retry/recheck or recursive parent creation.']
    (ROOT/'analysis/evidence/audits/install-directory-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:early four named directory checks,final13/4 pointer tables and complete attribute/create helpers')


if __name__=='__main__':main()
