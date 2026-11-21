"""Compare130/131 DirectX probe's OS-major admission; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble,intervals


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    specs={'1.3.0':('93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad','deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146'),
           '1.3.1':('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664')}
    result={'kind':'static-win9x-version-gate-history','versions':{}};bodies=[];callers=[];import_sets=[];headers=[]
    for version,(ah,eh)in specs.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a)
        slots={i.address:i.name.decode()for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert slots[0x534574]=='GetVersion'and slots[0x53458c]=='LoadLibraryA'and slots[0x534558]=='GetProcAddress'and slots[0x534764]=='MessageBoxA'
        assert get(0x4b65a4,0x4b65b5).hex()==('ff15744553003c05733b31c0e9ea010000'if version=='1.3.0'else'ff15744553003c04733b31c0e9ea010000')
        assert p.get_string_at_rva(0x13fefc)==b'DDRAW.DLL'and p.get_string_at_rva(0x13ff08)==b'DirectDrawCreate'
        assert p.get_string_at_rva(0x13ca02)==b'The DirectX 5 drivers must be installed to run.'
        spans=[('complete_probe',0x4b6590,0x4b67ac),('caller_gate',0x4b5726,0x4b573f),('diagnostic',0x4b5e98,0x4b5ead)]
        bodies.append(get(*spans[0][1:]));callers.append(get(*spans[1][1:]))
        names=sorted((d.dll.decode().lower(),i.name.decode()if i.name else '#'+str(i.ordinal))for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports);import_sets.append(names)
        header={k:getattr(p.OPTIONAL_HEADER,k)for k in ['MajorOperatingSystemVersion','MinorOperatingSystemVersion','MajorSubsystemVersion','MinorSubsystemVersion','Subsystem','DllCharacteristics']};headers.append(header)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'optional_header':header,'normal_import_count':len(names),'normalized_import_sha256':sha(json.dumps(names).encode()),'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    delta=intervals(*bodies,0x4b6590);assert delta==[{'start_va':'004b65ab','end_va_exclusive':'004b65ac','reference_hex':'05','modern_hex':'04'}]
    assert callers[0]==callers[1]and headers[0]==headers[1]and import_sets[0]==import_sets[1]
    result['probe_differences']=delta
    result['limits']=['GetVersion low byte is compared unsigned;minor version/platform bits are not tested by this gate.',
        'Major4 now continues to existing DDRAW/symbol/object checks;does not guarantee probe result5 or successful startup.',
        'No observed Windows98/Me execution,loader compatibility,full OS support or API behavior.',
        'Normal import/header equality does not qualify delay/dynamic/transitive dependencies.',
        'No target/API/instruction execution,compilation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/win9x-version-gate-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:130/131 complete540-byte DirectX probe differs only minimum OS major5->4;caller/import/header retained')


if __name__=='__main__':main()
