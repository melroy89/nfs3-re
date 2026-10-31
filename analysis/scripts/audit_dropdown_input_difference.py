"""Static dropdown input envelope and shared-tail comparison."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    images={}
    result={'kind':'static-dropdown-input-comparison','range_end':'exclusive','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/dropdown-input';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in [(0x463ff0,0x46455d),(0x4640e2,0x4640f6),(0x464158,0x46417b),(0x464294,0x4642f3),(0x464553,0x46455d)]:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=[images[k] for k in ('original','official_modern')]
    regions=[(0x46401f,0x464024),(0x464073,0x464078),(0x46407c,0x464087),(0x4640ed,0x4640f6),(0x464163,0x46417b),(0x464209,0x464212),(0x464258,0x46425e),(0x464294,0x4642f3),(0x464553,0x46455d)]
    a,b=[p.get_data(0x63ff0,0x56d) for p in (old,new)]
    changed=[0x463ff0+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert all(any(start<=address<end for start,end in regions) for address in changed)
    result['changed_addresses']=[f'{address:08x}' for address in changed]
    result['changed_region_envelopes']=[{'start':f'{start:08x}','end':f'{end:08x}'} for start,end in regions]
    assert old.get_data(0x6417b,0x8e)==new.get_data(0x6417b,0x8e)
    result['identical_open_positioning']={'start':'0046417b','end':'00464209','sha256':hashlib.sha256(old.get_data(0x6417b,0x8e)).hexdigest()}
    result['limits']=['Full span is a containing envelope, not a claim that every byte is a function instruction.','Shared sound tail and paired routes inspected; complete action semantics unresolved.','No key events, target instructions or audio execution.']
    (ROOT/'analysis/evidence/audits/original-modern-dropdown-input.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: dropdown input baseline-bound envelope and shared-tail witnesses retained')


if __name__=='__main__':main()
