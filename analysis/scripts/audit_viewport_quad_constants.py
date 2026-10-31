"""Verify six changed draw arguments without executing target instructions."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    start, end = 0x4a75e0, 0x4a78b6
    sites = [0x4a77bf, 0x4a77cd, 0x4a781d, 0x4a782d, 0x4a787e, 0x4a788c]
    result = {'kind': 'viewport-quad-draw-argument-comparison', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/viewport-quad-constants'
    capture.mkdir(parents=True, exist_ok=True)
    normalized = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        data = pe.get_data(start - 0x400000, end - start)
        assert len(data) == 726 and data[-1] == 0xc3
        bits = 0x3f440000 if label == 'original' else 0x3f447ae1
        masked = bytearray(data)
        for site in sites:
            offset = site - start
            assert data[offset:offset + 5] == b'\x68' + struct.pack('<I', bits)
            masked[offset + 1:offset + 5] = b'\0' * 4
        normalized.append(masked)
        path = capture / f'{label}.asm'
        path.write_bytes(subprocess.check_output([
            'objdump', '-d', '-Mintel', f'--start-address={start}',
            f'--stop-address={end}', relative], cwd=ROOT))
        result['binaries'][label] = {
            'path': relative, 'sha256': expected,
            'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
            'span_sha256': hashlib.sha256(data).hexdigest(),
            'assembly': str(path.relative_to(ROOT)),
            'push_sites': [f'{site:08x}' for site in sites],
            'argument_bits': f'{bits:08x}',
            'binary32_value': struct.unpack('<f', struct.pack('<I', bits))[0]}
    assert normalized[0] == normalized[1]
    result['limits'] = [
        'Draw argument semantics and visible effects unresolved.',
        'Retained callees may differ; whole rendering equivalence not established.',
        'No target execution, Ghidra writes or executable changes.']
    (ROOT / 'analysis/evidence/audits/viewport-quad-constants.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print('PASS: complete 726-byte envelope differs only in six PUSH arguments')


if __name__ == '__main__':
    main()
