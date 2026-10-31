"""Static paired reference-dimension reads in complete HUD functions."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x484b70,0x484c10),(0x48ae70,0x48b29f),(0x48d110,0x48d4b3),
       (0x4800a0,0x4808af),(0x487210,0x48733c),(0x4880b0,0x488470),
       (0x48a660,0x48aa3e),(0x48aa40,0x48ae69)]


def main():
    result={'kind':'hud-reference-dimension-consumers','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/hud-reference-consumers'
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
    expected=[(0x484b70,[0xb,0xc,0xd]),(0x48ae70,[0x19,0x1a,0x1b,0x32,0x33,0x34,0x5b,0x5d,0x5e,0x5f]),(0x48d110,[0x2fc,0x2fd,0x2fe])]
    for i,(start,changes) in enumerate(expected):
        assert [j for j,(a,b) in enumerate(zip(old[i],new[i])) if a!=b]==changes
    assert old[0][0xa:0xf]==b'\xa1'+struct.pack('<I',0x7cdac8)
    assert new[0][0xa:0xf]==b'\xa1'+struct.pack('<I',0x7a2748)
    for index,offset in [(1,0x17),(1,0x30),(2,0x2fa)]:
        assert old[index][offset:offset+6]==bytes.fromhex('db05c8da7c00')
        assert new[index][offset:offset+6]==bytes.fromhex('db0548277a00')
    assert old[1][0x5b:0x61]==bytes.fromhex('d905bcd65500')
    assert new[1][0x5b:0x61]==bytes.fromhex('db054c277a00')
    additional_reads={
        3:[(0x480187,0xdb,0x7cdac8,0x7a2748)],
        4:[(a,0xdb,0x7cdac8,0x7a2748) for a in (0x487238,0x487251,0x487284,0x4872b3)],
        5:[(0x4880c7,0xdb,0x7cdba0,0x7a2758),(0x48818d,0xdb,0x7cdb98,0x7a2750),
           (0x4881a4,0xdb,0x7cdb9c,0x7a2754),(0x48832f,0xdb,0x7cdb98,0x7a2750),
           (0x488346,0xdb,0x7cdb9c,0x7a2754)],
        6:[(a,0xdb,0x7cdac8,0x7a2748) for a in (0x48a670,0x48a714)],
        7:[(0x48ab47,0xd9,0x55d6b8,0x7a2748),(0x48abfa,0xd9,0x55d6b8,0x7a2748),
           (0x48ac06,0xdb,0x7cdac8,0x7a2748),(0x48ac53,0xd9,0x55d6bc,0x7a274c),
           (0x48ae0f,0xdb,0x7cdac8,0x7a2748)]}
    for index,reads in additional_reads.items():
        expected_body=bytearray(old[index]);start=SPANS[index][0]
        for address,opcode,source,destination in reads:
            offset=address-start
            assert old[index][offset:offset+6]==bytes([opcode,5])+struct.pack('<I',source)
            expected_body[offset:offset+6]=bytes([0xdb,5])+struct.pack('<I',destination)
        if index==3:
            offset=0x480831-start
            assert old[index][offset:offset+7]==bytes.fromhex('c7403c0000443f')
            expected_body[offset:offset+7]=bytes.fromhex('c7403c0000453f')
        assert bytes(expected_body)==new[index]
    result['additional_reads']={f'{SPANS[i][0]:08x}':[
        {'instruction':f'{a:08x}','old_opcode':f'{op:02x}','old_source':f'{src:08x}',
         'modern_source':f'{dst:08x}'} for a,op,src,dst in rows] for i,rows in additional_reads.items()}
    result['limits']=['Static dimension-source, FLD/FILD and quad constant changes only; no HUD pixel comparison.',
        'Other globals, callers, aliasing and x87 state remain separate contracts.']
    (ROOT/'analysis/evidence/audits/hud-reference-consumers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: eight complete bodies; dimension read replacements and one quad-field constant account for every difference')


if __name__=='__main__':main()
