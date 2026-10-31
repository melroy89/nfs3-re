"""Paired dialog dispatch, Tab normalization and sound request evidence."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-dialog-input-comparison','range_end':'exclusive','binaries':{}};images={}
    capture=ROOT/'analysis/captures/modern-differences/dialog-input';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=[(0x445e60,0x445efa),(0x444910,0x4449c6)]
        if label=='official_modern':spans.append((0x4f1fcc,0x4f1ff0))
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        table=struct.unpack('<4I',pe.get_data(0x45e48,16))
        assert table==((0x445ea1,0x445eab,0x445eb5,0x445ebf) if label=='original' else (0x444910,0x444b20,0x444f50,0x445520))
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'dispatch_table':[f'{x:08x}' for x in table]}
    for start,end in [(0x445e60,0x445e9a),(0x445ec7,0x445efa)]:
        a,b=[p.get_data(start-0x400000,end-start) for p in images.values()];assert a==b
    old,new=[images[k] for k in ('original','official_modern')]
    a,b=[p.get_data(0x44910,0xb6) for p in (old,new)]
    changed=[0x444910+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert changed==[0x44496c,0x44496d,0x44498e,0x44498f]
    result['first_handler_changed_addresses']=[f'{x:08x}' for x in changed]
    for address in (0x44496b,0x44498d):
        for pe,target in ((old,0x444570),(new,0x43eb88)):
            data=pe.get_data(address-0x400000,5);assert data[0]==0xe8
            assert address+5+int.from_bytes(data[1:],'little',signed=True)==target
    pe=images['official_modern'];imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address==0x534738};assert imports=={0x534738:'GetAsyncKeyState'}
    result['modern_key_import']={'00534738':'GetAsyncKeyState'}
    result['limits']=['Static only; no dialog, key event or audio execution.','Handler return3 semantic identity and complete handler behavior remain unresolved.']
    (ROOT/'analysis/evidence/audits/original-modern-dialog-input.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: dialog counterparts, dispatch tables, retained tail and Shift query helper')


if __name__=='__main__':main()
