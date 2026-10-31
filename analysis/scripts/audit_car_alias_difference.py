"""Static list-render alias comparison; no UI or target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-car-list-alias-comparison','range_end':'exclusive','binaries':{}};images={}
    capture=ROOT/'analysis/captures/modern-differences/car-alias';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=[(0x4d0d50,0x4d0ff9),(0x4d1390,0x4d13f3),(0x4d0dfb,0x4d0e35),(0x4d1400,0x4d140f),(0x4d1410,0x4d1422),(0x4d06f0,0x4d0a0f),(0x4d1480,0x4d14ee),(0x4d1000,0x4d10d8),(0x4d06f0,0x4d071b),(0x4d09f2,0x4d0a0f),(0x4dfd56,0x4dfd73 if label=='original' else 0x4dfd6d),(0x452100,0x45210a),(0x4d1430,0x4d1471 if label=='original' else 0x4d1450),(0x461a70,0x461a96),(0x452020,0x45208c),(0x4628d0,0x4629bf),(0x4634d0,0x463ddc),(0x463841,0x463859),(0x463875,0x463894),(0x4638a7,0x4638f4),(0x461d25,0x461d51),(0x463b74,0x463bc5),(0x4e9ec0,0x4e9efb)]
        if label=='official_modern':spans.extend([(0x4728f4,0x472923),(0x472924,0x472959),(0x4628ec,0x46291a),(0x4634e7,0x463501),(0x46456d,0x464587),(0x4645e3,0x464609)])
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        strings={f'{a:08x}':pe.get_data(a-0x400000,40).split(b'\0')[0].decode('ascii') for a in (0x53aa34,0x537e80,0x537c34,0x537e88)}
        assert list(strings.values())==['cars','cars','car2','carShowcase']
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'strings':strings}
    old,new=[images[k] for k in ('original','official_modern')]
    assert old.get_data(0xe9ec0,59)==new.get_data(0xe9ec0,59)
    for address in (0x463b7c,0x463baf):
        for pe,target in ((old,0x4e9ec0),(new,0x4728f4)):
            data=pe.get_data(address-0x400000,5);assert data[0]==0xe8
            assert address+5+int.from_bytes(data[1:],'little',signed=True)==target
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    members=subprocess.check_output(['7z','l','-slt',str(archive)]).decode().splitlines()
    menus=[line[7:] for line in members if line.startswith('Path = fedata/menus/') and line.lower().endswith('.mnu')]
    assert len(menus)==52
    matches=[]
    for member in menus:
        data=subprocess.check_output(['7z','x','-so',str(archive),member])
        section='';fields=[]
        for number,line in enumerate(data.decode('latin1').splitlines(),1):
            if line.startswith('['):section=line
            if line.lower() in ('listname=cars','listname=car2','listname=carshowcase'):
                fields.append({'line':number,'section':section,'field':line})
        if fields:matches.append({'member':member,'sha256':hashlib.sha256(data).hexdigest(),'matches':fields})
    assert sum(len(row['matches']) for row in matches)==10
    result['font_filename_formats']={label:{f'{address:08x}':pe.get_data(address-0x400000,24).split(b'\0')[0].decode('ascii') for address in (0x540b94,0x540ba4,0x540bb0)} for label,pe in images.items()}
    assert all(list(row.values())==['%sCP16BI.ffn','%sCP1BI.ffn','%ssmall6.ffn'] for row in result['font_filename_formats'].values())
    result['font_asset_inventory']={'official_archive_ffn_members':[line[7:] for line in members if line.startswith('Path = ') and line.lower().endswith('.ffn')],'local_pairs':[]}
    for name in ('CP16BI.FFN','CP1BI.FFN','SMALL6.FFN'):
        base=ROOT/'nfs3_decomp.rep/Electronic Arts/Need For Speed III'
        paths=[base/'gamedata_org/DashHud'/name,base/'GAMEDATA/DASHHUD'/name]
        values=[path.read_bytes() for path in paths]
        result['font_asset_inventory']['local_pairs'].append({'name':name,'files':[{'path':str(path.relative_to(ROOT)),'length':len(data),'sha256':hashlib.sha256(data).hexdigest()} for path,data in zip(paths,values)],'byte_identical':values[0]==values[1],'provenance':'Local backup and installed copies; not authenticated retail or packaged Modern replacements.'})
    result['official_menu_scan']={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'menu_count':len(menus),'matching_members':matches}
    for start,end in [(0x463841,0x463859),(0x463875,0x463894),(0x4638a7,0x4638f4)]:
        assert old.get_data(start-0x400000,end-start)==new.get_data(start-0x400000,end-start)
    result['track_policy_strings']={f'{a:08x}':new.get_data(a-0x400000,32).split(b'\0')[0].decode('ascii') for a in (0x537e34,0x5382ec,0x53aa3c)}
    assert list(result['track_policy_strings'].values())==['tracks','rectrk','tracks']
    start,end=0x4628d0,0x4629bf
    a,b=[pe.get_data(start-0x400000,end-start) for pe in (old,new)]
    changes=[start+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    regions=[(0x4628ea,0x46291a),(0x462972,0x462973),(0x462980,0x462981)]
    assert all(any(lo<=address<hi for lo,hi in regions) for address in changes)
    assert old.get_data(0x62971,5)==bytes.fromhex('0505000000')
    assert new.get_data(0x62971,5)==bytes.fromhex('050f000000')
    assert old.get_data(0x6297f,5)==bytes.fromhex('0505000000')
    assert new.get_data(0x6297f,5)==bytes.fromhex('0502000000')
    result['complete_004628d0']={'end_exclusive':f'{end:08x}','length':end-start,'changed_addresses':[f'{address:08x}' for address in changes],'covering_regions':[[f'{lo:08x}',f'{hi:08x}'] for lo,hi in regions],'scope':'Entry through both observed RETs; excludes alignment and next function.'}
    result['retained_layout_dependencies']=[]
    for start,end in [(0x461a70,0x461a96),(0x452020,0x45208c),(0x452100,0x45210a),(0x4d1000,0x4d10d8),(0x4d06f0,0x4d071b),(0x4d09f2,0x4d0a0f),(0x4d06f0,0x4d0a0f),(0x4d1480,0x4d14ee),(0x4d1390,0x4d13f3),(0x4d0dfb,0x4d0e35),(0x4d1400,0x4d140f),(0x4d1410,0x4d1422),(0x4d0d50,0x4d0ff9)]:
        a,b=[pe.get_data(start-0x400000,end-start) for pe in (old,new)]
        assert a==b
        result['retained_layout_dependencies'].append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','length':end-start,'sha256':hashlib.sha256(a).hexdigest(),'byte_identical':True})
    def call_target(pe,address):
        data=pe.get_data(address-0x400000,5);assert data[0]==0xe8
        return address+5+int.from_bytes(data[1:],'little',signed=True)
    assert call_target(old,0x4d144e)==call_target(new,0x4d143f)==0x4d1000
    assert call_target(old,0x4d1453)==0x4dfd56
    assert old.get_data(0xd1458,3)==bytes.fromhex('db5df8')
    assert old.get_data(0xd1467,3)==bytes.fromhex('db45fc')
    assert new.get_data(0xd1435,6)==bytes.fromhex('ff053c1b5600')
    assert new.get_data(0xd1444,6)==bytes.fromhex('ff0d3c1b5600')
    result['x87_measurement_wrapper']={'entry':'004d1430','original_end_exclusive':'004d1471','modern_end_exclusive':'004d1450','shared_callee':'004d1000','original_conversion':'call004dfd56; FISTP signed DWORD; FILD signed DWORD','modern_conversion':'No local x87 conversion; return callee state','shared_global':'00561b3c','scope':'Static local instructions; callee and runtime values unresolved.'}
    result['glyph_storage_sections']={}
    for label,pe in images.items():
        section=next(s for s in pe.sections if s.Name.startswith(b'.bss'))
        assert section.PointerToRawData==0 and section.IMAGE_SCN_CNT_UNINITIALIZED_DATA
        addresses=[0x83f4e0,0x83f700,0x83f8c0,0x83fc40,0x83fe00,0x840184,0x84018c]
        lo=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
        hi=lo+max(section.Misc_VirtualSize,section.SizeOfRawData)
        assert all(lo<=address<hi for address in addresses)
        result['glyph_storage_sections'][label]={'section':'.bss','start':f'{lo:08x}','extent_from_section_header':f'{hi-lo:08x}','virtual_size':section.Misc_VirtualSize,'raw_size_field':section.SizeOfRawData,'raw_pointer':section.PointerToRawData,'characteristics':f'{section.Characteristics:08x}','addresses':[f'{address:08x}' for address in addresses],'interpretation':'Uninitialized storage; no file-backed glyph metrics inferred.'}
    result['font_scale_factor']={}
    for label,pe in images.items():
        data=pe.get_data(0x140bc8,4);assert data==bytes.fromhex('cdcc4c3b')
        section=next(s for s in pe.sections if s.VirtualAddress<=0x140bc8<s.VirtualAddress+s.SizeOfRawData and s.PointerToRawData!=0)
        result['font_scale_factor'][label]={'address':'00540bc8','bytes':data.hex(),'section':section.Name.decode().rstrip('\0'),'file_offset':section.PointerToRawData+0x140bc8-section.VirtualAddress}
    start,end=0x4634d0,0x463ddc
    a,b=[pe.get_data(start-0x400000,end-start) for pe in (old,new)]
    changed=[start+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    regions=[(0x4634e1,0x463501),(0x463b7d,0x463b80),(0x463bb0,0x463bb3)]
    assert len(changed)==36
    assert all(any(lo<=address<hi for lo,hi in regions) for address in changed)
    assert all(any(lo<=address<hi for address in changed) for lo,hi in regions)
    assert a[-1:]==b[-1:]==b'\xc3'
    result['complete_004634d0']={'start':f'{start:08x}','end_exclusive':f'{end:08x}','length':end-start,'changed_addresses':[f'{v:08x}' for v in changed],'covering_regions':[[f'{lo:08x}',f'{hi:08x}'] for lo,hi in regions],'boundary':'Observed entry to final RET; not imported from an assumed original Ghidra function boundary.'}
    result['additional_track_policy_callers']={
        '004628d0':{'name_offset':'0x60','original':'35 for tracks/rectrk in any mode; otherwise15','modern':'35 only for mode3 and tracks/rectrk; otherwise15'},
        '004634d0':{'name_offset':'0x64','original':'35 for every mode3 name; otherwise15','modern':'35 only for mode3 and tracks/rectrk; otherwise15'},
        'scope':'Complete 004628d0 and 004634d0 paired bodies; no runtime claim.'}
    assert old.get_data(0x13aa9c,7)==new.get_data(0x13aa9c,7)==b'rectrk\0'
    for address in (0x4628ef,0x4634ea):
        data=new.get_data(address-0x400000,5)
        assert data[0]==0xe8 and address+5+int.from_bytes(data[1:],'little',signed=True)==0x472924
    result['limits']=['Static alias and caller policy only; full renderer and asset bindings not audited.','No UI display or language-dependent output observed.']
    (ROOT/'analysis/evidence/audits/original-modern-car-alias.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired call retargeting, aliases and identical ASCII comparator')


if __name__=='__main__':main()
