"""Static replay mirror/variant admission witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS=[(0x484450,0x4844c0),(0x422aa0,0x422b65),
       (0x4844c0,0x484588),(0x4c5097,0x4c50af),
       (0x48f7b0,0x48f81b),(0x48f970,0x48fa09),(0x48f550,0x48f69a),
       (0x431800,0x43182d)]


def main():
    capture=ROOT/'analysis/captures/modern-differences/replay-mirror'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-replay-mirror-comparison','range_end':'exclusive','binaries':{},
        'limits':['No replay, input or target execution.','Default F7-to-action chain is static; actual keyboard delivery/rendered mirror unverified.']}
    builders={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in SPANS:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        assert pe.get_data(0x48f9c8-0x400000,5)==bytes.fromhex('be04410000')
        builders[label]=pe.get_data(0x48f550-0x400000,0x14a)
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    assert builders['original']==builders['official_modern']
    result['binding_chain']={'encoded':'00004104','slot':'0079c3cc',
        'shared_action_base':'0079c3a0','action_index':11,'scan_index':'0041',
        'action_builder_identical':True}
    (ROOT/'analysis/evidence/audits/original-modern-replay-mirror.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: replay toggle, eligibility, refresh and input witnesses for both baselines')


if __name__=='__main__':main()
