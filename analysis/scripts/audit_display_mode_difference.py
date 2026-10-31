"""Static original/Modern display-mode enumerator and menu-list witnesses.

Requires pefile/GNU objdump; no game, driver or instruction execution.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4bed90, 0x4bee72), (0x448210, 0x4482e8), (0x517610, 0x51788d),
                 (0x472d10, 0x472f19), (0x4483a0, 0x4483fe), (0x4bef50, 0x4bf10f), (0x44b1a0,0x44b206)],
    'official_modern': [(0x4bed90, 0x4beeb0), (0x448210, 0x448345), (0x4beeb0, 0x4bef9d),
                        (0x448394, 0x448425), (0x472d10, 0x472e1d),
                        (0x472aac, 0x472aeb), (0x4f9140, 0x4f915e), (0x44b1a0,0x44b206), (0x448348,0x44837c)],
}


def main():
    capture = ROOT/'analysis/captures/modern-differences/display-modes'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-display-mode-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['Driver-provided records were not executed or mutated.',
            'Menu count boundary is not a proved reachable storage fault.',
            'Driver DLL enumeration limits and actual UI behavior remain untested.']}
    images=[]
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        images.append(pe)
        rows = []
        for start, end in SPANS[label]:
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = capture/f'{label}-{start:08x}.asm'
            output.write_text(text)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    selected_accessors=images[1].get_data(0x48348,52)
    assert selected_accessors==bytes.fromhex('a15c82a1003b056082a100720731c0a35c82a10069c014010000053083a100c3e8dbffffff8b4010c3909090e8cfffffff8b00c3')
    result['selected_record_accessors']={'selector':'00448348','field10_accessor':'00448368',
        'field0_accessor':'00448374','record_stride':276,'index':'00a1825c','count':'00a18260',
        'base':'00a18330','limits':'Unsigned index normalization does not reject an empty list; original counterparts unverified.'}
    original_recovery,modern_recovery=[p.get_data(0x4b1a0,102) for p in images]
    assert [i for i,(a,b) in enumerate(zip(original_recovery,modern_recovery)) if a!=b]==[0x46,0x47]
    assert original_recovery[0x45:0x4a]==bytes.fromhex('e8663d0700')
    assert modern_recovery[0x45:0x4a]==bytes.fromhex('e8c63c0700')
    result['recovery_call']={'instruction':'0044b1e5','original_target':'004bef50',
        'modern_target':'004beeb0','input_eax':1,'limits':'Caller does not check application return; no runtime recovery test.'}
    output = ROOT/'analysis/evidence/audits/original-modern-display-modes.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: original/Modern identity and enumerator/menu instruction captures')


if __name__ == '__main__':
    main()
