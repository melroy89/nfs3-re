"""Static paired reference-dimension reads in three complete HUD functions."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x484b70,0x484c10),(0x48ae70,0x48b29f),(0x48d110,0x48d4b3)]


def main():
    result={'kind':'hud-reference-dimension-consumers','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/hud-reference-consumers'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in SPANS:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    expected=[(0x484b70,[0xb,0xc,0xd]),(0x48ae70,[0x19,0x1a,0x1b,0x32,0x33,0x34,0x5b,0x5d,0x5e,0x5f]),(0x48d110,[0x2fc,0x2fd,0x2fe])]
    for i,(start,changes) in enumerate(expected):
        assert [j for j,(a,b) in enumerate(zip(old[i],new[i])) if a!=b]==changes
    assert old[0][0xa:0xf]==b'\xa1'+struct.pack('<I',0x7cdac8)
    assert new[0][0xa:0xf]==b'\xa1'+struct.pack('<I',0x7a2748)
    for index,offset in [(1,0x17),(1,0x30),(2,0x2fa)]:
        assert old[index][offset:offset+6]==bytes.fromhex('db05c8da7c00')
        assert new[index][offset:offset+6]==bytes.fromhex('db0548277a00')
    assert old[1][0x5b:0x61]==bytes.fromhex('d905bcd65500')
    assert new[1][0x5b:0x61]==bytes.fromhex('db054c277a00')
    result['limits']=['Static dimension-source and FLD/FILD changes only; no HUD pixel comparison.',
        'Other globals, callers, aliasing and x87 state remain separate contracts.']
    (ROOT/'analysis/evidence/audits/hud-reference-consumers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 160/1071/931-byte bodies; four width reads and one typed height read')


if __name__=='__main__':main()
