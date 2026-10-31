"""Static raster session registration removal and inactive shutdown branch."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x524650,0x524693),(0x5246a0,0x5247ab),(0x524620,0x524635),
       (0x524640,0x524650),(0x5247ab,0x5247b1)]


def main():
    result={'kind':'raster-session-cleanup-registration','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/raster-session'
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
    assert old[0][:11]==new[0][:11] and old[0][17:]==new[0][17:]
    assert old[0][11:17]==bytes.fromhex('0f844a010000')
    assert new[0][11:17]==bytes.fromhex('743290909090')
    assert old[4]==bytes.fromhex('0f84defeffff') and new[4]==b'\x90'*6
    assert old[1][:0xad]==new[1][:0xad] and old[1][0xe7:]==new[1][0xe7:]
    assert new[1][0xad:0xbb]==bytes.fromhex('31c0b001a2f0af56005e5a595bc3')
    assert new[1][0xbb:0xe7]==b'\x90'*44
    for i in (2,3):assert new[i]==b'\x90'*len(new[i])
    result['limits']=['Static branch/registration witnesses only; no renderer or process-exit execution.',
        'Cleanup registration helper semantics, replacement ownership and callback lifetime remain unverified.']
    (ROOT/'analysis/evidence/audits/raster-session-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 67/267-byte session envelopes, removed callbacks and original shared shutdown tail')


if __name__=='__main__':main()
