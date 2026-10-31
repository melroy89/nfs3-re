"""Compare the complete bounded shape-conversion envelope without execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    start, end = 0x4d37a0, 0x4d3f42
    result = {'kind': 'shape-conversion-descriptor-comparison', 'binaries': {}}
    blobs = {}
    capture = ROOT / 'analysis/captures/modern-differences/shape-conversion'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        blob = pe.get_data(start - pe.OPTIONAL_HEADER.ImageBase, end - start)
        assert len(blob) == end - start
        blobs[label] = blob
        path = capture / f'{label}-{start:08x}.asm'
        path.write_bytes(subprocess.check_output([
            'objdump', '-d', '-Mintel', f'--start-address={start}',
            f'--stop-address={end}', relative], cwd=ROOT))
        result['binaries'][label] = {'path': relative, 'sha256': expected,
            'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
            'span_sha256': hashlib.sha256(blob).hexdigest(),
            'assembly': str(path.relative_to(ROOT))}
    old, new = blobs['original'], blobs['official_modern']
    runs = []
    for offset, (a, b) in enumerate(zip(old, new)):
        if a == b:
            continue
        address = start + offset
        if runs and runs[-1][1] == address:
            runs[-1][1] += 1
        else:
            runs.append([address, address + 1])
    assert runs == [[0x4d37be, 0x4d37c3], [0x4d37f0, 0x4d3827]]
    assert old[0x1e:0x24] == bytes.fromhex('ff1580f99e00')
    assert new[0x1e:0x24] == bytes.fromhex('90a15c3a7a00')
    assert new[0x6b:0x87] == b'\x90' * 28
    assert old[0x87:] == new[0x87:]
    result['changed_runs'] = [{'start': f'{a:08x}', 'end_exclusive': f'{b:08x}'} for a, b in runs]
    result['changed_bytes'] = sum(a != b for a, b in zip(old, new))
    result['identical_suffix'] = {'start': '004d3827', 'end_exclusive': '004d3f42', 'bytes': end - 0x4d3827}
    result['limits'] = ['Static comparison only; no renderer execution or pixel comparison.',
        'Descriptor validity and all caller contracts are not established by this bounded audit.']
    (ROOT / 'analysis/evidence/audits/shape-conversion-difference.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: complete 1954-byte envelope; two changed runs; identical 1819-byte suffix')


if __name__ == '__main__':
    main()
