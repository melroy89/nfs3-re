"""Retain setup-button asset and callback witnesses; never execute target code."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-setup-website-comparison', 'range_end': 'exclusive', 'binaries': {}, 'assets': {}}
    spans = ((0x453051, 0x453068), (0x452e60, 0x452f16),
             (0x461270, 0x4613db), (0x44b6c8, 0x44b6de),
             (0x44b7ec, 0x44b8ad), (0x449762, 0x4497c9))
    capture = ROOT / 'analysis/captures/modern-differences/setup-website'
    capture.mkdir(parents=True, exist_ok=True)
    pairs = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        code = [pe.get_data(a - 0x400000, b - a) for a, b in spans]
        data_spans = [(0x557e10, 16), (0x556e40, 0xbc), (0x555c48, 24), (0x44b20c, 4)]
        data_rows = [{'address': f'{a:08x}', 'size': size, 'hex': pe.get_data(a-0x400000, size).hex()} for a, size in data_spans]
        assert pe.get_data(0x4b20c, 4) == (0x44b7ec).to_bytes(4, 'little')
        assert pe.get_data(0x156e70, 4) == (0x461270).to_bytes(4, 'little')
        pairs.append(code + [bytes.fromhex(row['hex']) for row in data_rows])
        token = pe.get_data(0x13965c, 64).split(b'\0')[0].decode('ascii')
        assert token == 'SETUP_NfsWebSite'
        rows = []
        for (start, end), data in zip(spans, code):
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'token_at_0053965c': token, 'spans': rows, 'retained_data': data_rows}
    assert pairs[0] == pairs[1]
    assets = {
        'official_modern': ROOT / 'analysis/captures/modern-differences/upstream/package/fedata/menus/setup.mnu',
        'local_uppercase_backup': ROOT / 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/SETUP.MNU',
    }
    for label, path in assets.items():
        raw = path.read_bytes()
        lines = raw.decode('latin1').splitlines()
        selected = [{'line': i, 'text': line} for i, line in enumerate(lines, 1) if any(word in line.lower() for word in ('website', 'credits'))]
        buttons = []
        current = None
        for line in lines:
            if line.startswith('['):
                if current is not None:
                    buttons.append(current)
                current = {} if line == '[button]' else None
            elif current is not None and '=' in line:
                key, value = line.split('=', 1)
                if key in ('text', 'codelink', 'nextmenu', 'buttontype'):
                    current[key] = value
        if current is not None:
            buttons.append(current)
        result['assets'][label] = {'buttons_in_file_order': buttons, 'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw), 'website_or_credits_lines': selected}
    assert not result['assets']['official_modern']['website_or_credits_lines']
    assert any('SETUP_NfsWebSite' in row['text'] for row in result['assets']['local_uppercase_backup']['website_or_credits_lines'])
    modern_buttons = result['assets']['official_modern']['buttons_in_file_order']
    backup_buttons = result['assets']['local_uppercase_backup']['buttons_in_file_order']
    assert len(modern_buttons) == len(backup_buttons) == 6
    assert modern_buttons[:4] == backup_buttons[:4]
    assert modern_buttons[5] == backup_buttons[5]
    assert modern_buttons[4] == {'text': 'kMenuMAINOptions001', 'nextmenu': 'options', 'buttontype': 'LR1of2'}
    assert backup_buttons[4] == {'codelink': 'SETUP_NfsWebSite', 'text': 'kMenuSETUPNFSWebsi001', 'buttontype': 'LR1of2'}
    result['limits'] = ['No runtime menu selection or callback execution.', 'Uppercase local backup is not authenticated retail provenance.', 'Removal is supported; historical v1.0.0 Credits route and v1.4.0 Options introduction remain unresolved; final asset selects Options.']
    (ROOT / 'analysis/evidence/audits/original-modern-setup-website.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: pinned binaries, identical callback/binding, asset removal witness')


if __name__ == '__main__':
    main()
