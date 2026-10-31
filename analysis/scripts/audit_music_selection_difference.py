"""Static music selection comparison; no audio execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {'original': [(0x40ffd0,0x410027),(0x4103a0,0x41045d)],
    'official_modern': [(0x40fefc,0x40ff80),(0x40ff9c,0x40fffb),
        (0x4103a0,0x410446),(0x410606,0x410615),
        (0x4b5d30,0x4b5d35),(0x4a3489,0x4a348e)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/music-selection'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-music-selection-comparison','range_end':'exclusive','binaries':{},
        'limits':['No sound/game/instruction execution.','Track asset names, RNG distribution and audible behavior unverified.']}
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
            item['menu_cycle_ids']=list(pe.get_data(0x40ff80-0x400000,6))
            item['menu_seed_map']=list(pe.get_data(0x40ff88-0x400000,20))
        else:
            item['fixed_race_targets']=[f'{v:08x}' for v in struct.unpack('<10I',pe.get_data(0x40ffa4-0x400000,40))]
        result['binaries'][label]=item
    (ROOT/'analysis/evidence/audits/original-modern-music-selection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: music baselines, selection spans and menu cycle tables')


if __name__=='__main__':main()
