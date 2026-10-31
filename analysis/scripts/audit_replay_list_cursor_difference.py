"""Static selectlist registration and replay keyboard cursor calculation."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/replay-list-cursor';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-replay-list-cursor-comparison','range_end':'exclusive','binaries':{}};images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe
        start,end=0x462fa0,0x4633cd;path=capture/f'{label}-{start:08x}.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
        name,template,tag=struct.unpack('<3I',pe.get_data(0x157ad0,12));assert pe.get_data(name-0x400000,32).split(b'\0')[0]==b'selectlist'
        words=struct.unpack('<14I',pe.get_data(template-0x400000,56));assert words[12]==0x462fa0
        result['binaries'][label]={'path':relative,'sha256':expected,'span':{'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},'widget_row_00557ad0':[f'{v:08x}' for v in (name,template,tag)],'template_words':[f'{v:08x}' for v in words]}
    result['identical_ranges']=[]
    for start,end in [(0x462fa0,0x46326f),(0x463274,0x463370),(0x4633a7,0x4633cd)]:
        raw=images['original'].get_data(start-0x400000,end-start);assert raw==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(raw).hexdigest()})
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z';assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    raw=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/loadsave.mnu']);lines=raw.decode('latin1').splitlines();i=lines.index('codelink=replays');assert lines[i-4]=='[selectlist]'
    result['official_asset']={'member':'fedata/menus/loadsave.mnu','sha256':hashlib.sha256(raw).hexdigest(),'replays_record':lines[i-4:i+4]}
    result['limits']=['No keyboard, cursor, rendering or target execution.','Selectlist handler address envelope retained through its final RET; no Ghidra metadata changes.','Widget registration and authored replay control support association; full menu instantiation/runtime admission untested.']
    (ROOT/'analysis/evidence/audits/original-modern-replay-list-cursor.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired selectlist handler, registration, unchanged ranges and official replay control')


if __name__=='__main__':main()
