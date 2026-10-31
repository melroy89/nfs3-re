"""Compare a bounded THRASH_about setup prefix; never load target DLLs."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from inventory_legacy_dll_candidates import GAME

SPECS = [
    ('legacy_candidate', 'VOODOO2A.DLL',
     'f65f00e6fa6a5a67e11ff38d661b3d493474d0e075c9183a7b244b1143cea88e',
     0x60001a60, 0x60001b5e, 0x6000fd54,
     [(0x60001a7f, 'b958464433', 'ECX immediate', '33444658'),
      (0x60001a84, 'be68000000', 'ESI immediate', '00000068'),
      (0x60001ace, 'be10000000', 'ESI immediate', '00000010'),
      (0x60001ad3, 'bf18fe0060', 'EDI immediate', '6000fe18'),
      (0x60001af4, '893590fd0060', 'ESI store destination', '6000fd90'),
      (0x60001afa, '893d94fd0060', 'EDI store destination', '6000fd94')]),
    ('official_matching_wrapper', 'drivers/glide3x/voodoo2a.dll',
     'f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b',
     0x60001bb0, 0x60001cb4, 0x6000fd10,
     [(0x60001bd5, 'b932464433', 'ECX immediate', '33444632'),
      (0x60001bda, 'be68000000', 'ESI immediate', '00000068'),
      (0x60001c24, 'be00000000', 'ESI immediate', '00000000'),
      (0x60001c29, 'bf00300160', 'EDI immediate', '60013000'),
      (0x60001c4a, '89354cfd0060', 'ESI store destination', '6000fd4c'),
      (0x60001c50, '893d50fd0060', 'EDI store destination', '6000fd50')]),
]


def main():
    candidates = json.loads((ROOT/'analysis/evidence/audits/legacy-dll-candidates.json').read_text())
    out = {'scope': 'THRASH_about setup prefixes and selected mode-producing helper bodies', 'files': {}}
    for label, relative, wanted, start, end, descriptor, checks in SPECS:
        path = ROOT/GAME/relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == wanted
        pe = pefile.PE(data=raw)
        base = pe.OPTIONAL_HEADER.ImageBase
        exports = {e.name: base+e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols}
        assert exports[b'_THRASH_about@0'] == start
        rows = []
        for va, encoded, role, value in checks:
            assert pe.get_data(va-base, len(bytes.fromhex(encoded))).hex() == encoded
            rows.append({'va': f'{va:08x}', 'bytes': encoded, 'role': role, 'value': value})
        prefix = pe.get_data(start-base, end-start)
        asm = subprocess.check_output(['objdump', '-d', '-Mintel',
            f'--start-address={start}', f'--stop-address={end}', str(path)], text=True)
        out['files'][label] = {'path': str(path.relative_to(ROOT)), 'sha256': wanted,
            'export_va': f'{start:08x}', 'descriptor_va': f'{descriptor:08x}',
            'prefix_end_exclusive': f'{end:08x}', 'prefix_bytes': len(prefix),
            'prefix_sha256': hashlib.sha256(prefix).hexdigest(),
            'prefix_hex': prefix.hex(), 'disassembly': asm, 'checked_instructions': rows}
    helper_specs = {
        'legacy_candidate': [(0x600018c0, 0x60001a53)],
        'official_matching_wrapper': [(0x600018d8, 0x60001b79), (0x600012e8, 0x600013e9)],
    }
    for label, spans in helper_specs.items():
        row = out['files'][label]
        path = ROOT/row['path']
        pe = pefile.PE(str(path))
        base = pe.OPTIONAL_HEADER.ImageBase
        row['mode_helper_spans'] = []
        for start, end in spans:
            raw = pe.get_data(start-base, end-start)
            row['mode_helper_spans'].append({
                'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'hex': raw.hex(),
                'disassembly': subprocess.check_output(['objdump', '-d', '-Mintel',
                    f'--start-address={start}', f'--stop-address={end}', str(path)], text=True)})
    modern = pefile.PE(str(ROOT/out['files']['official_matching_wrapper']['path']))
    for va, encoded in [(0x60001327, '83fb64'), (0x60001330, 'ff054cfd0060'),
                        (0x60001304, '6bf828'), (0x60001b67, 'ff054cfd0060'),
                        (0x60001b70, 'a3d4270160')]:
        assert modern.get_data(va-modern.OPTIONAL_HEADER.ImageBase, len(bytes.fromhex(encoded))).hex() == encoded
    assert out['files']['official_matching_wrapper']['sha256'] == candidates['files']['modern_voodoo']['sha256']
    out['limits'] = ['Setup writes are not final descriptor values after later hardware-dependent calls.',
        'Local legacy candidate is not independently authenticated retail or paired with nfs3_org.exe.',
        'No API-size/version names assigned to literal +8=0x68; +0x3c/+0x40 mode roles use the separate executable consumer audit.',
        'No DLL execution, compatibility test, Ghidra mutation or executable modification.']
    (ROOT/'analysis/evidence/audits/voodoo-about-setup.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: pinned DLLs, exported entry addresses and seventeen setup/mode instruction checks')


if __name__ == '__main__':
    main()
