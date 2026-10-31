"""Compare frontend page switch extension and selected record/resource; no execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-frontend-page-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No rendering, decompression or target execution.', 'Record 75 selection at runtime not proven.']}
    capture = ROOT/'analysis/captures/modern-differences/frontend-page'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x441cb0, 0x44236c), (0x437820, 0x4378b6)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}',
                f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        row = {'path': relative, 'sha256': expected, 'spans': rows,
               'switch_table_first_five': [f'{a:08x}' for a in struct.unpack('<5I', pe.get_data(0x41c90,20))],
               'record_75_words': [f'{a:08x}' for a in struct.unpack('<4I',pe.get_data(0x155c08,16))]}
        if label == 'official_modern':
            row['sixth_switch_target'] = f'{struct.unpack("<I",pe.get_data(0x41ca4,4))[0]:08x}'
            row['strings'] = {f'{a:08x}': pe.get_data(a-0x400000,40).split(b'\0')[0].decode('ascii') for a in (0x53f7d4,0x53f7e0)}
        result['binaries'][label] = row
    bodies = [p.get_data(0x41cb0,0x44236c-0x441cb0) for p in images]
    changes = [0x441cb0+i for i,(a,b) in enumerate(zip(*bodies)) if a!=b]
    assert changes == [0x441d03]
    result['main_body_changed_addresses'] = [f'{a:08x}' for a in changes]
    assert result['binaries']['original']['switch_table_first_five'] == result['binaries']['official_modern']['switch_table_first_five']
    assert result['binaries']['official_modern']['sixth_switch_target'] == '00437820'
    (ROOT/'analysis/evidence/audits/original-modern-frontend-page.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baselines, one-byte main-body delta, retained five targets, new resource record')


if __name__ == '__main__':
    main()
