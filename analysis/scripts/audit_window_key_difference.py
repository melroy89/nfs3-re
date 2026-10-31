"""Static window-key translator and Modern mapping tables."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-window-key-comparison', 'range_end': 'exclusive', 'binaries': {}}
    images = {}
    capture = ROOT / 'analysis/captures/modern-differences/window-key'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        rows = []
        for start, end in [(0x4ccaa0, 0x4ccc67 if label == 'original' else 0x4ccaf6)]:
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path':relative,'sha256':expected,'spans':rows}
    pe=images['official_modern']
    result['modern_tables']={}
    for address,count in [(0x4ccaf8,23),(0x4ccb54,12)]:
        raw=pe.get_data(address-0x400000,count*4)
        pairs=[list(struct.unpack_from('<HH',raw,i*4)) for i in range(count)]
        assert pairs[-1]==[0,0]
        result['modern_tables'][f'{address:08x}']={'pairs':pairs,'sha256':hashlib.sha256(raw).hexdigest()}
    imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address==0x534744}
    assert imports=={0x534744:'GetKeyState'}
    result['modern_import']={'00534744':'GetKeyState'}
    result['limits']=['Static only; no keyboard events or UI behavior tested.','Original mappings inspected from branch tree; no exhaustive executable equivalence test.']
    (ROOT / 'analysis/evidence/audits/original-modern-window-key.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: paired window-key translator bodies, Modern mapping tables and GetKeyState import')


if __name__ == '__main__':
    main()
