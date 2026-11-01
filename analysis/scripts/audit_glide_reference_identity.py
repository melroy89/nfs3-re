"""Keep three Glide renderer identities distinct; static PE and byte inventory."""
import json
import subprocess
import struct
import pefile
from audit_dx5_reference_final import sha, intervals, disassemble
from audit_thrash_loader_difference import ROOT


def exports(pe):
    return [{'name': e.name.decode('ascii') if e.name else None, 'ordinal': e.ordinal,
             'rva': f'{e.address:08x}', 'forwarder': e.forwarder.decode('ascii') if e.forwarder else None}
            for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]


def imports(pe):
    return {library.dll.decode('ascii').casefold(): [entry.name.decode('ascii') if entry.name else entry.ordinal
            for entry in library.imports] for library in pe.DIRECTORY_ENTRY_IMPORT}


def main():
    specs = {
        'hosted_reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
            '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127', 'voodoo2a.dll',
            '99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b'),
        'official_final': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
            'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3', 'drivers/glide3x/voodoo2a.dll',
            'f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b')}
    raws = {}
    sources = {}
    for role, (path, expected, member, dll_sha) in specs.items():
        archive = ROOT/path
        assert sha(archive.read_bytes()) == expected
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), member])
        assert sha(raw) == dll_sha
        raws[role] = raw
        sources[role] = {'archive': path, 'archive_sha256': expected, 'member': member}
    path = 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/VOODOO2A.DLL'
    raws['local_legacy_candidate'] = (ROOT/path).read_bytes()
    assert sha(raws['local_legacy_candidate']) == 'f65f00e6fa6a5a67e11ff38d661b3d493474d0e075c9183a7b244b1143cea88e'
    sources['local_legacy_candidate'] = {'path': path}
    images = {role: pefile.PE(data=raw) for role, raw in raws.items()}
    result = {'kind': 'three-way-glide-baseline-identity', 'baselines': {}, 'paired_reference_final_regions': []}
    for role, pe in images.items():
        assert pe.OPTIONAL_HEADER.ImageBase == 0x60000000
        strings = []
        for group in getattr(pe, 'FileInfo', []):
            for entry in group:
                for table in getattr(entry, 'StringTable', []):
                    strings.append({k.decode('ascii'): v.decode('ascii') for k, v in table.entries.items()})
        result['baselines'][role] = {**sources[role], 'bytes': len(raws[role]), 'sha256': sha(raws[role]),
            'exports': exports(pe), 'imports': imports(pe), 'version_strings': strings,
            'sections': [{'name': s.Name.rstrip(b'\0').decode('ascii'), 'rva': f'{s.VirtualAddress:08x}',
                'virtual_size': s.Misc_VirtualSize, 'raw_size': s.SizeOfRawData,
                'raw_pointer': s.PointerToRawData} for s in pe.sections]}
    ref, final, local = (images[k] for k in ('hosted_reference', 'official_final', 'local_legacy_candidate'))
    assert exports(ref) == exports(final) and len(exports(ref)) == 34
    rx = {e['name']: e for e in exports(ref)}
    lx = {e['name']: e for e in exports(local)}
    assert rx.keys() == lx.keys() and all(rx[name]['rva'] != lx[name]['rva'] for name in rx)
    assert imports(ref)['glide3x.dll'] == ['_grCoordinateSpace@4', '_grQueryResolutions@8', '_grVertexLayout@12']
    assert 'glide3x.dll' not in imports(local)
    assert 'glide3x.dll' not in imports(final) and 'ddraw.dll' not in imports(final)
    for index, label, expected_count in [(0, 'code-including-padding', 3307), (1, 'imports', 1218), (2, 'initialized-data', 363)]:
        x, y = ref.sections[index], final.sections[index]
        assert (x.VirtualAddress, x.SizeOfRawData) == (y.VirtualAddress, y.SizeOfRawData)
        assert x.PointerToRawData and y.PointerToRawData
        a, b = x.get_data(), y.get_data()
        count = sum(x != y for x, y in zip(a, b))
        assert count == expected_count
        result['paired_reference_final_regions'].append({'label': label, 'bytes': len(a),
            'reference_sha256': sha(a), 'final_sha256': sha(b), 'differing_bytes': count,
            'changed_intervals': intervals(a, b, 0x60000000+x.VirtualAddress)})
    result['about_mode_construction'] = {'captures': [], 'reference_fixed_records': []}
    for role, pe, start, end, label in [
        ('hosted_reference', ref, 0x1bb0, 0x1d4d, 'complete-about'),
        ('official_final', final, 0x1bb0, 0x1d4d, 'complete-about'),
        ('hosted_reference', ref, 0x1940, 0x1bb0, 'complete-reference-mode-helper'),
        ('hosted_reference', ref, 0x18b0, 0x1934, 'complete-reference-query-helper'),
        ('official_final', final, 0x18d8, 0x1b79, 'complete-final-mode-helper')]:
        body = pe.get_data(start, end-start)
        result['about_mode_construction']['captures'].append({'role': role, 'label': label,
            'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
            'sha256': sha(body), 'disassembly': disassemble(body, 0x60000000+start)})
    about_changes = intervals(ref.get_data(0x1bb0, 0x19d), final.get_data(0x1bb0, 0x19d), 0x60001bb0)
    assert len(about_changes) == 6 and sum(len(row['reference_hex'])//2 for row in about_changes) == 63
    result['about_mode_construction']['about_changed_intervals'] = about_changes
    for pe, count, pointer in [(ref, 16, 0x6000fdd4), (final, 0, 0x60013000)]:
        assert pe.get_data(0x1c24, 5) == b'\xbe'+struct.pack('<I', count)
        assert pe.get_data(0x1c29, 5) == b'\xbf'+struct.pack('<I', pointer)
    assert ref.get_data(0x1d22, 5).hex() == 'e819fcffff'
    assert final.get_data(0x1d11, 5).hex() == 'e8c2fbffff'
    assert ref.get_data(0x1d3e, 5).hex() == 'e8fdfbffff'
    assert final.get_data(0x1d3e, 5).hex() == 'e895fbffff'
    for index in range(17):
        raw = ref.get_data(0xfdd4+index*40, 40)
        values = struct.unpack('<10I', raw)
        if index:
            assert values[2] == 16
        else:
            assert raw == bytes(40)
        result['about_mode_construction']['reference_fixed_records'].append({'index': index,
            'va': f'{0x6000fdd4+index*40:08x}', 'words': list(values)})
    assert ref.get_data(0x1a58, 5).hex() == '83fd107eac'
    thunk = ref.get_data(0xd89a, 6)
    assert thunk[:2] == bytes.fromhex('ff25')
    iat = struct.unpack('<I', thunk[2:])[0]
    imports_by_va = {entry.address: entry.name for library in ref.DIRECTORY_ENTRY_IMPORT for entry in library.imports}
    assert imports_by_va[iat] == b'_grQueryResolutions@8'
    assert ref.get_data(0x18db, 5).hex() == 'e8babf0000'
    assert ref.get_data(0x1904, 5).hex() == 'e891bf0000'
    result['about_mode_construction']['reference_query_binding'] = {'thunk_va': '6000d89a',
        'thunk_hex': thunk.hex(), 'iat_va': f'{iat:08x}', 'name': '_grQueryResolutions@8',
        'scope': 'Two direct helper calls through static import thunk; no provider invocation.'}
    result['loader_lifetime'] = {'captures': [], 'imports': {}, 'resolved_names': {}}
    for role, pe, start, end, label in [
        ('hosted_reference', ref, 0x1020, 0x1552, 'complete-reference-loader'),
        ('hosted_reference', ref, 0x1560, 0x158d, 'complete-reference-module-release'),
        ('official_final', final, 0x1020, 0x1107, 'complete-final-loader'),
        ('official_final', final, 0x1108, 0x111e, 'complete-final-shutdown-gate')]:
        body = pe.get_data(start, end-start)
        result['loader_lifetime']['captures'].append({'role': role, 'label': label,
            'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
            'sha256': sha(body), 'disassembly': disassemble(body, 0x60000000+start)})
    for role, pe in [('hosted_reference', ref), ('official_final', final)]:
        by_va = {entry.address: entry.name.decode('ascii') if entry.name else entry.ordinal
                 for library in pe.DIRECTORY_ENTRY_IMPORT for entry in library.imports}
        assert by_va[0x6000e1b4] == 'FreeLibrary'
        assert by_va[0x6000e1fc] == 'GetProcAddress'
        assert by_va[0x6000e210] == 'LoadLibraryA'
        result['loader_lifetime']['imports'][role] = {f'{v:08x}': by_va[v] for v in (0x6000e1b4, 0x6000e1fc, 0x6000e210)}
        assert pe.get_string_at_rva(0xf010) == b'_grGlideInit@0'
        assert pe.get_string_at_rva(0xf020) == b'_grGlideShutdown@0'
    assert ref.get_data(0x1579, 8).hex() == '522eff15b4e10060'
    assert ref.get_data(0x1581, 8).hex() == '31db891d0cfd0060'
    assert final.get_data(0x1108, 22).hex() == 'a1d027016085c0740cff1514100160ff0dd0270160c3'
    assert final.get_data(0x10de, 32).hex() == 'a1d027016085c07517ff15101001606880180060ff15d8100160ff05d0270160'
    bindings = []
    for index in range(128):
        pointer, slot = struct.unpack('<2I', final.get_data(0x1120+8*index, 8))
        if not pointer:
            break
        bindings.append({'name': final.get_string_at_rva(pointer-0x60000000).decode('ascii'), 'slot': f'{slot:08x}'})
    else:
        raise AssertionError('Missing binding terminator')
    slots = {row['slot']: row['name'] for row in bindings}
    assert slots['60011010'] == '_grGlideInit@0' and slots['60011014'] == '_grGlideShutdown@0'
    result['loader_lifetime']['resolved_names'] = {'60011010': slots['60011010'], '60011014': slots['60011014']}
    result['loader_lifetime']['final_required_binding_count'] = len(bindings)
    raw = raws['official_final']
    literal = struct.pack('<I', 0x600127d0)
    offsets = [i for i in range(len(raw)-3) if raw[i:i+4] == literal]
    locations = [final.get_rva_from_offset(i)+0x60000000 for i in offsets]
    assert locations == [0x600010df, 0x600010fa, 0x60001109, 0x60001119]
    result['loader_lifetime']['init_cell_exact_literal_operands'] = [f'{v:08x}' for v in locations]
    result['export_comparison'] = {'reference_final_entries_equal': 34,
                                   'reference_local_names_equal': 34, 'reference_local_changed_rvas': 34}
    result['limits'] = [
        'Author-reference bundle is mixed and not authenticated pristine retail; resource dates/attributions are claims.',
        'Same export RVA is correspondence evidence, not complete function/ABI or runtime equivalence.',
        'Previous local-candidate semantic results cannot be transferred to hosted-reference code without new comparison.',
        'Absent static imports do not establish absence of dynamic library/API use.',
        'Raw intervals include padding and are not function boundaries or independently explained features.',
        'No DLL loading, target execution, reconstruction, compilation or saved Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/glide-reference-identity.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:three pinned Glide identities;34 hosted/final export entries match; all34 local RVAs differ; new reference/final region map')


if __name__ == '__main__':
    main()
