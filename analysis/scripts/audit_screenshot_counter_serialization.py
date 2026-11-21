"""Locate screenshot counter inside the config save/load block; static only."""
import hashlib,json
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    path,pin,_=SPECS['official_modern'];raw=(ROOT/path).read_bytes();assert sha(raw)==pin
    pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
    assert get(0x472869,0x472875).hex()=='b9f020000031dbbe40bb6f00'
    assert get(0x472898,0x4728a2).hex()=='c7806018000000000000'
    assert get(0x4728a9,0x4728ae).hex()=='bbf0200000'
    assert get(0x472a7f,0x472a89).hex()=='bf40bb6f00e857030700'
    assert get(0x472a94,0x472aa4).hex()=='5789c8c1e902f2a58ac880e103f2a45f'
    assert get(0x4e31c7,0x4e31cf).hex()=='f00fc105e0d16f00'
    assert get(0x4c451b,0x4c4520).hex()=='a3e0d16f00'
    base=0x6fbb40;counter=0x6fd1e0;offset=counter-base;assert offset==0x16a0 and offset+4<=0x20f0
    spans=[('save',0x472820,0x4728d3),('load',0x472980,0x472b48),
           ('accepted_header_normalizer',0x472230,0x472248),
           ('counter_selection',0x4e31c4,0x4e31ef),('directory_reset',0x4c450d,0x4c452c)]
    result={'kind':'static-screenshot-counter-serialization','baseline':{'path':path,'sha256':pin},
        'layout':{'block_base':f'{base:08x}','block_bytes':0x20f0,'counter':f'{counter:08x}',
                  'counter_offset':offset,'counter_bytes':4,'save_temporary_cleared_offset':0x1860},
        'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                     'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans],
        'verified':[
            'Atomic screenshot counter lies at offset16a0 within the20f0-byte config block copied by the save path.',
            'Only explicit post-copy clear in the inspected save body targets1860,not counter offset16a0.',
            'Load body copies read buffer to006fbb40 before header checks;counter belongs to that declared block extent.',
            'Directory helper can subsequently reset counter to0;serialization inclusion does not guarantee retained number.',
            'This supports conditional cross-launch counter persistence via config.dat,not a directory maximum scan.'],
        'limits':[
            'Static copy extents and requested I/O only;allocation/helper preservation,successful full read/write and actual file bytes not newly validated.',
            'Normal forward-copy/direction-flag assumptions apply;no concurrent snapshot atomicity established.',
            'All startup/caller/default/profile/alias writes and process-exit save ordering not closed.',
            'No game,file API,target instructions,compilation or Ghidra writes executed.']}
    (ROOT/'analysis/evidence/audits/screenshot-counter-serialization.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:screenshot counter at config+16a0 lies inside save/load extent;clear1860 is distinct')


if __name__=='__main__':main()
