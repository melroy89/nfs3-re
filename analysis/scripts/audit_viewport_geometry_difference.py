"""Static viewport/border arithmetic witnesses, without target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4be570,0x4be5d1),(0x4be5e0,0x4be8d2),
        (0x4beb00,0x4beb15),(0x4beb40,0x4beb56),(0x47f650,0x47fbdc)],
    'official_modern': [(0x4be570,0x4be5d1),(0x4be5e0,0x4be85a),
        (0x4be89c,0x4be8b5),(0x47f650,0x47f9bd),
        (0x4be85c,0x4be89b),(0x4be84c,0x4be85a),(0x4bea13,0x4bea2f)],
}


def main():
    capture=ROOT/'analysis/captures/modern-differences/viewport-geometry'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-viewport-border-comparison','range_end':'exclusive',
        'binaries':{},'limits':['No rendering or target instructions executed.',
            'Profile flags and all downstream transforms are not fully mapped.',
            'x87 rounding/precision can affect stored integer/float results.']}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data)
        rows=[]
        spans=list(SPANS[label])+[(a,a+5) for a in (0x48106d,0x4812cd,0x4813cb,0x481b6d,0x481eee,0x47fdc2)]
        for start,end in spans:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        if label == 'official_modern':
            for site in (0x4be851, 0x4bea2a):
                call = pe.get_data(site-0x400000, 5)
                assert call[0] == 0xe8 and site+5+int.from_bytes(call[1:], 'little', signed=True) == 0x4be85c
        floats={}
        for va in (0x538ad8,0x53a9d4,0x53a9e0,0x53b4f8,0x53b4fc):
            raw=pe.get_data(va-0x400000,4)
            floats[f'{va:08x}']={'little_endian_hex':raw.hex(),'binary32_value':struct.unpack('<f',raw)[0]}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'file_backed_floats':floats}
    output=ROOT/'analysis/evidence/audits/original-modern-viewport-geometry.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: both fingerprints, viewport/border instruction captures and file-backed floats')


if __name__=='__main__': main()
