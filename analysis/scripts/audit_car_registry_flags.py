"""Static removed manufacturer-specific flag assignment and copy-source getter."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'car-registry-manufacturer-flags','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/car-registry-flags'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x439d90,0x43a4c2),(0x43ba20,0x43ba2a),(0x439af0,0x439b14),(0x4396e0,0x4396f3),(0x439a50,0x439aa5),(0x43a4f0,0x43a579)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        strings={f'{a:08x}':pe.get_data(a-0x400000,40).split(b'\0')[0].decode() for a in (0x5376f0,0x5376f8,0x537720)}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'strings':strings}
    old,new=blobs['original'],blobs['official_modern']
    lo,hi=0x43a20e-0x439d90,0x43a25c-0x439d90
    assert old[0][:lo]==new[0][:lo] and old[0][hi:]==new[0][hi:]
    assert new[0][lo:hi]==bytes.fromhex('eb4c')+b'\x90'*76
    for a in (0x43a22e,0x43a255):assert old[0][a-0x439d90:a-0x439d90+7]==bytes.fromhex('80888003000020')
    assert old[1]==bytes.fromhex('5589e5b8207753005dc3')
    assert new[1]==bytes.fromhex('5589e5b8342c7a005dc3')
    assert old[2:]==new[2:]
    assert old[3][8:17]==bytes.fromhex('8b808003000083e020')
    assert old[5][6:15]==bytes.fromhex('833db8d36f00037509')
    assert old[5][20:24]==bytes.fromhex('85c0750b')
    result['limits']=['Static manufacturer flag assignment and getter only; no car selection or pursuit execution.',
        'Complete eligibility caller coverage, path-buffer initialization and manufacturer metadata admission remain partially qualified.']
    (ROOT/'analysis/evidence/audits/car-registry-flags.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: registry removal and getter; identical flag accessor, resolver and mode-3 eligibility body')


if __name__=='__main__':main()
