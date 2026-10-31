"""Static renderer selection and optional DirectDraw compatibility witnesses."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4f87e0, 0x4f882e), (0x50ead0, 0x50eb2a),
                 (0x4b59c0, 0x4b5a28)],
    'official_modern': [(0x4b57c4, 0x4b57f3), (0x4f1ea0, 0x4f1ed2),
                        (0x4b5a58, 0x4b5acd)],
}


def main():
    capture = ROOT / 'analysis/captures/modern-differences/renderer-selection'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-renderer-selection-comparison', 'range_end': 'exclusive',
              'binaries': {}, 'limits': ['No DLL/API or target execution.',
              'Original table entries are candidates, not proof of successful loading.',
              'Compatibility option effects and historical introduction remain unverified.']}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        def string(va):
            return pe.get_data(va - 0x400000, 128).split(b'\0')[0].decode('ascii')
        rows = []
        for start, end in SPANS[label]:
            output = capture / f'{label}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        item = {'path': relative, 'sha256': expected, 'spans': rows}
        if label == 'original':
            item['environment_key'] = string(0x54d700)
            item['driver_name_table'] = []
            for index in range(11):
                slot = 0x55fd68 + 4*index
                pointer = struct.unpack('<I', pe.get_data(slot-0x400000, 4))[0]
                item['driver_name_table'].append({'index': index, 'slot': f'{slot:08x}',
                    'pointer': f'{pointer:08x}', 'string': string(pointer)})
            assert item['environment_key'] == 'THRASH_DRIVERNAME'
        else:
            item['optional_interface'] = {'dll': string(0x53f76c), 'export': string(0x53f778)}
            assert item['optional_interface'] == {'dll': 'DDRAW.DLL', 'export': 'SetAppCompatData'}
        result['binaries'][label] = item
    output = ROOT / 'analysis/evidence/audits/original-modern-renderer-selection.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baseline hashes, renderer selection/compatibility spans and strings')


if __name__ == '__main__':
    main()
