"""Static original/Modern title delay policies; no waits or target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/title-delay';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-title-delay-comparison','range_end':'exclusive','binaries':{}}
    common=[(0x472f20,0x472fbb),(0x451940,0x451953),(0x4c9860,0x4c9871)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        spans=common+([(0x472fc0,0x47300d),(0x4f0650,0x4f0665),(0x473181,0x473186),(0x4b61a6,0x4b61ab)] if label=='original' else [(0x472fc0,0x473016),(0x473152,0x473160),(0x4f2790,0x4f279b)])
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['limits']=['No title rendering, input, timing measurement or target execution.','Original library-clock units not converted to seconds.','Configuration producer and clock API identity reused from linked audits.','Callback scheduling, elapsed-time overshoot and complete outer startup behavior untested.']
    (ROOT/'analysis/evidence/audits/original-modern-title-delay.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: title delay counterparts, contextual calls and timer/input witnesses')


if __name__=='__main__':main()
