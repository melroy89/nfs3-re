"""Static music selection comparison; no audio execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON = [(0x4e8b60,0x4e8bce),(0x4e0dee,0x4e0e2b),(0x4104f0,0x4107b2),(0x4109d0,0x410a3c),
          (0x4e6f0c,0x4e705c),(0x4e73d0,0x4e7466),(0x4e7470,0x4e74e1)]
RETAINED = [(0x4e8b60,0x4e8bce),(0x4e0dee,0x4e0e2b),(0x4104f0,0x41057f),(0x4106b8,0x4107b2),
            (0x4109d0,0x410a3c),(0x4e6f0c,0x4e705c),
            (0x4e73d0,0x4e7466),(0x4e7470,0x4e74e1)]

SPANS = {'original': [(0x40ffd0,0x410027),(0x410030,0x410329),(0x4103a0,0x41045d),
        (0x4a3690,0x4a38bc),(0x4107c0,0x4109cc),
        (0x418620,0x418670),(0x4187e0,0x41883f)],
    'official_modern': [(0x40fefc,0x40ff80),(0x40ff9c,0x40fffb),
        (0x4103a0,0x410446),(0x410606,0x410615),
        (0x4b5d21,0x4b5d3a),(0x4a33f0,0x4a354b),
        (0x40fed0,0x40fefa),(0x51778c,0x5177de),
        (0x4a3690,0x4a38bc),(0x4a35d0,0x4a3681),
        (0x4107c0,0x41099b),(0x418620,0x418644),
        (0x4187e0,0x41880c),(0x438100,0x43812f)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/music-selection'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-music-selection-comparison','range_end':'exclusive','binaries':{},
        'limits':['No sound/game/instruction execution.','Audible track identity, RNG distribution and complete playback-route coverage unverified.']}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in SPANS[label]+COMMON:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows}
        adjustments=list(struct.unpack('<10i',pe.get_data(0x1525d0,40)))
        assert adjustments==([15,6,15,0,15,6,15,0,0,0] if label=='original' else [0]*10)
        item['file_backed_level_adjustments_005525d0']=adjustments
        descriptor=struct.unpack('<5I',pe.get_data(0x156be0,20))
        assert descriptor[0]==0x5382a8 and descriptor[4]==0x6fbbe4
        assert pe.get_data(0x1382a8,16).split(b'\0')[0]==b'tunenames'
        ids=[]
        for i in range(24):
            ident=struct.unpack('<H',pe.get_data(descriptor[1]-0x400000+2*i,2))[0]
            if ident==0:break
            ids.append(ident)
        expected_ids=([463,464,465]+list(range(162,173)) if label=='original'
                      else [465,463,464]+list(range(162,172))+[1943,1941,1942])
        assert ids==expected_ids
        item['race_choice_descriptor_00556be0']=[f'{v:08x}' for v in descriptor]
        item['race_choice_label_ids']=ids
        tracks_descriptor=struct.unpack('<5I',pe.get_data(0x1563fc,20))
        assert tracks_descriptor[4]==0x6fd4ac
        assert pe.get_data(tracks_descriptor[0]-0x400000,16).split(b'\0')[0]==b'tracks'
        item['tracks_descriptor_005563fc']=[f'{v:08x}' for v in tracks_descriptor]
        menu_descriptor=struct.unpack('<5I',pe.get_data(0x156bf4,20))
        assert menu_descriptor[0]==0x5382b4 and menu_descriptor[4]==0x6fbbec
        assert pe.get_data(0x1382b4,16).split(b'\0')[0]==b'menutunes'
        menu_ids=[]
        for i in range(24):
            ident=struct.unpack('<H',pe.get_data(menu_descriptor[1]-0x400000+2*i,2))[0]
            if ident==0:break
            menu_ids.append(ident)
        assert menu_ids==([466]+list(range(467,474)) if label=='original' else [1946,1944,1945]+list(range(467,474)))
        item['menu_choice_descriptor_00556bf4']=[f'{v:08x}' for v in menu_descriptor]
        item['menu_choice_label_ids']=menu_ids
        if label=='official_modern':
            item['menu_cycle_ids']=list(pe.get_data(0x40ff80-0x400000,6))
            item['menu_seed_map']=list(pe.get_data(0x40ff88-0x400000,20))
        else:
            pointers=struct.unpack('<10I',pe.get_data(0x1525a8,40))
            item['original_track_stems_005525a8']=[{'index':i,'pointer':f'{pointer:08x}','stem':pe.get_data(pointer-0x400000,32).split(b'\0')[0].decode()} for i,pointer in enumerate(pointers)]
            assert [row['stem'] for row in item['original_track_stems_005525a8']]==['home','lost','atla','alpi','home','lost','atla','alpi','empr','chuck']
            item['style_tokens']={f'{a:08x}':pe.get_data(a-0x400000,16).split(b'\0')[0].decode() for a in (0x536898,0x5368a4,0x5368d8,0x5368e0)}
            item['fixed_race_targets']=[f'{v:08x}' for v in struct.unpack('<10I',pe.get_data(0x40ffa4-0x400000,40))]
        result['binaries'][label]=item
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    ids=sorted({ident for item in result['binaries'].values() for ident in item['race_choice_label_ids']+item['menu_choice_label_ids']})
    labels={}
    for ident in ids:
        offset=struct.unpack_from('<I',english,4*ident)[0]
        labels[str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    result['official_english']={'member':'fedata/text/text.eng','sha256':hashlib.sha256(english).hexdigest(),'labels':labels}
    result['limits'].append('Original list IDs decoded with official Modern English; original retail language provenance unverified.')
    original=images['original'].get_data(0xa3690,0x22c)
    modern=images['official_modern'].get_data(0xa3690,0x22c)
    changed=[0x4a3690+i for i,(a,b) in enumerate(zip(original,modern)) if a!=b]
    assert changed==list(range(0x4a36c6,0x4a36e1))+list(range(0x4a36f9,0x4a36fb))
    assert images['official_modern'].get_data(0xa36c6,2)==bytes.fromhex('eb19')
    assert images['official_modern'].get_data(0xa36c8,25)==b'\x90'*25
    result['race_session_outer_changed_byte_ranges']=[['004a36c6','004a36e1'],['004a36f9','004a36fb']]
    result['identical_music_ranges']=[]
    for start,end in RETAINED:
        data=images['original'].get_data(start-0x400000,end-start)
        assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_music_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}',
            'sha256':hashlib.sha256(data).hexdigest()})
    (ROOT/'analysis/evidence/audits/original-modern-music-selection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: music baselines, selection spans and menu cycle tables')


if __name__=='__main__':main()
