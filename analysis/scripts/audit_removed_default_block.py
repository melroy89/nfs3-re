"""Read-only original/final removed config-default block classification."""
import json
import pefile
import struct
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-removed-config-default-block','binaries':{}}
    images={}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw);images[label]=p
        spans=[(0x472545,0x47262b),(0x40faf0,0x40fb0f),(0x437e00,0x43806b)]
        if label=='official_modern':spans += [(0x472248,0x472295),(0x472aff,0x472b09)]
        else:spans += [(0x472250,0x472300),(0x4ee310,0x4ee3b1)]
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
    names=['english','german','french','spanish','italian','swedish']
    assert [old.get_string_at_rva(0x13afd8+i*8).decode() for i in range(6)]==names
    assert old.get_data(0x72267,5).hex()=='a34cbb6f00'
    for address,value in [(0x47227f,1),(0x47229c,2),(0x4722b9,3),(0x4722d6,4),(0x4722f3,5)]:
        assert old.get_data(address-0x400000,10)==bytes.fromhex('c7054cbb6f00')+value.to_bytes(4,'little')
    result['removed_language_mapper']={'start':'00472250','end_exclusive':'00472300',
        'buffer':'007a2634','destination':'006fbb4c','exact_case_sensitive_names':names,
        'comparison':'004ee310..004ee3b1 returns0 on equal NUL-terminated strings',
        'no_match':'No local destination write; retains incoming active-language state',
        'modern_replacement':'INI selector lowercases, validates and falls back to English;00472aff copies007a3a50 to006fbb4c',
        'limits':'Comparator uses DWORD reads beyond an early byte; ordinary valid padded storage assumed, no arbitrary-pointer safety claim.'}
    slider_specs=[(0x5375a8,'ASLD_MENUMUSIC',0x6fbbe8),
                  (0x5375b8,'ASLD_RACEMUSIC',0x6fbbf0),
                  (0x5375c8,'ASLD_SOUNDFX',0x6fbbf4),
                  (0x5375d8,'ASLD_ENGINEVOLUME',0x6fbbf8),
                  (0x5375ec,'ASLD_SPEECHVOLUME',0x6fbbfc)]
    for pe in images.values():
        for address,token,destination in slider_specs:
            assert pe.get_string_at_rva(address-0x400000).decode()==token
        assert struct.unpack('<d',pe.get_data(0x137600,8))[0]==1/127
    before,after=[pe.get_data(0x37e00,0x26b) for pe in (old,new)]
    assert before[:0x42]==after[:0x42] and before[0x5f:]==after[0x5f:]
    result['slider_binding']={'initializer':'00437e00..0043806b',
        'same_body_except':'00437e42..00437e5f; separate frontend-sound setup rewrite',
        'scale_address':'00537600','scale_binary64':1/127,
        'rows':[{'token_address':f'{a:08x}','token':t,'setting':f'{d:08x}'} for a,t,d in slider_specs],
        'limits':'Names from code-bound menu tokens; not measured acoustic units or runtime slider observations.'}
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
