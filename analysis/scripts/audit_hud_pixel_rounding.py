"""Static removed FRNDINT-helper calls in HUD pixel conversion; no execution."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

CALLS=[0x480999,0x4809a3,0x4809aa,0x4809b3]


def main():
    result={'kind':'hud-pixel-rounding-call-removal','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/hud-pixel-rounding'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x480910,0x4809f7),(0x4dfd56,0x4dfd74)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'][0],blobs['official_modern'][0]
    allowed=set()
    for address in CALLS:
        offset=address-0x480910;allowed.update(range(offset,offset+5))
        assert old[offset]==0xe8
        assert address+5+struct.unpack('<i',old[offset+1:offset+5])[0]==0x4dfd56
        assert new[offset:offset+5]==bytes.fromhex('eb03909090')
    assert [i for i,(a,b) in enumerate(zip(old,new)) if a!=b]==sorted(allowed)
    for address in [0x4809bd,0x4809c5,0x4809d3,0x4809df]:
        assert old[address-0x480910:address-0x480910+3]==bytes.fromhex('db5dfc')
    result['removed_calls']=[f'{a:08x}' for a in CALLS]
    result['limits']=['No x87 execution or pixel comparison; numerical examples in prose are conditional derivations.',
        'Caller control words, exceptional inputs and all layout producers remain unverified.']
    (ROOT/'analysis/evidence/audits/hud-pixel-rounding.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 231-byte envelope; exactly four removed helper calls; retained four FISTP instructions')


if __name__=='__main__':main()
