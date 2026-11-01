"""Static paired reference-dimension reads in complete HUD functions."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x484b70,0x484c10),(0x48ae70,0x48b29f),(0x48d110,0x48d4b3),
       (0x4800a0,0x4808af),(0x487210,0x48733c),(0x4880b0,0x488470),
       (0x48a660,0x48aa3e),(0x48aa40,0x48ae69),(0x48e790,0x48e91b),
       (0x451530,0x451585),(0x4d1390,0x4d13f3),(0x4d0d50,0x4d0ff9)]


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
        scale_constants=pe.get_data(0x13b620,16)
        assert scale_constants==struct.pack('<4f',0.0015625 if label=='original' else 0.0017,0.8,0.6,0.5)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'hud_scale_constants':{'address':'0053b620','bytes':scale_constants.hex(),
                'binary32_values':list(struct.unpack('<4f',scale_constants)),
                'gear_default_destination':'00791b54','fallback_destination':'00791b4c',
                'limits':'Caller/default-state evidence only; no rendered font-size measurement.'}}
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
    assert [i for i,(a,b) in enumerate(zip(old[8],new[8])) if a!=b]==[0x153]
    assert old[8][0x14a:0x155]==bytes.fromhex('c7841a60bc6f0000008040')
    assert new[8][0x14a:0x155]==bytes.fromhex('c7841a60bc6f0000004040')
    result['hud_variant_constant']={'instruction':'0048e8da','original_bits':'40800000',
        'modern_bits':'40400000','field':'selected 1a4-byte profile +10h',
        'limits':'Field meaning and rendered transition remain unverified.'}
    for index in (9,10,11):assert old[index]==new[index]
    adapter=new[9]
    assert adapter[6:15].hex()=='833d34925500007436'
    assert adapter[0x21:0x26].hex()=='a1501b7900'
    assert adapter[0x36:0x3b].hex()=='a1541b7900'
    assert adapter[0x3d:0x42].hex()=='a14c1b7900'
    assert adapter[0x48:0x4f].hex()=='e813fe0700ddd8'
    images={label:pefile.PE(str(ROOT/SPECS[label][0])) for label in SPECS}
    threshold_bytes=images['original'].get_data(0x1395e0,8)
    assert threshold_bytes==images['official_modern'].get_data(0x1395e0,8)
    assert struct.unpack('<d',threshold_bytes)[0]==0.6
    for pe in images.values():
        assert pe.get_data(0xd0d64,12).hex()=='813dc8da7c00800200007c28'
        assert pe.get_data(0xd13ce,12).hex()=='db05c8da7c00d80dc80b5400'
    examples=[]
    old_k=struct.unpack('<f',images['original'].get_data(0x13b620,4))[0]
    new_k=struct.unpack('<f',images['official_modern'].get_data(0x13b620,4))[0]
    for width,height in ((1920,1080),(2560,1080),(1280,1024)):
        synthetic=(3*width)>>2;offset=(height-synthetic)>>1
        reference=width if offset>=0 else (4*height)//3
        examples.append({'width':width,'height':height,'modern_reference_width':reference,
            'original_unrounded_base':width*old_k,'modern_unrounded_base':reference*new_k})
    result['font_scale_consumer_link']={
        'identical_complete_bodies':[{'start':f'{SPANS[i][0]:08x}','end_exclusive':f'{SPANS[i][1]:08x}'} for i in (9,10,11)],
        'adapter':'00451530 uses00559234 gate:0 forwards requested argument; nonzero chooses00791b50/54/4c then calls004d1390 and discards old-scale ST0.',
        'ordered_request_selection':'request>=1 ->00791b50;0.6<=request<1 ->00791b54;request<0.6 ->00791b4c. Unordered first comparison follows the >=1 arm if nontrapping.',
        'binary64_threshold':{'address':'005395e0','hex':threshold_bytes.hex(),'value':0.6},
        'producer':'00484b70 writes the consumed scales; changed input actual width007cdac8 -> fitted reference width007a2748, plus changed base coefficient.',
        'retained_bitmap_branch':'004d1390 flag00840188 nonzero uses actual width007cdac8 and retained1/320 coefficient; flag0 accepts supplied scale.',
        'retained_bitmap_loader':'004d0d50 still chooses FFN files by signed width007cdac8>=640.',
        'ordinary_reference_width_examples':examples,
        'limits':['Derived unrounded base-scale arithmetic, not original-instruction probes or rendered font sizes.',
            'Reference-width formulas reused from viewport-geometry evidence; ordinary positive fitting dimensions only.',
            'Text-adapter/backend and font-state gates make this a scoped path, not a universal all-font height policy.',
            'Shared font storage, callers, asset/font selection, x87 state and later overrides remain separate.']}
    result['limits']=['Static dimension-source, FLD/FILD and quad/header constant changes only; no HUD pixel comparison.',
        'Other globals, callers, aliasing and x87 state remain separate contracts.']
    (ROOT/'analysis/evidence/audits/hud-reference-consumers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: twelve complete bodies; changed HUD inputs and retained text-scale/bitmap contracts verified')


if __name__=='__main__':main()
