"""Retain static instruction witnesses for the two hash-pinned THRASH loaders.

Does not execute target instructions or change an executable/Ghidra database.
Requires pefile and GNU objdump. Modern's export table is data, not code.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / 'analysis/captures/modern-differences/thrash-loader'
SPECS = {
    'original': ('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3_org.exe',
                 'b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b',
                 [(0x4f8390, 0x4f8793)]),
    'official_modern': ('analysis/captures/modern-differences/upstream/package/nfs3.exe',
                        '240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6',
                        [(0x4f84a8, 0x4f853b), (0x4b5844, 0x4b5a3c), (0x4f1ed4, 0x4f1ef3), (0x4b5a58, 0x4b5a92)]),
}


def main():
    import pefile
    CAPTURE.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-dual-binary-instruction-witness', 'binaries': {},
              'limits': ['No target execution or renderer DLL validation.',
                         'Release-to-release introduction dates not verified.',
                         'Modern export-table addresses are data, not instructions.']}
    for label, (relative, expected, spans) in SPECS.items():
        path = ROOT / relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected, relative
        pe = pefile.PE(data=raw)
        base = pe.OPTIONAL_HEADER.ImageBase
        captures = []
        for start, end in spans:
            data = pe.get_data(start-base, end-start)
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                    f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = CAPTURE / f'{label}-{start:08x}.asm'
            output.write_text(text)
            captures.append({'start': f'{start:08x}', 'exclusive_end': f'{end:08x}',
                             'bytes_sha256': hashlib.sha256(data).hexdigest(),
                             'assembly': str(output.relative_to(ROOT)),
                             'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'ranges': captures}
        if label == 'official_modern':
            assert pe.get_data(0xb5a58,20).hex() == '60e8e6fdffff85c0750ab8a4d15300e8a0fcffff'
            assert pe.get_string_at_rva(0x13d1a4) == b'The thrash driver is not found.'
            assert pe.get_string_at_rva(0x13d1c4) == b'Cannot load the thrash driver.'
            result['missing_driver_diagnostic'] = {
                'sequence':'004b5a58..004b5a6c',
                'gate':'004b5844 returns0 -> message0053d1a4 ->004b570c at004b5a67',
                'message':'The thrash driver is not found.',
                'distinct_load_failure_message':'0053d1c4: Cannot load the thrash driver.',
                'limits':'Configuration/file admission failures share missing-driver wording; no actual dialog or filesystem/API execution.'}
            assert pe.get_string_at_rva(0x53f78c-base) == b'KERNEL32.DLL'
            assert pe.get_string_at_rva(0x53f7b4-base) == b'SetDllDirectoryA'
            assert pe.get_data(0x4f1ed4-base,31) == bytes.fromhex(
                '53515289c3b88cf75300bab4f75300e8d4ffffff85c0740353ffd05a595bc3')
            assert pe.get_data(0x4b58b5-base,10) == bytes.fromhex('b830397a00e815c60300')
            result['modern_dll_directory_contract'] = {
                'entry': '004f1ed4', 'directory_argument': 'EAX, supplied as007a3930 at004b58b5',
                'module': 'KERNEL32.DLL', 'export': 'SetDllDirectoryA',
                'preserved_registers': ['EBX','ECX','EDX'],
                'return': 'zero if unresolved; otherwise raw export EAX; caller ignores it',
                'limits': ['No OS-version acceptance or wrapper DLL execution.',
                           'All renderer-specific dependency lookup outcomes remain unverified.']}
            table = []
            for va in range(0x4f8390, 0x4f84a0, 8):
                name, slot = struct.unpack('<II', pe.get_data(va-base, 8))
                value = pe.get_data(name-base, 96).split(b'\0')[0].decode('ascii')
                assert value.startswith('_THRASH_')
                table.append({'table_va': f'{va:08x}', 'export': value,
                              'name_va': f'{name:08x}', 'slot_va': f'{slot:08x}'})
            assert pe.get_data(0x4f84a0-base, 4) == b'\0'*4
            result['modern_export_table'] = table
            literals = {}
            for va, expected_text in ((0x53f61c,'ThrashDriver'),(0x53f70c,'THRASH'),
                                      (0x53f71c,'Type'),(0x53f724,'FogSupport')):
                value = pe.get_string_at_rva(va-base).decode('ascii')
                assert value == expected_text
                literals[f'{va:08x}'] = value
            for va, encoded in ((0x4b593e,'6a00'), (0x4b594a,'ff1574465300'),
                                (0x4b5965,'b001eb0a'), (0x4b598c,'ff1570465300')):
                assert pe.get_data(va-base,len(bytes.fromhex(encoded))).hex() == encoded
            lower_bytes = bytes.fromhex('83f8417c0883f85a7f0383c020c3')
            assert pe.get_data(0x4f0ae0-base,len(lower_bytes)) == lower_bytes
            result['modern_type_and_capability_contract'] = {
                'ascii_lower_helper': {'start': '004f0ae0', 'end_exclusive': '004f0aee', 'hex': lower_bytes.hex()},
                'literals': literals, 'type_default_argument': 0,
                'type_first_byte_mapping': {'d': 64, 'v': 16, 's': 2, 'other_including_zero': 1},
                'fog_default': 0, 'fog_normalization': 'nonzero result becomes1',
                'limits': ['Empty returned Type follows generic mask1; no complete string enum/mandatory Type validation shown.',
                           'Final key is ThrashDriver; historical release wording VideoDriver is not the final parser literal.',
                           'LightBeams and complete driver lifetime not established by this parser witness.']}

        else:
            # Track each explicit name PUSH to its following GetProcAddress,
            # then the EAX store. Reject incomplete/duplicate recovered bindings.
            text = (CAPTURE/'original-004f8390.asm').read_text()
            pending = None
            resolved = None
            bindings = []
            for line in text.splitlines():
                match = re.search(r'push\s+0x([0-9a-f]+)', line)
                if match:
                    va = int(match[1], 16)
                    if 0x54d3a4 <= va <= 0x54d664:
                        pending = pe.get_data(va-base, 96).split(b'\0')[0].decode('ascii')
                if 'call' in line and '0x534558' in line:
                    assert pending is not None
                    resolved, pending = pending, None
                match = re.search(r'mov\s+(?:DWORD PTR )?ds:0x([0-9a-f]+),eax', line)
                if match and resolved:
                    bindings.append({'export': resolved, 'slot_va': f'{int(match[1],16):08x}'})
                    resolved = None
            assert len(bindings) == 34 and len({b['export'] for b in bindings}) == 34
            result['original_explicit_bindings'] = bindings
    old = {b['export']: b['slot_va'] for b in result['original_explicit_bindings']}
    new = {b['export']: b['slot_va'] for b in result['modern_export_table']}
    result['all_34_export_names_and_slots_match'] = old == new
    assert old == new
    output = ROOT/'analysis/evidence/audits/original-modern-thrash-loader.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: input hashes, 34 identical name/slot bindings, instruction captures')


if __name__ == '__main__':
    main()
