"""Verify grouped one-byte renderer-mask changes across complete function envelopes."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = [
    (0x41a120,0x41a354,0x41a1c8), (0x491190,0x491bb8,0x491225),
    (0x491bc0,0x492362,0x492208), (0x492370,0x492973,0x4925a2),
    (0x492980,0x493361,0x492c15), (0x49d800,0x49d8eb,0x49d814),
    (0x4cb750,0x4cbc84,0x4cb870), (0x4cbc90,0x4cc539,0x4cbf31),
    (0x4ddb40,0x4de064,0x4ddd59), (0x4de070,0x4de6f9,0x4de0be),
    (0x4de700,0x4decd1,0x4de770),
]


def main():
    result = {'kind':'effect-renderer-mask-expansion','binaries':{},'functions':[]}
    capture = ROOT/'analysis/captures/modern-differences/effect-renderer-masks'
    capture.mkdir(parents=True,exist_ok=True)
    blobs = {}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        rows=[]
        blobs[label]=[]
        for start,end,changed in SPANS:
            data=pe.get_data(start-0x400000,end-start)
            blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    for i,(start,end,changed) in enumerate(SPANS):
        old,new=blobs['original'][i],blobs['official_modern'][i]
        offset=changed-start
        assert [j for j,(a,b) in enumerate(zip(old,new)) if a!=b]==[offset]
        assert old[offset]==0x40 and new[offset]==0x50
        assert new[offset-2:offset] in (b'\xf6\xc4',b'\xf6\xc3') or new[offset-6:offset]==bytes.fromhex('f605583a7a00')
        result['functions'].append({'entry':f'{start:08x}','bytes':end-start,'changed_byte':f'{changed:08x}'})
    changed_inputs=[v for v in range(256) if bool(v&0x40)!=bool(v&0x50)]
    assert changed_inputs==[v for v in range(256) if (v&0x10) and not(v&0x40)]
    result['predicate_changed_byte_inputs']=changed_inputs
    result['limits']=['Static code and exhaustive Boolean mask comparison only; no rendered observations.',
        'Equal code tails do not prove equal data, x87 state or full machine-state equivalence.']
    (ROOT/'analysis/evidence/audits/effect-renderer-masks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(SPANS)} complete envelopes, {sum(b-a for a,b,_ in SPANS)} bytes; 11 isolated 40-to-50 masks; 256 predicate inputs')


if __name__=='__main__':main()
