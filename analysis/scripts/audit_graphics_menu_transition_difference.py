"""Retain corresponding graphics menu init/transition bodies; static only."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-graphics-menu-transition-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/graphics-menu-transition'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x448440, 0x4484d7), (0x4484e0, 0x448561)] if label == 'original' else [(0x448440, 0x4484ba), (0x4484bc, 0x448553), (0x43778c, 0x4377c1), (0x448348, 0x448368), (0x44837c, 0x448392), (0x448394, 0x4483fd), (0x448400, 0x448425)]
        rows = []
        for start, end in spans:
            data = pe.get_data(start-0x400000, end-start)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        table = pe.get_data(0x156068, 24)
        cancel = pe.get_data(0x138d84, 40).split(b'\0')[0].decode()
        assert cancel == 'CANCEL_GRAPHICS_OPTIONS'
        expected_callback = 0x4484e0 if label == 'original' else 0x4484bc
        assert int.from_bytes(table[16:20], 'little') == expected_callback
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'graphics_registration_row_00556068_hex': table.hex(), 'cancel_token_00538d84': cancel, 'string_at_00538d7c': pe.get_data(0x138d7c, 32).split(b'\0')[0].decode()}
    out['limits'] = ['No display or callback execution.', 'Mode-list nonempty and valid descriptor/item/backup prerequisites are not proved.', 'Changed field meanings and helper dependencies prevent inferring whole-menu equivalence.']
    (ROOT / 'analysis/evidence/audits/original-modern-graphics-menu-transition.json').write_text(json.dumps(out, indent=2) + '\n')
    print('PASS: pinned graphics registration, counterpart bodies and Modern helper witnesses')


if __name__ == '__main__':
    main()
