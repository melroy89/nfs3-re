"""Paired cursor positioning and new validity-gated sound wrappers; static only."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/cursor-position';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-cursor-position-comparison','range_end':'exclusive','binaries':{}};images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=[(0x444570,0x4445ce),(0x445160,0x4451c2 if label=='original' else 0x4451c1),(0x49bfc0,0x49bff7)]
        if label=='official_modern':spans += [(0x43eb88,0x43eb9d),(0x43eba0,0x43ebb5)]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        calls=[]
        for address in (0x4455a1,0x4455cb,0x4455fd,0x445627):
            data=pe.get_data(address-0x400000,5);assert data[0]==0xe8
            calls.append({'address':f'{address:08x}','target':f'{address+5+int.from_bytes(data[1:],"little",signed=True):08x}','bytes':data.hex()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'navigation_call_witnesses':calls}
    raw=images['original'].get_data(0x9bfc0,0x37);assert raw==images['official_modern'].get_data(0x9bfc0,0x37)
    result['identical_cursor_bridge']={'start':'0049bfc0','end':'0049bff7','sha256':hashlib.sha256(raw).hexdigest()}
    result['limits']=['No cursor, sound, input or target execution.','Call witnesses are five-byte direct calls, not complete outer navigation routines.','No catalog-specific replay keyboard fix or uniform original return inferred.']
    (ROOT/'analysis/evidence/audits/original-modern-cursor-position.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired positioning bodies, identical bridge and new wrapper call witnesses')


if __name__=='__main__':main()
