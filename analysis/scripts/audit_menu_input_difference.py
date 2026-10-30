"""Static menu navigation/chat witnesses; no UI, network or target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON=[(0x441700,0x4417ef),(0x441b20,0x441c87),(0x42d810,0x42d856),
        (0x449f30,0x44a0b5),(0x44a0c0,0x44a23b)]


def main():
    capture=ROOT/'analysis/captures/modern-differences/menu-input'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-menu-input-chat-comparison','range_end':'exclusive',
        'binaries':{},'limits':['No UI/network/target execution.',
            'Active-entry callbacks and every asset-defined navigation action not validated.',
            'Empty-string rejection is a caller guard, not a universal send API contract.']}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data)
        spans=list(COMMON)+[(0x44a240,0x44a2c9 if label=='original' else 0x44a2c2),
                            (0x44a2d0,0x44a439 if label=='original' else 0x44a436)]
        if label=='official_modern':spans += [(0x4f1fcc,0x4f1ff0),(0x4f93ec,0x4f9400)]
        rows=[]
        for start,end in spans:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        strings={f'{a:08x}':pe.get_data(a-0x400000,32).split(b'\0')[0].decode('ascii')
                 for a in ((0x538fbc,0x537834) if label=='original' else
                           (0x538fbc,0x53be28,0x53be2e,0x53be36,0x53be3e,0x537834))}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'strings':strings}
    for index in (0,2,3,4):
        assert result['binaries']['original']['spans'][index]['bytes_sha256']==result['binaries']['official_modern']['spans'][index]['bytes_sha256']
    output=ROOT/'analysis/evidence/audits/original-modern-menu-input.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: fingerprints, unchanged lobby/send/navigation bodies and changed dispatch/chat captures')


if __name__=='__main__':main()
