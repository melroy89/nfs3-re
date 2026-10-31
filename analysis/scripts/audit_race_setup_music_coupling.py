"""Static removal of tune-selector-derived global assignment in setup reconciliation."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'race-setup-tune-selector-coupling','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/race-setup-music-coupling'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);data=pe.get_data(0x4be60,0x46e);blobs[label]=data
        path=capture/f'{label}-0044be60.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x44be60','--stop-address=0x44c2ce',relative],cwd=ROOT))
        result['binaries'][label]={'path':relative,'sha256':expected,'start':'0044be60',
            'end_exclusive':'0044c2ce','span_sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))}
    old,new=blobs['original'],blobs['official_modern']
    assert old[:0x44]==new[:0x44] and old[0x61:]==new[0x61:]
    assert old[0x44:0x61]==bytes.fromhex('833de4bb6f00007507b801000000eb0231c08b3d00bc6f00a3d8bb6f00')
    assert new[0x44:0x61]==bytes.fromhex('8b3d00bc6f00eb15')+b'\x90'*21
    result['changed_bytes']=sum(a!=b for a,b in zip(old,new))
    result['limits']=['Static assignment/control-flow comparison only; no music/menu execution.',
        'Destination global meaning and complete writer/consumer lifetime remain unverified.']
    (ROOT/'analysis/evidence/audits/race-setup-music-coupling.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 1134-byte envelope; only tune-selector-derived global assignment removed')


if __name__=='__main__':main()
