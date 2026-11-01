"""Static historical abort presentation routing, without target execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_x87_precision_history import calls


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    old=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']['1.5.3']
    new=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())['packages']['1.6.0']
    specs={'1.5.3':(old['archive'],old['archive_sha256'],old['executable_sha256']),
           '1.6.0':(new['archive_path'],new['archive_sha256'],next(x['sha256'] for x in new['members'] if x['member']=='nfs3.exe'))}
    capture=ROOT/'analysis/captures/modern-differences/abort-history';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'historical-abort-presentation','versions':{},'limits':[
        'Static historical pair, not measured presentation duration or all abort routes.',
        'No proof of original500ms duration; no target instructions, API calls or rendering.',
        'Direct E8 sites are bounded candidates; indirect callers and callbacks remain outside this scan.']}
    images={}
    for version,(relative,archive_hash,exe_hash) in specs.items():
        archive=ROOT/relative;assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_hash
        binary=capture/f'nfs3-{version}.exe';binary.write_bytes(raw)
        pe=pefile.PE(data=raw);images[version]=pe
        assert calls(pe,0x494bd0)==([0x4a33eb] if version=='1.5.3' else [0x4a3532])
        assert any(i.name==b'SleepEx' and i.address==0x534604 for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports)
        spans=[(0x494bd0,0x494c5a),(0x4df8e0,0x4df8ef)]
        spans += ([(0x4a33d0,0x4a33fb),(0x4a3542,0x4a356a)] if version=='1.5.3'
                  else [(0x4a33d0,0x4a33f0),(0x4a3514,0x4a354b)])
        rows=[]
        for start,end in spans:
            output=capture/f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'bytes_sha256':sha(pe.get_data(start-0x400000,end-start)),
                'assembly':str(output.relative_to(ROOT)),'assembly_sha256':sha(output.read_bytes())})
        result['versions'][version]={'archive':relative,'archive_sha256':archive_hash,'executable_sha256':exe_hash,
            'overlay_call_candidates':[f'{v:08x}' for v in calls(pe,0x494bd0)],'spans':rows}
    a,b=images.values()
    assert a.get_data(0x93bd0,138)==b.get_data(0x93bd0,138)
    assert a.get_data(0xdf8e0,15)==b.get_data(0xdf8e0,15)
    assert b.get_data(0xa3532,18).hex()=='e89916ffffb8c8000000e89fc3030031c040'
    result['retained_overlay_bytes']=138
    result['retained_wait_adapter_bytes']=15
    result['new_wait_request']={'milliseconds':200,'alertable':True,'call':'004a353c','api':'SleepEx'}
    relative,expected,_=SPECS['original']
    raw=(ROOT/relative).read_bytes();assert sha(raw)==expected
    original=pefile.PE(data=raw)
    poller=original.get_data(0xa33d0,43)
    assert poller==a.get_data(0xa33d0,43)
    output=capture/'original-004a33d0.asm'
    output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
        '--start-address=0x4a33d0','--stop-address=0x4a33fb',relative],cwd=ROOT))
    result['original_poller']={'executable':relative,'sha256':expected,'start':'004a33d0',
        'end_exclusive':'004a33fb','bytes_sha256':sha(poller),'identical_to_153':True,
        'assembly':str(output.relative_to(ROOT)),'assembly_sha256':sha(output.read_bytes()),
        'timing_limit':'No direct fixed-delay call in this complete poller; transitive renderer/cleanup timing and claimed500ms remain unverified.'}
    (ROOT/'analysis/evidence/audits/abort-presentation-153-160.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: overlay unchanged; historical draw moves from poller to loading exit with200ms alertable wait')


if __name__=='__main__':main()
