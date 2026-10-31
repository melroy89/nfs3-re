"""Refresh the shallow release-note index in the original/Modern comparison."""
import hashlib
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = '<!-- BEGIN GENERATED MODERN CHANGE LIST -->'
END = '<!-- END GENERATED MODERN CHANGE LIST -->'


def main():
    source = ROOT / 'analysis/captures/modern-differences/upstream/package/readme_en.txt'
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d'
    lines = raw.decode('utf-8-sig').splitlines()
    catalog = (ROOT / 'analysis/modern-patch-change-catalog.md').read_text()
    rows = [[c.strip() for c in line.strip('|').split('|')]
            for line in catalog.splitlines() if line.startswith('| MP')]
    assert len(rows) == len({r[0] for r in rows}) == 290
    assert len({r[1] for r in rows}) == 12
    out = [START, '## Complete release-note change list', '',
           'This first-reference index includes all **290 release-note entries across 12 releases**, grouped newest first. Descriptions below reproduce the full source bullets, including vendor claims; they are not all independently verified differences between the supplied original and final Modern executables. Historical fixes, reversals, DLLs, assets and configuration changes are included. This is a release-history inventory, not an exhaustive inventory of undocumented binary changes.', '',
           'Use the stable IDs when choosing original or Modern behaviour for a reconstructed C module. An executable comparison can guide reconstruction of original behaviour; it does not supply the original source code. The [detailed catalog](modern-patch-change-catalog.md) retains source line numbers, categories, evidence links and qualifications. **Static** means bounded static support, **Partial** means only part of the claim is supported, **Unresolved** includes historical claims needing other releases, and **Claimed** means vendor-only. None of these labels establishes runtime equivalence.', '',
           'Generated from the hash-pinned English README and the catalog by `python3 analysis/scripts/update_change_list_appendix.py`. Refresh after catalog status changes; do not edit this generated section manually.', '']
    release = None
    counts = Counter()
    for row_index, (ident, version, number, _short, _category, evidence) in enumerate(rows):
        if version != release:
            release = version
            out += [f'### Version {release}', '', '| ID | Reported change | Review |', '|---|---|---|']
        index = int(number) - 1
        assert lines[index].startswith('- '), (ident, number)
        parts = [lines[index][2:].strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith('- '):
            assert not lines[index].startswith('---'), ident
            parts.append(lines[index].strip())
            index += 1
        description = ' '.join(parts).replace('|', '&#124;').replace('<', '&lt;').replace('>', '&gt;')
        if evidence.startswith('Vendor-claimed'):
            status = 'Claimed'
        elif evidence.startswith(('Static-supported', 'Confirmed statically', 'Modern mechanism verified')):
            status = 'Static'
        elif evidence.startswith('Partial'):
            status = 'Partial'
        else:
            status = 'Unresolved'
        counts[status] += 1
        out.append(f'| {ident} | {description} | {status} |')
        # A blank line before the next release heading is added below.
        if row_index + 1 < len(rows):
            next_row = rows[row_index + 1]
            if next_row[1] != version:
                out.append('')
    out[3:3] = [f"Current catalog labels: **{counts['Claimed']} Claimed, {counts['Static']} Static, {counts['Partial']} Partial, {counts['Unresolved']} Unresolved**. These are evidence labels, not a completion percentage.", '']
    out += ['', END]
    report = ROOT / 'analysis/original-modern-differences.md'
    text = report.read_text()
    block = '\n'.join(out)
    if START in text:
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
        title = '# Original versus Modern Patch: executable differences\n'
        text = text.replace(title, title + '\nFor a shallow inventory, see the [complete release-note change list](#complete-release-note-change-list) below.\n', 1)
    report.write_text(text)
    print(f'Updated {len(rows)} entries across 12 releases: {dict(counts)}')


if __name__ == '__main__':
    main()
