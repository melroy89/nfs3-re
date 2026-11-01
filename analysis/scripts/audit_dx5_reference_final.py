"""Static DX5 reference/final pairing; never loads either DLL."""
import hashlib
import json
import re
import subprocess
import tempfile
import uuid

import pefile
from audit_thrash_loader_difference import ROOT, SPECS


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
        return [line.strip() for line in output.splitlines() if re.match(r'^\s*[0-9a-f]+:', line)]


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
    # Mode policy: complete callbacks and retained classifier, plus bounded setup witnesses.
    result['mode_policy'] = {'captures': [], 'assertions': []}
    spans = [('reference', a, 0x17bc, 0x18e3, 'complete-enumeration-callback'),
             ('modern', b, 0x17bc, 0x187d, 'complete-enumeration-callback'),
             ('reference', a, 0x1b80, 0x1c23, 'first-setup-tail'),
             ('modern', b, 0x1b80, 0x1bf1, 'first-setup-tail'),
             ('reference', a, 0x21da, 0x2288, 'second-setup-tail'),
             ('modern', b, 0x21da, 0x2256, 'second-setup-tail'),
             ('reference', a, 0x25f0, 0x26b1, 'complete-pixel-classifier'),
             ('modern', b, 0x25f0, 0x26b1, 'complete-pixel-classifier')]
    for role, pe, start, end, label in spans:
        raw = pe.get_data(start, end-start)
        result['mode_policy']['captures'].append({'role': role, 'label': label,
            'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
            'sha256': sha(raw), 'hex': raw.hex(), 'disassembly': disassemble(raw, 0x60000000+start)})
    assert a.get_data(0x25f0, 0xc1) == b.get_data(0x25f0, 0xc1)
    checks = [('modern', b, 0x17df, '3d800200000f828700000081fbe0010000727f', 'unsigned width640/height480 admission'),
              ('modern', b, 0x1804, '833a647368ff02', 'new-key count100 admission'),
              ('modern', b, 0x1816, '394f0875dd', 'raw depth comparison before classifier conversion'),
              ('modern', b, 0x1820, '83fd037505b90f000000', 'classifier3 stored depth15'),
              ('modern', b, 0x1855, '83f8037610', 'unsigned quotient cap3 branch'),
              ('reference', a, 0x1b80, 'bbb0040000', 'first clear request1200'),
              ('modern', b, 0x1b80, 'bba00f0000', 'first clear request4000'),
              ('reference', a, 0x21da, 'bbb0040000', 'second clear request1200'),
              ('modern', b, 0x21da, 'bba00f0000', 'second clear request4000'),
              ('modern', b, 0x1bc7, 'c7054c20016002000000', 'first count seed2'),
              ('modern', b, 0x2221, 'c7054c20016002000000', 'second count seed2'),
              ('modern', b, 0x2691, '83fb207514b806000000', 'classifier accepts32 with RGB mask predicates')]
    for role, pe, rva, expected, label in checks:
        assert pe.get_data(rva, len(bytes.fromhex(expected))).hex() == expected, label
        result['mode_policy']['assertions'].append({'role': role, 'va': f'{0x60000000+rva:08x}',
                                                    'hex': expected, 'meaning': label})
    result['state_selector_15'] = {'captures': []}
    for role, pe in [('reference', a), ('modern', b)]:
        for start, end, label in [(0x2b58, 0x34d1, 'complete-setstate-body'),
                                   (0x2994, 0x2a4d, 'table-generator'),
                                   (0x2a50, 0x2af8, 'table-expander'),
                                   (0x4f64, 0x4fb2, 'numeric-device-state-adapter')]:
            raw = pe.get_data(start, end-start)
            result['state_selector_15']['captures'].append({'role': role, 'label': label,
                'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
                'sha256': sha(raw), 'disassembly': disassemble(raw, 0x60000000+start)})
    changes = intervals(a.get_data(0x2b58, 0x979), b.get_data(0x2b58, 0x979), 0x60002b58)
    assert [(c['start_va'], c['end_va_exclusive']) for c in changes] == [
        ('60002e47', '60002e78'), ('6000341c', '60003498')]
    assert b.get_data(0x2e47, 5).hex() == 'e942fdffff'
    assert b.get_data(0x2e4c, 0x2c) == b'\x90'*0x2c
    assert b.get_data(0x341c, 0x7c) == b'\x90'*0x7c
    assert a.get_data(0x2b8e, 12) == b.get_data(0x2b8e, 12)
    for start, end in [(0x2994, 0x2a4d), (0x2a50, 0x2af8), (0x4f64, 0x4fb2)]:
        assert a.get_data(start, end-start) == b.get_data(start, end-start)
    result['state_selector_15']['changed_intervals'] = changes
    result['state_selector_15']['limits'] = [
        'Numeric selector15h removal from this export only; no claim of all fog removal.',
        'Device object identity and API enumeration names are not established by numeric state calls alone.',
        'Retained table helpers and other entry routes remain present; caller usage and rendered effects are untested.']
    result['lock_callback'] = {'captures': []}
    for role, pe in [('reference', a), ('modern', b)]:
        for start, end, label in [(0x11d4, 0x1366, 'complete-lockwindow-body'),
                                   (0x1368, 0x13d0, 'complete-unlockwindow-body')]:
            raw = pe.get_data(start, end-start)
            result['lock_callback']['captures'].append({'role': role, 'label': label,
                'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
                'sha256': sha(raw), 'disassembly': disassemble(raw, 0x60000000+start)})
    wrapper = b.get_data(0x1880, 0x11)
    assert wrapper.hex() == '5389c3a19c28016085c0740353ffd05bc3'
    result['lock_callback']['new_adapter'] = {'start_va': '60001880', 'end_va_exclusive': '60001891',
        'sha256': sha(wrapper), 'disassembly': disassemble(wrapper, 0x60001880)}
    assert a.get_data(0x123a, 0x1366-0x123a) == b.get_data(0x123a, 0x1366-0x123a)
    assert a.get_data(0x1368, 0x68) == b.get_data(0x1368, 0x68)
    assert b.get_data(0x11f8, 8).hex() == '31c040e880060000'
    assert b.get_data(0x1229, 0x10).hex() == '85c0740d31c0e84c060000e9ed000000'
    # Every differing byte in the shared code section must belong to one reviewed cluster.
    clusters = [(0x1020, 0x10d4, 'descriptor-publication'),
                (0x11d4, 0x1366, 'lock-callback-notification'),
                (0x17bc, 0x18e3, 'mode-callback-and-new-notification-adapter'),
                (0x1b80, 0x1c23, 'first-mode-setup-tail'),
                (0x21da, 0x2288, 'second-mode-setup-tail'),
                (0x2b58, 0x34d1, 'removed-state-selector-route')]
    result['code_byte_accounting'] = []
    assigned = set()
    for start, end, label in clusters:
        changed = {r for r in range(start, end) if a.get_data(r, 1) != b.get_data(r, 1)}
        assert not assigned.intersection(changed)
        assigned.update(changed)
        result['code_byte_accounting'].append({'label': label,
            'start_va': f'{0x60000000+start:08x}', 'end_va_exclusive': f'{0x60000000+end:08x}',
            'differing_bytes': len(changed)})
    all_changed = {0x1000+i for i, (x, y) in enumerate(zip(a.sections[0].get_data(), b.sections[0].get_data())) if x != y}
    assert assigned == all_changed and len(assigned) == 710
    result['unassigned_code_section_differing_bytes'] = 0
    # Cross-component binding: final DX5's rejected selector is the EXE fog trial.
    exe_path, exe_sha, _ = SPECS['official_modern']
    exe_raw = (ROOT/exe_path).read_bytes()
    assert sha(exe_raw) == exe_sha
    exe = pefile.PE(data=exe_raw)
    assert exe.get_data(0x13f70c, 7) == b'THRASH\0'
    assert exe.get_data(0x13f724, 11) == b'FogSupport\0'
    imports = {entry.address: entry.name.decode('ascii') if entry.name else entry.ordinal
               for library in exe.DIRECTORY_ENTRY_IMPORT for entry in library.imports}
    assert imports[0x534670] == 'GetPrivateProfileIntA'
    official_archive = ROOT/specs['modern'][0]
    ini_member = 'drivers/dx5/thrash.ini'
    ini = subprocess.check_output(['7z', 'x', '-so', str(official_archive), ini_member])
    ini_lines = [line.strip() for line in ini.decode('ascii').splitlines() if line.strip()]
    assert 'File=dx5a.dll' in ini_lines and 'Type=d3d' in ini_lines
    assert not any(line.split('=', 1)[0].casefold() == 'fogsupport' for line in ini_lines)
    result['exe_dx5_fog_admission'] = {'exe': exe_path, 'exe_sha256': exe_sha,
        'config_member': ini_member, 'config_sha256': sha(ini), 'config_text': ini.decode('ascii'),
        'FogSupport_key_present': False, 'GetPrivateProfileIntA_iat': '00534670', 'captures': []}
    for start, end, label in [(0x4b597b, 0x4b599e, 'INI-opt-in-default0-and-normalization'),
                               (0x4b5bb0, 0x4b5bd6, 'conditional-state21-value4-trial'),
                               (0x431c1c, 0x431c33, 'complete-fog-admission-recompute')]:
        raw = exe.get_data(start-0x400000, end-start)
        result['exe_dx5_fog_admission']['captures'].append({'label': label,
            'start_va': f'{start:08x}', 'end_va_exclusive': f'{end:08x}',
            'sha256': sha(raw), 'hex': raw.hex(), 'disassembly': disassemble(raw, start)})
    assert exe.get_data(0xb5980, 2).hex() == '6a00'
    assert exe.get_data(0xb5bb9, 10).hex() == '6a046a15ff156cf99e00'
    assert exe.get_data(0xb5bc3, 9).hex() == '85c07505a3543a7a00'
    assert exe.get_data(0x31c1c, 23).hex() == 'a1543a7a002305d4d16f00230534925500a3643a7a00c3'
    result['exe_dx5_fog_admission']['limits'] = [
        'Conditional on the configured path selecting this INI, the bound slot selecting this DX5 DLL, and the common trial route being reached.',
        'No runtime INI API, renderer dispatch, fog output or complete later-write lifetime was observed.',
        'Decimal21 equals hex15h; do not confuse this with decimal state15.']
    budget_spans=[]
    for lo,hi in [(0x1937,0x1aed),(0x1c35,0x1c4e)]:
        left,right=[pe.get_data(lo,hi-lo) for pe in images]
        assert left==right
        budget_spans.append({'start':f'{0x60000000+lo:08x}','end_exclusive':f'{0x60000000+hi:08x}',
            'sha256':sha(left),'bytes_hex':left.hex(),'disassembly':disassemble(left,0x60000000+lo)})
    for pe in images:
        assert pe.get_data(0x11970,16)==uuid.UUID('b3a6f3e0-2b43-11cf-a2de-00aa00b93356').bytes_le
        assert pe.get_data(0x1937,5).hex()=='68b80e0160'
        assert pe.get_data(0x1a93,5).hex()=='ff515c85c0'
        assert pe.get_data(0x1a9e,10).hex()=='c705b40e016000002000'
        assert pe.get_data(0x1c35,20).hex()=='89f00fafc38b94245003000001c28915b40e0160'
        assert pe.get_data(0x10eb4,4)==bytes(4)
    result['mode_budget_producer']={'identical_spans':budget_spans,
        'interface_iid_address':'60011970','iid':'b3a6f3e0-2b43-11cf-a2de-00aa00b93356',
        'interface_publication':'QueryInterface at60001952 writes60010eb8; HRESULT checked after release at6000197b',
        'query':'vtable+5ch at60001a93,IDirectDraw2::GetAvailableVidMem',
        'caps':'10004000h,local video-memory query',
        'stack_outputs':'At steadyESP S,total=S+350h,free=S+34ch,caps=S+358h',
        'success':'60001c35..60001c49 writes wrap32(total + wrap32(ESI*EBX)) to60010eb4',
        'surface_values':'GetSurfaceDesc at60001a13 outputsS+2e0h; ESI=lPitch(+10h),EBX=height(+8h),after accounting for pushes',
        'failure':'60001a9e writes00200000h,2MiB',
        'initial_file_backed_value':'00000000',
        'primary_header':'https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/ddraw.h',
        'api_context':'https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-getavailablevidmem',
        'limits':['Read-only static ABI/dataflow; no memory query or provider executed.',
                  'The Learn page describes the laterIDirectDraw7 API; exactv2 IID/order/structure mapping comes from the header.',
                  'GetSurfaceDesc return is not locally tested before dimensions/pitch use; success/valid fields assumed for their names.',
                  'Returned total plus surface estimate is a driver heuristic,not physical VRAM capacity or proven allocation success.',
                  'Only selected direct producers are established; aliases,later writes and full enumeration lifecycle remain separate.']}
    result['limits'] = [
        'Reference is author-hosted and matches the previously inventoried local root D3DA hash; not authenticated pristine retail.',
        'Raw changed intervals are byte inventory, not function boundaries or complete semantic attribution.',
        'Descriptor +40 pointer relocation is verified; selected initialization/callback paths are captured below; exhaustive consumers remain follow-up.',
        'All section VirtualSize fields are zero. BSS raw pointer is zero; no file-backed BSS bytes were read.',
        'Relocations, resources, headers and export-section bytes are not semantically compared here.',
        'No target execution, reconstruction, compilation or saved database mutation.']
    out = ROOT/'analysis/evidence/audits/dx5-reference-final.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: 34 identical export entries; 710 code-section differing bytes; equal import/data sections; bounded descriptor pointer change')


if __name__ == '__main__':
    main()
