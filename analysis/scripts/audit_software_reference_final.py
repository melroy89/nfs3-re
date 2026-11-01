"""Static software-renderer pairing and bounded mode-depth comparison."""
import json
import subprocess

import pefile
from audit_dx5_reference_final import sha, intervals, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs = {
        'reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
            '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127',
            'softtria.dll', '8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02'),
        'modern': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
            'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3',
            'drivers/softtri/softtria.dll', '9479203471f4dd615788769bac365043d903505af370c48df69e5d6a1e6f8732')}
    result = {'kind': 'software-renderer-reference-final', 'baselines': {}, 'paired_regions': [], 'bodies': []}
    images = []
    for role, (path, expected, member, dll_sha) in specs.items():
        archive = ROOT/path
        assert sha(archive.read_bytes()) == expected
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), member])
        assert sha(raw) == dll_sha
        pe = pefile.PE(data=raw)
        assert pe.OPTIONAL_HEADER.ImageBase == 0x60000000
        images.append(pe)
        overlay_offset = pe.get_overlay_data_start_offset()
        overlay = raw[overlay_offset:] if overlay_offset is not None else b''
        result['baselines'][role] = {'archive': path, 'archive_sha256': expected, 'member': member,
            'bytes': len(raw), 'sha256': dll_sha,
            'exports': [{'name': e.name.decode('ascii') if e.name else None,
                         'ordinal': e.ordinal, 'rva': f'{e.address:08x}',
                         'forwarder': e.forwarder.decode('ascii') if e.forwarder else None}
                        for e in pe.DIRECTORY_ENTRY_EXPORT.symbols],
            'sections': [{'name': s.Name.rstrip(b'\0').decode('ascii'), 'rva': f'{s.VirtualAddress:08x}',
                          'virtual_size': s.Misc_VirtualSize, 'raw_size': s.SizeOfRawData,
                          'raw_pointer': s.PointerToRawData} for s in pe.sections],
            'trailing_overlay': {'offset': overlay_offset, 'bytes': len(overlay), 'sha256': sha(overlay)}}
    a, b = images
    assert result['baselines']['reference']['exports'] == result['baselines']['modern']['exports']
    assert len(a.DIRECTORY_ENTRY_EXPORT.symbols) == 34
    assert result['baselines']['reference']['trailing_overlay']['bytes'] == 28514
    assert result['baselines']['modern']['trailing_overlay']['bytes'] == 0
    for index, label in [(0, 'shared-code-section-including-padding'), (1, 'import-section'), (2, 'data-section')]:
        sa, sb = a.sections[index], b.sections[index]
        assert sa.PointerToRawData and sb.PointerToRawData
        assert (sa.VirtualAddress, sa.SizeOfRawData) == (sb.VirtualAddress, sb.SizeOfRawData)
        x, y = sa.get_data(), sb.get_data()
        count = sum(x != y for x, y in zip(x, y))
        assert count == (44 if index == 0 else 0)
        result['paired_regions'].append({'label': label, 'bytes': len(x), 'reference_sha256': sha(x),
            'modern_sha256': sha(y), 'differing_bytes': count,
            'changed_intervals': intervals(x, y, 0x60000000+sa.VirtualAddress)})
    assert len(result['paired_regions'][0]['changed_intervals']) == 9
    for start, end, label in [(0x2330, 0x2412, 'complete-about-body'),
                               (0x2480, 0x2580, 'complete-mode-callback'),
                               (0x2e80, 0x2f41, 'complete-pixel-classifier'),
                               (0x26f6, 0x27ac, 'bounded-mode-table-allocation-seed-and-callback-registration')]:
        x, y = a.get_data(start, end-start), b.get_data(start, end-start)
        if start != 0x2480:
            assert x == y
        for role, raw in [('reference', x), ('modern', y)]:
            result['bodies'].append({'role': role, 'label': label, 'start_va': f'{0x60000000+start:08x}',
                'end_va_exclusive': f'{0x60000000+end:08x}', 'sha256': sha(raw),
                'disassembly': disassemble(raw, 0x60000000+start)})
    assert a.get_data(0x2494, 10).hex() == '83fe0f7505be10000000'
    assert b.get_data(0x2494, 10).hex() == '83fe10756deb03909090'
    assert a.get_data(0x2537, 4).hex() == '85ed749b'
    assert b.get_data(0x2537, 4).hex() == '85ed74cb'
    assert a.get_data(0x24e1, 10) == b.get_data(0x24e1, 10) == bytes.fromhex('83fd037505be0f000000')
    result['limits'] = [
        'Author-hosted reference bundle, not authenticated pristine retail.',
        'Shared code-section byte inventory includes padding; not all nine intervals are semantically classified.',
        'Only callback admission and retained classifier/about bodies interpreted here; selected setup seeds/registration are captured; exhaustive consumers remain follow-up.',
        'Raw16 admission can still publish depth15 for classifier3; not every stored depth equals16.',
        'Trailing overlay identity/size only; purpose and original authenticity unresolved.',
        'VirtualSize0 and BSS raw pointer0 are retained metadata, not file-backed zero initializers.',
        'No driver loading, OS calls, instruction probes, executable edits or database writes.']
    (ROOT/'analysis/evidence/audits/software-reference-final.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:34 matching exports;44 code-section differing bytes in9 intervals; raw16 callback admission; equal import/data sections')


if __name__ == '__main__':
    main()
