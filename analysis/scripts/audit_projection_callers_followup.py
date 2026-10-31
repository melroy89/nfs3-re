"""Check wide-angle caller ABI adjustment and relocated scaling constants."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'projection-caller-followup', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/projection-callers'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        blobs[label] = []
        for start, end in [(0x495190, 0x495223), (0x4dbda0, 0x4dbddf)]:
            data = pe.get_data(start - 0x400000, end - start)
            blobs[label].append(data)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        constants = []
        for address in ([0x53be28, 0x53be2c] if label == 'original' else [0x53bdd4, 0x53bdd8]):
            data = pe.get_data(address - 0x400000, 4)
            constants.append({'address': f'{address:08x}', 'bytes_hex': data.hex(),
                'binary32_value': struct.unpack('<f', data)[0]})
        assert [c['bytes_hex'] for c in constants] == ['cdcccc3a', '8988083b']
        result['binaries'][label] = {'path': relative, 'sha256': expected,
            'spans': rows, 'scaling_constants': constants}
    old, new = blobs['original'], blobs['official_modern']
    assert [i for i, (a, b) in enumerate(zip(old[0], new[0])) if a != b] == [0x34, 0x35, 0x47, 0x48]
    assert old[0][0x32:0x38] == bytes.fromhex('d80d28be5300')
    assert new[0][0x32:0x38] == bytes.fromhex('d80dd4bd5300')
    for offset in (0x12, 0x27):
        assert old[1][offset:offset+4] == struct.pack('<I', 120)
        assert new[1][offset:offset+4] == struct.pack('<f', 120.0)
    assert [i for i, (a, b) in enumerate(zip(old[1], new[1])) if a != b] == [0x12, 0x14, 0x15, 0x27, 0x29, 0x2a]
    result['limits'] = ['Static bytes only; no rendered output or x87 state equivalence.',
        'Callee interface correspondence relies on the linked projection comparison.']
    (ROOT / 'analysis/evidence/audits/projection-callers-followup.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: identical relocated float constants and integer-120 to binary32-120 caller adjustment')


if __name__ == '__main__':
    main()
