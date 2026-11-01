"""Static historical role-profile map-zoom default stores."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


SPECS_HISTORY={
 '1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'),
 '1.3.1':('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664'),
 '1.4.0':('8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9','7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d')}


def main():
    result={'kind':'static-map-zoom-default-history','versions':{}}
    blocks={}
    for version,(archive_hash,exe_hash) in SPECS_HISTORY.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/relative;assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_hash
        pe=pefile.PE(data=raw)
        start,end=(0x485943,0x48596c) if version=='1.4.0' else (0x485949,0x485974)
        body=pe.get_data(start-0x400000,end-start);blocks[version]=body
        targets=[0x6fbc60+i*0x1a4 for i in range(6)]
        if version=='1.4.0':
            expected=bytes.fromhex('bb00004040')+b''.join(b'\x89\x1d'+struct.pack('<I',a) for a in targets)
            values=[3.0]*6
        else:
            expected=bytes.fromhex('b800004040bb0000803f')+b''.join((b'\xa3' if i%2==0 else b'\x89\x1d')+struct.pack('<I',a) for i,a in enumerate(targets))
            values=[3.0,1.0]*3
        assert body==expected
        result['versions'][version]={'archive':relative,'archive_sha256':archive_hash,'member':'nfs3.exe','sha256':exe_hash,
            'profile_plus10_values':values,'destinations':[f'{a:08x}' for a in targets],
            'capture':{'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,start)}}
    assert blocks['1.1.0']==blocks['1.3.1']
    relative,digest,_=SPECS['official_modern'];raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
    pe=pefile.PE(data=raw)
    assert pe.get_data(0x85932,len(blocks['1.4.0']))==blocks['1.4.0']
    result['final_retention']={'path':relative,'sha256':digest,'start':'00485932','end_exclusive':'0048595b','default_store_block_identical_to140':True}
    result['reused_evidence']=['analysis/evidence/audits/map-marker-scaling-difference.json',
        'analysis/evidence/audits/original-modern-hud-layout.json']
    result['limits']=['No game, map, API or extracted instructions executed.',
        'This audit verifies default stores; role selection, clamping and map-zoom consumers use linked paired evidence, not fresh all-history consumer equivalence.',
        '1.1.0 establishes early presence, not1.0.0 introduction.',
        'Stored zoom multiplier is not a measured final map coverage or pixel-size ratio; fitted map/marker scaling is separate.',
        'Saved preferences, later writers, active profiles and actual rendering remain unverified.']
    (ROOT/'analysis/evidence/audits/map-zoom-default-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: early131 alternating3/1 stores;140 all3 boundary and identical final store block')


if __name__=='__main__':main()
