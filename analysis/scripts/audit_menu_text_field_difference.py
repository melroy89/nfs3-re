"""Retain paired menu text-field writer and official numeric-ID uses, offline."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    spans = ((0x449240, 0x4493aa), (0x442b10, 0x442b5c), (0x449990, 0x4499ad),
             (0x4493b0, 0x449504), (0x448f50, 0x448fc4), (0x4f0430, 0x4f0487))
    result = {'kind': 'static-menu-text-field-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/menu-text-field'
    capture.mkdir(parents=True, exist_ok=True)
    paired = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        bodies = []
        rows = []
        for start, end in spans:
            body = pe.get_data(start-0x400000, end-start)
            bodies.append(body)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(body).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        paired.append(bodies)
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'type_dispatch_00449218': [f'{x:08x}' for x in struct.unpack('<7I', pe.get_data(0x49218, 28))],
            'selected_type5_field_rows': {f'{a:08x}': pe.get_data(a-0x400000, 16).hex() for a in (0x557c40, 0x557e00)},
            'symbol_prefixes': [pe.get_data(a-0x400000, 16).split(b'\0')[0].decode() for a in (0x538f74, 0x538f7c)]}
    assert paired[0][1:] == paired[1][1:]
    changes = [0x449240+i for i, (a, b) in enumerate(zip(paired[0][0], paired[1][0])) if a != b]
    assert min(changes) == 0x449342 and max(changes) == 0x449370
    result['writer_changed_byte_addresses'] = [f'{x:08x}' for x in changes]
    for key in ('type_dispatch_00449218', 'selected_type5_field_rows', 'symbol_prefixes'):
        assert result['binaries']['original'][key] == result['binaries']['official_modern'][key]
    archive = ROOT / 'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    result['official_archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert result['official_archive_sha256'] == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    uses = []
    for path in sorted((ROOT / 'analysis/captures/modern-differences/upstream/package/fedata/menus').glob('*.mnu')):
        data = path.read_bytes()
        assert data == subprocess.check_output(['7z', 'x', '-so', str(archive), f'fedata/menus/{path.name}'])
        for number, line in enumerate(data.decode('latin1').splitlines(), 1):
            if line.strip().startswith('text=str_'):
                uses.append({'path': str(path.relative_to(ROOT)), 'file_sha256': hashlib.sha256(data).hexdigest(), 'line': number, 'field': line.strip()})
    assert len(uses) == 10
    result['official_numeric_text_uses'] = uses
    result['limits'] = ['No parser, instruction or game execution.', 'Numeric parsing and language lookup failure/overflow contracts are not exhaustively validated.', 'Registration code identity is not registration-table identity.']
    (ROOT / 'analysis/evidence/audits/original-modern-menu-text-field.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: writer delta localized; five retained helpers; 10 official numeric text uses')


if __name__ == '__main__':
    main()
