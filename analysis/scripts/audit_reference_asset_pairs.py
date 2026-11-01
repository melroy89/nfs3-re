"""Inventory paired reference/Modern menu assets and compare HUD literals statically."""
import collections
import difflib
import hashlib
import json
import re
import struct
import subprocess

import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def files(path, expected):
    archive = ROOT/path
    assert sha(archive.read_bytes()) == expected
    listing = subprocess.check_output(['7z', 'l', '-slt', str(archive)], text=True)
    members = {}
    for block in listing.split('\n\n'):
        fields = dict(line.split(' = ', 1) for line in block.splitlines() if ' = ' in line)
        name = fields.get('Path', '')
        if 'Size' not in fields or not name.lower().endswith(('.mnu', '.pos')):
            continue
        key = name.casefold()
        assert key not in members
        members[key] = (name, subprocess.check_output(['7z', 'x', '-so', str(archive), name]))
    return members


def identity(entry):
    name, raw = entry
    return {'member': name, 'bytes': len(raw), 'sha256': sha(raw)}


def main():
    specs = {
        'reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
                      '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'),
        'modern': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
                   'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3')}
    bundles = {role: files(*spec) for role, spec in specs.items()}
    old, new = bundles['reference'], bundles['modern']
    assert len(old) == 86 and len(new) == 52
    result = {'kind': 'reference-final-asset-pair-inventory',
              'archives': {role: {'path': path, 'sha256': digest} for role, (path, digest) in specs.items()},
              'assets': [], 'hud_literal_comparison': []}
    counts = collections.Counter()
    for key in sorted(old.keys() | new.keys()):
        row = {'normalized_path': key}
        for role, members in bundles.items():
            if key in members:
                row[role] = identity(members[key])
        if key in old and key in new:
            a, b = old[key][1], new[key][1]
            row['status'] = 'identical' if a == b else 'changed'
            aa, bb = a.decode('latin1').splitlines(), b.decode('latin1').splitlines()
            row['line_endings_only'] = a != b and aa == bb
            # Text-level evidence only: no invented section identity from positional alignment.
            edits = difflib.SequenceMatcher(a=aa, b=bb, autojunk=False).get_opcodes()
            row['text_line_counts'] = {'reference': len(aa), 'modern': len(bb),
                'removed_or_replaced': sum(j-i for op, i, j, _, _ in edits if op != 'equal'),
                'added_or_replaced': sum(j-i for op, _, _, i, j in edits if op != 'equal')}
        else:
            row['status'] = 'reference-only' if key in old else 'modern-only'
        counts[row['status']] += 1
        result['assets'].append(row)
    assert counts['modern-only'] == 0 and counts['reference-only'] == 34
    assert counts['changed'] == 52 and counts['identical'] == 0
    assert not any(row.get('line_endings_only') for row in result['assets'])
    relative, expected, _ = SPECS['official_modern']
    exe = (ROOT/relative).read_bytes()
    assert sha(exe) == expected
    pe = pefile.PE(data=exe)
    embedded = pe.get_data(0x53eb20-0x400000, 0x900)
    assert len(embedded) == 0x900
    result['embedded_table'] = {'exe': relative, 'exe_sha256': expected, 'va': '0053eb20',
                                'bytes': len(embedded), 'sha256': sha(embedded)}
    number = r'([+-]?(?:\d*\.\d+|\d+))'
    pattern = re.compile(r'^([^:]+):\s*\('+number+','+number+r'\)\s*-\s*\('+number+','+number+r'\)\s*$')
    names = None
    for key in sorted(k for k in old if k.endswith('.pos')):
        rows = []
        for line in old[key][1].decode('ascii').splitlines():
            if not line.strip():
                continue
            match = pattern.fullmatch(line)
            assert match, (key, line)
            rows.append((match.group(1), [struct.pack('<f', float(v)) for v in match.groups()[1:]]))
        assert len(rows) == 138
        if names is None:
            names = [name for name, _ in rows]
        assert [name for name, _ in rows] == names
        profiles = []
        for profile in range(6):
            changed = []
            fields = 0
            for slot in range(23):
                name, values = rows[profile*23+slot]
                base = (profile*24+slot)*16
                bits = [embedded[base+i*4:base+i*4+4] for i in range(4)]
                count = sum(x != y for x, y in zip(values, bits))
                if count:
                    changed.append(name)
                    fields += count
            profiles.append({'profile': profile, 'changed_rectangles_of_23': len(changed),
                             'differing_coordinate_fields_of_92': fields, 'changed_record_names': changed})
        result['hud_literal_comparison'].append({'member': old[key][0], 'sha256': sha(old[key][1]),
            'parsed_records': len(rows), 'profiles': profiles})
    result['counts'] = dict(counts)
    result['limits'] = [
        'Author-hosted reference bundle is not authenticated pristine retail.',
        'Casefold matching is deliberate Windows-style path pairing, not Linux installation validation.',
        'Reference-only means absent from final patch archive, not deleted or unreachable at runtime.',
        'Menu line-edit counts preserve text order; no widget identity or semantic equivalence inferred.',
        'HUD compares ordered coordinate literals as binary32 using host float parsing; not target parser or x87 execution.',
        'HUD compares23 text rectangles per profile with first23 embedded rectangles, excluding extra24th slot and later aspect transforms.',
        'No asset installation, game execution, target instructions or database mutation.']
    (ROOT/'analysis/evidence/audits/reference-asset-pairs.json').write_text(json.dumps(result, indent=2)+'\n')
    out = ['# Reference bundle versus final package: menu and HUD asset index', '',
        'Generated by [the static asset audit](scripts/audit_reference_asset_pairs.py); full identities and limits are in [the manifest](evidence/audits/reference-asset-pairs.json).', '',
        'The reference is the [author-hosted bundle](original-modern-original-reference-bundle.md), not authenticated pristine retail. Paths are paired case-insensitively. Both archive hashes and the Modern EXE hash are checked before comparisons.', '',
        '## Menu and package coverage', '',
        f'Of52 paired menu files, {counts["changed"]} differ and {counts["identical"]} are identical. Another28 reference menus and six reference HUD-position files are absent from the final patch archive; no final-only menu/HUD file occurs in this suffix scope.', '',
        '**Archive absence does not establish deletion from an installed game.** Patch packages can depend on retained base-game files. Text-line counts are localization leads, not numbers of changed controls or gameplay features.', '',
        '| Paired menu | Result | Reference / Modern lines | Removed-or-replaced / added-or-replaced lines |',
        '|---|---|---:|---:|']
    for row in result['assets']:
        if 'reference' in row and 'modern' in row:
            c = row['text_line_counts']
            out.append(f'| `{row["normalized_path"].split("/")[-1]}` | {row["status"]} | {c["reference"]} / {c["modern"]} | {c["removed_or_replaced"]} / {c["added_or_replaced"]} |')
    out += ['', '## Reference-only assets', '', '| Member | Interpretation |', '|---|---|']
    for row in result['assets']:
        if row['status'] == 'reference-only':
            out.append(f'| `{row["reference"]["member"]}` | Not included in final patch archive |')
    out += ['', '## HUD coordinate-literal comparison', '',
        'Each reference POS file contains138 ordered records: six profiles ×23 rectangles. Their name order matches across all six files. Compare those coordinates with the first23 rectangles of each24-rectangle embedded Modern profile at0053eb20; the extra rectangle and later aspect adjustment are excluded. See [the instruction-level HUD analysis](original-modern-hud-layout.md) for profile layout, pair swapping and initialization.', '',
        'Counts below compare binary32 encodings of parsed decimal literals. This is an ordered asset/table comparison, not execution of the original parser, destination-memory equivalence or rendered layout validation. It does not prove which file the author used to create the embedded table.', '',
        '| Reference POS | Changed rectangles /138 | Differing coordinate fields /552 |', '|---|---:|---:|']
    for row in result['hud_literal_comparison']:
        out.append(f'| `{row["member"].split("/")[-1]}` | {sum(p["changed_rectangles_of_23"] for p in row["profiles"])} | {sum(p["differing_coordinate_fields_of_92"] for p in row["profiles"])} |')
    out += ['', 'The manifest lists changed record names per profile for follow-up. No original-language file is silently substituted for the established EXE baseline. Header defaults, the extra24th rectangle, parser edge cases, runtime reset/persistence and actual appearance remain separate evidence requirements.', '']
    (ROOT/'analysis/original-modern-reference-assets-index.md').write_text('\n'.join(out))
    print(f'PASS:86 reference and52 final assets; {dict(counts)}; six138-record HUD literal comparisons')


if __name__ == '__main__':
    main()
