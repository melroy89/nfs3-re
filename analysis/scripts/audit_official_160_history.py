"""Pin author-hosted v1.6.0 and final v1.6.1 members; never execute them."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    archives = {
        '1.6.0': ('history/nfs3_modern_patch_v1.6.0.7z',
                  '9e1bb8f034026f6f2641417d59f46203f787771394767ca4c6ae4474e4324bb8',
                  'https://veg.by/files/nfs3/nfs3_modern_patch_v1.6.0.7z'),
        '1.6.1': ('nfs3_modern_patch.7z',
                  'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3',
                  'https://veg.by/files/nfs3/nfs3_modern_patch.7z')}
    result = {'kind': 'official-160-161-artifact-baseline', 'packages': {},
              'limits': ['Author-hosted bytes and internal version banners, not publisher-signature verification.',
                         'Member identity/export metadata only; no function correspondence or historical feature qualification.',
                         'No DLL loading, installation, game execution, compilation or database mutation.']}
    for version, (relative, expected, url) in archives.items():
        archive = ROOT / 'analysis/captures/modern-differences/upstream' / relative
        assert digest(archive.read_bytes()) == expected
        readme = subprocess.check_output(['7z', 'x', '-so', str(archive), 'readme_en.txt'])
        banner = readme.splitlines()[0].decode('ascii')
        assert banner.startswith('Need For Speed III Modern Patch v' + version + ' ')
        rows = []
        for member in ('nfs3.exe', 'drivers/dx6/dx6a.dll', 'drivers/dx7/dx7a.dll', 'drivers/dx8/dx8a.dll'):
            raw = subprocess.check_output(['7z', 'x', '-so', str(archive), member])
            pe = pefile.PE(data=raw)
            export_directory = getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None)
            exports = [{'name': e.name.decode('ascii'), 'rva': f'{e.address:08x}'}
                       for e in (export_directory.symbols if export_directory else [])
                       if e.name]
            rows.append({'member': member, 'bytes': len(raw), 'sha256': digest(raw),
                         'image_base': f'{pe.OPTIONAL_HEADER.ImageBase:08x}',
                         'named_exports': exports})
        result['packages'][version] = {'url': url, 'archive_path': str(archive.relative_to(ROOT)),
            'archive_bytes': archive.stat().st_size, 'archive_sha256': expected,
            'readme_sha256': digest(readme), 'readme_banner': banner, 'members': rows}
    result['member_identity_comparison'] = [
        {'member': a['member'], 'identical_bytes_by_sha256': a['sha256'] == b['sha256'],
         'older_bytes': a['bytes'], 'newer_bytes': b['bytes']}
        for a, b in zip(result['packages']['1.6.0']['members'], result['packages']['1.6.1']['members'])]
    (ROOT / 'analysis/evidence/audits/official-160-161-baseline.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: two pinned packages, matching version banners and four members per package')


if __name__ == '__main__':
    main()
