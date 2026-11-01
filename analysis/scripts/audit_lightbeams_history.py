"""Pinned historical capability readers; no target execution."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs=[('1.2.0','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003',
            [(0x4b57e3,0x4b586c),(0x470ad4,0x470adb)],0x53eebc,0x53eea4),
           ('1.3.1','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664',
            [(0x4b57e3,0x4b5851)],0x53eea8,0x53ee90)]
    output={'kind':'static-historical-LightBeams-reader-and-defaults','releases':{}}
    for version,digest,spans,key,section in specs:
        path=f'analysis/captures/modern-differences/upstream/history/nfs3-{version}.exe'
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw)
        assert p.get_string_at_rva(key-0x400000)==b'LightBeams'
        assert p.get_string_at_rva(section-0x400000)==b'THRASH'
        imports={e.address:e.name.decode() for lib in p.DIRECTORY_ENTRY_IMPORT for e in lib.imports if e.name}
        assert imports[0x534674]=='GetPrivateProfileIntA'
        output['releases'][version]={'path':path,'sha256':digest,
            'spans':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                      'sha256':sha(p.get_data(a-0x400000,b-a)),
                      'bytes_hex':p.get_data(a-0x400000,b-a).hex(),
                      'disassembly':disassemble(p.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.2.0.7z'
    assert sha(archive.read_bytes())=='151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b'
    assert sha(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']))==specs[0][1]
    configs={}
    for driver in ['dgvoodoo','softtri','dx5','dx8','dx6','nglide']:
        member=f'drivers/{driver}/thrash.ini'
        data=subprocess.check_output(['7z','x','-so',str(archive),member])
        configs[member]={'sha256':sha(data),'text':data.decode('ascii')}
    output['v120_archive_sha256']=sha(archive.read_bytes());output['v120_packaged_configs']=configs
    final=ROOT/'analysis/captures/modern-differences/upstream/package/nfs3.exe';raw=final.read_bytes()
    assert sha(raw)=='240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6'
    assert b'lightbeams' not in raw.lower()
    output['final_ascii_key_absent']={'sha256':sha(raw),'case_insensitive':True}
    output['contracts']={'v120_lightbeams_default':'1 for type d/v,0 for s/other; read normalized to0/1 at007a392c',
        'v120_fog_default':'1 for type v,0 otherwise; read normalized to0/4 at007a3a64',
        'v131_defaults':'Both literal0; same respective0/1 and0/4 normalization and destinations',
        'v120_consumer':'00470ad4 TEST BYTE[007a392c],1; zero branches00470b1b'}
    output['limits']=['Static reads and a local consumer gate; no visible beam/fog support or API execution established.',
        'Absence of final literal does not prove rendering removal, alternate key absence or full downstream equivalence.',
        '1.3.1 extracted EXE hash matches prior pinned historical audits; only1.2.0 archive/member is re-extracted here.',
        'No precise removal boundary between1.3.1 andfinal1.6.1 claimed.']
    (ROOT/'analysis/evidence/audits/lightbeams-history.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS: historical LightBeams/FogSupport readers, defaults, local gate and packaged configuration captured')


if __name__=='__main__':main()
