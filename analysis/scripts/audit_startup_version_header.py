"""Bounded static resource/version-header producer audit; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-startup-version-header', 'binaries': {},
              'limits': ['No target or Windows API execution.',
                         'Scanner conversion widths, overlapping writes, failures and later writers remain unqualified.']}
    capture = ROOT/'analysis/captures/modern-differences/startup-version-header'
    capture.mkdir(parents=True, exist_ok=True)
    for label in ('original', 'official_modern'):
        relative, expected, _ = SPECS[label]
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        row = {'path': relative, 'sha256': expected, 'spans': []}
        for start, end in [(0x4a38f0, 0x4a39d2), (0x4a3a56, 0x4a3ab9)]:
            output = capture/f'{label}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            row['spans'].append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        if label == 'original':
            assert pe.get_string_at_rva(0xa2f50) == b'nfs3.exe'
            assert pe.get_string_at_rva(0x13ce2c) == b'\\StringFileInfo\\040904b0\\FileVersion'
            assert pe.get_string_at_rva(0x13ce68) == b'%d, %d.%d'
            tables = [t.entries for group in pe.FileInfo for info in group
                      for t in getattr(info, 'StringTable', [])]
            assert any(t.get(b'FileVersion') == b'27, 2.0' for t in tables)
            assert pe.get_data(0xa3a7f,10).hex() == '68bae8550068b8e85500'
            assert pe.get_data(0xa3a97,5).hex() == 'e8acca0400'
            assert pe.get_data(0x15e8b8,8) == bytes(8)
            imports = {i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
            row['version_imports'] = {f'{a:08x}':imports[a] for a in (0x534674,0x534678,0x53467c)}
            assert list(row['version_imports'].values()) == ['GetFileVersionInfoA','GetFileVersionInfoSizeA','VerQueryValueA']
            row['producer'] = {'reader': '004a38f0..004a39d2',
                'seed_filename': 'nfs3.exe; on initial size-query failure, retry current module filename',
                'query': '\\StringFileInfo\\040904b0\\FileVersion',
                'resource_value': '27, 2.0', 'destination': '0055e898', 'copy_limit': 31,
                'scanner_call': '004a3a97 ->004f0548', 'format': '%d, %d.%d',
                'destinations_in_order': ['local EBP-10h','0055e8b8','0055e8ba'],
                'return_gate': 'Rejects zero conversion result, not an explicit three-conversion check'}
        else:
            assert pe.get_string_at_rva(0x15e898) == b'27, 2.0'
            assert pe.get_data(0x15e8a0,12).hex() == 'f02000000600000000000000'
            assert pe.get_data(0xa3a56,0x63) == b'\x90'*0x63
            row['replacement'] = 'Startup reader/scan callsite removed; file-backed string and size20f0/version6/zero template.'
        result['binaries'][label] = row
    output = ROOT/'analysis/evidence/audits/startup-version-header.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baseline identities, original resource/parse destinations, Modern removal/template')


if __name__ == '__main__':
    main()
