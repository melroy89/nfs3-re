"""Static five caller-immediate edits; playback policy belongs to separate callee audit."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

CASES=[(0x4449d0,0x444a52,[0x4449fe]),(0x4450c0,0x44514c,[0x4450ee]),
       (0x445680,0x44574f,[0x4456ae,0x4456e4]),(0x44a6b0,0x44a860,[0x44a81c])]


def main():
    result={'kind':'frontend-hover-sound-caller-immediates','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/hover-sound-calls'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end,sites in CASES:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            for address in sites:
                offset=address-start
                assert data[offset:offset+5]==b'\xba'+struct.pack('<I',45 if label=='original' else 127)
                assert data[offset+5:offset+8]==bytes.fromhex('31c0e8')
                assert address+12+struct.unpack('<i',data[offset+8:offset+12])[0]==0x4181d0
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT)),
                'mov_edx_sites':[f'{v:08x}' for v in sites]})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    for i,(start,_,sites) in enumerate(CASES):
        assert [j for j,(a,b) in enumerate(zip(blobs['original'][i],blobs['official_modern'][i])) if a!=b]==[v-start+1 for v in sites]
    result['limits']=['Static callers only; no audio or hover execution.',
        'The separate frontend-sound comparison establishes that Modern ignores incoming EDX.']
    (ROOT/'analysis/evidence/audits/frontend-hover-sound-calls.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four complete envelopes, five isolated EDX 45-to-127 edits and retained sound-ID-0 calls')


if __name__=='__main__':main()
