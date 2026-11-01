"""Static police-list row/panel spacing constants and their consumers."""
import hashlib,json,struct
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-police-list-spacing','binaries':{}};bodies={}
    for label,(relative,digest,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        constants={}
        for address in [0x53b598,0x53b5a0,0x53b8cc,0x53b8d4]:
            data=get(address,address+8);value=struct.unpack('<d',data)[0]
            assert value==((20.0 if label=='original' else 12.414) if address in [0x53b598,0x53b8cc] else 1/13)
            constants[f'{address:08x}']={'hex':data.hex(),'binary64':value}
        spans=[(0x48a660,0x48aa3e),(0x481ca0,0x481cd8),(0x481d44,0x481d78),
               (0x4d14f0,0x4d1531),(0x4d1540,0x4d1583)]
        rows=[];bodies[label]=[]
        for a,b in spans:
            data=get(a,b);bodies[label].append(data)
            rows.append({'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(data),
                         'hex':data.hex(),'disassembly':disassemble(data,a)})
        assert get(0x48a70b,0x48a714).hex()=='db45fcdc0dccb85300'
        assert get(0x48a722,0x48a728).hex()=='dc0dd4b85300'
        assert get(0x48a732,0x48a73a).hex()=='e81f560500db5de0'
        assert get(0x48a8c2,0x48a8cd).hex()=='8b45e08b153cfe550001c7'
        assert get(0x481cbb,0x481cd8).hex()=='db45fcdc0d98b55300dc0da0b55300e887e00500db5df48b4df40fafcf'
        result['binaries'][label]={'path':relative,'sha256':digest,'constants':constants,'captures':rows}
    old,new=bodies.values()
    assert old[1]==new[1] and old[3:]==new[3:]
    differences=[0x48a660+i for i,(a,b) in enumerate(zip(old[0],new[0]))if a!=b]
    assert differences==[0x48a672,0x48a673,0x48a674,0x48a716,0x48a717,0x48a718]
    result['renderer_changed_bytes']=[f'{a:08x}'for a in differences]
    result['derived_equal_metric_ratio']={'modern_over_original_before_truncation':12.414/20,
        'assumptions':'Same ordinary positive summed font metrics, before integer conversion; no physical pixel or measured height claim.'}
    result['limits']=['No game, text, drawing or extracted instruction execution.',
        'Constants and direct row/panel consumers verified, not complete layout equivalence to the standard standings list.',
        'Metric helpers read loaded font-bank tables/effective scale; actual metrics, assets and caller scale can differ.',
        'Integer conversion, x87 control/status/exceptions and wrapping integer products require chosen-version semantics.',
        'Panel sample counts, clipping/visibility, caller/profile admission and1.0.0 introduction unverified.',
        'Unchanged metric helper instructions do not imply unchanged table contents, scale or transitive truncation-helper behavior.']
    (ROOT/'analysis/evidence/audits/police-list-spacing.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired20->12.414 binary64 constants, retained metric/panel consumers and renderer row advance')


if __name__=='__main__':main()
