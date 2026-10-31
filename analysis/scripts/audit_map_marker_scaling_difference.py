"""Static map-marker extent producer/quad consumer comparison."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'map-marker-scale-comparison','binaries':{},'limits':[
        'Static producer/consumer evidence, not rendered size or runtime initialization.',
        'Reference width follows aspect-dependent construction; not universally physical width or height.']}
    capture=ROOT/'analysis/captures/modern-differences/map-marker-scale';capture.mkdir(parents=True,exist_ok=True)
    blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for a,b in [(0x48d110,0x48d4b3),(0x48cc60,0x48cce8),(0x48d4c0,0x48e76d)]:
            v=pe.get_data(a-0x400000,b-a);blobs[label].append(v)
            path=capture/f'{label}-{a:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={a}',f'--stop-address={b}',relative],cwd=ROOT))
            rows.append({'start':f'{a:08x}','exclusive_end':f'{b:08x}','sha256':hashlib.sha256(v).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        constants=[]
        for a,value in [(0x53b9ac,0.5),(0x53b9cc,9.0),(0x53b9d0,1/640),(0x53b9d4,22.0),(0x53b9d8,14.0),(0x53b9dc,10.0)]:
            v=pe.get_data(a-0x400000,4);assert v==struct.pack('<f',value)
            constants.append({'address':f'{a:08x}','hex':v.hex(),'binary32':struct.unpack('<f',v)[0]})
        assert pe.get_data(0x48e173-0x400000,26)==bytes.fromhex('ff35f0307900ff35f8307900ff75be8b4576ff75bae8d3eaffff')
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'constants':constants}
    old,new=blobs['original'],blobs['official_modern']
    assert old[1:]==new[1:]
    assert [0x48d110+i for i,(a,b) in enumerate(zip(old[0],new[0])) if a!=b]==[0x48d40c,0x48d40d,0x48d40e]
    assert old[0][0x2fa:0x300]==bytes.fromhex('db05c8da7c00')
    assert new[0][0x2fa:0x300]==bytes.fromhex('db0548277a00')
    result['extent_fields']={'007930e4':'9*width*k','007930f8':'22*width*k','00793104':'14*width*k','007930ec':'10*width*k','k':'binary32 approximation to1/640 at0053b9d0'}
    result['confirmed_square_marker_call']={'site':'0048e188','width':'007930f8','height':'007930f0, copied from007930f8','consumer':'0048cc60','geometry':'centre plus/minus half extents; no claim of final rendered pixels'}
    (ROOT/'analysis/evidence/audits/map-marker-scaling-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: marker producer width replacement, identical marker/map consumers and extent constants')


if __name__=='__main__':main()
