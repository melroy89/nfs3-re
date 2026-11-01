"""Parse all six retained1.5.0/1.5.1 text assets; no game/text-loader execution."""
import hashlib
import difflib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_historical_lockwindow_failure import ARCHIVES
from audit_dx5_reference_final import disassemble


def parse(raw):
    first=struct.unpack_from('<I',raw)[0]
    assert first%4==0
    count=first//4
    assert count in (1936,1941)
    offsets=struct.unpack_from('<'+'I'*count,raw)
    assert offsets[0]==first and all(a<b for a,b in zip(offsets,offsets[1:]))
    records=[]
    for i,offset in enumerate(offsets):
        end=raw.index(0,offset)
        bound=offsets[i+1] if i+1<count else len(raw)
        assert end+1==bound
        records.append(raw[offset:end])
    return offsets,records


def display(raw):
    return {'hex':raw.hex(),'latin1_display':raw.decode('latin1')}


def main():
    result={'kind':'historical-localization-151','archives':{},'languages':{},
            'indexing':'zero-based positional entries, not independently named game string IDs',
            'limits':['Static packaged assets only; no game loader/rendering or translation-quality review.',
                      'Latin1 is a reversible display convention, not proof of game font/encoding.',
                      'Five added records and changed existing indices do not independently verify every advertised correction.']}
    assets={}
    menus={}
    helper_images=[]
    capture=ROOT/'analysis/captures/modern-differences/localization-151'
    capture.mkdir(parents=True,exist_ok=True)
    for version,expected in ARCHIVES.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        path=ROOT/relative
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        result['archives'][version]={'path':relative,'sha256':expected}
        exe_raw=subprocess.check_output(['7z','x','-so',str(path),'nfs3.exe'])
        expected_exe={'1.5.0':'d9db8ead63a9697c4c6c3933e720cd93565f67bd4b264e8bbc0d98d03c236dae',
                      '1.5.1':'4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17'}[version]
        assert hashlib.sha256(exe_raw).hexdigest()==expected_exe
        pe=pefile.PE(data=exe_raw)
        unit_index=struct.unpack('<I',pe.get_data(0x565f3,4))[0]
        maximum=struct.unpack('<I',pe.get_data(0xd1851,4))[0]
        assert (unit_index,maximum)==((1932,1935) if version=='1.5.0' else (1936,1940))
        descriptor=struct.unpack('<5I',pe.get_data(0x1567a8,20))
        assert descriptor==(0x538008,0x5562d2,0,0,0x6fbc4c)
        assert pe.get_string_at_rva(0x138008)==b'widescreen'
        frame_ids=struct.unpack('<3H',pe.get_data(0x1562d2,6))
        assert frame_ids==((184,1933,0) if version=='1.5.0' else (1932,1933,0))
        helper_images.append(pe.get_data(0x56590,0xaa))
        spans=[]
        for lo,hi in [(0x456590,0x45663a),(0x4d1850,0x4d187e)]:
            code=pe.get_data(lo-0x400000,hi-lo)
            out=capture/f'{version}-{lo:08x}.asm'
            out.write_text('\n'.join(disassemble(code,lo))+'\n')
            spans.append({'start':f'{lo:08x}','end_exclusive':f'{hi:08x}',
                'bytes_sha256':hashlib.sha256(code).hexdigest(),'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        result['archives'][version]['exe_consumer']={'sha256':expected_exe,'member':'nfs3.exe',
            'track_length_unit_index':unit_index,'lookup_maximum_index':maximum,'spans':spans,
            'frame_descriptor_address':'005567a8','frame_descriptor_dwords':[f'{x:08x}' for x in descriptor],
            'frame_label_list_address':'005562d2','frame_label_words':list(frame_ids)}
        for name in ('camera','graphics'):
            member=f'fedata/menus/{name}.mnu'
            raw=subprocess.check_output(['7z','x','-so',str(path),member])
            menus[version,name]=raw
        for lang in ('eng','ger','fre','spa','ita','swe'):
            member=f'fedata/text/text.{lang}'
            raw=subprocess.check_output(['7z','x','-so',str(path),member])
            offsets,records=parse(raw)
            assets[version,lang]=(offsets,records)
            result['languages'].setdefault(lang,{})[version]={'member':member,
                'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                'entries':len(records),'offset_table_bytes':offsets[0],
                'complete_payload_partition':True}
    result['selected_menu_changes']={}
    for name in ('camera','graphics'):
        a=menus['1.5.0',name];b=menus['1.5.1',name]
        old=a.decode('latin1').splitlines();new=b.decode('latin1').splitlines()
        changes=[(tag,i,j,k,l) for tag,i,j,k,l in difflib.SequenceMatcher(a=old,b=new).get_opcodes() if tag!='equal']
        if name=='camera':
            assert all(tag=='insert' for tag,*_ in changes)
            assert sum(l-k for tag,i,j,k,l in changes)==15
            assert a.count(b'listname=rearcamera')==0 and b.count(b'listname=rearcamera')==2
            assert b'text=lang1938' in b and b'maxvisitem=5' in b
        else:
            assert a.replace(b'text=lang1537',b'text=lang1937')==b
            assert a.count(b'text=lang1537')==1
        result['selected_menu_changes'][name]={
            'old_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),
            'member':f'fedata/menus/{name}.mnu',
            'line_diff':list(difflib.unified_diff(old,new,fromfile='1.5.0',tofile='1.5.1',n=2))}
    assert assets['1.5.0','eng'][1][1537]==assets['1.5.1','eng'][1][1537]==b'Rear View Mirror'
    assert [0x456590+i for i,(a,b) in enumerate(zip(*helper_images)) if a!=b]==[0x4565f3]
    for lang,row in result['languages'].items():
        old_offsets,old=assets['1.5.0',lang];new_offsets,new=assets['1.5.1',lang]
        changed=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
        assert changed==([1283,1932] if lang=='fre' else [1932])
        assert old[1932]==new[1936]==b'km'
        row['track_length_token_preserved']=True
        assert old[1933]==new[1933]==b'2:1'
        row['frame_first_choice']={'old_index':184,'old':display(old[184]),'new_index':1932,'new':display(new[1932]),
            'second_choice_unchanged':1933}
        row['changed_existing']=[{'index':i,'old_offset':old_offsets[i],'new_offset':new_offsets[i],
            'old':display(old[i]),'new':display(new[i])}for i in changed]
        row['added']=[{'index':i,'offset':new_offsets[i],'value':display(new[i])}for i in range(len(old),len(new))]
    (ROOT/'analysis/evidence/audits/historical-localization-151.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('PASS: two archives, twelve complete text-table partitions, exact changed/additional entries')


if __name__=='__main__':
    main()
