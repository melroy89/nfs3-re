"""Static environment grid gate, renderer mask and vector argument comparisons."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x479500,0x479671),(0x47a190,0x47a1e8),(0x47b850,0x47ba68),(0x47b380,0x47b39f)]


def main():
    result={'kind':'environment-grid-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/environment-grid'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in SPANS:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert [i for i,(a,b) in enumerate(zip(old[0],new[0])) if a!=b]==[0x4f]
    assert old[0][0x4c:0x51]==bytes.fromhex('6800008040') and new[0][0x4c:0x51]==bytes.fromhex('6800006040')
    assert old[1][:0x14]==new[1][:0x14] and old[1][0x22:]==new[1][0x22:]
    assert old[1][0x14:0x22]==bytes.fromhex('833d2cbc6f0001741e833a017419')
    assert new[1][0x14:0x22]==bytes.fromhex('89d0e8d511000085c0741ceb0190')
    assert [i for i,(a,b) in enumerate(zip(old[2],new[2])) if a!=b]==[0xaa]
    assert old[2][0xa4:0xab]==bytes.fromhex('f605583a7a0040')
    assert new[2][0xa4:0xab]==bytes.fromhex('f605583a7a0050')
    assert new[3]==bytes.fromhex('833d2cbc6f0000750e833801750c833dd8d16f0000740331c0c331c0b001c3')
    result['limits']=['Static code/argument comparison only; no environment rendering executed.',
        'Context tag meanings, full flag producers, vector parameter units and visual effects remain partially qualified.']
    (ROOT/'analysis/evidence/audits/environment-grid-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 369/88/536-byte matched envelopes and complete 31-byte Modern admission helper')


if __name__=='__main__':main()
