"""Account for all file-byte differences in pinned reference/final sound DLLs."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, intervals
from audit_thrash_loader_difference import ROOT


def fields(structure):
    return {names[0]: getattr(structure, names[0]) for names in structure.__keys__}


def main():
    specs = {
        'reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
            '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127',
            '30288653eb2e0b59a3173530433a4adb8ea0dc66cdbc46aadf742dc53ab62b46'),
        'modern': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
            'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3',
            '63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3')}
    result = {'kind': 'sound-reference-final-full-file-byte-accounting', 'baselines': {}, 'paired_sections': []}
    images = []
    raws = []
    for role, (path, archive_sha, dll_sha) in specs.items():
        archive = ROOT/path
        assert sha(archive.read_bytes()) == archive_sha
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'eacsnd.dll'])
        assert sha(raw) == dll_sha
        pe = pefile.PE(data=raw)
        images.append(pe)
        raws.append(raw)
        assert pe.OPTIONAL_HEADER.ImageBase == 0x400000 and pe.OPTIONAL_HEADER.SizeOfHeaders == 0x400
        assert pe.get_overlay_data_start_offset() is None
        result['baselines'][role] = {'archive': path, 'archive_sha256': archive_sha,
            'member': 'eacsnd.dll', 'sha256': dll_sha, 'bytes': len(raw),
            'entry_rva': f'{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08x}',
            'exports': [{'name': e.name.decode('ascii') if e.name else None,
                         'ordinal': e.ordinal, 'rva': f'{e.address:08x}',
                         'forwarder': e.forwarder.decode('ascii') if e.forwarder else None}
                        for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]}
    a, b = images
    old, new = raws
    assert len(old) == 42496 and len(new) == 44032
    assert new[0x400:len(old)] == old[0x400:]
    assert len(a.sections) == 6 and len(b.sections) == 7
    assert result['baselines']['reference']['exports'] == result['baselines']['modern']['exports']
    assert len(a.DIRECTORY_ENTRY_EXPORT.symbols) == 16
    assert a.OPTIONAL_HEADER.AddressOfEntryPoint == b.OPTIONAL_HEADER.AddressOfEntryPoint
    for sa, sb in zip(a.sections, b.sections):
        assert (sa.VirtualAddress, sa.Misc_VirtualSize, sa.SizeOfRawData, sa.PointerToRawData) == (
                sb.VirtualAddress, sb.Misc_VirtualSize, sb.SizeOfRawData, sb.PointerToRawData)
        row = {'reference_name': sa.Name.rstrip(b'\0').decode('ascii'),
               'modern_name': sb.Name.rstrip(b'\0').decode('ascii'),
               'rva': f'{sa.VirtualAddress:08x}', 'virtual_size': sa.Misc_VirtualSize,
               'raw_size': sa.SizeOfRawData, 'raw_pointer': sa.PointerToRawData}
        if sa.PointerToRawData:
            assert sa.get_data() == sb.get_data()
            row.update({'file_backed': True, 'sha256': sha(sa.get_data())})
        else:
            row.update({'file_backed': False, 'contents': 'Not read from file offset0; uninitialized storage metadata only.'})
        result['paired_sections'].append(row)
    result['header_field_changes'] = {}
    for label, x, y in [('dos', a.DOS_HEADER, b.DOS_HEADER), ('coff', a.FILE_HEADER, b.FILE_HEADER),
                         ('optional', a.OPTIONAL_HEADER, b.OPTIONAL_HEADER)]:
        xx, yy = fields(x), fields(y)
        result['header_field_changes'][label] = {key: {'reference': xx[key], 'modern': yy[key]}
                                                 for key in xx if xx[key] != yy[key]}
    result['header_file_offset_intervals'] = intervals(old[:0x400], new[:0x400], 0)
    result['header_interval_address_kind'] = 'file-offsets, not VAs'
    result['directory_changes'] = []
    for index, (x, y) in enumerate(zip(a.OPTIONAL_HEADER.DATA_DIRECTORY, b.OPTIONAL_HEADER.DATA_DIRECTORY)):
        if (x.VirtualAddress, x.Size) != (y.VirtualAddress, y.Size):
            result['directory_changes'].append({'index': index, 'reference': [x.VirtualAddress, x.Size],
                                                'modern': [y.VirtualAddress, y.Size]})
    resources = []
    for kind in b.DIRECTORY_ENTRY_RESOURCE.entries:
        for identifier in kind.directory.entries:
            for language in identifier.directory.entries:
                leaf = language.data.struct
                data = b.get_data(leaf.OffsetToData, leaf.Size)
                resources.append({'type_id': kind.id, 'resource_id': identifier.id, 'language_id': language.id,
                    'rva': f'{leaf.OffsetToData:08x}', 'bytes': leaf.Size, 'sha256': sha(data)})
    assert len(resources) == 1 and (resources[0]['type_id'], resources[0]['resource_id'], resources[0]['language_id']) == (16, 1, 0)
    strings = {}
    for group in b.FileInfo:
        for entry in group:
            for table in getattr(entry, 'StringTable', []):
                strings[table.LangID.decode('ascii')] = {k.decode('ascii'): v.decode('ascii') for k, v in table.entries.items()}
    assert strings['040904b0']['ProductVersion'] == '1.5.3'
    extra = b.sections[-1]
    assert extra.Name.rstrip(b'\0') == b'.rsrc' and extra.PointerToRawData == len(old)
    assert extra.SizeOfRawData == len(new)-len(old) == 1536
    result['added_resource_section'] = {'rva': f'{extra.VirtualAddress:08x}', 'raw_pointer': extra.PointerToRawData,
        'raw_bytes': extra.SizeOfRawData, 'sha256': sha(extra.get_data()), 'resources': resources, 'version_strings': strings}
    result['complete_file_byte_accounting'] = {'shared_postheader_bytes': len(old)-0x400,
        'shared_postheader_equal': True, 'added_bytes': len(new)-len(old),
        'unclassified_differing_byte_locations': 0,
        'meaning': 'All differences localized to first1024 file bytes and appended resource section; not all metadata effects interpreted.'}
    result['limits'] = [
        'Reference bundle is author-hosted, not authenticated pristine retail.',
        'Equal section bytes establish no implementation-byte change in this pair, not full runtime equivalence.',
        'Headers/resource/image-layout changes can affect loading/introspection; no loader/API behavior tested.',
        'Version strings are metadata claims, not authenticated build dates or final package version.',
        'BSS contents, dynamic imports/callbacks, calling context and ambient x87 state remain runtime dependencies.',
        'No DLL loading, target instructions, reconstruction, compilation or Ghidra database writes.']
    (ROOT/'analysis/evidence/audits/sound-reference-final.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:16 matching exports; all41472 shared post-header bytes identical; differences confined to headers and1536 added resource bytes')


if __name__ == '__main__':
    main()
