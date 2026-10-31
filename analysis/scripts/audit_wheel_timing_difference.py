"""Static full-body comparison of both wheel-spin timing source changes."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'wheel-spin-timing-source', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/wheel-timing'
    capture.mkdir(parents=True, exist_ok=True)
    bodies = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        bodies[label] = []
        for start, end in [(0x4b9140, 0x4b9280), (0x4b9280, 0x4b93bf)]:
            data = pe.get_data(start - 0x400000, end - start)
            bodies[label].append(data)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        constants = pe.get_data(0x14004c, 0x74)
        bodies[label].append(constants)
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'constant_span': {'start': '0054004c', 'end_exclusive': '005400c0',
                'bytes_hex': constants.hex(), 'sha256': hashlib.sha256(constants).hexdigest()}}
    old, new = bodies['original'], bodies['official_modern']
    for index, (start, instruction, oldhex, newhex) in enumerate([
        (0x4b9140, 0x4b9157, '8b3528fe5500', '8bb0c0080000'),
        (0x4b9280, 0x4b9296, '8b1d28fe5500', '8b98c0080000')]):
        offset = instruction - start
        assert old[index][offset:offset+6] == bytes.fromhex(oldhex)
        assert new[index][offset:offset+6] == bytes.fromhex(newhex)
        assert [i for i, (a, b) in enumerate(zip(old[index], new[index])) if a != b] == list(range(offset+1, offset+5))
    assert old[2] == new[2]
    result['limits'] = ['Static evidence only; no animation, replay or multiplayer validation.',
        'Object tick lifecycle and caller coverage remain as bounded in the vehicle-dispatch report.']
    (ROOT / 'analysis/evidence/audits/wheel-timing-difference.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: complete 320/319-byte bodies differ only at two tick-source operands; 116 constant bytes identical')


if __name__ == '__main__':
    main()
