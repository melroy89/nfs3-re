"""Read-only original/final removed config-default block classification."""
import json
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-removed-config-default-block','binaries':{}}
    images={}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw);images[label]=p
        spans=[(0x472545,0x47262b),(0x40faf0,0x40fb0f)]
        if label=='official_modern':spans += [(0x472248,0x472295)]
        result['binaries'][label]={'path':path,'sha256':digest,'spans':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'bytes_hex':p.get_data(a-0x400000,b-a).hex(),
             'sha256':sha(p.get_data(a-0x400000,b-a)),
             'disassembly':disassemble(p.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new=images['original'],images['official_modern']
    assert new.get_data(0x72566,197)==b'\x90'*197
    assert old.get_data(0x72561,5).hex()=='e8eafcffff'
    assert new.get_data(0x72561,5).hex()=='e9c5000000'
    assert old.get_data(0xfaf0,31)==new.get_data(0xfaf0,31)
    result['partition']=[{'start':'00472566','end_exclusive':'004725be','role':'six header+18 stores gated by006fbb4c, EBX or literal1'},
        {'start':'004725be','end_exclusive':'00472611','role':'inline audio default values and selectors'},
        {'start':'00472611','end_exclusive':'0047262b','role':'capability predicate -> audio mode3/0'}]
    result['audio_default_stores']={
        '006fbbe8':[100,95],'006fbbf0':[100,95],'006fbbf4':[100,95],
        '006fbbf8':[100,95],'006fbbfc':[127,108],'006fbbe4':[2,0],
        '006fbbe0':[1,1],'006fbbec':[0,0],'006fbbdc':[0,0],
        '006fbbd8':[1,None],'006fd1d0':[None,83]}
    result['limits']=['Table values are static instruction-derived stores, not executed observations.',
        'None means no direct store in the compared block/helper, not absence of initialization elsewhere.',
        'Modern low-byte assignments are safe to interpret as whole small constants here because retained predicate returns normalized0/1.',
        'Profile EBX provenance and replacement HUD values are separately documented, not re-proven by this bounded capture.',
        'Caller coverage, serialized layout, actual sound and user-visible slider units remain separate.']
    (ROOT/'analysis/evidence/audits/removed-default-block.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:197-byte removed block, replacement jump, sound helper and retained normalized predicate')


if __name__=='__main__':main()
