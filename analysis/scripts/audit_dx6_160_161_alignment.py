"""Static DX6 half-unit vertex adjustment; no renderer execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def main():
    baseline=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())
    capture=ROOT/'analysis/captures/modern-differences/dx6-alignment';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-dx6-160-161-vertex-alignment','versions':{},'range_end':'exclusive'}
    images={}
    sites=[0x60005712,0x60006329,0x600063ed,0x600064d7,0x60006583,0x60006633,0x6000670d,0x600067b3]
    for version in ('1.6.0','1.6.1'):
        package=baseline['packages'][version];archive=ROOT/package['archive_path']
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==package['archive_sha256']
        member='drivers/dx6/dx6a.dll'
        raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        expected=next(row['sha256'] for row in package['members'] if row['member']==member)
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[version]=pe
        binary=capture/f'dx6-{version}.dll';binary.write_bytes(raw)
        spans=[]
        for start,end in [(0x6000e514,0x6000e54b)]+[(site,site+15) for site in sites]:
            body=pe.get_data(start-0x60000000,end-start)
            output=capture/f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
            spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(body).hexdigest(),
                          'assembly':str(output.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        assert struct.unpack('<f',pe.get_data(0xf158,4))[0]==0.5
        result['versions'][version]={'archive_sha256':package['archive_sha256'],'member':member,'sha256':expected,'spans':spans}
    patches=[]
    for site in sites:
        old=images['1.6.0'].get_data(site-0x60000000,5)
        new=images['1.6.1'].get_data(site-0x60000000,5)
        assert old.hex()=='68c4010000' and new[0]==0xe8
        assert site+5+int.from_bytes(new[1:],'little',signed=True)==0x6000e514
        patches.append({'site':f'{site:08x}','old':old.hex(),'new':new.hex()})
    helper=images['1.6.1'].get_data(0xe514,55)
    assert helper.hex()=='51578b7c240c8b4c241085c9741bd90558f10060d907d8e1d91fd94704d8e1d95f0483c720e2edddd85f59ff3424c7442404c4010000c3'
    result['patches']=patches
    result['contract']={'helper':'6000e514..6000e54b,55 bytes',
        'input':'Entry stack+4 vertex pointer,stack+8 DWORD count; ECX/EDI saved/restored.',
        'writes':'For nonzero count, subtract binary32 constant0.5 from floats+0/+4 of each32-byte vertex; store each result binary32.',
        'stack_adapter':'After restoring registers, duplicate return address, replace next stack DWORD with1c4h, RET; net caller-stack effect matches replaced PUSH1c4h.',
        'limits':['Eight patched sites verified; not all exported draw reachability or every driver mode.',
                  'Mutates supplied vertices; repeated submission of same unreinitialized buffer can repeat correction.',
                  'Assumes valid pointer/count and ordinary x87 execution; count0 skips arithmetic. No C/ABI/runtime equivalence claim.']}
    result['limits']=['Author-hosted1.6.0/1.6.1 DX6 pair only; DX7/DX8 and original retail driver remain separate.',
                      'No rasterization, texture sampling, visual sharpness or graphics API execution tested.']
    (ROOT/'analysis/evidence/audits/dx6-160-161-alignment.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned DX6 pair, eight PUSH-to-CALL patches and complete half-unit adjustment adapter')


if __name__=='__main__':main()
