"""Static DX5 reference/final pairing; never loads either DLL."""
import hashlib
import json
import subprocess
import tempfile

import pefile
from audit_thrash_loader_difference import ROOT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def intervals(a, b, base):
    result = []
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        if not result or result[-1]['end_va_exclusive'] != f'{base+i:08x}':
            result.append({'start_va': f'{base+i:08x}', 'end_va_exclusive': f'{base+i+1:08x}',
                           'reference_hex': f'{x:02x}', 'modern_hex': f'{y:02x}'})
        else:
            result[-1]['end_va_exclusive'] = f'{base+i+1:08x}'
            result[-1]['reference_hex'] += f'{x:02x}'
            result[-1]['modern_hex'] += f'{y:02x}'
    return result


def disassemble(raw, address):
    with tempfile.NamedTemporaryFile() as f:
        f.write(raw)
        f.flush()
        output = subprocess.check_output(['objdump', '-D', '-b', 'binary', '-m', 'i386',
            '-Mintel', f'--adjust-vma={address}', f.name], text=True)
        return [line.strip() for line in output.splitlines() if line.startswith('6000')]


def main():
    specs = {
        'reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
                      '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127',
                      'd3da.dll', 'ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02'),
        'modern': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
                   'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3',
                   'drivers/dx5/dx5a.dll', '6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42')}
    result = {'kind': 'static-dx5-reference-final-pair', 'baselines': {}}
    images = []
    for role, (path, archive_hash, member, dll_hash) in specs.items():
        archive = ROOT / path
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), member])
        assert sha(raw) == dll_hash
        pe = pefile.PE(data=raw)
        assert pe.OPTIONAL_HEADER.ImageBase == 0x60000000
        images.append(pe)
        exports = [{'name': e.name.decode('ascii') if e.name else None,
                    'ordinal': e.ordinal, 'rva': f'{e.address:08x}', 'forwarder':
                    e.forwarder.decode('ascii') if e.forwarder else None}
                   for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]
        result['baselines'][role] = {'archive': path, 'archive_sha256': archive_hash,
            'member': member, 'bytes': len(raw), 'sha256': dll_hash, 'exports': exports,
            'sections': [{'name': s.Name.rstrip(b'\0').decode('ascii'),
                          'rva': f'{s.VirtualAddress:08x}', 'virtual_size': s.Misc_VirtualSize,
                          'raw_size': s.SizeOfRawData, 'raw_pointer': s.PointerToRawData}
                         for s in pe.sections]}
    a, b = images
    assert result['baselines']['reference']['exports'] == result['baselines']['modern']['exports']
    assert len(a.DIRECTORY_ENTRY_EXPORT.symbols) == 34
    result['equal_export_name_ordinal_rva_forwarder_inventory'] = True
    result['paired_file_backed_regions'] = []
    for index, label in [(0, 'code-section-including-padding'), (1, 'import-section'), (2, 'data-section')]:
        sa, sb = a.sections[index], b.sections[index]
        assert sa.VirtualAddress == sb.VirtualAddress and sa.SizeOfRawData == sb.SizeOfRawData
        assert sa.PointerToRawData and sb.PointerToRawData
        x, y = sa.get_data(), sb.get_data()
        changes = intervals(x, y, 0x60000000 + sa.VirtualAddress)
        count = sum(x != y for x, y in zip(x, y))
        assert count == (710 if index == 0 else 0)
        result['paired_file_backed_regions'].append({'label': label, 'bytes': len(x),
            'reference_sha256': sha(x), 'modern_sha256': sha(y),
            'differing_bytes': count, 'changed_intervals': changes})
    result['bounded_bodies'] = []
    for start, end, label in [(0x1020, 0x10d4, 'THRASH_about'),
                               (0x1618, 0x1734, 'selection-helper-and-THRASH_selectdisplay')]:
        x, y = a.get_data(start, end-start), b.get_data(start, end-start)
        changes = intervals(x, y, 0x60000000+start)
        if start == 0x1020:
            assert [(r['start_va'], r['reference_hex'], r['modern_hex']) for r in changes] == [
                ('60001091', '9020', '009e')]
            assert x[0x70:0x75] == bytes.fromhex('ba90200160')
            assert y[0x70:0x75] == bytes.fromhex('ba009e0160')
            assert x[0x9a:0xa0] == y[0x9a:0xa0] == bytes.fromhex('891550200160')
            assert x[0xaa:0xaf] == y[0xaa:0xaf] == bytes.fromhex('b810200160')
        else:
            assert x == y
        result['bounded_bodies'].append({'label': label, 'start_va': f'{0x60000000+start:08x}',
            'end_va_exclusive': f'{0x60000000+end:08x}', 'bytes': len(x),
            'reference_sha256': sha(x), 'modern_sha256': sha(y), 'changed_intervals': changes,
            'disassembly': {role: disassemble(raw, 0x60000000+start)
                            for role, raw in [('reference', x), ('modern', y)]}})
    result['limits'] = [
        'Reference is author-hosted and matches the previously inventoried local root D3DA hash; not authenticated pristine retail.',
        'Raw changed intervals are byte inventory, not function boundaries or complete semantic attribution.',
        'Descriptor +40 pointer relocation is verified; pointed-to initialization and all consumers remain follow-up.',
        'All section VirtualSize fields are zero. BSS raw pointer is zero; no file-backed BSS bytes were read.',
        'Relocations, resources, headers and export-section bytes are not semantically compared here.',
        'No target execution, reconstruction, compilation or saved database mutation.']
    out = ROOT/'analysis/evidence/audits/dx5-reference-final.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: 34 identical export entries; 710 code-section differing bytes; equal import/data sections; bounded descriptor pointer change')


if __name__ == '__main__':
    main()
