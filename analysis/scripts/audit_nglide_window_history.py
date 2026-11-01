"""Static1.5.2/1.5.3 nGlide package correspondence; no loader/driver execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import intervals

SPECS={'1.5.2':'23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd',
       '1.5.3':'0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64'}
MEMBERS=['drivers/nglide/thrash.ini','drivers/nglide/glide3x.dll','drivers/nglide/voodoo2a.dll']


def main():
    result={'kind':'historical-nglide-window-package','versions':{},
            'limits':['Component byte/header correspondence only; regression cause and windowed behaviour unresolved.',
                      'No Windows loader, nGlide, game or API execution.']}
    blobs={}
    for version,expected in SPECS.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        path=ROOT/relative;assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        row={'archive':relative,'sha256':expected,'members':[]}
        for member in MEMBERS:
            raw=subprocess.check_output(['7z','x','-so',str(path),member]);blobs[version,member]=raw
            row['members'].append({'member':member,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        result['versions'][version]=row
    for member in MEMBERS[:2]:assert blobs['1.5.2',member]==blobs['1.5.3',member]
    old,new=[blobs[v,MEMBERS[2]]for v in SPECS]
    assert len(old)==len(new)==69120
    changes=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
    assert changes==[0xd8,0xd9,0x104,0x105,0x158,0x159,0x15c]
    images=[pefile.PE(data=x)for x in (old,new)]
    section_rows=[]
    for a,b in zip(images[0].sections,images[1].sections):
        assert a.__pack__()==b.__pack__()
        backed=bool(a.PointerToRawData and a.SizeOfRawData)
        if backed:assert a.get_data()==b.get_data()
        section_rows.append({'name':a.Name.rstrip(b'\0').decode(),'rva':f'{a.VirtualAddress:08x}',
            'raw_offset':a.PointerToRawData,'raw_bytes':a.SizeOfRawData,
            'file_backed':backed,'sha256':hashlib.sha256(a.get_data()).hexdigest()if backed else None,'identical_layout_and_backed_payload':True})
    headers=[]
    for version,pe in zip(SPECS,images):
        dirs={d.name:{'rva':f'{d.VirtualAddress:08x}','size':d.Size}for d in pe.OPTIONAL_HEADER.DATA_DIRECTORY
              if d.name in ('IMAGE_DIRECTORY_ENTRY_IMPORT','IMAGE_DIRECTORY_ENTRY_IAT')}
        headers.append({'version':version,'checksum':f'{pe.OPTIONAL_HEADER.CheckSum:08x}',
            'computed_checksum':f'{pe.generate_checksum():08x}','directories':dirs})
    assert headers[0]['directories']['IMAGE_DIRECTORY_ENTRY_IMPORT']=={'rva':'0000e000','size':0x6e4}
    assert headers[1]['directories']['IMAGE_DIRECTORY_ENTRY_IMPORT']=={'rva':'0000e000','size':0x3c}
    assert headers[0]['directories']['IMAGE_DIRECTORY_ENTRY_IAT']=={'rva':'00000000','size':0}
    assert headers[1]['directories']['IMAGE_DIRECTORY_ENTRY_IAT']=={'rva':'0000e174','size':0xfc}
    result['adapter']={'member':MEMBERS[2],'changed_file_offsets':[f'{x:08x}'for x in changes],
        'changed_runs':intervals(old,new,0),'sections':section_rows,'headers':headers,
        'whole_file_limit':'All seven changes confined to these header fields; no unclassified trailing byte changes'}
    (ROOT/'analysis/evidence/audits/nglide-window-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: two archives, identical nGlide/INI, seven adapter header bytes and all section payloads equal')


if __name__=='__main__':main()
