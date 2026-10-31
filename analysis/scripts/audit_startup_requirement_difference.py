"""Static paired startup requirement checks; no memory/display API execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/startup-requirements';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-startup-requirement-comparison','range_end':'exclusive','binaries':{}}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=([(0x4b5f10,0x4b5fee),(0x4b608b,0x4b6097)] if label=='original' else [(0x4b5748,0x4b57c1),(0x4b570c,0x4b5746),(0x4b5c07,0x4b5c11)])
        spans += [(0x4516a0,0x4516fa if label=='original' else 0x4516f4),(0x4f07d0,0x4f083e)]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        imports=[{'iat':f'{i.address:08x}','name':i.name.decode(),'dll':d.dll.decode()} for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address in (0x534580,0x534740,0x534754,0x534458,0x534764,0x534500,0x534514)]
        item={'path':relative,'sha256':expected,'spans':rows,'imports':imports}
        if label=='official_modern':item['messages']={f'{a:08x}':pe.get_data(a-0x400000,240).split(b'\0')[0].decode() for a in (0x53d27a,0x53d29a,0x53d202)}
        result['binaries'][label]=item
    data=images['original'].get_data(0xf07d0,0x6e);assert data==images['official_modern'].get_data(0xf07d0,0x6e)
    result['identical_disk_geometry_wrapper']={'start':'004f07d0','end':'004f083e','sha256':hashlib.sha256(data).hexdigest()}
    result['limits']=['No memory, disk, desktop, dialog or target API execution.','Memory fields described by exact offsets; no complete API structure/type reconstruction.','Current-directory helper, API failures and diagnostic termination internals are not fully audited here.','No release-note attribution inferred solely from a changed startup routine.']
    (ROOT/'analysis/evidence/audits/original-modern-startup-requirements.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: startup requirement counterparts, caller witnesses, imports and messages')


if __name__=='__main__':main()
