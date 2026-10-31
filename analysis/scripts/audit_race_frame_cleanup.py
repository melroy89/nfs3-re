"""Static race-frame snapshot insertion and dialog-clear wrapper bypass."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'race-frame-cleanup-call-edges','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/race-frame-cleanup'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x4bc650,0x4bc65f if label=='original' else 0x4bc664),(0x4bc670,0x4bc67f),
                          (0x4b7c20,0x4b7c2f),(0x44be20,0x44be34),(0x445f10,0x445f33)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][:13]==new[0][:13] and old[0][13:]==new[0][18:]==bytes.fromhex('5dc3')
    assert new[0][13:18]==bytes.fromhex('e8beb5ffff')
    assert old[1]==bytes.fromhex('5589e5e8a8f7f8ffe8b3feffff5dc3')
    assert new[1]==bytes.fromhex('5589e5e89898f8ffe8b3feffff5dc3')
    assert old[2]==new[2] and old[4]==new[4]
    assert old[2][3:13]==bytes.fromhex('a184367d00a328fe5500')
    assert old[3][4:17]==bytes.fromhex('31d2891534925500e8dfa0ffff')
    assert new[3]==b'\x90'*20
    result['limits']=['Static local call edges and stores only; no frame, dialog or tick execution.',
        'All caller cadence, shared-state lifetime and incidental register effects remain unverified.']
    (ROOT/'analysis/evidence/audits/race-frame-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: expanded frame finalizer, direct dialog clear and exact snapshot/wrapper stores')


if __name__=='__main__':main()
