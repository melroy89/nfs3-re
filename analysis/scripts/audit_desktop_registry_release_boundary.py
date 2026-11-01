"""Static desktop registry access-mask change in adjacent historical EXEs."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, intervals, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs=[('1.3.0','93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
            'deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146',0xf003f),
           ('1.3.1','6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934',
            '199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664',0x20019)]
    result={'kind':'static-historical-desktop-registry-mask-boundary','releases':{}}
    bodies=[]
    for version,archive_sha,exe_sha,mask in specs:
        path=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/path;assert sha(archive.read_bytes())==archive_sha
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_sha
        pe=pefile.PE(data=raw);body=pe.get_data(0xb6520,104);bodies.append(body)
        imports={entry.address:entry.name.decode() for library in pe.DIRECTORY_ENTRY_IMPORT
                 for entry in library.imports if entry.name}
        assert imports[0x53446c]=='RegOpenKeyExA' and imports[0x534470]=='RegQueryValueExA'
        assert pe.get_data(0xb6543,5)==b'\x68'+mask.to_bytes(4,'little')
        assert pe.get_data(0xb654f,5).hex()=='6801000080'
        assert pe.get_string_at_rva(0x13feb0)==b'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders'
        assert pe.get_string_at_rva(0x13fef4)==b'Desktop'
        result['releases'][version]={'archive':path,'archive_sha256':archive_sha,'member':'nfs3.exe','sha256':exe_sha,
            'function_start':'004b6520','function_end_exclusive':'004b6588','function_bytes':104,
            'function_sha256':sha(body),'bytes_hex':body.hex(),'disassembly':disassemble(body,0x4b6520),
            'access_mask':f'{mask:08x}','mask_instruction':'004b6543','open_call':'004b6554',
            'query_call':'004b6575','buffer':'007a3ae0','initial_capacity':256,
            'api_bindings':{f'{va:08x}':imports[va] for va in (0x53446c,0x534470)}}
    changed=[0x4b6520+i for i,(a,b) in enumerate(zip(*bodies)) if a!=b]
    assert changed==[0x4b6544,0x4b6546]
    result['changed_bytes']=[f'{address:08x}' for address in changed]
    result['changed_intervals']=intervals(*bodies,0x4b6520)
    result['constant_reference']='https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights'
    result['conclusion']='The complete104-byte helper changes only two bytes in PUSH access-mask: KEY_ALL_ACCESS000f003f -> KEY_READ00020019.'
    result['limits']=['Requested rights changed; no query success, permission outcome, OS/Wine compatibility or screenshot output observed.',
        'Unchanged helper returns the buffer even on open/query failure; no local RegCloseKey added.',
        'Final1.6.1 removes this helper; do not describe the historical mask change as a surviving final desktop lookup.',
        'Archive labels are not authenticated development chronology; no registry, target or screenshot executed.']
    (ROOT/'analysis/evidence/audits/desktop-registry-release-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.3.0/1.3.1 complete Desktop helpers; only two access-mask bytes change')


if __name__=='__main__':main()
