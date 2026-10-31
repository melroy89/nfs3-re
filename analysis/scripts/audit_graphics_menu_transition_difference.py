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
        spans = [(0x448440, 0x4484d7), (0x4484e0, 0x448561)] if label == 'original' else [(0x448440, 0x4484ba), (0x4484bc, 0x448553), (0x43778c, 0x4377c1), (0x448348, 0x448368), (0x44837c, 0x448392), (0x448394, 0x4483fd), (0x448400, 0x448425), (0x4377c4, 0x437801), (0x437801, 0x43781d), (0x448639, 0x448647), (0x44d2a0, 0x44d2c5)]
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
        if label == 'official_modern':
            out['binaries'][label]['fog_control_tokens'] = {f'{a:08x}': pe.get_data(a-0x400000, 32).split(b'\0')[0].decode() for a in (0x538a20, 0x538a2c)}
            sites = (0x448458, 0x448642, 0x44d2c0)
            for site in sites:
                data = pe.get_data(site-0x400000, 5)
                assert data[0] == 0xe8 and site+5+int.from_bytes(data[1:], 'little', signed=True) == 0x4377c4
            out['binaries'][label]['inspected_fog_gate_direct_calls'] = [f'{site:08x}' for site in sites]
    out['limits'] = ['No display or callback execution.', 'Mode-list nonempty and valid descriptor/item/backup prerequisites are not proved.', 'Changed field meanings and helper dependencies prevent inferring whole-menu equivalence.']
    (ROOT / 'analysis/evidence/audits/original-modern-graphics-menu-transition.json').write_text(json.dumps(out, indent=2) + '\n')
    print('PASS: pinned graphics registration, counterpart bodies and Modern helper witnesses')


if __name__ == '__main__':
    main()
