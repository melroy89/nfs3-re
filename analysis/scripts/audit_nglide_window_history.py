"""Static1.5.2/1.5.3 nGlide package correspondence; no loader/driver execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import intervals, disassemble

SPECS={'1.5.2':'23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd',
       '1.5.3':'0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64'}
MEMBERS=['drivers/nglide/thrash.ini','drivers/nglide/glide3x.dll','drivers/nglide/voodoo2a.dll']


def main():
    result={'kind':'historical-nglide-window-package','versions':{},
            'limits':['Selected package/header and EXE mode-publication comparison; regression cause and windowed behaviour unresolved.',
                      'No Windows loader, nGlide, game or API execution.']}
    blobs={}
    exe_images=[]
    capture=ROOT/'analysis/captures/modern-differences/nglide-window-history'
    capture.mkdir(parents=True,exist_ok=True)
    for version,expected in SPECS.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        path=ROOT/relative;assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        row={'archive':relative,'sha256':expected,'members':[]}
        for member in MEMBERS:
            raw=subprocess.check_output(['7z','x','-so',str(path),member]);blobs[version,member]=raw
            row['members'].append({'member':member,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        exe_raw=subprocess.check_output(['7z','x','-so',str(path),'nfs3.exe'])
        exe=pefile.PE(data=exe_raw);exe_images.append(exe)
        spans=[]
        end=0x4bef9f if version=='1.5.2' else 0x4bef8f
        for lo,hi in [(0x4beeb0,end),(0x4cdb10,0x4cdbcd),(0x4cdbd0,0x4cdc14),(0x4cdc20,0x4cdc4c)]:
            code=exe.get_data(lo-0x400000,hi-lo)
            out=capture/f'{version}-{lo:08x}.asm'
            out.write_text('\n'.join(disassemble(code,lo))+'\n')
            spans.append({'start':f'{lo:08x}','end_exclusive':f'{hi:08x}',
                'bytes_sha256':hashlib.sha256(code).hexdigest(),'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        if version=='1.5.2':
            assert exe.get_data(0xbef3e,26).hex()=='f6059043560001750c8b068b5604e87fec0000eb05e8c8ec0000'
        else:
            assert exe.get_data(0xbef3e,10).hex()=='8b068b5604e888ec0000'
        imports={i.address:i.name.decode()for d in exe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534750]=='GetSystemMetrics'
        row['exe']={'member':'nfs3.exe','sha256':hashlib.sha256(exe_raw).hexdigest(),'spans':spans,
                    'GetSystemMetrics_iat':'00534750'}
        result['versions'][version]=row
    for lo,hi in [(0x4cdb10,0x4cdbcd),(0x4cdbd0,0x4cdc14),(0x4cdc20,0x4cdc4c)]:
        assert exe_images[0].get_data(lo-0x400000,hi-lo)==exe_images[1].get_data(lo-0x400000,hi-lo)
    result['exe_mode_publication']={'old_gate':'004bef3e tests00564390 bit0;zero usesselectedmodewidth/height through004cdbd0;nonzero calls004cdc20',
        'new_route':'004bef3e loadsselectedmodewidth/height and alwayscalls004cdbd0 at004bef43',
        'retained_helpers':'Three complete sizing-helper bodies identical; centering versus desktop-size differs by caller route',
        'limits':'No assertion of sole repair cause, selecteddriver success, validcatalogpointer or actual windowed result'}
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
    print('PASS: two archives, identical nGlide/INI, seven adapter header bytes, equal section payloads and EXE mode-publication witnesses')


if __name__=='__main__':main()
