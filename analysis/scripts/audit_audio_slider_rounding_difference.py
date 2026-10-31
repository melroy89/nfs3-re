"""Compare five complete audio-slider callbacks and seven removed truncation calls."""
import hashlib
import json
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    spans = [(0x437990,0x4379af),(0x4379b0,0x4379cf),(0x4379d0,0x437a1d),
             (0x437a20,0x437a6d),(0x437a70,0x437a8f)]
    sites = [0x4379a1,0x4379c1,0x4379f4,0x437a0d,0x437a44,0x437a5d,0x437a81]
    images = {}
    out = {'kind':'static-audio-slider-rounding-comparison','baselines':{}}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw); images[label]=pe
        bodies=[]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start)
            bodies.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'hex':data.hex(),'sha256':hashlib.sha256(data).hexdigest()})
        constants=pe.get_data(0x137578,40)
        assert struct.unpack('<5d',constants)==(127.0,)*5
        out['baselines'][label]={'path':relative,'sha256':expected,'bodies':bodies,
            'constants_00537578_hex':constants.hex()}
    for site in sites:
        old=images['original'].get_data(site-0x400000,5)
        assert old[0]==0xe8 and site+5+int.from_bytes(old[1:],'little',signed=True)==0x4dfd56
        assert images['official_modern'].get_data(site-0x400000,5)==bytes.fromhex('eb03909090')
    changed=[]
    for start,end in spans:
        a,b=[pe.get_data(start-0x400000,end-start) for pe in images.values()]
        changed.extend(start+i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
    assert len(changed)==35 and all(any(site<=va<site+5 for site in sites) for va in changed)
    out['changed_addresses']=[f'{va:08x}' for va in changed]
    out['removed_call_sites']=[f'{site:08x}' for site in sites]
    out['limits']=['No audio, callback or instruction execution.','Ambient x87 control/state and getter leaf contracts not universally qualified.',
        'No claim of audible difference or historical release attribution.']
    (ROOT/'analysis/evidence/audits/audio-slider-rounding-difference.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: five complete callbacks,35 changed bytes at seven removed truncation calls, five127 constants')


if __name__=='__main__':main()
