"""Static paired renderer state14 setter comparison."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-render-state14-comparison','range_end':'exclusive','binaries':{}};images={}
    capture=ROOT/'analysis/captures/modern-differences/state14';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in [(0x431900,0x431a99),(0x470ad0,0x470b1e if label=='original' else 0x470afa),(0x470b20,0x470b6a),(0x470b90,0x470bb8)]:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['identical_ranges']=[]
    for start,end in [(0x431900,0x431a99),(0x470b20,0x470b6a),(0x470b90,0x470bb8)]:
        a,b=[p.get_data(start-0x400000,end-start) for p in images.values()];assert a==b
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(a).hexdigest()})
    result['limits']=['Static only; no driver invocation or visual result.','State14 semantics and complete enable-global lifecycle unresolved.']
    (ROOT/'analysis/evidence/audits/original-modern-state14.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: state14 setter counterparts, retained scaled helper and reset routine')


if __name__=='__main__':main()
