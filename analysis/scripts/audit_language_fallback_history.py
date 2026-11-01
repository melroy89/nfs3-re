"""Compare author-hosted 1.5.0 through 1.5.3 fallback tables statically."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


PACKAGES = {
    '1.5.0': ('de6cbbbce4b77765f96472aaf8c12a4e245e2abceaf26dd9b84215442b1f4a0f',
              'd9db8ead63a9697c4c6c3933e720cd93565f67bd4b264e8bbc0d98d03c236dae', 0x78f),
    '1.5.1': ('c7b66da29ef8cd58c56e27a403bd2889d8a4f0f7cac0873c28a1b4b5a09723de',
              '4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17', 0x794),
    '1.5.2': ('23830061e5ed489900b03c98d81727d951c59e9247d7006803460d38ee9a34cd',
              'd532b0252610d9de2e826efc399d4d733d84d4758e47b5fadc94bf5c1d4449bb', 0x794),
    '1.5.3': ('0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64',
              '07e987193ebeb4b30ac3912f90d8b98f2a34b37632dbad232ecfcea12fdb7c0a', 0x79a),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    history = ROOT / 'analysis/captures/modern-differences/upstream/history'
    capture = ROOT / 'analysis/captures/modern-differences/language-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'historical-language-fallback-static-comparison', 'packages': {},
              'limits': ['Author-hosted identities/internal banners, not publisher signatures.',
                         'Conditional lookup derivation, no target instructions or language loading.',
                         'No observed crash, localization rendering or complete consumer coverage.']}
    bodies = {}
    for version, (archive_hash, exe_hash, upper) in PACKAGES.items():
        name = f'nfs3_modern_patch_v{version}.7z'
        archive = history / name
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        assert sha(raw) == exe_hash
        readme = subprocess.check_output(['7z', 'x', '-so', str(archive), 'readme_en.txt'])
        banner = readme.splitlines()[0].decode('ascii')
        assert banner.startswith('Need For Speed III Modern Patch v' + version + ' ')
        binary = history / f'nfs3-{version}.exe'
        binary.write_bytes(raw)
        pe = pefile.PE(data=raw)
        assert pe.OPTIONAL_HEADER.ImageBase == 0x400000
        body = pe.get_data(0xd1850, 46)
        assert body[:5] == b'\x3d' + struct.pack('<I', upper)
        assert body[5:].hex() == '7606e854ffffffc3526bd004a1803a56003910770fb894d2530081ea201e00007f0231d20304025ac3'
        bodies[version] = body
        table_rva = 0x13d294
        first = struct.unpack('<I', pe.get_data(table_rva, 4))[0]
        count = first // 4
        assert first % 4 == 0 and count == {'1.5.0': 8, '1.5.1': 9, '1.5.2': 9, '1.5.3': 19}[version]
        entries = []
        for i in range(count):
            offset = struct.unpack('<I', pe.get_data(table_rva + 4*i, 4))[0]
            assert offset >= first
            text = pe.get_data(table_rva + offset, 512).split(b'\0')[0].decode('latin-1')
            entries.append({'id': 1928+i, 'relative_offset': offset, 'text': text})
        overreads = []
        for identifier in range(1928+count, upper+1):
            index = identifier-1928
            value = struct.unpack('<I', pe.get_data(table_rva+4*index, 4))[0]
            pointer = (0x400000 + table_rva + value) & 0xffffffff
            mapped = any(0x400000+s.VirtualAddress <= pointer <
                         0x400000+s.VirtualAddress+max(s.Misc_VirtualSize, s.SizeOfRawData)
                         for s in pe.sections)
            assert not mapped
            overreads.append({'id': identifier, 'fallback_index': index,
                              'word_read': f'{value:08x}', 'returned_pointer': f'{pointer:08x}',
                              'inside_any_pe_section': mapped})
        spans = []
        for start, end in [(0x4d1750, 0x4d17ae), (0x4d1850, 0x4d187e)]:
            output = capture / f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', str(binary.relative_to(ROOT))], cwd=ROOT))
            spans.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                          'bytes_sha256': sha(pe.get_data(start-0x400000, end-start)),
                          'assembly': str(output.relative_to(ROOT)), 'assembly_sha256': sha(output.read_bytes())})
        result['packages'][version] = {'url': 'https://veg.by/files/nfs3/'+name,
            'archive': str(archive.relative_to(ROOT)), 'archive_sha256': archive_hash,
            'executable_sha256': exe_hash, 'executable_bytes': len(raw),
            'readme_banner': banner, 'readme_sha256': sha(readme),
            'lookup_upper_id': upper, 'fallback_base': '0053d294',
            'offset_table_bytes': first, 'fallback_entries': entries,
            'conditional_fallback_overreads': overreads, 'spans': spans}
    assert len(result['packages']['1.5.1']['conditional_fallback_overreads']) == 4
    assert len(result['packages']['1.5.2']['conditional_fallback_overreads']) == 4
    assert not result['packages']['1.5.0']['conditional_fallback_overreads']
    assert not result['packages']['1.5.3']['conditional_fallback_overreads']
    assert bodies['1.5.1'][5:] == bodies['1.5.2'][5:] == bodies['1.5.3'][5:] == bodies['1.5.0'][5:]
    result['lookup_difference'] = 'Only the upper-ID immediate changes in the complete 46-byte lookup body.'
    (ROOT / 'analysis/evidence/audits/language-fallback-history.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: four historical identities; 1.5.1/1.5.2 admit four entries beyond the fallback table; 1.5.3 covers its range')


if __name__ == '__main__':
    main()
