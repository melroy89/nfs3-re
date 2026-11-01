"""Compare bounded static control-instruction inventories in four pinned DLL pairs."""
import json
import re
import subprocess
import tempfile
import pefile
from audit_dx5_reference_final import sha
from audit_thrash_loader_difference import ROOT


def main():
    archives = {
        'reference': ('analysis/captures/modern-differences/upstream/history/nfs3_orig.7z',
                      '374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'),
        'final': ('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z',
                  'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3')}
    specs = [
        ('dx5', 'd3da.dll', 'ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02',
         'drivers/dx5/dx5a.dll', '6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42', 31),
        ('software', 'softtria.dll', '8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02',
         'drivers/softtri/softtria.dll', '9479203471f4dd615788769bac365043d903505af370c48df69e5d6a1e6f8732', 23),
        ('sound', 'eacsnd.dll', '30288653eb2e0b59a3173530433a4adb8ea0dc66cdbc46aadf742dc53ab62b46',
         'eacsnd.dll', '63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3', 20),
        ('glide', 'voodoo2a.dll', '99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b',
         'drivers/glide3x/voodoo2a.dll', 'f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b', 28)]
    for path, expected in archives.values():
        assert sha((ROOT/path).read_bytes()) == expected
    pattern = re.compile(r'\b(fldcw|fnstcw|fstcw|fninit|finit)\b')
    extended = re.compile(r'\b(fldenv|fnstenv|fstenv|frstor|fnsave|fsave|fxrstor|fxsave|ldmxcsr|stmxcsr)\b')
    result = {'kind': 'four-paired-DLL-control-site-comparison', 'archives': archives, 'pairs': []}
    for label, old_member, old_hash, new_member, new_hash, expected_count in specs:
        versions = []
        for role, member, expected in [('reference', old_member, old_hash), ('final', new_member, new_hash)]:
            raw = subprocess.check_output(['7z', 'x', '-so', str(ROOT/archives[role][0]), member])
            assert sha(raw) == expected
            pe = pefile.PE(data=raw)
            base = pe.OPTIONAL_HEADER.ImageBase
            with tempfile.NamedTemporaryFile(suffix='.dll') as f:
                f.write(raw)
                f.flush()
                asm = subprocess.check_output(['objdump', '-d', '-Mintel', f.name], text=True)
            groups = {'primary': [], 'environment_state': []}
            for line in asm.splitlines():
                group = 'primary' if pattern.search(line) else 'environment_state' if extended.search(line) else None
                if group is None:
                    continue
                match = re.match(r'^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\s*(.*)$', line)
                assert match, line
                va = int(match[1], 16)
                code = bytes.fromhex(match[2])
                assert pe.get_data(va-base, len(code)) == code
                context = pe.get_data(va-base-32, 64+len(code))
                groups[group].append({'va': f'{va:08x}', 'encoding': code.hex(),
                    'instruction': match[3].strip(), 'context_start_va': f'{va-32:08x}',
                    'context_bytes': len(context), 'context_sha256': sha(context)})
            versions.append({'role': role, 'member': member, 'sha256': expected,
                             'bytes': len(raw), 'image_base': f'{base:08x}', 'groups': groups})
        assert len(versions[0]['groups']['primary']) == len(versions[1]['groups']['primary']) == expected_count
        assert versions[0]['groups'] == versions[1]['groups']
        result['pairs'].append({'label': label, 'primary_candidate_count': expected_count,
            'environment_candidate_count': len(versions[0]['groups']['environment_state']),
            'site_and_context_comparison': 'identical', 'versions': versions})
    result['primary_total_per_side'] = sum(row['primary_candidate_count'] for row in result['pairs'])
    assert result['primary_total_per_side'] == 102
    result['limits'] = [
        'GNU objdump linear decoding candidates, not control-flow/reachability validation of every site.',
        'Contexts cover32 bytes before/after each encoded instruction, not complete functions or all operand producers.',
        'Initial/runtime memory operands and ambient control words are not inferred equal from instruction equality.',
        'Only four author-reference/final pairs; no authenticated pristine retail or all-runtime-component claim.',
        'Imported callees, external threads, generated code and other instructions/indirect state effects remain separate.',
        'No DLL loading, target instructions, instruction probes, reconstruction, compilation or database mutation.']
    (ROOT/'analysis/evidence/audits/paired-dll-x87-sites.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:102 primary control candidates per side across four pairs; identical sites/encodings/short contexts; environment-state candidates also compared')


if __name__ == '__main__':
    main()
