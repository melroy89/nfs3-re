"""Retain original/Modern panorama callback counterparts and menu controls."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-credits-panorama-comparison', 'range_end': 'exclusive', 'binaries': {}, 'assets': {}}
    capture = ROOT / 'analysis/captures/modern-differences/credits-panorama'
    capture.mkdir(parents=True, exist_ok=True)
    restores = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x454d60, 0x454e3d), (0x454e40, 0x454e79), (0x454e80, 0x454e9d), (0x454ea0, 0x454f02)] if label == 'original' else [(0x454d40, 0x454d6f), (0x454d70, 0x454d8a), (0x454d8c, 0x454da6), (0x454da8, 0x454dc5), (0x454dc8, 0x454e43), (0x45d77e, 0x45d798), (0x44a24c, 0x44a2c2), (0x44a315, 0x44a436), (0x461270, 0x4613db)]
        rows = []
        for start, end in spans:
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        restores.append(pe.get_data((0x454e80 if label == 'original' else 0x454da8)-0x400000, 0x1d))
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'label_id_words_005563dc_hex': pe.get_data(0x1563dc, 8).hex(),
            'tokens': {f'{a:08x}': pe.get_data(a-0x400000, 40).split(b'\0')[0].decode() for a in (0x537bbc, 0x537bc4, 0x5398d4, 0x5398e0, 0x5398e8, 0x5398ec, 0x5398f4)}}
        if label == 'official_modern':
            template = pe.get_data(0x156e40, 0xbc)
            assert int.from_bytes(template[0x30:0x34], 'little') == 0x461270
            assert template[0x58:0x5c] == bytes(4)
            out['binaries'][label]['button_template_00556e40_hex'] = template.hex()
            out['binaries'][label]['arrow_tokens'] = {f'{a:08x}': pe.get_data(a-0x400000, 16).split(b'\0')[0].decode() for a in (0x53be36, 0x53be3e)}
    assert restores[0] == restores[1]
    archive = ROOT / 'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    assets = {'official': ROOT / 'analysis/captures/modern-differences/upstream/package/fedata/menus/credits1.mnu', 'local_uppercase_backup': ROOT / 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/CREDITS1.MNU'}
    for label, path in assets.items():
        raw = path.read_bytes()
        if label == 'official':
            assert raw == subprocess.check_output(['7z', 'x', '-so', str(archive), 'fedata/menus/credits1.mnu'])
        out['assets'][label] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'selected_fields': [{'line': i, 'field': line} for i, line in enumerate(raw.decode('latin1').splitlines(), 1) if line.startswith(('codelink=', 'text=', 'buttontype='))]}
    out['official_related_arrow_fields'] = []
    for name in ('credits.mnu', 'slides.mnu'):
        relative = f'analysis/captures/modern-differences/upstream/package/fedata/menus/{name}'
        data = (ROOT/relative).read_bytes()
        assert data == subprocess.check_output(['7z', 'x', '-so', str(archive), f'fedata/menus/{name}'])
        fields = [{'line': i, 'field': line} for i, line in enumerate(data.decode('latin1').splitlines(), 1) if line.startswith(('codelink=keyleft ', 'codelink=keyright '))]
        assert len(fields) == 2
        out['official_related_arrow_fields'].append({'path': relative, 'sha256': hashlib.sha256(data).hexdigest(), 'fields': fields})
    out['limits'] = ['No rendering, keyboard or callback execution.', 'The distant missing-Next exit is retained; unrelated entry paths to its shared code are not analyzed.', 'Backup assets are not authenticated retail provenance; release introduction remains unverified.']
    (ROOT / 'analysis/evidence/audits/original-modern-credits-panorama.json').write_text(json.dumps(out, indent=2) + '\n')
    print('PASS: callback counterparts, moved-identical restore, shared exit and official menu fields')


if __name__ == '__main__':
    main()
