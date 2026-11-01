"""Bounded static resource/version-header producer audit; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-startup-version-header', 'binaries': {},
              'limits': ['No target or Windows API execution.',
                         'Malformed/overflow inputs, runtime resource selection and later writers remain unqualified.']}
    capture = ROOT/'analysis/captures/modern-differences/startup-version-header'
    capture.mkdir(parents=True, exist_ok=True)
    for label in ('original', 'official_modern'):
        relative, expected, _ = SPECS[label]
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        row = {'path': relative, 'sha256': expected, 'spans': []}
        for start, end in [(0x4a38f0, 0x4a39d2), (0x4a3a56, 0x4a3ab9), (0x4f04f0, 0x4f0569),
                           (0x50c640, 0x50ca08), (0x50d0f0, 0x50d55e),
                           (0x4e0e30, 0x4e0e59)]:
            output = capture/f'{label}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            row['spans'].append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        row['static_version_imports'] = [
            {'dll': d.dll.decode(), 'name': i.name.decode(), 'iat': f'{i.address:08x}'}
            for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
            if i.name and i.name in (b'GetFileVersionInfoA', b'GetFileVersionInfoSizeA', b'VerQueryValueA')]
        if label == 'original':
            assert pe.get_string_at_rva(0xa2f50) == b'nfs3.exe'
            assert pe.get_string_at_rva(0x13ce2c) == b'\\StringFileInfo\\040904b0\\FileVersion'
            assert pe.get_string_at_rva(0x13ce68) == b'%d, %d.%d'
            tables = [t.entries for group in pe.FileInfo for info in group
                      for t in getattr(info, 'StringTable', [])]
            assert any(t.get(b'FileVersion') == b'27, 2.0' for t in tables)
            assert pe.get_data(0xa3a7f,10).hex() == '68bae8550068b8e85500'
            assert pe.get_data(0xa3a97,5).hex() == 'e8acca0400'
            assert pe.get_data(0x15e898,32) == bytes(32)
            assert pe.get_data(0x15e8b8,8) == bytes(8)
            imports = {i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
            row['version_imports'] = {f'{a:08x}':imports[a] for a in (0x534674,0x534678,0x53467c)}
            assert list(row['version_imports'].values()) == ['GetFileVersionInfoA','GetFileVersionInfoSizeA','VerQueryValueA']
            assert pe.get_data(0x10c7c4,16).hex() == 'b901000000bb0a0000008d54240489f0'
            assert pe.get_data(0x10c91c,6).hex() == '80e603887710'
            assert pe.get_data(0x10d4e2,5).hex() == 'f6c6107412'
            assert pe.get_data(0x10d500,3).hex() == '268918'
            assert pe.get_data(0xe0e30,0x29).hex() == '515689c685db740f803a00740a408a0a428848ff4b75f131d285db7407404b8850ffebf589f05e59c3'
            assert pe.get_data(0xa3a9f,4).hex() == '85c07516'
            assert pe.get_data(0x10c8f2,5).hex() == 'b8ffffffff'
            row['reader_failure_and_copy'] = {
                'failure_return': '0 for zero size after retry, allocationNULL, data/query failure or zero queriedlength',
                'cleanup': 'Allocated buffer reaches004f79f0 on data/query failure and success',
                'success_flag': 'Set1 at004a39ac before copy; no parse validation in reader',
                'copy': '004e0e30 copies until sourceNUL or count exhausted, then zero-pads remainingcount; no extra terminator',
                'count': 'unsignedmin(queriedlength,31) at startup',
                'termination_condition': 'Byte0055e8b7 untouched by atmost31-byte copy, initiallyzero; valid terminator if not altered elsewhere',
                'scanner_gate': '004a3a9f testszero only; nonzero includes partial counts1/2 and scanner EOFreturnffffffff',
                'limits': 'No API failure injection, source pointer validation, real malformed-resource run or full scanner error contract'}
            row['scanner_contract'] = {
                'wrapper_chain': '004f0548 ->004f0520 ->0050c650',
                'format_flags': '0050c904 resets flags to low two bits; plain d has no h/l/L/I64 modifier',
                'decimal_dispatch': '0050c7c4 selects signed base10 ->0050d0f0',
                'accumulation': '0050d35f..0050d38e uses32-bit multiply/add',
                'ordinary_store': '0050d4cd..0050d503 consumes next pointer and storesDWORD at0050d500; h selectsWORD separately',
                'successful_conversion_values': [27, 2, 0],
                'conditional_template_hex': '0200000000000000',
                'conditions': 'All three conversions succeed for27,2.0; last two template bytes retain initialzero; no later writes',
                'modern_header_consequence': 'Low versionWORD2 fails minimum6 and takes grouped reset'}
            row['producer'] = {'reader': '004a38f0..004a39d2',
                'seed_filename': 'nfs3.exe; on initial size-query failure, retry current module filename',
                'query': '\\StringFileInfo\\040904b0\\FileVersion',
                'resource_value': '27, 2.0', 'destination': '0055e898', 'copy_limit': 31,
                'scanner_call': '004a3a97 ->004f0548', 'format': '%d, %d.%d',
                'destinations_in_order': ['local EBP-10h','0055e8b8','0055e8ba'],
                'return_gate': 'Rejects zero conversion result, not an explicit three-conversion check'}
        else:
            assert not row['static_version_imports']
            assert all(d.dll.lower() != b'version.dll' for d in pe.DIRECTORY_ENTRY_IMPORT)
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
