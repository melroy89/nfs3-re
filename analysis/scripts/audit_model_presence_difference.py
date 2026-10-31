"""Static model-key presence predicate correspondence."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-model-presence-comparison','range_end':'exclusive','binaries':{}};images={}
    capture=ROOT/'analysis/captures/modern-differences/model-presence';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=[(0x438ad0,0x438aed),(0x439990,0x4399e4),(0x427142,0x427147)]
        spans += [(0x439ce0,0x439d12)] if label=='original' else [(0x439cd4,0x439cfd),(0x439d00,0x439d19)]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        data=pe.get_data(0x27142,5);assert data[0]==0xe8
        target=0x427147+int.from_bytes(data[1:],'little',signed=True)
        assert target==(0x439ce0 if label=='original' else 0x439d00)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'paired_caller_target':f'{target:08x}'}
    for start,end in [(0x438ad0,0x438aed),(0x439990,0x4399e4)]:
        a,b=[p.get_data(start-0x400000,end-start) for p in images.values()];assert a==b
    result['limits']=['No resource lookup or target instruction execution.','Selectors 0x25/0x26 are raw values; human-readable identities and list initialization remain unresolved.']
    (ROOT/'analysis/evidence/audits/original-modern-model-presence.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired presence policy, shared caller and identical key construction/search bodies')


if __name__=='__main__':main()
