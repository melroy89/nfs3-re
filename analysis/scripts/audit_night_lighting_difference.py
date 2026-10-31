"""Static paired night-lighting admission and retained execution body."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/night-lighting';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-night-lighting-comparison','range_end':'exclusive','binaries':{}};images={}
    spans=[(0x41c670,0x41c9e4),(0x4bbde0,0x4bbe3a),(0x41d04e,0x41d06d)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['identical_ranges']=[]
    for start,end in [(0x41c670,0x41c684),(0x41c6cc,0x41c9e4),(0x4bbde0,0x4bbe3a),(0x41d04e,0x41d06d)]:
        data=images['original'].get_data(start-0x400000,end-start);assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest()})
    result['limits']=['No graphics, night race or instruction execution.','Context type1 and option global not assigned mirror/quality names without producer evidence.','Identical body does not establish transitive numeric, allocation or rendered equivalence.']
    (ROOT/'analysis/evidence/audits/original-modern-night-lighting.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: night-lighting counterparts, bounded gate delta, retained body and arena helper')


if __name__=='__main__':main()
