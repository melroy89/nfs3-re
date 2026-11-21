"""Date known16 clock-call changes to152->153; static only."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_clock_source_difference import SITES,TIMER_SPANS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.5.2':('23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd','d532b0252610d9de2e826efc399d4d733d84d4758e47b5fadc94bf5c1d4449bb'),
          '1.5.3':('0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64','07e987193ebeb4b30ac3912f90d8b98f2a34b37632dbad232ecfcea12fdb7c0a')}
    result={'kind':'static-clock-source-history','versions':{}};images=[];imports=[]
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);images.append(p);entries={(d.dll.decode().lower(),i.name.decode()if i.name else '#'+str(i.ordinal))for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports};imports.append(entries)
        slots={i.address:(d.dll.decode().lower(),i.name.decode())for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        site_rows=[];iat=0x534568 if version=='1.5.2'else 0x534664
        assert slots[iat]==(('kernel32.dll','GetTickCount')if version=='1.5.2'else('winmm.dll','timeGetTime'))
        for a in SITES:
            body=p.get_data(a-0x400000,7);n=6 if a==0x4f2792 and version=='1.5.3'else 7
            assert body[:n]==(b'\xff\x15'if n==6 else b'\x2e\xff\x15')+struct.pack('<I',iat)
            site_rows.append({'address':f'{a:08x}','hex':body[:n].hex(),'iat':f'{iat:08x}','name':slots[iat][1]})
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'sites':site_rows,'imports':[{'dll':d,'name':n}for d,n in sorted(entries)],'timer_ranges':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(p.get_data(a-0x400000,b-a))}for a,b in TIMER_SPANS],'reader_disassembly':disassemble(p.get_data(0xf2790,12),0x4f2790)}
    assert imports[1]-imports[0]=={('winmm.dll','timeGetTime')}and not imports[0]-imports[1]
    result['normalized_ranges']=[]
    for a,b in TIMER_SPANS:
        old=bytearray(images[0].get_data(a-0x400000,b-a));new=images[1].get_data(a-0x400000,b-a)
        for site in SITES:
            if a<=site and site+7<=b:old[site-a+3:site-a+7]=struct.pack('<I',0x534664)
        assert old==new
        result['normalized_ranges'].append({'start':f'{a:08x}','end_exclusive':f'{b:08x}','equal_after_only_clock_operand_changes':True})
    result['limits']=['Known16-site list reused,not exhaustive dynamic/indirect clock inventory.',
        'Normal import-set change is not delay/dynamic dependency or API-success evidence.',
        'No timing accuracy,jitter,frame pacing,replay/network equivalence or rollover behavior measured.',
        'MP153-014 generic startup fix is not attributed to this clock change;cause remains unverified.',
        'No target/API/instruction execution,compilation or executable/Ghidra edits.']
    (ROOT/'analysis/evidence/audits/clock-source-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:16 known clock calls changeGetTickCount->timeGetTime at152->153;timer ranges otherwise retained')


if __name__=='__main__':main()
