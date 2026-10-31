"""Static event notification change in the async-read wait path."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'async-read-wait-notification','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/async-wait'
    capture.mkdir(parents=True,exist_ok=True)
    blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x5345e8]=='SetEvent' and imports[0x534604]=='SleepEx'
        for start,end in [(0x4f0cd0,0x4f0d1c),(0x4dfb20,0x4dfb3d),(0x4ff780,0x4ff7a3),(0x4df8e0,0x4df8ef)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'imports':{'005345e8':'SetEvent','00534604':'SleepEx'}}
    old,new=blobs['original'],blobs['official_modern']
    assert old[1:]==new[1:]
    assert old[0][:0x20]==new[0][:0x20] and old[0][0x2c:]==new[0][0x2c:]
    assert old[0][0x20:0x2c]==bytes.fromhex('8b12b8e40b9f00e824eefeff')
    assert new[0][0x20:0x2c]==bytes.fromhex('8b02e839eefeffe884ea0000')
    result['changed_bytes']=sum(a!=b for a,b in zip(old[0],new[0]))
    assert result['changed_bytes']==10
    result['limits']=['No event/thread execution or race test.',
        'Event handle lifetime, flag consumers, all state writers and scheduling remain unverified.']
    (ROOT/'analysis/evidence/audits/async-wait-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 76-byte caller and three identical supporting wrappers; SetEvent/SleepEx imports verified')


if __name__=='__main__':main()
