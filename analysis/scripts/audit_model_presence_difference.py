"""Static model-key presence predicate correspondence."""
import hashlib
import json
import subprocess
import struct
from decode_logo_refpack import decode
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-model-presence-comparison','range_end':'exclusive','binaries':{}};images={}
    capture=ROOT/'analysis/captures/modern-differences/model-presence';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=[(0x4a44c3,0x4a45c7),(0x4dfd56,0x4dfd6d),(0x438ad0,0x438aed),(0x439990,0x4399e4),(0x4a40c0,0x4a4386 if label=='original' else 0x4a4371),(0x4270c0,0x427182),(0x460478,0x46048e)]
        spans += [(0x439ce0,0x439d12),(0x4a4390,0x4a440d)] if label=='original' else [(0x439cd4,0x439cfd),(0x439d00,0x439d19),(0x4a4374,0x4a443f),(0x4a444c,0x4a44c3),(0x4a457b,0x4a45bf),(0x4d7d90,0x4d7dc7),(0x4d6070,0x4d6109),(0x4f24e0,0x4f255e),(0x4ea658,0x4ea665)]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        data=pe.get_data(0x27142,5);assert data[0]==0xe8
        target=0x427147+int.from_bytes(data[1:],'little',signed=True)
        assert target==(0x439ce0 if label=='original' else 0x439d00)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'paired_caller_target':f'{target:08x}'}
    result['animation_scale_constant']={}
    for label,pe in images.items():
        raw=pe.get_data(0x13cf04,8);assert struct.unpack('<d',raw)[0]==0.8
        result['animation_scale_constant'][label]={'address':'0053cf04','bytes':raw.hex(),'binary64':0.8}
    result['file_backed_animation_initial_state']={}
    for label,pe in images.items():
        rows=[]
        for address,expected_value in [(0x55e984,0),(0x55e95c,-1)]:
            rva=address-0x400000;section=pe.get_section_by_rva(rva)
            assert section.PointerToRawData and rva-section.VirtualAddress+4<=section.SizeOfRawData
            value=struct.unpack('<i',pe.get_data(rva,4))[0];assert value==expected_value
            rows.append({'address':f'{address:08x}','signed_value':value,'file_offset':pe.get_offset_from_rva(rva)})
        result['file_backed_animation_initial_state'][label]=rows
    result['logo_loader_source_strings']={}
    for label,pe in images.items():
        result['logo_loader_source_strings'][label]={f'{a:08x}':pe.get_data(a-0x400000,24).split(b'\0')[0].decode('ascii') for a in (0x53cf0c,0x53cf18,0x53cf20,0x53a970)}
    result['background_resource_strings']={}
    for label,pe in images.items():
        name=pe.get_data(0x137090,12).split(b'\0')[0].decode('ascii');assert name=='opp1.qfs'
        result['background_resource_strings'][label]=name
    old,new=[images[k] for k in ('original','official_modern')]
    a,b=[p.get_data(0x270c0,0xc2) for p in (old,new)]
    changed=[0x4270c0+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert all(0x427143<=address<0x427147 for address in changed)
    result['background_caller_changed_addresses']=[f'{address:08x}' for address in changed]
    for start,end in [(0x438ad0,0x438aed),(0x439990,0x4399e4)]:
        a,b=[p.get_data(start-0x400000,end-start) for p in images.values()];assert a==b
    assert new.get_data(0x13cf0c,32).split(b'\0')[0]==b'logos.qfs'
    result['modern_logo_archive_name']='logos.qfs'
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    packed=subprocess.check_output(['7z','x','-so',str(archive),'fedata/art/logos.qfs'])
    decoded=decode(packed)
    assert decoded[:4]==b'SHPI' and len(decoded)==524516
    tables=[];start=0
    while True:
        offset=decoded.find(b'LTBL',start)
        if offset<0:break
        count=struct.unpack_from('<I',decoded,offset+4)[0]
        records=[list(struct.unpack_from('<III',decoded,offset+8+12*j)) for j in range(count)]
        tables.append({'decoded_offset':offset,'count':count,'records':records,'payload_words':[[r[1]&0xffff,r[1]>>16,r[2]&0xffff,r[2]>>16] for r in records]});start=offset+4
    assert [t['count'] for t in tables]==[6,5]
    assert [[r[0] for r in t['records']] for t in tables]==[[0]*6,[0,37,38,26,27]]
    links=[]
    assert new.get_data(0x166d54+0x7d,1)==b'\x20'
    assert struct.unpack_from('<I',decoded,8)[0]==2
    for j in range(2):
        name,offset=struct.unpack_from('<4sI',decoded,16+8*j)
        header=struct.unpack_from('<I',decoded,offset)[0]
        assert header==0x0400107d
        next_offset=offset+(header>>8)
        assert decoded[next_offset]==0x6f
        assert decoded[next_offset+8:next_offset+12]==b'LTBL'
        assert next_offset+8==tables[j]['decoded_offset']
        links.append({'entry_name':name.decode(),'entry_offset':offset,'header':f'{header:08x}','metadata_offset':next_offset,'returned_ltbl_offset':next_offset+8})
    result['logo_metadata_links']=links
    result['official_logo_asset']={'member':'fedata/art/logos.qfs','packed_sha256':hashlib.sha256(packed).hexdigest(),'decoded_sha256':hashlib.sha256(decoded).hexdigest(),'decoded_size':len(decoded),'ltbl_magic_scan':tables}
    result['limits']=['No resource lookup or target instruction execution.','Selectors 0x25/0x26 are raw values; human-readable identities and list initialization remain unresolved.']
    (ROOT/'analysis/evidence/audits/original-modern-model-presence.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired presence policy, shared caller and identical key construction/search bodies')


if __name__=='__main__':main()
