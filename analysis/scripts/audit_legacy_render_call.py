"""Static removed no-op call and distinct Modern fog-gated state helper."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'legacy-render-noop-and-fog-helper','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/legacy-render-call'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x4c6f00,0x4c70eb),(0x431c20,0x431c25),(0x431c34,0x431c4d)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][:0xbc]==new[0][:0xbc] and old[0][0xc8:]==new[0][0xc8:]
    assert old[0][0xbc:0xc8]==bytes.fromhex('ba0500000089f8e858acf6ff')
    assert new[0][0xbc:0xc8]==bytes.fromhex('eb0a')+b'\x90'*10
    assert old[1]==bytes.fromhex('5589e55dc3')
    assert new[2]==bytes.fromhex('833d543a7a0000740fb815000000ba04000000e8b4fcffffc3')
    result['limits']=['No rendering or instruction execution; incidental register/flag dependencies unverified.',
        'Modern helper is not asserted to replace original no-op; original same-address counterpart unresolved.']
    (ROOT/'analysis/evidence/audits/legacy-render-call.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 491-byte batch envelope, original five-byte no-op and separate 25-byte Modern helper')


if __name__=='__main__':main()
