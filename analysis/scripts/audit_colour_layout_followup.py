"""Static four immediate edits across three complete colour-control functions."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

CASES=[(0x43dfb0,0x43e033,[(0x43e019,12,8)]),
       (0x4569a0,0x456a1f,[(0x456a16,45,38)]),
       (0x4571e0,0x45724e,[(0x45720b,5,8),(0x457218,48,28)])]


def main():
    result={'kind':'colour-control-layout-immediates','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/colour-layout'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end,sites in CASES:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            for address,old,new in sites:assert data[address-start]==(old if label=='original' else new)
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    for i,(start,_,sites) in enumerate(CASES):
        assert [j for j,(a,b) in enumerate(zip(blobs['original'][i],blobs['official_modern'][i])) if a!=b]==[a-start for a,_,_ in sites]
    result['limits']=['Static field/argument offsets only; no visual rendering or interaction test.',
        'Text metrics, aliasing and device/display scaling remain separate contracts.']
    (ROOT/'analysis/evidence/audits/colour-layout-followup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 131/127/110-byte bodies; exactly four layout-immediate changes')


if __name__=='__main__':main()
