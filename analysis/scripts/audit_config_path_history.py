"""Pin the historical config-prefix transition without file/API execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    specs = {
        '1.1.0': ('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac',
                  '59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72',
                  'readme-en.txt', 'Need For Speed III Widescreen Patch v1.1.0', 0x4a6f0c, 0x4a6f2d),
        '1.2.0': ('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b',
                  '4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003',
                  'readme_en.txt', 'Need For Speed III Modern Patch v1.2.0', 0x4a6f04, 0x4a6f6e),
    }
    capture = ROOT/'analysis/captures/modern-differences/config-path-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'historical-config-path-transition', 'versions': {},
        'limits': ['Author-hosted artifacts and internal banners, not signature verification.',
                   'Default initialization and formatting dataflow only; later writers/CWD and actual I/O unobserved.',
                   'v1.0.0 introduction and supplied-original prefix producer not established.']}
    for version, (archive_hash, exe_hash, member, banner_prefix, start, end) in specs.items():
        name = f'nfs3_modern_patch_v{version}.7z'
        archive = ROOT/'analysis/captures/modern-differences/upstream/history'/name
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        assert sha(raw) == exe_hash
        readme = subprocess.check_output(['7z', 'x', '-so', str(archive), member])
        banner = readme.splitlines()[0].decode('ascii')
        assert banner.startswith(banner_prefix+' ')
        binary = capture/f'nfs3-{version}.exe'
        binary.write_bytes(raw)
        pe = pefile.PE(data=raw)
        strings = pe.get_data(0x13ec2c, 1400).split(b'\0')[:24]
        assert len(strings) == 24 and all(strings)
        assert strings[17] == (b'.\\' if version == '1.1.0' else b'.\\FeData\\Config\\')
        assert pe.get_data(start-0x400000,12) == bytes.fromhex('31c9be2cec5300bab4277a00')
        assert pe.get_data(start-0x400000+12,20).hex() == '89d7acaa84c075fa4181c28000000083f9187cec'
        call = pe.get_data(0xa6e36,5)
        assert call[0] == 0xe8 and 0x4a6e3b+struct.unpack('<i',call[1:])[0] == start
        assert pe.get_string_at_rva(0x13b00c) == b'%sconfig.dat'
        spans = []
        for first, stop in [(start,end),(0x4a6e36,0x4a6e3b),
                            (0x472820,0x4728d3),(0x4729aa,0x4729c3)]:
            output = capture/f'{version}-{first:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={first}',f'--stop-address={stop}',str(binary.relative_to(ROOT))],cwd=ROOT))
            spans.append({'start':f'{first:08x}','end_exclusive':f'{stop:08x}',
                'bytes_sha256':sha(pe.get_data(first-0x400000,stop-first)),
                'assembly':str(output.relative_to(ROOT)),'assembly_sha256':sha(output.read_bytes())})
        result['versions'][version] = {'url':'https://veg.by/files/nfs3/'+name,
            'archive':str(archive.relative_to(ROOT)),'archive_sha256':archive_hash,
            'executable_sha256':exe_hash,'readme_member':member,'readme_banner':banner,
            'readme_sha256':sha(readme),'path_source':'0053ec2c','slot_stride':128,
            'default_slots':[{'index':i,'destination':f'{0x7a27b4+128*i:08x}',
                              'value':s.decode('ascii')} for i,s in enumerate(strings)],
            'config_prefix':'007a3034','derived_default_config_path':strings[17].decode('ascii')+'config.dat',
            'spans':spans}
    (ROOT/'analysis/evidence/audits/config-path-110-120.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.1.0/1.2.0 path-slot initialization; config prefix changes from root-relative to FeData/Config')


if __name__ == '__main__':
    main()
