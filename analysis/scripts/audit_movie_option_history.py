"""Static singular/plural movie-option history and title-admission linkage."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble
from audit_mode_capacity_history import HISTORY as EARLY

SPECS={
 '1.1.0':(*EARLY['1.1.0'][:2],0x4b62c4,0x4b62f1,0x53ee74,0x53ee28),
 '1.2.0':(*EARLY['1.2.0'][:2],0x4b62c4,0x4b62f6,0x53ee58,0x53edf8),
 '1.5.1':('c7b66da29ef8cd58c56e27a403bd2889d8a4f0f7cac0873c28a1b4b5a09723de',
           '4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17',0x4b55b6,0x4b55ce,0x53ed24,None),
 '1.5.2':('23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd',
           'd532b0252610d9de2e826efc399d4d733d84d4758e47b5fadc94bf5c1d4449bb',0x4b55b6,0x4b55ce,0x53ed24,None),
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    capture=ROOT/'analysis/captures/modern-differences/movie-option-history'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-movie-disable-key-history','versions':{},
        'limits':['No INI, environment, command-line, movie, API or target execution.',
                  '1.0.0 artifact not inspected;1.1.0 is retained early evidence, not proof of introduction.',
                  'Selected key read and switch slot do not exclude every alternative writer/parser or external wrapper.',
                  'Title-request suppression does not establish every possible intro/movie call path or successful playback.']}
    branches={};masks={}
    for version,(archive_hash,exe_hash,start,end,keyptr,sectionptr) in SPECS.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/relative;assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_hash
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        key=pe.get_string_at_rva(keyptr-0x400000).decode()
        assert key==('NoMovies' if version=='1.5.2' else 'NoMovie')
        switchptr=struct.unpack('<I',get(0x55eb60,0x55eb64))[0]
        switch=pe.get_string_at_rva(switchptr-0x400000).decode()
        assert switch==('-nomovies' if version=='1.5.2' else '-nomovie')
        reader_end=0x4fb703 if version=='1.1.0' else 0x4fb713
        spans=[(start,end),(0x4fb6f0,reader_end),(0x4730d0,0x473169)]
        if version in ('1.5.1','1.5.2'):spans.append((0x4a2f90,0x4a2ffc))
        rows=[]
        for a,b in spans:
            data=get(a,b);path=capture/f'{version}-{a:08x}.asm'
            path.write_text('\n'.join(disassemble(data,a))+'\n')
            rows.append({'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                'bytes':len(data),'sha256':sha(data),'hex':data.hex(),
                'assembly':str(path.relative_to(ROOT)),'assembly_sha256':sha(path.read_bytes())})
        if version!='1.1.0':
            assert get(0x4fb6f2,0x4fb6f7).hex()=='e83d000000'
        if sectionptr:
            assert pe.get_string_at_rva(sectionptr-0x400000)==b'NFS3'
            assert b'\xbf'+struct.pack('<I',0x55eb2c) in get(start,end)
            assert get(end-8,end).hex()=='8a47010c08884701'
            assert get(0x47313d,0x473146).hex()=='f6052deb5500087523'
            assert pe.get_string_at_rva(0x13b048)==b'titleav.mad'
        else:
            branches[version]=get(start,end)
            assert get(start,end).hex()=='bb24ed530031d2e82e61040085c074080fba2d2ceb55000b'
            mask=get(0x4a2f90,0x4a2ffc);masks[version]=mask
            assert get(0x4a2f93,0x4a2fa7).hex()=='c70568277a00000000000fba252ceb55000b724c'
        imports={e.address:e.name.decode()for d in pe.DIRECTORY_ENTRY_IMPORT for e in d.imports if e.name}
        call_site=0x4fb6fa if version=='1.1.0' else 0x4fb70a
        encoded=get(call_site,call_site+6);assert encoded[:2]==b'\xff\x15'
        profile_iat=struct.unpack('<I',encoded[2:])[0]
        assert imports[profile_iat]=='GetPrivateProfileIntA'
        result['versions'][version]={'archive':relative,'archive_sha256':archive_hash,'member':'nfs3.exe','sha256':exe_hash,
            'key_pointer':f'{keyptr:08x}','key':key,'switch_slot':11,'switch_pointer':f'{switchptr:08x}','switch':switch,
            'reader_profile_import':f'{profile_iat:08x} GetPrivateProfileIntA',
            'environment_fallback_in_reader':version!='1.1.0','spans':rows}
    assert branches['1.5.1']==branches['1.5.2']
    assert masks['1.5.1']==masks['1.5.2']
    result['checks']={'151_152_movie_setting_branch_identical':True,'151_152_complete_mask_builder_identical':True,
        'rename':'Both INI key NoMovie->NoMovies and switch slot11 -nomovie->-nomovies at1.5.1/1.5.2.',
        'early_title_gate':'1.1.0/1.2.0 setup tests byte0055eb2d mask08h = DWORD0055eb2c bit11 before title request.',
        'set_only':'Nonzero setting sets bit11; zero path does not explicitly clear it.',
        'fallback_scope':'No legacy singular-key retry in the captured1.5.2 setting branch; not a whole-program alias exclusion.'}
    (ROOT/'analysis/evidence/audits/movie-option-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four pinned historical movie keys/switches, early title gate and151/152 rename with retained flag/mask logic')


if __name__=='__main__':main()
