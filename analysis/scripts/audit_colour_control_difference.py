"""Paired frontend colour mouse-control dispatch; no UI/audio execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/colour-control';capture.mkdir(parents=True,exist_ok=True)
    common=[(0x43e8e0,0x43eacb),(0x43e7a0,0x43e8df),(0x43dd90,0x43ddc1),(0x43dc90,0x43dd50),(0x43ddd0,0x43de19)]
    result={'kind':'static-colour-control-comparison','range_end':'exclusive','binaries':{}};images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        end=0x43ebb8 if label=='original' else 0x43eb85
        for start,stop in [(0x43ead0,end)]+common:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={stop}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{stop:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,stop-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['identical_ranges']=[]
    for start,end in common+[(0x43ead0,0x43eb1c)]:
        data=images['original'].get_data(start-0x400000,end-start);assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest()})
    result['limits']=['No UI, audio or instruction execution.','No padding or universal sound-consistency conclusion from this handler.','Original full body extends beyond Modern function range; same-VA changed-byte count is not a whole-function semantic comparison.']
    (ROOT/'analysis/evidence/audits/original-modern-colour-control.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: full colour handler counterparts, shared prefix and five identical helpers')


if __name__=='__main__':main()
