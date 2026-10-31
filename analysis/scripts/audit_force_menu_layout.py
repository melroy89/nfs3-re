"""Complete static force-menu initializer delta; no device/game execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

REGIONS=[(0x447e07,0x447e24),(0x447e94,0x447ece),
         (0x447f04,0x447f41),(0x447f82,0x447fbb),
         (0x447ffc,0x448035),(0x448076,0x4480af),(0x4480f4,0x44812d)]
TOKENS=[0x538cbc,0x538ccc,0x538ce0,0x538cf4,0x538d04,0x538d14,0x538d24]


def main():
    result={'kind':'force-feedback-menu-layout-removal','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/force-menu-layout'
    capture.mkdir(parents=True,exist_ok=True)
    bodies=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);start,end=0x447dd0,0x4481bd
        body=pe.get_data(start-0x400000,end-start);bodies.append(body)
        path=capture/f'{label}.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
            f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
        rows=[]
        for a,b in REGIONS:
            data=pe.get_data(a-0x400000,b-a)
            rows.append({'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':data.hex()})
            if label=='official_modern':
                expected_data=(bytes.fromhex('89c8e806f8feffeb14')+b'\x90'*20
                               if a==0x447e07 else bytes([0xeb,b-a-2])+b'\x90'*(b-a-2))
                assert data==expected_data
        result['binaries'][label]={'path':relative,'sha256':expected,
            'start':f'{start:08x}','end_exclusive':f'{end:08x}',
            'span_bytes':len(body),'span_sha256':hashlib.sha256(body).hexdigest(),
            'assembly':str(path.relative_to(ROOT)),'replacement_regions':rows,
            'strings':{f'{a:08x}':pe.get_data(a-0x400000,40).split(b'\0')[0].decode('ascii') for a in TOKENS}}
    old,new=bodies
    changed=[0x447dd0+i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    assert len(changed)==376
    assert all(any(a<=va<b for a,b in REGIONS) for va in changed)
    result['changed_bytes']=len(changed)
    result['limits']=['No menu or force-feedback runtime validation.',
        'Preserved bytes do not prove transitive callee equivalence or identical incidental register/flag state.',
        'Field roles documented by offsets unless separately established.']
    (ROOT/'analysis/evidence/audits/force-menu-layout.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 1005-byte initializer; all 376 changed bytes confined to seven replacements')


if __name__=='__main__':main()
