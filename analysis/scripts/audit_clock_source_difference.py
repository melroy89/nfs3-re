"""Static original/Modern clock source and loading-timing witnesses."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SITES=[0x48eb97,0x48ebe4,0x48ed70,0x48ed8e,0x48f13d,0x48f160,0x48f17b,
       0x49faba,0x49fad9,0x4ed169,0x4ed2ec,0x4ed366,0x4ed3a6,0x4f2792,
       0x4f6e9c,0x4f6ee3]
TIMER_SPANS=[(0x48eb90,0x48ec3d),(0x48ed30,0x48ee27),
             (0x48eff0,0x48f070),(0x48f075,0x48f1e5)]


def main():
    capture=ROOT/'analysis/captures/modern-differences/clock-source'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-clock-loading-timing-comparison','range_end':'exclusive',
        'binaries':{},'clock_sites':[],
        'limits':['No target/API timing, scheduling, frame-rate or synchronization measurement.',
            'Direct IAT sites do not exclude indirect calls or dynamically resolved time sources.',
            'Normalized byte equality is not runtime-state equivalence.']}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        data=(ROOT/relative).read_bytes();assert hashlib.sha256(data).hexdigest()==expected
        pe=pefile.PE(data=data);images[label]=pe
        spans=list(TIMER_SPANS)+[(0x4f2790,0x4f279c if label=='original' else 0x4f279b),
                                 (0x533d18,0x533d1e)]
        if label=='original':spans += [(0x4a3400,0x4a35cb)]
        else:spans += [(0x4a33d0,0x4a35a5),(0x490134,0x4901c3),
                      (0x495230,0x495268),(0x4955a0,0x4955c4),(0x451960,0x4519b0),
                      (0x4b5624,0x4b5634)]
        spans += [(a,a+7) for a in SITES if a!=0x4f2792]
        rows=[]
        for start,end in spans:
            text=subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True)
            output=capture/f'{label}-{start:08x}.asm';output.write_text(text)
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        imports={f'{i.address:08x}':{'dll':d.dll.decode(),'name':i.name.decode()}
            for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
            if i.name and i.name in (b'GetTickCount',b'timeGetTime',b'timeBeginPeriod',b'timeEndPeriod',b'timeSetEvent')}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'clock_imports':imports}
    for a in SITES:
        row={'address':f'{a:08x}'}
        for label,iat in [('original',0x534568),('official_modern',0x534664)]:
            raw=images[label].get_data(a-0x400000,7)
            prefix=3 if raw[:3]==b'\x2e\xff\x15' else 2
            assert raw[prefix-2:prefix]==b'\xff\x15'
            assert struct.unpack('<I',raw[prefix:prefix+4])[0]==iat
            row[label+'_instruction_hex']=raw[:prefix+4].hex()
        result['clock_sites'].append(row)
    normalized=[]
    for start,end in TIMER_SPANS:
        old=bytearray(images['original'].get_data(start-0x400000,end-start))
        modern=images['official_modern'].get_data(start-0x400000,end-start)
        replaced=[]
        for a in SITES:
            if start<=a and a+7<=end:
                assert old[a-start:a-start+3]==b'\x2e\xff\x15'
                old[a-start+3:a-start+7]=struct.pack('<I',0x534664);replaced.append(f'{a:08x}')
        assert bytes(old)==modern
        normalized.append({'start':f'{start:08x}','end':f'{end:08x}',
                           'only_changes_are_clock_IAT_operands':True,'sites':replaced})
    result['normalized_timer_ranges']=normalized
    output=ROOT/'analysis/evidence/audits/original-modern-clock-source.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 16 clock callsites, 3 timer functions after operand normalization, loading spans')


if __name__=='__main__':main()
