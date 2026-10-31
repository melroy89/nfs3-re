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
        helper_spans=[]
        for start, stop in ((0x46a860,0x46a97c),(0x4693c0,0x469479),(0x4dfd56,0x4dfd73 if label=='original' else 0x4dfd6d),(0x449060,0x4490d8)):
            helper_path=capture/f'{label}-{start:08x}.asm'
            helper_path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={stop}',relative],cwd=ROOT))
            helper_spans.append({'start':f'{start:08x}','end':f'{stop:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,stop-start)).hexdigest(),
                'assembly':str(helper_path.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(helper_path.read_bytes()).hexdigest()})
        dispatch_path=capture/f'{label}-0046cb80.asm'
        dispatch_path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x46cb80','--stop-address=0x46cbbc',relative],cwd=ROOT))
        pair_path=capture/f'{label}-0046b3a0.asm'
        pair_path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x46b3a0','--stop-address=0x46c2e6',relative],cwd=ROOT))
        prefix=pe.get_data(0x69680,0xeab);prefixes.append(prefix)
        result['binaries'][label]={'path':relative,'sha256':expected,'start':'00469680','end':f'{end:08x}',
            'helper_spans':helper_spans,
            'step_event_dispatch':{'start':'0046cb80','end':'0046cbbc',
                'bytes_sha256':hashlib.sha256(pe.get_data(0x6cb80,0x3c)).hexdigest(),
                'assembly':str(dispatch_path.relative_to(ROOT)), 'assembly_sha256':hashlib.sha256(dispatch_path.read_bytes()).hexdigest(),
                'table_0046cb64_hex':pe.get_data(0x6cb64,24).hex()},
            'percentage_pair':{'start':'0046b3a0','end':'0046c2e6',
                'bytes_sha256':hashlib.sha256(pe.get_data(0x6b3a0,0x46c2e6-0x46b3a0)).hexdigest(),
                'assembly':str(pair_path.relative_to(ROOT)), 'assembly_sha256':hashlib.sha256(pair_path.read_bytes()).hexdigest(),
                'format':pe.get_data(0x13ae84,30).split(b'\0')[0].decode('ascii'),
                'constant_bytes_hex':pe.get_data(0x13aea8,12).hex()},
            'bytes_sha256':hashlib.sha256(pe.get_data(0x69680,end-0x469680)).hexdigest(),
            'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'unchanged_prefix_sha256':hashlib.sha256(prefix).hexdigest(),
            'slider_type_registry_00557b44_hex':pe.get_data(0x157b44,12).hex(),
            'slider_template_00557718_hex':pe.get_data(0x157718,0xbc).hex(),
            'slider_callback_row_00557718_hex':pe.get_data(0x157718,80).hex(),
            'step_descriptors_hex':{f'{a:08x}':pe.get_data(a-0x400000,16).hex() for a in (0x558324,0x558334)},
            'percenttype_descriptor':{'address':'00558224','words_hex':pe.get_data(0x158224,16).hex(),
                'keyword':pe.get_data(0x1386b4,30).split(b'\0')[0].decode('ascii')},
            'format':pe.get_data(0x13ae54,20).split(b'\0')[0].decode('ascii'),
            'constants_hex':{f'{a:08x}':pe.get_data(a-0x400000,4).hex() for a in (0x53ae70,0x53ae74,0x53ae78,0x53ae7c,0x53ae80)}}
    assert prefixes[0]==prefixes[1]
    result['identical_prefix_bytes']=0xeab
    assert result['binaries']['original']['helper_spans'][1]['bytes_sha256']==result['binaries']['official_modern']['helper_spans'][1]['bytes_sha256']
    result['quantizer_identical']=True
    assert result['binaries']['original']['helper_spans'][0]['bytes_sha256']==result['binaries']['official_modern']['helper_spans'][0]['bytes_sha256']
    result['step_handler_identical']=True
    for key in ('bytes_sha256','table_0046cb64_hex'):
        assert result['binaries']['original']['step_event_dispatch'][key]==result['binaries']['official_modern']['step_event_dispatch'][key]
    result['step_event_dispatch_identical']=True
    assert result['binaries']['original']['slider_callback_row_00557718_hex']==result['binaries']['official_modern']['slider_callback_row_00557718_hex']
    result['slider_callback_row_identical']=True
    for key in ('slider_type_registry_00557b44_hex','slider_template_00557718_hex'):
        assert result['binaries']['original'][key]==result['binaries']['official_modern'][key]
    assert result['binaries']['original']['helper_spans'][3]['bytes_sha256']==result['binaries']['official_modern']['helper_spans'][3]['bytes_sha256']
    result['template_installer_identical']=True
    images=[pefile.PE(str(ROOT/SPECS[k][0])) for k in ('original','official_modern')]
    pair_bodies=[p.get_data(0x6b3a0,0x46c2e6-0x46b3a0) for p in images]
    changes=[0x46b3a0+i for i,(a,b) in enumerate(zip(*pair_bodies)) if a!=b]
    assert changes==[0x46c1f0]
    result['percentage_pair_changed_addresses']=[f'{a:08x}' for a in changes]
    assert result['binaries']['original']['percentage_pair']['constant_bytes_hex']==result['binaries']['official_modern']['percentage_pair']['constant_bytes_hex']
    (ROOT/'analysis/evidence/audits/original-modern-slider-percentage.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baselines, complete slider bodies and identical 3755-byte prefix')


if __name__=='__main__':main()
