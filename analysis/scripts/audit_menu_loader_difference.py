"""Compare complete menu graph loaders and their path operand; no execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    start, end = 0x449510, 0x449891
    result = {'kind': 'static-menu-loader-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/menu-loader'
    capture.mkdir(parents=True, exist_ok=True)
    bodies = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        body = pe.get_data(start - 0x400000, end - start)
        bodies.append(body)
        assert body[0x4495ff-start] == 0xbe
        operand = int.from_bytes(body[0x449600-start:0x449604-start], 'little')
        assert operand == (0x538f84 if label == 'original' else 0x7a2d34)
        path = capture / f'{label}-{start:08x}.asm'
        path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'start': f'{start:08x}', 'end': f'{end:08x}', 'body_sha256': hashlib.sha256(body).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'path_source_operand': f'{operand:08x}', 'format_at_00538f94': pe.get_data(0x138f94, 16).split(b'\0')[0].decode(), 'mode_at_00538f9c': pe.get_data(0x138f9c, 8).split(b'\0')[0].decode()}
        if label == 'original':
            result['binaries'][label]['literal_path'] = pe.get_data(operand-0x400000, 64).split(b'\0')[0].decode()
    changes = [start+i for i, (a, b) in enumerate(zip(*bodies)) if a != b]
    assert changes == [0x449600, 0x449601, 0x449602]
    result['changed_byte_addresses'] = [f'{a:08x}' for a in changes]
    result['limits'] = ['Local instruction identity does not imply identical callees, imports, templates or assets.', 'Modern path buffer requires startup initialization; later writers and effective working directory remain runtime concerns.', 'No target instructions or filesystem opens performed.']
    (ROOT / 'analysis/evidence/audits/original-modern-menu-loader.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: complete loader differs only in three path-source operand bytes')


if __name__ == '__main__':
    main()
