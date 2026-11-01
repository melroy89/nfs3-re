"""Keep three Glide renderer identities distinct; static PE and byte inventory."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, intervals
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
