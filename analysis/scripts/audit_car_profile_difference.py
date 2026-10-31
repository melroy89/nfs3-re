"""Static car profile path and timestamp-gate removal comparison."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'car-profile-path-and-time-gate','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/car-profile'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x4dc800,0x4dc8af),(0x4dc940,0x4dca4e)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        assert pe.get_data(0x149770,10)==b'carspecs\\\0'
        assert pe.get_data(0x14977c,5)==b'.spc\0'
        imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534544]=='GetModuleFileNameA'
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][9:14]==bytes.fromhex('beb42f7a00')
    assert new[0][9:14]==bytes.fromhex('beb4307a00')
    assert new[0][0x35:0x5c]==bytes.fromhex('eb25')+b'\x90'*37
    for i,(a,b) in enumerate(zip(old[0],new[0])):
        assert a==b or i==0xb or 0x35<=i<0x5c
    assert old[1][:0x87]==new[1][:0x87] and old[1][0xab:]==new[1][0xab:]
    assert new[1][0x87:0xab]==bytes.fromhex('85c0746ceb1e')+b'\x90'*30
    result['changes']=[{'entry':f'{a:08x}','envelope_bytes':len(x),'changed_bytes':sum(v!=w for v,w in zip(x,y))}
        for a,x,y in zip((0x4dc800,0x4dc940),old,new)]
    result['limits']=['No profile files read, written or deleted; no target execution.',
        'Directory initialization, resource-loader failure semantics and complete profile format remain unqualified.']
    (ROOT/'analysis/evidence/audits/car-profile-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 175/270-byte profile envelopes, path literals, removed appender and time-gate branch')


if __name__=='__main__':main()
