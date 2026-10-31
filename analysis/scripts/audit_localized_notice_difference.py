"""Pair localized notice wrappers through a changed caller, statically."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'localized-notice-wrapper-comparison','binaries':{}};images=[]
    capture=ROOT/'analysis/captures/modern-differences/localized-notice';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images.append(pe);rows=[]
        spans=[(0x444a80,0x444b1d),(0x43fdd0,0x43fe0e),((0x444be0 if label=='original' else 0x43fda0),(0x444c0d if label=='original' else 0x43fdcc))]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start);out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest(),'assembly':str(out.relative_to(ROOT))})
        data=pe.get_data(0x3fe09,5);assert data[0]==0xe8
        assert 0x43fe0e+int.from_bytes(data[1:],'little',signed=True)==(0x444be0 if label=='original' else 0x43fda0)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=images
    assert old.get_data(0x44a80,0x9d)==new.get_data(0x44a80,0x9d)
    a,b=[p.get_data(0x3fdd0,0x3e) for p in images]
    changes=[0x43fdd0+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert all(0x43fe0a<=v<0x43fe0e for v in changes)
    assert old.get_data(0x44bf2,5)==bytes.fromhex('bb26020000')
    assert new.get_data(0x3fdb9,7)==bytes.fromhex('31c05089c389c1')
    result['correspondence']={'caller':'0043fe09','original':'00444be0','modern':'0043fda0','caller_changes':[f'{v:08x}' for v in changes],'constructor':'00444a80, complete157-byte body identical','original_lines':1,'modern_lines':2,'original_EBX':0x226,'modern_EBX':0,'shared_pointer_array':'00661090','added_localized_id':11}
    result['limits']=['No dialog, timing, localization or target execution.','Caller retarget establishes counterpart; same-address bytes do not.','Visible text and timeout/event-loop semantics not independently validated here.']
    (ROOT/'analysis/evidence/audits/localized-notice-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: moved wrapper correspondence, retained constructor and caller-only retarget')


if __name__=='__main__':main()
