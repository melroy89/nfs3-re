"""Compare slideshow navigation, binding and deferred refresh witnesses, offline."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-slideshow-navigation-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/slideshow-navigation'
    capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x453840, 0x453859), (0x453860, 0x45393e), (0x453c00, 0x453c4f), (0x453ed7, 0x453eec), (0x453ef0, 0x453f48)] if label == 'original' else [(0x453850, 0x453863), (0x453864, 0x45393d), (0x453c00, 0x453c4f), (0x453ed7, 0x453eee), (0x453ef0, 0x453f58)]
        spans += [(0x44aa30, 0x44aac9), (0x44a9e0, 0x44aa21), (0x44ab40, 0x44ac7c),
                  (0x44b6c8, 0x44b707), (0x44b7a7, 0x44b7ec), (0x44b30b, 0x44b382)]
        rows = []
        for start, end in spans:
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'tokens': {f'{a:08x}': pe.get_data(a-0x400000, 32).split(b'\0')[0].decode() for a in (0x5397a4, 0x5397b0)},
            'slides_registration_row_00555f90_hex': pe.get_data(0x155f90, 24).hex(),
            'action_switch_0044b208_hex': pe.get_data(0x4b208, 32).hex()}
        assert int.from_bytes(pe.get_data(0x4b21c, 4), 'little') == 0x44b7a7
    common = [p.get_data(0x5386d, 0x453931-0x45386d) for p in images]
    assert common[0] == common[1]
    out['retained_previous_core'] = {'start': '0045386d', 'end': '00453931', 'sha256': hashlib.sha256(common[0]).hexdigest()}
    out['retained_action9_path_ranges'] = []
    for start, end in ((0x44aa30, 0x44aac9), (0x44a9e0, 0x44aa21), (0x44ab40, 0x44ac7c), (0x44b6c8, 0x44b707), (0x44b7a7, 0x44b7ec)):
        pair = [p.get_data(start-0x400000, end-start) for p in images]
        assert pair[0] == pair[1]
        out['retained_action9_path_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pair[0]).hexdigest()})
    archive = ROOT / 'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    relative = 'analysis/captures/modern-differences/upstream/package/fedata/menus/slides.mnu'
    raw = (ROOT/relative).read_bytes()
    assert raw == subprocess.check_output(['7z', 'x', '-so', str(archive), 'fedata/menus/slides.mnu'])
    out['official_arrow_asset'] = {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'fields': [{'line': i, 'field': line} for i, line in enumerate(raw.decode('latin1').splitlines(), 1) if line.startswith(('codelink=keyleft ', 'codelink=keyright '))]}
    out['limits'] = ['No input, filesystem, renderer or target execution.', 'Binding/refresh snippets are explicitly partial; complete refresh routine and resources not validated.', 'Action9 path is traced conditionally; shared counter aliases, pending-menu overrides and complete callback admission remain separate.']
    (ROOT/'analysis/evidence/audits/original-modern-slideshow-navigation.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: explicit callback counterparts, retained previous core, deferred-refresh witnesses')


if __name__ == '__main__':
    main()
