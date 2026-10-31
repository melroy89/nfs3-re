"""Authored visible-count comparison; uppercase backups have uncertain provenance."""
import hashlib
import json
import subprocess
import pefile
import struct
from audit_thrash_loader_difference import ROOT,SPECS
from audit_controller_reset_asset import sections


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    listing=subprocess.check_output(['7z','l','-slt',str(archive)]).decode().splitlines()
    members=[l[7:] for l in listing if l.startswith('Path = fedata/menus/') and l.lower().endswith('.mnu')];assert len(members)==52
    result={'kind':'authored-menu-visible-count-comparison','members':[],'changed':[],'unpaired':[],'backup_only':[]}
    for member in members:
        modern=subprocess.check_output(['7z','x','-so',str(archive),member])
        backup=ROOT/'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus'/member.split('/')[-1].upper()
        assert backup.is_file();old=backup.read_bytes()
        result['members'].append({'member':member,'modern_sha256':hashlib.sha256(modern).hexdigest(),'backup':str(backup.relative_to(ROOT)),'backup_sha256':hashlib.sha256(old).hexdigest()})
        def index(data):
            rows={}
            for section in sections(data):
                f=section['fields']
                if 'maxvisitem' in f:
                    key=(section['section'],f.get('listname',''))
                    rows.setdefault(key,[]).append(f['maxvisitem'])
            return rows
        a,b=index(old),index(modern)
        for key,values in a.items():
            if key not in b:result['backup_only'].append({'member':member,'section':key[0],'listname':key[1],'backup':values})
        for key,values in b.items():
            if len(values)!=1 or len(a.get(key,[]))!=1:
                result['unpaired'].append({'member':member,'section':key[0],'listname':key[1],'modern':values,'backup':a.get(key,[])});continue
            if a[key]!=values:result['changed'].append({'member':member,'section':key[0],'listname':key[1],'backup':a[key][0],'modern':values[0]})
    result['binary_field_descriptors']={}
    layout_bodies={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for address in (0x557d80,0x557dc0):
            data=pe.get_data(address-0x400000,16);words=struct.unpack('<4I',data)
            assert pe.get_data(words[1]-0x400000,11)==b'maxvisitem\0'
            rows.append({'address':f'{address:08x}','words':[f'{word:08x}' for word in words],'sha256':hashlib.sha256(data).hexdigest()})
        bindings=[]
        for address,expected_type,expected_name,template in [(0x557ab4,0x11,'cascade',0x556ea8),(0x557ac0,0x1d,'droplist',0x556f0c)]:
            data=pe.get_data(address-0x400000,12);type_id,name_ptr,template_ptr=struct.unpack('<3I',data)
            name=pe.get_data(name_ptr-0x400000,16).split(b'\0')[0].decode('ascii')
            assert (type_id,name,template_ptr)==(expected_type,expected_name,template)
            callbacks={f'{offset:x}':f'{struct.unpack("<I",pe.get_data(template_ptr-0x400000+offset,4))[0]:08x}' for offset in (0x24,0x2c,0x30,0x34)}
            if type_id==0x1d:assert list(callbacks.values())==['00463e60','004634d0','00463ff0','00464560']
            bindings.append({'row':f'{address:08x}','type_id':type_id,'name':name,'template':f'{template_ptr:08x}','row_sha256':hashlib.sha256(data).hexdigest(),'callbacks_by_offset':callbacks})
        result.setdefault('widget_type_bindings',{})[label]=bindings
        spans=[]
        capture=ROOT/'analysis/captures/modern-differences/menu-visible-counts';capture.mkdir(parents=True,exist_ok=True)
        for start,end in [(0x4623a0,0x46249b),(0x4624a0,0x4628c8),(0x449060,0x4490d8),(0x449240,0x4492bf),(0x449393,0x4493a3),(0x442bf0,0x442c49),(0x442c50,0x442c74),(0x463ff0,0x464052),(0x4645e3,0x464601),(0x464560,0x4646db)]:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            spans.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        assert struct.unpack('<I',pe.get_data(0x4921c,4))[0]==0x4492aa
        layout_bodies[label]=pe.get_data(0x464560-0x400000,0x17b)
        assert pe.get_data(0x4623d8-0x400000,6)==bytes.fromhex('66c74054d007')
        assert pe.get_data(0x4624e8-0x400000,3)==bytes.fromhex('0fbff8')
        assert pe.get_data(0x4624f2-0x400000,8)==bytes.fromhex('668b515466895356')
        expected_padding = 5 if label == 'original' else 15
        expected_extent_add = 5 if label == 'original' else 2
        assert pe.get_data(0x4645ea-0x400000,5)==b'\x05'+struct.pack('<I',expected_padding)
        assert pe.get_data(0x4645f8-0x400000,5)==b'\x05'+struct.pack('<I',expected_extent_add)
        # Pin the overlapping-load witness; this is static byte inspection,
        # not execution of the original instructions.
        assert pe.get_data(0x464032-0x400000,3)==bytes.fromhex('8945fc')
        assert pe.get_data(0x464038-0x400000,6)==bytes.fromhex('8b55fac1fa10')
        result.setdefault('field_writer_spans',{})[label]=spans
        result['binary_field_descriptors'][label]={'path':relative,'sha256':expected,'rows':rows}
    cascade_images=[]
    for label in ('original','official_modern'):
        relative=SPECS[label][0];pe=pefile.PE(data=(ROOT/relative).read_bytes())
        cascade_images.append(pe.get_data(0x624a0,0x428))
    cascade_changes=[0x4624a0+i for i,(a,b) in enumerate(zip(*cascade_images)) if a!=b]
    cascade_regions=[(0x4624d2,0x4624d7),(0x462509,0x462525),(0x4625b6,0x4625c0),(0x462658,0x4626bf),(0x4628b7,0x4628c8)]
    assert all(any(lo<=address<hi for lo,hi in cascade_regions) for address in cascade_changes)
    result['cascade_input_difference_coverage']={'start':'004624a0','end_exclusive':'004628c8','original_last_ret':'004628c0','modern_last_jump':'004628c3','changed_addresses':[f'{v:08x}' for v in cascade_changes],'covering_regions':[[f'{lo:08x}',f'{hi:08x}'] for lo,hi in cascade_regions],'scope':'Envelope includes internal/reused tails and original alignment bytes after its last RET; no runtime claim.'}
    initializer_hashes=[next(row['sha256'] for row in result['field_writer_spans'][label] if row['start']=='004623a0') for label in ('original','official_modern')]
    assert initializer_hashes[0]==initializer_hashes[1]
    changed=[0x464560+i for i,(a,b) in enumerate(zip(layout_bodies['original'],layout_bodies['official_modern'])) if a!=b]
    regions=[(0x46456b,0x464587),(0x4645eb,0x4645ec),(0x4645f9,0x4645fa)]
    assert all(any(start<=address<end for start,end in regions) for address in changed)
    assert all(any(start<=address<end for address in changed) for start,end in regions)
    result['complete_layout_helper']={'start':'00464560','end_exclusive':'004646db','length':0x17b,'changed_addresses':[f'{address:08x}' for address in changed],'covering_regions':[[f'{start:08x}',f'{end:08x}'] for start,end in regions],'boundary':'Entry through both observed RET paths; excludes following alignment/data.'}
    # A little-endian DWORD at -6 overlaps the upper two bytes of local -8
    # and the lower two bytes of local -4. SAR16 selects the latter.
    witnesses=[]
    for lookup,count in [(0x12345678,3),(0x87654321,9),(0,16),(0x12345678,32768),(0xffffffff,65535)]:
        stack=struct.pack('<II',lookup,count)
        loaded=struct.unpack('<i',stack[2:6])[0]
        extracted=loaded>>16
        expected=struct.unpack('<h',struct.pack('<H',count & 0xffff))[0]
        assert extracted==expected
        witnesses.append({'lookup_value':lookup,'count':count,'extracted_signed_count_word':extracted})
    result['cascade_count_contract']={'initializer':'004623a0','input_handler':'004624a0','layout_helper':'004628d0','cap_offset':'0x54','effective_count_offset':'0x56','zero_cap_initialization':2000,'selection':'Signed low WORD of count compared with signed cap WORD; ordinary0..32767 gives minimum.','limits':'Callback registration and local consumers verified; active asset selection and callback invocation not observed.'}
    result['overlapping_load']={'interpretation':'signed low WORD of local -4 count; independent of local -8 descriptor value','host_byte_layout_witnesses':witnesses,'scope':'Host byte-layout arithmetic only; no target instructions executed.'}
    result['limits']=['Authored values only; runtime widget counts not measured.','Backup provenance unauthenticated; missing/ambiguous pairs reported.']
    (ROOT/'analysis/evidence/audits/menu-visible-counts.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'menus':len(members),'changed':result['changed'],'unpaired_count':len(result['unpaired']),'backup_only':result['backup_only']},indent=2))


if __name__=='__main__':main()
