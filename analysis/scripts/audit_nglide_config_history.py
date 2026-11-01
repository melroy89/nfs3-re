"""Static historical nGlide INI-to-environment setup, without target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    relative='analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.2.0.7z'
    archive=ROOT/relative
    archive_hash='151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b'
    assert sha(archive.read_bytes())==archive_hash
    expected={
        'drivers/nglide/nglide.dll':'bf075c8deec77ce8f87ee76b11662f257dd5cc5e9d91bc69cfd4afcc36b4301b',
        'drivers/dgvoodoo/voodoo2.dll':'857f8dd4dd997006012ae233722f382068c6c41d20c2f3166ba2b5df79122cc0',
        'drivers/nglide/thrash.ini':'df7c78608ed8c63b598fe3e373956a5435433c3138489855c146bb32e0833932'}
    result={'kind':'static-historical-nglide-configuration','archive':relative,
            'archive_sha256':archive_hash,'members':{}}
    for member,digest in expected.items():
        raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        assert sha(raw)==digest
        row={'sha256':digest};result['members'][member]=row
        if member.endswith('.ini'):
            row['text']=raw.decode('ascii')
            assert '[NGLIDE]\r\nResolution=0\r\nAspect=0\r\nRefresh=0\r\nVsync=1\r\nGamma=5\r\nSplash=0' in row['text']
            continue
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x60000000,b-a)
        nglide='nglide/' in member
        spans=[(0x60001020,0x600010f9 if nglide else 0x600010f4)]
        if nglide:
            spans.extend([(0x6000d8a0,0x6000d916),(0x600012c0,0x600012ca),(0x60009850,0x6000985e)])
            assert get(0x6000106b,0x60001070).hex()=='e830c80000'
            assert get(0x6000d8c4,0x6000d8ca).hex()=='ff1574e20060'
            assert get(0x6000d900,0x6000d906).hex()=='ff1520e20060'
            assert get(0x6000107f,0x60001085).hex()=='ff1510e20060'
            assert pe.get_string_at_rva(0x10cd4)==b'thrash.ini'
            assert pe.get_string_at_rva(0x10ce0)==b'NGLIDE'
        else:
            assert get(0x6000106b,0x60001070).hex()=='be04f00060'
        assert pe.get_string_at_rva(0xf004)==b'glide3x.dll'
        imports={entry.address:entry.name.decode() for dll in pe.DIRECTORY_ENTRY_IMPORT for entry in dll.imports if entry.name}
        for address,name in [(0x6000e210,'LoadLibraryA'),(0x6000e1ec,'GetModuleFileNameA')]:
            assert imports[address]==name
        if nglide:
            assert imports[0x6000e274]=='GetPrivateProfileSectionA'
            assert imports[0x6000e220]=='SetEnvironmentVariableA'
        row['imports']={f'{a:08x}':imports[a] for a in [0x6000e210,0x6000e1ec]+([0x6000e274,0x6000e220] if nglide else [])}
        row['captures']=[]
        for start,end in spans:
            body=get(start,end)
            row['captures'].append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,start)})
    result['verified']=[
        'The nGlide loader inserts a configuration helper before its first LoadLibraryA attempt; paired dgVoodoo loader lacks this call.',
        'Helper appends thrash.ini to its incoming adapter-directory buffer, reads an8192-byte NGLIDE section and builds names in a256-byte scratch buffer.',
        'Names receive NGLIDE_ prefix and ASCII a-z uppercase conversion; first equals separates name from unchanged value.',
        'Empty returned section exits without environment writes; no clear/reset loop exists in the complete helper.',
        'Loaded-provider handle nonzero bypasses configuration and provider loading in the complete loader.']
    result['limits']=[
        'Static1.2.0 bundled adapter pair, not all differences or a retail-original driver authentication claim.',
        'No API, provider, game or extracted instructions executed; API success and actual provider setting precedence untested.',
        'Missing section does not remove inherited or previously set environment variables; global-settings outcome is conditional.',
        'Profile-section return value, environment-write results and filename API failure are unchecked locally; no bounds check on constructed256-byte names.',
        'No complete memory-safety, path truncation, malformed/multi-string behavior or concurrent/later load lifecycle claim.',
        'This historical NGLIDE-specific DLL mechanism must not be confused with the final EXE generic ENV mechanism.']
    (ROOT/'analysis/evidence/audits/nglide-config-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.2.0 adapter pair, complete configuration helper, API bindings and pre-load order')


if __name__=='__main__':main()
