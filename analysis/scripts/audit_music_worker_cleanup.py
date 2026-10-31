"""Static music shutdown cleanup-call replacement and imported API witnesses."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'music-worker-cleanup-call-replacement','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/music-worker-cleanup'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x4e4a30,0x4e4b41),(0x4df870,0x4df894),(0x4dfc00,0x4dfc0d),(0x4dfb20,0x4dfb3d)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        expected_imports={0x534608:'TerminateThread',0x534488:'CloseHandle',0x5345e8:'SetEvent'}
        for address,name in expected_imports.items():assert imports[address]==name
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'imports':{f'{a:08x}':n for a,n in expected_imports.items()}}
    old,new=blobs['original'],blobs['official_modern']
    assert old[1:]==new[1:]
    assert old[0][:0xf8]==new[0][:0xf8] and old[0][0x105:]==new[0][0x105:]
    assert old[0][0xf8:0x105]==bytes.fromhex('8d818c00000031f6e83badffff')
    assert new[0][0xf8:0x105]==bytes.fromhex('8b818c000000e8cdb0ffff31f6')
    result['changed_bytes']=sum(a!=b for a,b in zip(old[0],new[0]))
    assert result['changed_bytes']==8
    result['limits']=['No audio/thread execution, scheduling observation or shutdown race test.',
        'Worker identity, prior wait-helper contract and record lifetime remain separate investigations.']
    (ROOT/'analysis/evidence/audits/music-worker-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 273-byte shutdown body; eight changed bytes; identical API wrappers and imports')


if __name__=='__main__':main()
