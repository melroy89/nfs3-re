"""Static texture descriptor cache, removed query and progress caller witnesses."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'texture-loading-followup','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/texture-loading-followup'
    capture.mkdir(parents=True,exist_ok=True)
    blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x49c5c0,0x49c5f9),(0x4d3f50,0x4d4075),(0x4d5370,0x4d56a3)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][5:11]==bytes.fromhex('ff1580f99e00')
    assert new[0][5:11]==bytes.fromhex('90a15c3a7a00')
    assert old[0][:5]==new[0][:5] and old[0][11:]==new[0][11:]
    assert old[1][0x13:0x1b]==bytes.fromhex('ff1580f99e0085c0')
    assert new[1][0x13:0x1b]==bytes.fromhex('eb06909090909090')
    assert old[1][:0x13]==new[1][:0x13] and old[1][0x1b:]==new[1][0x1b:]
    offsets=[0x37,0x15d,0x260,0x276]
    for i,offset in enumerate(offsets):
        assert old[2][offset-1]==new[2][offset-1]==0x68
        assert struct.unpack('<f',old[2][offset:offset+4])[0]==36+i
        assert struct.unpack('<f',new[2][offset:offset+4])[0]==10.5+0.5*i
    assert [i for i,(a,b) in enumerate(zip(old[2],new[2])) if a!=b]==[j for o in offsets for j in (o+2,o+3)]
    result['limits']=['No texture allocation, renderer query or loading display execution.',
        'Cached descriptor lifetime, query side effects and visible timing remain separate.']
    (ROOT/'analysis/evidence/audits/texture-loading-followup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 57/293/819-byte envelopes; descriptor query changes and four progress immediates')


if __name__=='__main__':main()
