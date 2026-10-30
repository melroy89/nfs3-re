"""Static loading-artwork tile/progress witnesses; no renderer/game execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

COMMON=[(0x4beb20,0x4beb3f),(0x431bc0,0x431c1a),(0x4ef760,0x4ef82c),
        (0x4ef1b0,0x4ef1e0),(0x4f1c30,0x4f1c6c),(0x4f2d78,0x4f2d93)]


def main():
    capture=ROOT/'analysis/captures/modern-differences/loading-artwork'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-loading-artwork-comparison','range_end':'exclusive',
        'binaries':{},'limits':['No target/rendering execution or performance measurement.',
            'Register liveness distinguishes helper arguments from preserved caller state.',
            'No full pixel/ownership/failure equivalence claim.']}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data);rows=[]
        spans=[(0x494cb0,0x494fa0 if label=='original' else 0x494f9c)]+COMMON
        for start,end in spans:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        addresses=(0x53bddc,0x53bde0,0x53bdf0,0x53bdf4,0x53bdf8,0x53bdfc) if label=='original' else (0x53bdcc,0x53bdd0)
        floats={f'{a:08x}':{'bits_le':pe.get_data(a-0x400000,4).hex(),
                'binary32':struct.unpack('<f',pe.get_data(a-0x400000,4))[0]} for a in addresses}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'float_constants':floats}
        if label=='original':result['binaries'][label]['step_double']=struct.unpack('<d',pe.get_data(0x13bde8,8))[0]
    for index in (5,6):
        assert result['binaries']['original']['spans'][index]['bytes_sha256']==result['binaries']['official_modern']['spans'][index]['bytes_sha256']
    output=ROOT/'analysis/evidence/audits/original-modern-loading-artwork.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: fingerprints, loading/helper captures and unchanged floor/ceil bodies')


if __name__=='__main__':main()
