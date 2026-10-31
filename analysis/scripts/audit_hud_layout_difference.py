"""Static HUD preset/default witnesses, without running target instructions."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS={'original':[(0x485680,0x485876),(0x485880,0x485a51)],
       'official_modern':[(0x485680,0x48575b),(0x48582c,0x485876),
                          (0x485880,0x4859f7),(0x448400,0x448425)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/hud-layout'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-hud-preset-default-comparison','range_end':'exclusive',
        'binaries':{},'limits':['No HUD/asset/target execution.',
            'Header fields are documented by offsets rather than unverified visual meanings.',
            'Shared-frame tail is not an independently callable ordinary function.']}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data);rows=[]
        for start,end in SPANS[label]:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        row={'path':relative,'sha256':expected,'spans':rows}
        old_slot=pe.get_data(0x55d454-0x400000,576)
        section=pe.get_section_by_rva(0x55d454-0x400000)
        assert section.PointerToRawData and len(old_slot)==576
        if label=='official_modern':assert old_slot==b'\0'*576
        base_references=[];position=0
        while True:
            offset=data.find(struct.pack('<I',0x55d454),position)
            if offset<0:break
            base_references.append(f'{pe.OPTIONAL_HEADER.ImageBase+pe.get_rva_from_offset(offset):08x}')
            position=offset+1
        assert base_references==(['00485810'] if label=='original' else [])
        row['original_extra_rectangle_table_storage']={
            'start':'0055d454','end_exclusive':'0055d694','bytes':576,
            'sha256':hashlib.sha256(old_slot).hexdigest(),
            'file_offset':pe.get_offset_from_rva(0x55d454-0x400000),
            'all_zero':not any(old_slot),
            'exact_absolute_base_encodings':base_references,
            'search_limit':'All file bytes; computed/interior references, startup writes and external access not excluded.'}
        if label=='original':
            assert pe.get_data(0x53ebb8-0x400000,10)==b'nulla.dll\0'
            row['future_modern_preset_area_original_sample']={
                'address':'0053ebb8','value':'nulla.dll',
                'relation':'Inside Modern embedded table 0053eb20..0053f420; not a shared semantic object.'}
        if label=='original':
            row['strings']={f'{a:08x}':pe.get_data(a-0x400000,64).split(b'\0')[0].decode('ascii')
                for a in (0x53b660,0x53b66c,0x53b674,0x53b678)}
            row['locale_character_table_hex']=pe.get_data(0x47bbb8-0x400000,7).hex()
        else:
            raw=pe.get_data(0x53eb20-0x400000,0x900)
            row['embedded_preset_table']={'va':'0053eb20','bytes':len(raw),
                'file_offset':pe.get_offset_from_rva(0x53eb20-0x400000),'sha256':hashlib.sha256(raw).hexdigest()}
            row['aspect_constants']={f'{a:08x}':struct.unpack('<f',pe.get_data(a-0x400000,4))[0]
                for a in (0x53f420,0x53f424)}
            row['symmetric_divisor_signed_int32']=struct.unpack('<i',pe.get_data(0x53f428-0x400000,4))[0]
        result['binaries'][label]=row
    assert result['binaries']['official_modern']['symmetric_divisor_signed_int32']==2
    original=pefile.PE(str(ROOT/SPECS['original'][0]));modern=pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    assert original.get_data(0x8582c,0x4a)==modern.get_data(0x8582c,0x4a)
    result['shared_frame_tail_0048582c_bytes_identical']=True
    output=ROOT/'analysis/evidence/audits/original-modern-hud-layout.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: fingerprints, HUD initialization/default spans and preset provenance')


if __name__=='__main__':main()
