"""Static dropdown input envelope and shared-tail comparison."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-dropdown-input-comparison','range_end':'exclusive','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/dropdown-input';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in [(0x463ff0,0x46455d),(0x4640e2,0x4640f6),(0x464158,0x46417b),(0x464294,0x4642f3)]:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['limits']=['Full span is a containing envelope, not a claim that every byte is a function instruction.','Shared sound tail and paired routes inspected; complete action semantics unresolved.','No key events, target instructions or audio execution.']
    (ROOT/'analysis/evidence/audits/original-modern-dropdown-input.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: dropdown input baseline-bound envelope and shared-tail witnesses retained')


if __name__=='__main__':main()
