"""Retain Race Now helper, original setup and dependency witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-race-now-entry-comparison', 'range_end': 'exclusive',
              'binaries': {}, 'limits': ['Modern helper is not a same-address original counterpart.',
              'Original setup body includes credits gating and coordinate writes; not a one-to-one helper match.', 'No menu or target execution.']}
    capture = ROOT/'analysis/captures/modern-differences/race-now-entry'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x437600, 0x4377be), (0x4377d0, 0x43798e)] if label == 'original' else [(0x437614, 0x4376fb), (0x437600, 0x437612)]
        if label == 'official_modern':
            spans += [(0x4374d5, 0x4374dc), (0x437600, 0x437611), (0x437e39, 0x437e49),
                      (0x43d5dc, 0x43d5e3), (0x442ae1, 0x442ae8), (0x4432e9, 0x4432f0),
                      (0x447e07, 0x447e0e), (0x44844f, 0x448456), (0x448639, 0x448640),
                      (0x45d920, 0x45d928), (0x45e990, 0x45e998),
                      (0x4405a7, 0x4405b1), (0x440723, 0x44072a), (0x4530b2, 0x4530b9),
                      (0x45d2dc, 0x45d2e6), (0x45d60f, 0x45d619)]
        spans += [(0x442a40, 0x442a95), (0x4cf090, 0x4cf11e), (0x44a5cb, 0x44a5e5)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                         'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                         'assembly': str(path.relative_to(ROOT)),
                         'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'tokens': {f'{a:08x}': pe.get_data(a-0x400000, 40).split(b'\0')[0].decode('ascii')
                       for a in (0x53a998, 0x53a990, 0x53714c, 0x537494, 0x53750c, 0x537518, 0x537524, 0x537530, 0x53753c, 0x537548, 0x537554, 0x537560, 0x53756c)}}
    def normalized_instructions(start, end):
        source = (capture/f'original-{start:08x}.asm').read_text()
        instructions = []
        import re
        for line in source.splitlines():
            parts = line.split('\t')
            if len(parts) < 3 or not parts[0].strip().endswith(':'):
                continue
            instruction = parts[2].strip()
            def normalize_address(match):
                value = int(match.group(), 16)
                return f'local+{value-start:x}' if start <= value < end else match.group()
            instructions.append(re.sub(r'0x[0-9a-f]+', normalize_address, instruction))
        return instructions
    old_fun = normalized_instructions(0x437600, 0x4377be)
    old_hard = normalized_instructions(0x4377d0, 0x43798e)
    assert old_fun == old_hard and len(old_fun) > 100
    result['original_funkeys_hardkeys_normalized_instructions'] = {
        'count': len(old_fun), 'matching': True,
        'normalization': 'objdump mnemonic/operands; function-local targets replaced by offsets; external target addresses retained',
        'sha256': hashlib.sha256(('\n'.join(old_fun)+'\n').encode()).hexdigest()}
    images = [pefile.PE(str(ROOT/SPECS[k][0])) for k in ('original', 'official_modern')]
    result['inspected_direct_callers'] = []
    modern = images[1]
    for site in (0x4374d7, 0x43760a, 0x437e44, 0x43d5de, 0x442ae3, 0x4432eb, 0x447e09,
                 0x448451, 0x44863b, 0x45d923, 0x45e993):
        data = modern.get_data(site-0x400000, 5)
        assert data[0] == 0xe8 and site+5+int.from_bytes(data[1:], 'little', signed=True) == 0x437614
        result['inspected_direct_callers'].append(f'{site:08x}')
    result['menu_state_direct_writes'] = []
    for site in (0x4405a7, 0x45d2dc, 0x45d60f):
        assert modern.get_data(site-0x400000, 10) == bytes.fromhex('c7056c277a0001000000')
        result['menu_state_direct_writes'].append({'address': f'{site:08x}', 'value': 1})
    for site in (0x440725, 0x4530b4):
        assert modern.get_data(site-2-0x400000, 7) == bytes.fromhex('31c0a36c277a00')
        result['menu_state_direct_writes'].append({'address': f'{site:08x}', 'value': 0})
    result['identical_helpers'] = []
    for start, end in ((0x442a40, 0x442a95), (0x4cf090, 0x4cf11e), (0x44a5cb, 0x44a5e5)):
        bodies = [p.get_data(start-0x400000, end-start) for p in images]
        assert bodies[0] == bodies[1]
        result['identical_helpers'].append(f'{start:08x}')
    result['hardkeys_asset_funtxt_fields'] = {}
    archive = ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    for label, relative in (
        ('official_modern', 'analysis/captures/modern-differences/upstream/package/fedata/menus/hardkeys.mnu'),
        ('local_uppercase_backup', 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/HARDKEYS.MNU')):
        data = (ROOT/relative).read_bytes()
        if label == 'official_modern':
            assert data == subprocess.check_output(['7z', 'x', '-so', str(archive), 'fedata/menus/hardkeys.mnu'])
        fields = [{'line': i, 'text': line} for i, line in enumerate(data.decode('latin1').splitlines(), 1) if line.lower().startswith('codelink=funtxt_')]
        result['hardkeys_asset_funtxt_fields'][label] = {'path': relative, 'sha256': hashlib.sha256(data).hexdigest(), 'fields': fields}
    assert not result['hardkeys_asset_funtxt_fields']['official_modern']['fields']
    assert len(result['hardkeys_asset_funtxt_fields']['local_uppercase_backup']['fields']) == 5
    (ROOT/'analysis/evidence/audits/original-modern-race-now-entry.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, Modern helper, original credits gate and exact tokens')


if __name__ == '__main__':
    main()
