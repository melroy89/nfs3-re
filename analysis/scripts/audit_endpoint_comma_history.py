"""Pin historical comma normalization and retained decimal contract; static only."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble

HISTORY = {
    '1.4.0': ('8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9',
              '7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d'),
    '1.5.0': ('de6cbbbce4b77765f96472aaf8c12a4e245e2abceaf26dd9b84215442b1f4a0f',
              'd9db8ead63a9697c4c6c3933e720cd93565f67bd4b264e8bbc0d98d03c236dae'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    capture = ROOT/'analysis/captures/modern-differences/endpoint-comma-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-endpoint-comma-release-boundary', 'binaries': {},
        'limits': ['No target instructions, parser, provider, sockets or network executed.',
                   'Classification bytes are file-backed snapshots; later locale/table writes not excluded.',
                   'Forward LODSB traversal assumes direction flag clear and readable writable NUL-terminated input.',
                   'Adapter normalization is not provider acceptance or complete address validation.']}
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert sha(raw) == expected
        images[label] = (raw, {'path': relative, 'sha256': expected})
    for version, (archive_hash, executable_hash) in HISTORY.items():
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive = ROOT/relative
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        assert sha(raw) == executable_hash
        images[version] = (raw, {'archive': relative, 'archive_sha256': archive_hash,
                                'member': 'nfs3.exe', 'sha256': executable_hash})
    bodies, converters, tables, callers = {}, [], [], {}
    for label, (raw, identity) in images.items():
        pe = pefile.PE(data=raw)
        def get(start, end):
            return pe.get_data(start-0x400000, end-start)
        spans = [(0x4f0430, 0x4f0487, 'decimal-converter'),
                 (0x49ea70, 0x49ead3, 'endpoint-caller')]
        if label != 'original':
            end = 0x4a2f83 if label == '1.4.0' else 0x4a2f8d
            bodies[label] = get(0x4a2f50, end)
            spans.append((0x4a2f50, end, 'normalizer'))
        rows = []
        for start, end, name in spans:
            data = get(start, end)
            path = capture/f'{label}-{name}.asm'
            path.write_text('\n'.join(disassemble(data, start))+'\n')
            rows.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                         'bytes': len(data), 'hex': data.hex(), 'sha256': sha(data),
                         'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': sha(path.read_bytes())})
        converter = get(0x4f0430, 0x4f0487)
        converters.append(converter)
        assert get(0x4f046b, 0x4f0478).hex() == '6bd20a31db8a1801da4083ea30'
        table = get(0x564ef0, 0x564ff0)
        tables.append(table)
        classes = {name: [x for x in range(256) if table[(x+1)&255]&bit]
                   for name, bit in [('leading_space', 2), ('digit', 0x20)]}
        assert classes == {'leading_space': [9,10,11,12,13,32], 'digit': list(range(48,58))}
        callers[label] = get(0x49ea70, 0x49ead3)
        result['binaries'][label] = {**identity, 'spans': rows,
            'classification_table': {'start': '00564ef0', 'bytes': 256, 'sha256': sha(table), **classes}}
    assert all(x == converters[0] for x in converters)
    assert all(x == tables[0] for x in tables)
    assert bodies['1.5.0'] == bodies['official_modern']
    assert callers['1.4.0'] == callers['1.5.0'] == callers['official_modern']
    old, new = bodies['1.4.0'], bodies['1.5.0']
    assert len(old) == 51 and len(new) == 61
    assert old[0x11:0x15].hex() == '3c3a75f7'
    assert new[0x11:0x1b].hex() == '3c2c7506c646ff2eebf1'
    result['checks'] = {'converter_identical_all_inputs': True, 'classification_table_identical': True,
        '150_normalizer_identical_official_final': True, 'historical_and_final_endpoint_caller_identical': True,
        '140_normalizer_bytes': len(old), '150_normalizer_bytes': len(new),
        'new_comma_branch': '004a2f61..004a2f6b',
        'arithmetic': 'Each digit accumulates modulo2^32; optional negation also modulo2^32; final port gate accepts nonzero unsigned EAX<=65535.'}
    (ROOT/'analysis/evidence/audits/endpoint-comma-history.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: pinned1.4.0/1.5.0 comma branch, final body equality, four converter/table identities')


if __name__ == '__main__':
    main()
