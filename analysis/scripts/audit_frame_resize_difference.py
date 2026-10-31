"""Compare viewport resize wrapper, input witnesses and retained adjustment helper."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-viewport-resize-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/frame-resize'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe); rows = []
        for start,end in ((0x4be970, 0x4bea31 if label == 'original' else 0x4bea36), (0x4bea40,0x4beaf7),(0x4c4fbe,0x4c4ff2)):
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path':relative,'sha256':expected,'spans':rows}
    result['retained_ranges'] = []
    for start,end in ((0x4bea40,0x4beaf7),(0x4c4fbe,0x4c4ff2),(0x4be970,0x4be9a3),(0x4be9aa,0x4bea2a)):
        pair=[p.get_data(start-0x400000,end-start) for p in images];assert pair[0]==pair[1]
        result['retained_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pair[0]).hexdigest()})
    assert images[0].get_data(0xbea2a,7)==images[1].get_data(0xbea2f,7)
    call=images[1].get_data(0xbea2a,5)
    assert call[0]==0xe8 and 0x4bea2f+int.from_bytes(call[1:],'little',signed=True)==0x4be85c
    result['changed_gate']={'start':'004be9a3','original_hex':images[0].get_data(0xbe9a3,7).hex(),'modern_hex':images[1].get_data(0xbe9a3,7).hex()}
    result['limits']=['No input, resizing or target execution.','Held action indexes are observed; human key labels and release-introduction dates remain separate.','Visual horizon/camera-shift effect and runtime state admission not validated.']
    (ROOT/'analysis/evidence/audits/original-modern-frame-resize.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: retained input/adjustment bodies; narrowed gate and added rectangle refresh')


if __name__=='__main__': main()
