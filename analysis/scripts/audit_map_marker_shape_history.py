"""Bound map-marker smoothing claim with retained code and local/150 HUD asset."""
import collections,hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def shape(raw):
    assert raw[:4]==b'SHPI'and struct.unpack_from('<I',raw,4)[0]==len(raw)
    count=struct.unpack_from('<I',raw,8)[0];assert count==25
    directory=[struct.unpack_from('<4sI',raw,16+8*i)for i in range(count)]
    offsets=[a for _,a in directory];assert offsets==sorted(offsets)and offsets[0]>=16+8*count
    assert len(set(n for n,_ in directory))==count
    offset=dict(directory)[b'1555'];assert offset==0x40110
    assert raw[offset]==0x7d and struct.unpack_from('<HH',raw,offset+4)==(32,32)
    start=offset+16;end=start+32*32*4
    assert end<=offsets[directory.index((b'1555',offset))+1]
    hist=collections.Counter(raw[start+3:end:4])
    return {'directory_sha256':sha(raw[:16+8*count]),'shape_offset':offset,'header_hex':raw[offset:offset+16].hex(),
            'payload_start':start,'payload_end_exclusive':end,'payload_sha256':sha(raw[start:end]),
            'highest_byte_histogram':{str(k):v for k,v in sorted(hist.items())},
            'intermediate_highest_byte_pixels':sum(v for k,v in hist.items()if k not in (0,255))}


def main():
    result={'kind':'static-map-marker-shape-history','versions':{}};bodies=[]
    spans=[('map_renderer',0x48d4c0,0x48e76d),('marker_rectangle',0x48cc60,0x48cce8),
           ('hud_loader',0x47f590,0x47f645),('batch_initializer',0x484070,0x484211),
           ('shape_depth',0x499e90,0x499ea0),('hue_shape_producer',0x43db20,0x43dbd4),
           ('opaque_colour_packer',0x43de20,0x43de60),('argb_compositor_admission',0x523760,0x5237c6),
           ('argb_blend_weights',0x52387e,0x5238bf)]
    new_asset=None
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        assert get(0x566d54+0x7d,0x566d54+0x7e)==b'\x20'
        assert get(0x43de48,0x43de4d).hex()=='0d000000ff'
        assert get(0x52379f,0x5237aa).hex()=='89cbc1eb1881e3ff000000'
        bs=[get(a,b)for _,a,b in spans];bodies.append(bs)
        assert get(0x48cc84,0x48cc89).hex()=='6848da7600'
        assert get(0x47f5d6,0x47f5e5).hex()=='b9941a7900bb20000000baf0b45300'
        assert pe.get_string_at_rva(0x13b4f0)==b'1555'
        assert get(0x484174,0x48417f).hex()=='b848da76008b15981a7900'
        listing=subprocess.check_output(['7z','l','-slt',str(archive)],text=True)
        paths=[l[7:]for l in listing.splitlines()if l.startswith('Path = ')]
        members=[p for p in paths if p.lower().endswith('hud98.fsh')]
        row={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'hud98_members':members,
             'selected_code':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','bytes':b-a,'sha256':sha(get(a,b))}for n,a,b in spans]}
        if version=='1.4.0':assert members==[]
        else:
            assert members==['gamedata/dashhud/hud98.fsh']
            new_asset=subprocess.check_output(['7z','x','-so',str(archive),members[0]])
            assert sha(new_asset)=='86fbd66db92a554e293ebe4a03cf5f42c765152a8ae59053671f37b1552c515c'
            row['asset']={'member':members[0],'sha256':sha(new_asset),'bytes':len(new_asset),'shape1555':shape(new_asset)}
        result['versions'][version]=row
    assert bodies[0]==bodies[1]
    backup='nfs3_decomp.rep/Electronic Arts/Need For Speed III/gamedata_org/DashHud/HUD98.FSH'
    old=(ROOT/backup).read_bytes();assert sha(old)=='775348ef2840d54851f6249d40239315d013f398c54ea72600ff9d5977649c9e'
    old_shape=shape(old);new_shape=shape(new_asset);start,end=old_shape['payload_start'],old_shape['payload_end_exclusive']
    assert len(old)==len(new_asset)and old[:start]==new_asset[:start]and old[end:]==new_asset[end:]
    changed=sum(a!=b for a,b in zip(old,new_asset));assert changed==1050
    assert old_shape['intermediate_highest_byte_pixels']==0 and new_shape['intermediate_highest_byte_pixels']==116
    center=start+4*(16*32+16)
    assert old[center:center+4]==new_asset[center:center+4]==bytes.fromhex('7d7d7dff')
    result['local_backup']={'path':backup,'sha256':sha(old),'bytes':len(old),'shape1555':old_shape,'retail_provenance_verified':False}
    result['format_correspondence']={'depth_lookup_base':'00566d54','format7d_depth':32,
        'builtin_shape_producer':'0043db20 writes type7d and DWORD pixels from0043de20',
        'packer':'0043de20 packs three low8 channels into bits16/8/0 and ORsff000000',
        'compositor':'0052379f shifts packed input24;zero returns without drawing,255 branches to opaque path,intermediate to blend path',
        'scope':'Corroborates ARGB/alpha interpretation;does not prove this map texture traverses that raster compositor.'}
    result['comparison']={'changed_bytes':changed,'all_changes_within_1555_pixel_payload':True,'all_other_file_bytes_identical':True,
        'selected_code_identical140_150':True}
    result['verified']=['140 has no HUD98 archive member;150 bundles it;selected map/helper/loader/batch bodies are byte-identical.',
        'Loader requests tag1555 into00791a94;batch init uses its+4 cell00791a98 for0076da48;marker helper submits that batch address.',
        'Pinned local backup versus150 asset differs only within32x32 type7d payload1555:1050 bytes,116 new intermediate highest-byte pixels.']
    result['limits']=['Local backup is not authenticated retail or a demonstrated140 installed asset;absence in140 archive does not prove absence in game.',
        'Highest-byte softening is consistent with alpha-edge smoothing;complete conversion/upload/blend/rendered effect not validated.',
        'Builtin32-bit shape producer and ARGB compositor corroborate alpha interpretation,not proof this texture uses that compositor.',
        'No universal visual identity of all markers,all caller roles,asset path selection or successful renderer acceptance established.',
        'No target/API/instruction execution,compilation or Ghidra changes;only hashes/statistics published,not game pixel data.']
    (ROOT/'analysis/evidence/audits/map-marker-shape-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:retained map draw chain;150 HUD1555 differs only in pixels versus pinned local backup,116 intermediate high-byte pixels')


if __name__=='__main__':main()
