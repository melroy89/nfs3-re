"""Static FOV/projection comparison; no rendering or instruction execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

LEGACY=[(0x4fd280,0x4fd2a8),(0x4fd2b0,0x4fd3eb),(0x4fd3f0,0x4fd420)]

SPANS={'original':LEGACY+[(0x4dbcc0,0x4dbd97),(0x4becd0,0x4bed69),(0x4bf260,0x4bf370)],
       'official_modern':[(0x4dbc48,0x4dbd35),(0x4becd0,0x4bed69),
                          (0x4bf260,0x4bf370),(0x4be748,0x4be74d)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/projection'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-projection-comparison','range_end':'exclusive','binaries':{},
        'limits':['No render/game/instruction execution.','Formula summaries do not claim bit-exact libm/x87 equivalence.']}
    bodies={}
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
            item['float_constants']={f'{va:08x}':{'hex':pe.get_data(va-0x400000,4).hex(),
                'value':struct.unpack('<f',pe.get_data(va-0x400000,4))[0]}
                for va in [0x5401c0,0x5401c4,0x5401c8,0x53f420,0x5401cc,0x5401d0,0x5401d4]}
        if label=='official_modern':
            item['removed_legacy_ranges']=[]
            for start,end in LEGACY:
                blob=pe.get_data(start-0x400000,end-start)
                assert blob==b'\x90'*(end-start)
                item['removed_legacy_ranges'].append({'start':f'{start:08x}',
                    'end':f'{end:08x}','all_nop':True,'sha256':hashlib.sha256(blob).hexdigest()})
        result['binaries'][label]=item
        bodies[label]=pe.get_data(0x4bf260-0x400000,0x110)
    assert bodies['original']==bodies['official_modern']
    result['projection_builder_272_bytes_identical']=True
    (ROOT/'analysis/evidence/audits/original-modern-projection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: projection baselines, FOV/constants/callers and identical builder')


if __name__=='__main__':main()
