"""Static paired removal of frontend 16-bit display-depth override."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'frontend-depth-save-force-restore-removal','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/frontend-depth'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x473020,0x47307e),(0x473080,0x4730c6)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][0x21:0x36]==bytes.fromhex('a18c435600ba10000000a30890670089158c435600')
    assert new[0][0x21:0x36]==bytes.fromhex('eb13')+b'\x90'*19
    assert old[1][0x1b:0x25]==bytes.fromhex('a108906700a38c435600')
    assert new[1][0x1b:0x25]==bytes.fromhex('eb08')+b'\x90'*8
    for i,lo,hi in [(0,0x21,0x36),(1,0x1b,0x25)]:
        assert old[i][:lo]==new[i][:lo] and old[i][hi:]==new[i][hi:]
    result['limits']=['Static state writes only; no display-mode transition or rendering test.',
        'Full selected-mode propagation and incidental register contracts across callees remain separate.']
    (ROOT/'analysis/evidence/audits/frontend-depth-override.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 94/70-byte entry/restore envelopes; only paired depth override regions differ')


if __name__=='__main__':main()
