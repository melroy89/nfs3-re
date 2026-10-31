"""Compare Options mainonly assets and generic postgame flag producer/consumer."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-options-postgame-comparison', 'range_end': 'exclusive', 'binaries': {}, 'assets': {}}
    capture = ROOT/'analysis/captures/modern-differences/options-postgame'
    capture.mkdir(parents=True, exist_ok=True)
    all_data = []
    images = []
    spans = ((0x44a960, 0x44a9db), (0x44b24e, 0x44b271), (0x449240, 0x4492e9), (0x44b271, 0x44b28a))
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe); rows = []; bodies = []
        for start, end in spans:
            body = pe.get_data(start-0x400000, end-start); bodies.append(body)
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(body).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        template = pe.get_data(0x156e40, 0xbc)
        fields = pe.get_data(0x157c60, 32)
        assert template[0x14:0x18] == bytes(4)
        assert int.from_bytes(template[0x24:0x28], 'little') != 0
        assert int.from_bytes(fields[28:32], 'little') == 0x604ef6
        all_data.append(bodies+[template, fields])
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'button_template_00556e40_hex': template.hex(), 'field_rows_00557c60_00557c70_hex': fields.hex(), 'context_name_00539048': pe.get_data(0x139048, 32).split(b'\0')[0].decode()}
    assert all_data[0] == all_data[1]
    result['setup_initializer_comparison'] = {}
    setup_bodies = []
    for (label, (relative, _, _)), pe in zip(SPECS.items(), images):
        end = 0x4530bb if label == 'original' else 0x4530c0
        body = pe.get_data(0x52f80, end-0x452f80); setup_bodies.append(body)
        path = capture/f'{label}-00452f80.asm'
        path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', '--start-address=0x452f80', f'--stop-address={end}', relative], cwd=ROOT))
        result['setup_initializer_comparison'][label] = {'start': '00452f80', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(body).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'setup_row_00555f60_hex': pe.get_data(0x155f60, 24).hex(), 'options_row_00555c48_hex': pe.get_data(0x155c48, 24).hex()}
        opt_end = 0x442b04 if label == 'original' else 0x442aee
        opt_path = capture/f'{label}-00442aa0.asm'
        opt_path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', '--start-address=0x442aa0', f'--stop-address={opt_end}', relative], cwd=ROOT))
        result['setup_initializer_comparison'][label]['options_initializer'] = {'start': '00442aa0', 'end': f'{opt_end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(0x42aa0, opt_end-0x442aa0)).hexdigest(), 'assembly': str(opt_path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(opt_path.read_bytes()).hexdigest()}
    offset = 0x4530b4-0x452f80
    assert setup_bodies[0][:offset] == setup_bodies[1][:offset]
    assert setup_bodies[0][offset:] == setup_bodies[1][offset+5:]
    assert setup_bodies[1][offset:offset+5] == bytes.fromhex('a36c277a00')
    result['setup_initializer_comparison']['inserted_modern_store'] = {'address': '004530b4', 'hex': 'a36c277a00', 'effect': 'store EAX (zero from preceding XOR) to 007a276c'}
    archive = ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    for label, relative in (('official', 'analysis/captures/modern-differences/upstream/package/fedata/menus/options.mnu'), ('local_uppercase_backup', 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/OPTIONS.MNU')):
        data = (ROOT/relative).read_bytes()
        if label == 'official':
            assert data == subprocess.check_output(['7z', 'x', '-so', str(archive), 'fedata/menus/options.mnu'])
        sections = []; current = None
        for number, line in enumerate(data.decode('latin1').splitlines(), 1):
            if line.startswith('['):
                current = {'section': line, 'line': number, 'fields': {}}; sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                k, v = line.split('=', 1); current['fields'][k] = v
        selected = [s for s in sections if s['fields'].get('codelink') in ('racenow', 'credits', 'exitprogram')]
        assert len(selected) == 3
        for row in selected:
            if label == 'official': assert 'mainonly' not in row['fields'] and 'postonly' not in row['fields']
            else: assert row['fields']['mainonly'] == '1' and row['fields']['postonly'] == '0'
        result['assets'][label] = {'path': relative, 'sha256': hashlib.sha256(data).hexdigest(), 'controls': selected}
    result['limits'] = ['No runtime menu selection, visibility or rendering tested.', 'Backup assets are not authenticated retail provenance.', 'Later flags/field overrides and every postgame entry path remain unenumerated.']
    (ROOT/'analysis/evidence/audits/original-modern-options-postgame.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: retained generic gate/template/fields; official Options removes three mainonly restrictions')


if __name__ == '__main__':
    main()
