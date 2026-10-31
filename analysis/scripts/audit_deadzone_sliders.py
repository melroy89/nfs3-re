"""Static dead-zone value conversion and initializer differences."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'deadzone-slider-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/deadzone-sliders'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x442dd0,0x442e5a),(0x443070,0x44325c),(0x472b60,0x472d0d)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        assert struct.unpack('<f',pe.get_data(0x138a10,4))[0]==100.0
        assert pe.get_data(0x138a40,4)==bytes.fromhex('0ad7233c')
        names={f'{a:08x}':pe.get_data(a-0x400000,16).split(b'\0')[0].decode() for a in (0x538a20,0x538a28,0x538a30,0x538a38)}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'tail_widget_names':names}
    old,new=blobs['original'],blobs['official_modern']
    allowed=set()
    for address in (0x442e03,0x442e0d):
        o=address-0x442dd0;allowed.update(range(o,o+5))
        assert old[0][o]==0xe8 and address+5+struct.unpack('<i',old[0][o+1:o+5])[0]==0x4dfd56
        assert new[0][o:o+5]==bytes.fromhex('eb03909090')
    assert [i for i,(a,b) in enumerate(zip(old[0],new[0])) if a!=b]==sorted(allowed)
    for i,(a,b) in enumerate(zip(old[1],new[1])):
        assert a==b or i<0x16 or i==0x16e or i>=0x194
    assert old[1][0x16e]==242 and new[1][0x16e]==220
    assert new[1][:9]==bytes.fromhex('6089e583ec0889c3be')
    assert new[1][0x194:0x198]==bytes.fromhex('89ec61c3')
    assert new[1][0x198:]==b'\x90'*(0x1ec-0x198)
    assert [i for i,(a,b) in enumerate(zip(old[2],new[2])) if a!=b]==[0x133]
    assert old[2][0x130:0x136]==bytes.fromhex('837dfc107d4c')
    assert new[2][0x130:0x136]==bytes.fromhex('837dfc0f7d4c')
    result['capability_refresh']={'entry':'00472b60','end_exclusive':'00472d0d',
        'original_indices':'0..15','modern_indices':'0..14','record_stride':136,
        'limits':'Slot 15 remains in the primary device domain; no runtime stale-cache observation.'}
    result['limits']=['No controller, UI or x87 instruction execution.',
        'Downstream DirectInput property semantics and effective device response are not established here.']
    (ROOT/'analysis/evidence/audits/deadzone-sliders.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete slider envelopes plus 429-byte refresh; sole loop-limit edit 16-to-15')


if __name__=='__main__':main()
