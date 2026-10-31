"""Inventory official menu assets and case-distinct local backup routes, offline."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_SHA = 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'


def inspect(path):
    raw = path.read_bytes()
    sections = []
    current = None
    for number, line in enumerate(raw.decode('latin1').splitlines(), 1):
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            current = {'section': line, 'line': number, 'fields': {}}
            sections.append(current)
        elif current is not None and '=' in line and not line.startswith((';', '#')):
            key, value = line.split('=', 1)
            current['fields'][key.strip()] = value.strip()
    buttons = [{**s, 'fields': {k: v for k, v in s['fields'].items() if k in ('codelink', 'text', 'nextmenu', 'buttontype')}} for s in sections if s['section'] == '[button]']
    return {'path': str(path.relative_to(ROOT)), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'buttons': buttons}


def main():
    archive = ROOT / 'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA
    folder = ROOT / 'analysis/captures/modern-differences/upstream/package/fedata/menus'
    backup = ROOT / 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus'
    rows = []
    for path in sorted(folder.glob('*.mnu')):
        old_path = backup / path.name.upper()
        official = inspect(path)
        member = subprocess.check_output(['7z', 'x', '-so', str(archive), f'fedata/menus/{path.name}'])
        assert hashlib.sha256(member).hexdigest() == official['sha256'], path
        old = inspect(old_path) if old_path.is_file() else None
        rows.append({'name': path.name, 'official': official, 'uppercase_local_backup': old, 'byte_identical': official['sha256'] == old['sha256'] if old else None})
    assert len(rows) == 52
    for name in ('connect.mnu', 'ipx.mnu', 'interior.mnu'):
        row = next(r for r in rows if r['name'] == name)
        new = [b['fields'] for b in row['official']['buttons']]
        old = [b['fields'] for b in row['uppercase_local_backup']['buttons']]
        assert any(b.get('nextmenu') == 'options' for b in new)
        assert any('exitprogram' in b.get('codelink', '').split() for b in new)
        assert not any(b.get('nextmenu') == 'options' or 'exitprogram' in b.get('codelink', '').split() for b in old)
    result = {'kind': 'official-menu-route-inventory', 'archive_sha256': ARCHIVE_SHA,
              'limits': ['No target execution or actual selected-resource verification.', 'Uppercase backups are not authenticated retail assets.', 'Each official file is hash-compared with its member read directly from the pinned archive; no historical release package is inspected.'], 'files': rows}
    out = ROOT / 'analysis/evidence/inventories/official-menu-routes.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {len(rows)} official menus; {sum(r["uppercase_local_backup"] is not None for r in rows)} uppercase backups; {sum(r["byte_identical"] is True for r in rows)} byte-identical pairs; three target menus have added Options/Exit')


if __name__ == '__main__':
    main()
