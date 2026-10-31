"""Static config load/header comparison; no target/file API execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS={'original':[(0x472980,0x472b60),(0x4728e0,0x47297d)],
       'official_modern':[(0x472980,0x472b48),(0x472230,0x472248),
                          (0x4723f0,0x472402)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/config-loading'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-config-loading-comparison','range_end':'exclusive','binaries':{},
        'limits':['No config, game or instruction execution.','Header acceptance is not complete serialized-field validation.']}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in SPANS[label]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'file_backed_header_hex':pe.get_data(0x55e8a0-0x400000,12).hex(),
            'format_string':pe.get_data(0x53b00c-0x400000,30).split(b'\0')[0].decode('ascii'),
            'relevant_imports':{f'{i.address:08x}':i.name.decode()
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                if i.name and i.name in [b'CompareFileTime',b'GetFileTime',b'_lopen',b'_lclose',b'GetModuleFileNameA']}}
    (ROOT/'analysis/evidence/audits/original-modern-config-loading.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: config baselines, header bytes, import identities and load spans')


if __name__=='__main__':main()
