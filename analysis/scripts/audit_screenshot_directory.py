"""Retain Modern screenshot-directory admission and enumeration evidence."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    relative,expected,_=SPECS['official_modern']
    raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
    pe=pefile.PE(data=raw)
    capture=ROOT/'analysis/captures/modern-differences/screenshot-directory';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-modern-screenshot-directory','path':relative,'sha256':expected,'range_end':'exclusive','spans':[]}
    for start,end in [(0x4c44e8,0x4c452c),(0x4f9184,0x4f91e9),(0x4f93b8,0x4f93c5)]:
        path=capture/f'{start:08x}.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
        result['spans'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    imports={f'{i.address:08x}':i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address in (0x5344c8,0x5344cc,0x5344d0)}
    assert imports=={'005344c8':'FindClose','005344cc':'FindFirstFileA','005344d0':'FindNextFileA'}
    assert pe.get_data(0x13f7f4,16).split(b'\0')[0]==b'.\\screenshots\\'
    result['imports']=imports;result['directory_prefix']='.\\screenshots\\'
    result['limits']=['Modern mechanism only; original screenshot path is documented separately.','Zero return conflates no non-dot entry and enumeration failure.','No file enumeration or screenshot capture executed.']
    (ROOT/'analysis/evidence/audits/modern-screenshot-directory.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: Modern screenshot directory preparation, non-dot enumeration and imports')


if __name__=='__main__':main()
