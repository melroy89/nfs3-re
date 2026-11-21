"""Compare retained vehicle-effect bodies without executing target instructions."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble

SPANS = [
    ('tagged_effects', 0x4b8740, 0x4b90dc),
    ('part11', 0x4ba960, 0x4baa44),
    ('part10', 0x4baa50, 0x4bab69),
    ('masked_body', 0x4bab70, 0x4badf5),
    ('unmasked_body', 0x4bae00, 0x4bb10f),
    ('part5', 0x4bb110, 0x4bb1ff),
    ('parts_zero_through_four', 0x4bb200, 0x4bb495),
    ('variant_dispatch', 0x4bb4c0, 0x4bb5ce),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    images = {}
    for label in ('original', 'official_modern'):
        path, expected, _ = SPECS[label]
        raw = (ROOT / path).read_bytes()
        assert sha(raw) == expected
        images[label] = (raw, {'path': path, 'sha256': expected})
    for version, (archive_hash, exe_hash) in HISTORY.items():
        path = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT / path).read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(ROOT / path), 'nfs3.exe'])
        assert sha(raw) == exe_hash
        images[version] = (raw, {'archive': path, 'archive_sha256': archive_hash,
                               'member': 'nfs3.exe', 'sha256': exe_hash})
    result = {'kind': 'static-vehicle-effect-body-history', 'baselines': {}, 'ranges': []}
    bodies = {}
    for label, (raw, identity) in images.items():
        pe = pefile.PE(data=raw)
        assert pe.OPTIONAL_HEADER.ImageBase == 0x400000
        result['baselines'][label] = identity
        bodies[label] = {name: pe.get_data(a - 0x400000, b - a) for name, a, b in SPANS}
    for name, start, end in SPANS:
        reference = bodies['original'][name]
        assert len(reference) == end - start
        assert all(body[name] == reference for body in bodies.values())
        decoded = disassemble(reference, start)
        assert '\tret' in decoded[-1], name
        calls = [line for line in decoded if '\tcall ' in line and '0x4b8740' in line]
        result['ranges'].append({'name': name, 'start': f'{start:08x}',
            'end_exclusive': f'{end:08x}', 'bytes': len(reference),
            'sha256_all_four_baselines': sha(reference), 'identical_all_four': True,
            'decoded_direct_calls_to_tagged_helper': calls, 'disassembly': decoded})
    result['total_checked_bytes'] = sum(end - start for _, start, end in SPANS)
    result['limits'] = [
        'Eight selected saved-analysis ranges, not every vehicle/menu/renderer routine.',
        'Body identity does not imply identical inputs, globals, pointed-to data, callees or FPU state.',
        'Decoded direct calls within these ranges are not a complete incoming-reference census.',
        'No proof these paths implement the vendor taillight-colour claim or of rendered equivalence.',
        'Ranges end immediately after the checked terminal RET; this is not an independent CFG completeness proof.',
        'No game, DLL, target instructions, compiler or Ghidra writes executed.',
    ]
    (ROOT / 'analysis/evidence/audits/vehicle-effect-body-history.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(f"PASS: eight selected ranges, {result['total_checked_bytes']} bytes identical in four baselines")


if __name__ == '__main__':
    main()
