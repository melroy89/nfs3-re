"""Complete original/final RenderRaceFrame changed-region partition."""
import json
import pefile
from audit_dx5_reference_final import sha,disassemble,intervals
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-complete-race-frame-partition','binaries':{}};images={}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw);images[label]=pe
        spans=[(0x4bc680,0x4bc830),(0x431c30,0x431c45)]
        if label=='original':spans += [(0x4bc660,0x4bc66a)]
        result['binaries'][label]={'path':path,'sha256':digest,'spans':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'sha256':sha(pe.get_data(a-0x400000,b-a)),
             'bytes_hex':pe.get_data(a-0x400000,b-a).hex(),
             'disassembly':disassemble(pe.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new=images['original'],images['official_modern']
    a,b=[p.get_data(0xbc680,414) for p in (old,new)]
    runs=intervals(a,b,0x4bc680)
    assert [(r['start_va'],r['end_va_exclusive']) for r in runs]==[
        ('004bc687','004bc6a7'),('004bc794','004bc797'),('004bc7de','004bc81e')]
    for va in [0x431c30,0x431c40,0x4bc820]:assert old.get_data(va-0x400000,5).hex()=='5589e55dc3'
    assert old.get_data(0xbc660,10).hex()=='5589e5e8c8f3f8ff5dc3'
    assert new.get_data(0xbc793,5).hex()=='e898f2f8ff'
    assert new.get_data(0xbc7de,6).hex()=='5d5e5a595bc3'
    assert new.get_data(0xbc7e4,76)==b'\x90'*76
    result['changed_runs']=runs
    result['body_bounds']={'original':'004bc680..004bc81e,414 bytes','modern':'004bc680..004bc7e4,356 bytes'}
    result['outside_interval']='004bc7e4..004bc830:76 NOP-replaced bytes; begins inside originalCALL004bc7e3 operand, includes original epilogue and separate no-op004bc820/alignment.'
    result['classification']=['Entry reset/restore and no-op state-call removal004bc687..004bc6a7',
        'Same target0044ba30 reached directly instead of through old10-byte wrapper004bc660',
        'Exit no-op state-call, conditional reset/save/single-control sequence and moved epilogue004bc7de..004bc81e']
    result['limits']=['Static byte/call contracts only; surrounding callbacks may still modify x87 state.',
        'Same body bytes outside these regions do not prove equal state, inputs, outputs or rendering.',
        'No-op calls have stack/frame effects; full machine-state equivalence is not claimed.',
        'Control precision is distinct from memory storage and does not alone prove replay/network outcomes.']
    (ROOT/'analysis/evidence/audits/race-frame-partition.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete414-byte original frame; three changed regions, same-target wrapper bypass and76-byte outside tail')


if __name__=='__main__':main()
