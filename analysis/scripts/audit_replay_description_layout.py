"""Static replay DESCRIPTION_BOX rendering comparison."""
import json
import pefile
from audit_dx5_reference_final import sha,disassemble,intervals
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    out={'kind':'static-replay-description-layout','binaries':{}};images={}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        p=pefile.PE(data=raw);images[label]=p
        assert p.get_string_at_rva(0x138c24)==b'%s...'
        assert p.get_string_at_rva(0x138c2c)==b'DESCRIPTION_BOX'
        assert p.get_string_at_rva(0x138c3c)==b'replays'
        assert p.get_data(0x4749f,7).hex()=='c74054e0704400'
        spans=[(0x4470e0,0x44718f),(0x44748f,0x4474a6)]
        out['binaries'][label]={'path':path,'sha256':digest,'spans':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'sha256':sha(p.get_data(a-0x400000,b-a)),
             'bytes_hex':p.get_data(a-0x400000,b-a).hex(),
             'disassembly':disassemble(p.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new=images['original'],images['official_modern']
    a,b=[p.get_data(0x470e0,175) for p in (old,new)]
    assert sum(x!=y for x,y in zip(a,b))==90
    assert a[0x64:]==b[0x64:]
    assert new.get_data(0x47100,68)==b'\x90'*68
    assert old.get_data(0x470ee,6).hex()=='8b78048b7006'
    assert new.get_data(0x470eb,8).hex()=='0fbf78060fbf7008'
    assert old.get_data(0x46fed,243)==new.get_data(0x46fed,243)
    assert old.get_data(0x4718f,17)==new.get_data(0x4718f,17)
    out['changed_runs']=intervals(a,b,0x4470e0)
    out['contracts']={'old_initial_xy':'signedWORD context+6/context+8 extracted by DWORD loads +4/+6 thenSAR16',
        'new_initial_xy':'MOVSX signedWORD context+6/context+8',
        'old_heading':'localizedID480 via004d1850; format%s...; draw helper00452190',
        'old_rows_xy':'x+20,y+25 initially; y advances20 per record',
        'new_rows_xy':'x+20,y+20 initially; y advances20 per record',
        'row_storage':'00558d0c+i*120, i0..9; empty first byte skips draw but still advances row',
        'row_draw_constants':'ECX18, stack3 and colourff649dfd retained',
        'local_stack':'old260 bytes, new4 bytes'}
    out['limits']=['Static instructions only; no menu/render/runtime probe.',
        'Context coordinate units, helper ABI effects and actual placement remain unverified.',
        'Coordinate-value equality assumes readable little-endian context; old DWORD accesses have wider footprint.',
        'LabelID480 content, record population, resource version and complete menu lifecycle remain separate.']
    (ROOT/'analysis/evidence/audits/replay-description-layout.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: complete175-byte replay-description callback,90 differing bytes and retained75-byte row loop')


if __name__=='__main__':main()
