"""Static wrapper removal and relocated arena lifecycle calls."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-removed-render-lifecycle-wrappers','binaries':{}};images={}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw);images[label]=p
        spans=[(0x4bc947,0x4bc9a0),(0x434af0,0x434b15),(0x4a3390,0x4a33af)]
        spans += [(0x4a3652,0x4a3665)] if label=='original' else [(0x4a3652,0x4a366b),(0x4b5d73,0x4b5d8e)]
        result['binaries'][label]={'path':path,'sha256':digest,'spans':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'sha256':sha(p.get_data(a-0x400000,b-a)),
             'bytes_hex':p.get_data(a-0x400000,b-a).hex(),
             'disassembly':disassemble(p.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new=images['original'],images['official_modern']
    def target(pe,address):
        b=pe.get_data(address-0x400000,5);assert b[0]==0xe8
        return (address+5+struct.unpack('<i',b[1:])[0])&0xffffffff
    old_calls={0x4a3398:0x4bc980,0x4a33a3:0x4bc990,0x4a365b:0x4bc950,
               0x4bc983:0x434b00,0x4bc988:0x4bbd80,0x4bc993:0x4bbdc0,0x4bc998:0x434b10}
    new_calls={0x4b5d73:0x434870,0x4b5d78:0x4bbd80,0x4b5d89:0x4bbda4,
               0x4a3657:0x4c7150,0x4a365c:0x484220,0x4a3661:0x4cb730}
    for p,calls in [(old,old_calls),(new,new_calls)]:
        for a,b in calls.items():assert target(p,a)==b
    result['call_routes']={'original':{f'{a:08x}':f'{b:08x}' for a,b in old_calls.items()},
                           'modern':{f'{a:08x}':f'{b:08x}' for a,b in new_calls.items()}}
    assert new.get_data(0xbc950,80)==b'\x90'*80
    assert sum(a!=b for a,b in zip(old.get_data(0xbc947,89),new.get_data(0xbc947,89)))==79
    assert old.get_data(0xbc947,9)==new.get_data(0xbc947,9)
    for a in (0x434af0,0x434b10):assert old.get_data(a-0x400000,5).hex()=='5589e55dc3'
    original_shutdown_calls=[target(old,a) for a in range(0x4bc953,0x4bc976,5)]
    assert original_shutdown_calls==[0x434af0,0x4d5730,0x4c7150,0x4dbbe0,0x484220,0x4cb730,0x4c7b20]
    result['original_shutdown_sequence']=[f'{a:08x}' for a in original_shutdown_calls]
    result['limits']=['Static instruction/call-target comparison, not executed lifecycle or allocation proof.',
        'Three retained targets keep order at the shown Modern race-shutdown site; others may have different callers/roles.',
        'Full startup/shutdown ordering, indirect entries and transitive callees remain separate.',
        'Original434af0/434b10 are verified5-byte no-op bodies; their removal is not proof of whole machine-state equivalence.']
    (ROOT/'analysis/evidence/audits/removed-render-lifecycle-wrappers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:79 outside-body changes, three removed wrappers, relocated arena calls and three retained shutdown callees')


if __name__=='__main__':main()
