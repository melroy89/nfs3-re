"""Static pending-overlay and coordinate producer witnesses; no execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind':'static-pending-overlay-comparison','range_end':'exclusive','binaries':{},
              'limits':['Producer spans are selected witnesses, not complete containing functions.','No rendering or target execution.']}
    capture = ROOT/'analysis/captures/modern-differences/pending-overlay';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        spans=[(0x494bd0,0x494ca6),(0x494f42,0x494f79)] if label=='original' else [(0x494bd0,0x494c5a),(0x494ec0,0x494f12)]
        if label == 'official_modern': spans += [(0x494cde,0x494cf2),(0x4a3500,0x4a3544)]
        spans += [(0x4df8e0,0x4df8ef)]
        rows=[]
        for start,end in spans:
            p=capture/f'{label}-{start:08x}.asm';p.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(p.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        wait=pe.get_data(0x4df8e0-0x400000,15)
        assert wait==bytes.fromhex('51526a01502eff15044653005a59c3')
        imports={i.address:(d.dll.decode(),i.name.decode()) for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534604][1]=='SleepEx'
        if label=='official_modern':
            assert pe.get_data(0x4a3537-0x400000,10)==bytes.fromhex('b8c8000000e89fc30300')
        result.setdefault('wait_adapter',{})[label]={'start':'004df8e0','end_exclusive':'004df8ef',
            'hex':wait.hex(),'iat':'00534604','dll':imports[0x534604][0],
            'function':imports[0x534604][1],'arguments':'incoming EAX, alertable TRUE (1)',
            'limits':'No local elapsed-time retry; actual delay and APC/completion activity unobserved.'}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'format_0053bdc8':pe.get_data(0x13bdc8,30).split(b'\0')[0].decode('ascii')}
    (ROOT/'analysis/evidence/audits/original-modern-pending-overlay.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baseline hashes, complete overlay bodies, producer witnesses and formats')


if __name__=='__main__':main()
