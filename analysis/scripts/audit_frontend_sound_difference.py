"""Static frontend sound contract/volume comparison; no audio execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {'original': [(0x4181d0,0x418280),(0x4e9b20,0x4e9b5d)],
    'official_modern': [(0x4181d0,0x418262),(0x4e9b20,0x4e9b5d),
        (0x4376fc,0x43778c),(0x472248,0x472277),(0x4381a9,0x4381c5)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/frontend-sound'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-frontend-sound-comparison','range_end':'exclusive','binaries':{},
        'limits':['No sound/game/instruction execution.','Counter unit and backend audible behavior unverified.']}
    helpers={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in SPANS[label]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows}
        if label=='official_modern':
            item['slider_double_constants']={f'{va:08x}':struct.unpack('<d',pe.get_data(va-0x400000,8))[0]
                for va in [0x537600,0x537598]}
        result['binaries'][label]=item
        helpers[label]=pe.get_data(0x4e9b20-0x400000,0x3d)
    assert helpers['original']==helpers['official_modern']
    result['sound_record_initializer_identical']=True
    (ROOT/'analysis/evidence/audits/original-modern-frontend-sound.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: sound baselines, contract/slider spans, identical record initializer')


if __name__=='__main__':main()
