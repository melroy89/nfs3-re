"""Static PE resource identities, icon-group references and manifest XML fields."""
import hashlib,json,struct
import xml.etree.ElementTree as ET
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    specs={k:(v[0],v[1]) for k,v in SPECS.items()}
    specs['local_analysis']=('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe',
        '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb')
    out={'kind':'three-baseline-pe-resource-payload-comparison','binaries':{}}
    blobs={}
    for label,(relative,expected) in specs.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);resources={};payloads={}
        for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            for name in kind.directory.entries:
                for lang in name.directory.entries:
                    key=f'{kind.id}/{name.name if name.name is not None else name.id}/{lang.id}'
                    d=lang.data.struct;data=pe.get_data(d.OffsetToData,d.Size)
                    assert len(data)==d.Size
                    resources[key]={'rva':f'{d.OffsetToData:08x}','size':d.Size,
                        'file_offset':f'{pe.get_offset_from_rva(d.OffsetToData):08x}',
                        'sha256':hashlib.sha256(data).hexdigest()}
                    payloads[key]=data
        groups={}
        for key,data in payloads.items():
            if not key.startswith('14/'):continue
            reserved,kind,count=struct.unpack_from('<HHH',data)
            assert (reserved,kind)==(0,1) and len(data)==6+14*count
            entries=[]
            for i in range(count):
                w,h,col,res,planes,bits,size,ident=struct.unpack_from('<BBBBHHIH',data,6+14*i)
                target=f'3/{ident}/{key.rsplit("/",1)[1]}'
                assert res==0 and target in payloads and len(payloads[target])==size
                payload=payloads[target]
                if payload.startswith(b'\x89PNG\r\n\x1a\n'):
                    assert payload[12:16]==b'IHDR'
                    pw,ph=struct.unpack_from('>II',payload,16)
                    payload_header={'format':'PNG','width':pw,'height':ph}
                    assert (pw,ph)==(256,256)
                else:
                    header_size,pw,ph,pp,pb=struct.unpack_from('<IiiHH',payload)
                    assert header_size==40 and (pw,ph,pp,pb)==(w,2*h,planes,bits)
                    payload_header={'format':'BITMAPINFOHEADER','width':pw,
                                    'stored_height_with_masks':ph,'bit_count':pb}
                entries.append({'width_byte':w,'height_byte':h,'color_count':col,
                    'planes':planes,'bit_count':bits,'payload_bytes':size,
                    'icon_id':ident,'target_resource':target,'payload_header':payload_header})
            groups[key]=entries
        manifests={}
        for key,data in payloads.items():
            if not key.startswith('24/'):continue
            root=ET.fromstring(data)
            manifests[key]={'root':root.tag,'root_attributes':root.attrib,
                'elements':[{'tag':e.tag,'attributes':e.attrib} for e in root.iter() if e is not root]}
        section=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.rsrc')
        out['binaries'][label]={'path':relative,'sha256':expected,'resources':resources,
            'resource_count':len(resources),'payload_byte_sum':sum(len(b) for b in payloads.values()),
            'section_raw_bytes':section.SizeOfRawData,'icon_groups':groups,'manifests':manifests}
        blobs[label]=payloads
    old,new,local=[blobs[k] for k in ('original','official_modern','local_analysis')]
    assert len(old)==3 and len(new)==len(local)==13
    assert old['3/1/0']==new['3/200/0']==local['3/200/0']
    assert old['14/32512/0'][:-2]==new['14/ORIG.ICO/0'][:-2]
    assert struct.unpack('<H',old['14/32512/0'][-2:])[0]==1
    assert struct.unpack('<H',new['14/ORIG.ICO/0'][-2:])[0]==200
    assert len(out['binaries']['official_modern']['icon_groups']['14/MAIN.ICO/0'])==6
    changes=[key for key in new if new[key]!=local[key]]
    assert sorted(changes)==['16/1/0','24/1/0']
    assert new['24/1/0'].replace(b'1.6.1.0',b'1.6.2.0')==local['24/1/0']
    out['local_manifest_difference']='Only assemblyIdentity version changes from1.6.1.0 to1.6.2.0; other bytes identical.'
    out['retained_original_icon']={'original':'3/1/0','modern':'3/200/0',
        'sha256':hashlib.sha256(old['3/1/0']).hexdigest(),
        'group_difference':'Original group payload retained except final icon ID1 changes to200.'}
    out['official_to_local_changed_resource_keys']=sorted(changes)
    out['limits']=['Payload/group/XML identity only; no resource API, icon rendering, loader or application execution.',
        'Manifest declarations are not proof of OS/Wine enforcement or actual runtime privileges/theme.',
        'Resource counts, payload sums and section bytes include different kinds of data; not feature counts.']
    (ROOT/'analysis/evidence/audits/pe-resource-payloads.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 3 original/13 Modern resource leaves, retained original icon bytes, icon-group references and XML fields; local changes limited to version/manifest')


if __name__=='__main__':main()
