"""Static geometry-color admission comparison; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'geometry-color-admission-comparison','end_convention':'exclusive','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/geometry-color-admission';capture.mkdir(parents=True,exist_ok=True)
    images=[]
    spans=[(0x4ba350,0x4ba808),(0x4baaaa,0x4baab8),(0x4babd9,0x4babe7),(0x4bae7c,0x4bae8a),(0x4bb27a,0x4bb288)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images.append(pe);rows=[]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=images;start,end=0x4ba350,0x4ba808
    a,b=[pe.get_data(start-0x400000,end-start) for pe in images]
    changes=[start+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert all(0x4ba382<=v<0x4ba3af for v in changes)
    assert old.get_data(0xba3af,0x459)==new.get_data(0xba3af,0x459)
    assert old.get_data(0xba38f,5)==bytes.fromhex('83fb017507')
    assert new.get_data(0xba38d,14)==bytes.fromhex('8339017509833dd8d16f00007509')
    for site in (0x4baab3,0x4babe2,0x4bae85,0x4bb283):
        for pe in images:
            data=pe.get_data(site-0x400000,5);assert data[0]==0xe8
            assert site+5+int.from_bytes(data[1:],'little',signed=True)==start
    result['changed_addresses']=[f'{v:08x}' for v in changes]
    result['identical_tail']={'start':'004ba3af','end_exclusive':'004ba808','length':0x459,'sha256':hashlib.sha256(old.get_data(0xba3af,0x459)).hexdigest()}
    result['limits']=['Saved analysis label is not a complete data/algorithm contract.','Context first-DWORD producer and complete geometry/global meaning remain unresolved.','No rendering, game or instruction probes.']
    (ROOT/'analysis/evidence/audits/original-modern-geometry-color-admission.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {end-start}-byte envelope; {len(changes)} changed bytes confined to admission/prologue region')


if __name__=='__main__':main()
