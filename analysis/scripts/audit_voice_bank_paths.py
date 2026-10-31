"""Static paired removal of language path switches in sequence/radio loaders."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

CASES=[(0x4c94e0,0x4c9588,0x4c94f4,0x4c9526,0x4c94c0),
       (0x4c9890,0x4c998f,0x4c98a6,0x4c98d8,0x4c9874)]


def main():
    result={'kind':'sequence-radio-path-switch-removal','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/voice-bank-paths'
    capture.mkdir(parents=True,exist_ok=True)
    blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end,change,tail,table in CASES:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            tabledata=pe.get_data(table-0x400000,24)
            if label=='original':
                first=change+17
                assert struct.unpack('<6I',tabledata)==(first,first+7,first+14,first+21,first+28,first)
            else:assert tabledata==b'\x90'*24
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT)),
                'old_jump_table_address':f'{table:08x}','table_bytes_hex':tabledata.hex()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['changes']=[]
    for i,(start,end,change,tail,_) in enumerate(CASES):
        a,b=blobs['original'][i],blobs['official_modern'][i];lo,hi=change-start,tail-start
        assert a[:lo]==b[:lo] and a[hi:]==b[hi:]
        assert a[lo:lo+10]==bytes.fromhex('a14cbb6f0083f8057745')
        assert b[lo:hi]==bytes.fromhex('be342b7a00eb2b')+b'\x90'*43
        result['changes'].append({'entry':f'{start:08x}','changed_region_start':f'{change:08x}',
            'identical_tail_start':f'{tail:08x}','changed_bytes':sum(x!=y for x,y in zip(a,b))})
    result['limits']=['Static function/path switch evidence only; no audio or asset validation.',
        'Shared path initialization and selector producer limits remain in the sound-bank report.']
    (ROOT/'analysis/evidence/audits/voice-bank-paths.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete 168/255-byte envelopes; two shared-path replacements; original tables and Modern NOPs')


if __name__=='__main__':main()
