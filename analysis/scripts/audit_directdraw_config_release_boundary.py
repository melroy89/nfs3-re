"""Read-only historical DirectDrawLagFix configuration routing comparison."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs = [
        ('1.3.0', '93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
         'deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146',
         [(0x4a6e8d,0x4a6eaa),(0x4b55d8,0x4b562b),(0x4fb6f0,0x4fb713)]),
        ('1.3.1', '6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934',
         '199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664',
         [(0x4b55dc,0x4b5619),(0x4b561c,0x4b5668),(0x4b5720,0x4b5871),
          (0x4f93a8,0x4f93ba)])]
    result = {'kind':'static-historical-DirectDrawLagFix-config-boundary','releases':{}}
    pes = []
    for version, archive_hash, exe_hash, spans in specs:
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive = ROOT/relative
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        assert sha(raw) == exe_hash
        pe = pefile.PE(data=raw); pes.append(pe)
        imports = {e.address:e.name.decode() for lib in pe.DIRECTORY_ENTRY_IMPORT for e in lib.imports if e.name}
        expected = {0x534544:'GetModuleFileNameA',0x534674:'GetPrivateProfileIntA',
                    0x53454c:'GetModuleHandleA',0x53458c:'LoadLibraryA',0x534558:'GetProcAddress'}
        for address, name in expected.items(): assert imports[address] == name
        for address, value in [(0x53fefc,b'DDRAW.DLL'),(0x53fe40,b'SetAppCompatData')]:
            assert pe.get_string_at_rva(address-0x400000) == value
        result['releases'][version] = {'archive':relative,'archive_sha256':archive_hash,
            'member':'nfs3.exe','member_sha256':exe_hash,
            'imports':{f'{a:08x}':n for a,n in expected.items()},
            'spans':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                      'sha256':sha(pe.get_data(a-0x400000,b-a)),
                      'bytes_hex':pe.get_data(a-0x400000,b-a).hex(),
                      'disassembly':disassemble(pe.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new = pes
    def data(pe,va,size): return pe.get_data(va-0x400000,size)
    for pe, address, value in [(old,0x53edf8,b'NFS3'),(old,0x53ee34,b'DirectDrawLagFix'),
        (new,0x53ee78,b'drivers\\'),(new,0x53ee84,b'\\thrash.ini'),
        (new,0x53ee90,b'THRASH'),(new,0x53eec0,b'DirectDrawLagFix')]:
        assert pe.get_string_at_rva(address-0x400000)==value
    assert data(old,0x4a6ea2,7).hex()=='c747fc2e696e69'
    assert data(old,0x4b55e6,8).hex()=='31d242e802610400'
    assert data(old,0x4fb702,14).hex()=='683c267a00525355ff1574465300'
    assert data(new,0x4b5851,32).hex()=='6830397a006a0068c0ee53006890ee5300ff157446530085c07405e86bfdffff'
    assert data(old,0x4b55f2,57)==data(new,0x4b55e0,57)
    result['verified'] = {
        'old':'Executable sibling .ini (nfs3.ini under the shipped basename), section NFS3, key DirectDrawLagFix; caller default1, reader override path can replace default.',
        'new':'Executable directory + drivers\\ + selected driver name + \\thrash.ini; section THRASH, key DirectDrawLagFix; literal default0.',
        'optional_call':'Both use the same57-byte lookup/call tail: DDRAW.DLL, SetAppCompatData, PUSH0/PUSH0c/CALL EAX; absence skips call.'}
    result['limits'] = ['Static instruction comparison; no EXE, DLL, API or game executed.',
        'Path construction assumes normal module-path success, backslash and buffer capacity, and DF0 for string operations.',
        'Old filename follows executable basename, so renaming executable changes the inferred sibling INI name.',
        'Does not prove API effect, performance, OS compatibility, runtime defaults with overrides, or final1.6.1 rename.',
        'Historical archive identities are pinned, not authenticated development chronology.']
    (ROOT/'analysis/evidence/audits/directdraw-config-release-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: historical config filename/section/default relocation and identical optional API tail')


if __name__ == '__main__': main()
