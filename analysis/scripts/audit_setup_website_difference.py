"""Retain setup-button asset and callback witnesses; never execute target code."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-setup-website-comparison', 'range_end': 'exclusive', 'binaries': {}, 'assets': {}}
    spans = ((0x453051, 0x453068), (0x452e60, 0x452f16))
    capture = ROOT / 'analysis/captures/modern-differences/setup-website'
    capture.mkdir(parents=True, exist_ok=True)
    pairs = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        code = [pe.get_data(a - 0x400000, b - a) for a, b in spans]
        pairs.append(code)
        token = pe.get_data(0x13965c, 64).split(b'\0')[0].decode('ascii')
        assert token == 'SETUP_NfsWebSite'
        rows = []
        for (start, end), data in zip(spans, code):
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'token_at_0053965c': token, 'spans': rows}
    assert pairs[0] == pairs[1]
    assets = {
        'official_modern': ROOT / 'analysis/captures/modern-differences/upstream/package/fedata/menus/setup.mnu',
        'local_uppercase_backup': ROOT / 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/SETUP.MNU',
    }
    for label, path in assets.items():
        raw = path.read_bytes()
        lines = raw.decode('latin1').splitlines()
        selected = [{'line': i, 'text': line} for i, line in enumerate(lines, 1) if any(word in line.lower() for word in ('website', 'credits'))]
        result['assets'][label] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw), 'website_or_credits_lines': selected}
    assert not result['assets']['official_modern']['website_or_credits_lines']
    assert any('SETUP_NfsWebSite' in row['text'] for row in result['assets']['local_uppercase_backup']['website_or_credits_lines'])
    result['limits'] = ['No runtime menu selection or callback execution.', 'Uppercase local backup is not authenticated retail provenance.', 'Removal is supported; replacement Credits route and historical v1.0.0 introduction remain unresolved.']
    (ROOT / 'analysis/evidence/audits/original-modern-setup-website.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: pinned binaries, identical callback/binding, asset removal witness')


if __name__ == '__main__':
    main()
