"""Static CWD, INI selection and startup directory-table witnesses."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS={'original':[(0x4a38f0,0x4a39d2),(0x4e3340,0x4e33a0),(0x4f0260,0x4f027b),
           (0x4475a0,0x4477fd),(0x4a3d4a,0x4a3f7d),(0x4fce30,0x4fce35)],
       'official_modern':[(0x4a38f0,0x4a3938),(0x4a3984,0x4a39c6),
           (0x4a3e24,0x4a3e7e),(0x4a6e10,0x4a6f2e),(0x4f915e,0x4f916a),
           (0x4f916c,0x4f9187),(0x4f91ec,0x4f9229)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/startup-paths'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-startup-path-comparison','range_end':'exclusive',
        'binaries':{},'limits':['No working-directory/API/file changes or target execution.',
            'Original same-VA function is unrelated; no semantic match inferred.',
            'Path table strings are initialization defaults; runtime locale/config changes can alter slots.']}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data);rows=[]
        for start,end in SPANS[label]:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        row={'path':relative,'sha256':expected,'spans':rows}
        row['static_imports']={f'{i.address:08x}':i.name.decode()
            for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
            if i.address in (0x534544,0x5345d4,0x534520,0x534490)}
        if label=='official_modern':
            strings=pe.get_data(0x13f42c,1024).split(b'\0')[:22]
            assert len(strings)==22 and all(strings)
            row['default_path_slots']=[{'slot':i,'destination_va':f'{0x7a27b4+128*i:08x}',
                'value':s.decode('ascii')} for i,s in enumerate(strings)]
            tables={}
            for start,name in [(0x4a3938,'required_existing'),(0x4a3970,'create_if_absent')]:
                entries=[]
                for i in range(20):
                    a=struct.unpack('<I',pe.get_data(start-0x400000+4*i,4))[0]
                    if not a:break
                    delta=a-0x7a27b4;assert delta>=0 and delta%128==0 and delta//128<22
                    entries.append({'destination_va':f'{a:08x}','default_path':strings[delta//128].decode('ascii')})
                else:raise AssertionError('No table terminator')
                tables[name]=entries
            assert len(tables['required_existing'])==13 and len(tables['create_if_absent'])==4
            row['directory_tables']=tables
            row['ini_fallback']=pe.get_data(0x13f5d4,32).split(b'\0')[0].decode('ascii')
        result['binaries'][label]=row
    output=ROOT/'analysis/evidence/audits/original-modern-startup-paths.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: identities, startup/API spans, 22 initialized path slots and 13/4 directory tables')


if __name__=='__main__':main()
