"""Static speed-display consumer and official English unit labels."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    rows={}; blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);spans=[];blobs[label]=[]
        for a,b in [(0x48384a,0x48395a),(0x489d70,0x489df7)]:
            v=pe.get_data(a-0x400000,b-a);blobs[label].append(v)
            spans.append({'start':f'{a:08x}','exclusive_end':f'{b:08x}',
                          'sha256':hashlib.sha256(v).hexdigest(),'bytes':v.hex()})
        constants=[]
        for a in [0x53b83c,0x53b840]:
            v=pe.get_data(a-0x400000,4)
            constants.append({'address':f'{a:08x}','hex':v.hex(),'binary32_value':struct.unpack('<f',v)[0]})
        rows[label]={'path':relative,'sha256':expected,'spans':spans,'constants':constants}
    assert blobs['original']==blobs['official_modern']
    assert rows['original']['constants']==rows['official_modern']['constants']
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_hash=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    member='fedata/text/text.eng'
    data=subprocess.check_output(['7z','x','-so',str(archive),member]);extent=struct.unpack_from('<I',data)[0]
    assert extent%4==0 and extent<=len(data)
    labels=[]
    for ident,expected in [(0x156,b'MPH'),(0x157,b'KPH')]:
        assert ident*4<extent
        off=struct.unpack_from('<I',data,ident*4)[0];assert extent<=off<len(data)
        end=data.index(b'\0',off);assert data[off:end]==expected
        labels.append({'id':ident,'offset':off,'text':expected.decode()})
    result={'kind':'static-speed-unit-default-consumer','binaries':rows,
        'official_english':{'archive_sha256':archive_hash,'member':member,
            'sha256':hashlib.sha256(data).hexdigest(),'labels':labels},
        'limits':['Header default stores are separately audited by audit_hud_layout_difference.py.',
                  'Identical caller bytes do not establish identical rounding helper behavior or FPU state.',
                  'No drawing, runtime localization selection, persistence override or all speedometer paths tested.']}
    (ROOT/'analysis/evidence/audits/speed-unit-default-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: identical paired speed consumer/formatter, constants and pinned English MPH/KPH labels')


if __name__=='__main__':main()
