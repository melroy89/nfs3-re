"""Static complete indexed-slider geometry initializer comparison."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'indexed-slider-geometry-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/indexed-slider-geometry'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);data=pe.get_data(0x6c820,141);blobs[label]=data
        path=capture/f'{label}-0046c820.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x46c820','--stop-address=0x46c8ad',relative],cwd=ROOT))
        result['binaries'][label]={'path':relative,'sha256':expected,'start':'0046c820',
            'end_exclusive':'0046c8ad','span_sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))}
    old,new=blobs['original'],blobs['official_modern']
    assert old[:15]==new[:15] and old[0x39:]==new[0x39:]
    assert old[15:21]==bytes.fromhex('8b483ec1f910')
    assert new[15:19]==bytes.fromhex('0fb74840')
    assert old[0x20:0x26]==bytes.fromhex('81c394000000')
    assert new[0x1b:0x20]==bytes.fromhex('6681c39700')
    assert new[0x30:0x39]==bytes.fromhex('eb0790909090909090')
    result['changed_bytes']=sum(a!=b for a,b in zip(old,new))
    result['limits']=['Static code only; no layout rendering, malformed-index test or target execution.',
        'Table bounds, caller row domain and widget field meanings remain partially qualified.']
    (ROOT/'analysis/evidence/audits/indexed-slider-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: complete 141-byte envelope; {result["changed_bytes"]} changes confined to geometry block; 84-byte suffix identical')


if __name__=='__main__':main()
