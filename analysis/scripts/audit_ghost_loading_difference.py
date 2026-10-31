"""Static ghost wrapper restoration comparison; no file/game execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON=[(0x477b50,0x477bf8),(0x478100,0x4781a9),(0x472820,0x4728d3),(0x4723f0,0x472402)]


def main():
    capture=ROOT/'analysis/captures/modern-differences/ghost-loading'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-ghost-wrapper-comparison','range_end':'exclusive','binaries':{},
        'limits':['No ghost, game or instruction execution.','Restored bytes do not prove cross-version format or trajectory compatibility.']}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in COMMON+[(0x4466a0,0x446734 if label=='original' else 0x44673d)]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['identical_reader_ranges']=[]
    for start,end in COMMON[:2]:
        blob=images['original'].get_data(start-0x400000,end-start)
        assert blob==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_reader_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}',
            'sha256':hashlib.sha256(blob).hexdigest()})
    old_tail=images['original'].get_data(0x72774,0x9f)
    modern_tail=images['official_modern'].get_data(0x72778,0xa8)
    assert modern_tail==b'\x90'*168
    assert images['original'].get_data(0x727a3,3)==bytes.fromhex('f6c620')
    assert images['original'].get_data(0x727ed,3)==bytes.fromhex('f6c610')
    result['removed_original_defaults_tail']={'entry_locator':'004723f0',
        'aligned_capture_start':'00472774','end_exclusive':'00472813',
        'hex':old_tail.hex(),'sha256':hashlib.sha256(old_tail).hexdigest(),
        'modern_nop_interval':'00472778..00472820','modern_nop_bytes':168,
        'original_flag_byte':'0055eb2e','ordered_masks':['20h','10h'],
        'limit':'Original function tail only;00472778 lies inside original MOV EDI immediate. Full default-policy replacement and called helpers not qualified.'}
    (ROOT/'analysis/evidence/audits/original-modern-ghost-loading.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: ghost wrapper baselines/spans and identical reader/model resolver')


if __name__=='__main__':main()
