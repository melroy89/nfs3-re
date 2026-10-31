"""Static paired movie parameter initialization; no movie/audio execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/movie-volume'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-movie-volume-comparison','range_end':'exclusive','binaries':{}}
    images={}
    common=[(0x495bc0,0x4960e0),(0x4e9b20,0x4e9b93),(0x4f3a60,0x4f3a7e)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=common+([(0x4962c2,0x4962d6)] if label=='official_modern' else [])
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        data=pe.get_data(0x95e01,5);assert data[0]==0xe8
        target=0x495e06+int.from_bytes(data[1:],'little',signed=True)
        assert target==(0x4e9b20 if label=='original' else 0x4962c2)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'call_00495e01_target':f'{target:08x}'}
    result['identical_ranges']=[]
    for start,end in [(0x495df9,0x495e01),(0x495e06,0x495e3e),(0x4e9b20,0x4e9b93),(0x4f3a60,0x4f3a7e)]:
        data=images['original'].get_data(start-0x400000,end-start)
        assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest()})
    assert images['official_modern'].get_data(0x962ca,10)==bytes.fromhex('a1e8bb6f00247f884708')
    result['limits']=['No target, movie, audio or instruction execution.','Movie body retained as an address envelope, not asserted wholly identical.','Parameter byte correspondence verified; complete decoder/provider semantics and audible response unverified.']
    (ROOT/'analysis/evidence/audits/original-modern-movie-volume.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: movie initializer redirection, level mask, retained default and forwarding ranges')


if __name__=='__main__':main()
