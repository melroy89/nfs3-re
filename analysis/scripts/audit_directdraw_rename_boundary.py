"""Static 1.6.0/1.6.1 compatibility setting and dispatch boundary."""
import json
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs=[('1.6.0','analysis/captures/modern-differences/upstream/history/nfs3-1.6.0.exe',
            '9fd80c4cdc9827f190698f28aa93f1182218d7c557898fb2653abfc4148c7a72',
            [(0x4b57bc,0x4b57da),(0x4b591b,0x4b5937),(0x4b5a02,0x4b5a10)],
            {0x53f730:'DirectDrawLagFix',0x53f70c:'THRASH',0x53f748:'DDRAW.DLL',0x53f754:'SetAppCompatData'}),
           ('1.6.1','analysis/captures/modern-differences/upstream/package/nfs3.exe',
            '240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6',
            [(0x4b57c4,0x4b57f3),(0x4b599e,0x4b59e4)],
            {0x53f738:'DisableMaxWindowedMode',0x53f750:'NoDwmOffForPrimaryLock',
             0x53f730:'DDRAW',0x53f76c:'DDRAW.DLL',0x53f778:'SetAppCompatData'})]
    result={'kind':'static-DirectDraw-setting-rename-and-dispatch-release-boundary','releases':{}}
    for version,path,digest,spans,strings in specs:
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw)
        for va,value in strings.items():assert p.get_string_at_rva(va-0x400000).decode()==value
        imports={e.address:e.name.decode() for lib in p.DIRECTORY_ENTRY_IMPORT for e in lib.imports if e.name}
        assert imports[0x534670]=='GetPrivateProfileIntA'
        result['releases'][version]={'path':path,'sha256':digest,
            'strings':{f'{va:08x}':v for va,v in strings.items()},
            'spans':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                      'bytes_hex':p.get_data(a-0x400000,b-a).hex(),
                      'sha256':sha(p.get_data(a-0x400000,b-a)),
                      'disassembly':disassemble(p.get_data(a-0x400000,b-a),a)} for a,b in spans]}
        if version=='1.6.0':
            assert b'DisableMaxWindowedMode\0' not in raw and b'NoDwmOffForPrimaryLock\0' not in raw
            assert p.get_data(0xb5932,5).hex()=='a390277a00'
            assert p.get_data(0xb57d1,6).hex()=='6a006a0cffd0'
        else:
            assert p.get_data(0xb59b9,8).hex()=='0fba2d90277a000c'
            assert p.get_data(0xb59dc,8).hex()=='0fba2d90277a0001'
    result['conclusion']='Rename preserves selected request12, but state representation changes: old raw integer assignment/Boolean gate becomes accumulated bit12 plus new independent bit1 and bit-index dispatch.'
    result['limits']=['Read-only static inspection; no target/API execution or performance measurement.',
        'Old nonzero integers all select request12; new key nonzero setsbit12, not its raw integer value.',
        'New zero settings do not clear existing mask bits in this local block; caller/state lifetime and external ABI remain separate.',
        'Pinned historical/final artifacts do not prove every intermediate build or physical OS effect.']
    (ROOT/'analysis/evidence/audits/directdraw-rename-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned setting rename, old Boolean request12 and new accumulated bit12/bit1 dispatch')


if __name__=='__main__':main()
