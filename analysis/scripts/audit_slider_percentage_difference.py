"""Static slider percentage tail comparison; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-slider-percentage-comparison','range_end':'exclusive','binaries':{},
            'limits':['No UI execution or numeric input probes.','Slider type meanings require producer evidence.']}
    capture=ROOT/'analysis/captures/modern-differences/slider-percentage';capture.mkdir(parents=True,exist_ok=True)
    prefixes=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);end=0x46a5ea if label=='original' else 0x46a5af
        path=capture/f'{label}-00469680.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x469680',f'--stop-address={end}',relative],cwd=ROOT))
        prefix=pe.get_data(0x69680,0xeab);prefixes.append(prefix)
        result['binaries'][label]={'path':relative,'sha256':expected,'start':'00469680','end':f'{end:08x}',
            'bytes_sha256':hashlib.sha256(pe.get_data(0x69680,end-0x469680)).hexdigest(),
            'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'unchanged_prefix_sha256':hashlib.sha256(prefix).hexdigest(),
            'format':pe.get_data(0x13ae54,20).split(b'\0')[0].decode('ascii'),
            'constants_hex':{f'{a:08x}':pe.get_data(a-0x400000,4).hex() for a in (0x53ae70,0x53ae74,0x53ae78,0x53ae7c,0x53ae80)}}
    assert prefixes[0]==prefixes[1]
    result['identical_prefix_bytes']=0xeab
    (ROOT/'analysis/evidence/audits/original-modern-slider-percentage.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baselines, complete slider bodies and identical 3755-byte prefix')


if __name__=='__main__':main()
