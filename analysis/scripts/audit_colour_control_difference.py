"""Paired frontend colour mouse-control dispatch; no UI/audio execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/colour-control';capture.mkdir(parents=True,exist_ok=True)
    common=[(0x43e8e0,0x43eacb),(0x43e7a0,0x43e8df),(0x43dd90,0x43ddc1),(0x43dc90,0x43dd50),(0x43ddd0,0x43de19)]
    result={'kind':'static-colour-control-comparison','range_end':'exclusive','binaries':{}};images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        end=0x43ebb8 if label=='original' else 0x43eb85
        for start,stop in [(0x43ead0,end),(0x456ce0,0x456e98),(0x457030,0x4571d1),(0x43ebc0,0x43ebec)]+common:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={stop}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{stop:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,stop-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        bindings=[]
        for address in (0x557b54,0x557b60):
            name,template,tag=struct.unpack('<3I',pe.get_data(address-0x400000,12))
            words=struct.unpack('<25I',pe.get_data(template-0x400000,100))
            bindings.append({'row':f'{address:08x}','name':pe.get_data(name-0x400000,32).split(b'\0')[0].decode(),'template':f'{template:08x}','tag':tag,'template_words':[f'{v:08x}' for v in words]})
        assert bindings[0]['name']=='carclrselect' and bindings[0]['template_words'][11:13]==['00456ce0','00457030']
        assert bindings[1]['name']=='colorwheel' and bindings[1]['template_words'][11]=='0043ebc0'
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'widget_bindings':bindings}
    result['dropdown_changed_byte_addresses']={}
    for start,end,expected in [(0x456ce0,0x456e98,[0x456db2,0x456e2a,0x456e2b]),(0x457030,0x4571d1,[0x457107,0x457142])]:
        old=images['original'].get_data(start-0x400000,end-start);new=images['official_modern'].get_data(start-0x400000,end-start)
        changes=[start+i for i,(a,b) in enumerate(zip(old,new)) if a!=b];assert changes==expected
        result['dropdown_changed_byte_addresses'][f'{start:08x}']=[f'{a:08x}' for a in changes]
    result['identical_ranges']=[]
    for start,end in common+[(0x43ead0,0x43eb1c)]:
        data=images['original'].get_data(start-0x400000,end-start);assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest()})
    result['limits']=['No UI, audio or instruction execution.','Dropdown inset and sound operands verified separately from wheel; rendered/audible consistency untested.','Original full body extends beyond Modern function range; same-VA changed-byte count is not a whole-function semantic comparison.']
    (ROOT/'analysis/evidence/audits/original-modern-colour-control.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: full colour handler counterparts, shared prefix and five identical helpers')


if __name__=='__main__':main()
