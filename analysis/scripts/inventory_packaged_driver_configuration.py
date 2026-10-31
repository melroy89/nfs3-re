"""Inventory final-package driver settings and bounded literal searches, without loading code."""
import configparser
import hashlib
import json
import subprocess
from audit_thrash_loader_difference import ROOT


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    archive = ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    wanted = 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    assert digest(archive.read_bytes()) == wanted
    listing = subprocess.check_output(['7z','l','-slt',str(archive)], text=True)
    names = [line[7:] for line in listing.splitlines() if line.startswith('Path = ')]
    members = sorted(name for name in names if name.lower().endswith(('.exe','.dll','.ini')))
    assert len(members) == 22
    rows = []
    for name in members:
        raw = subprocess.check_output(['7z','x','-so',str(archive),name])
        searches = {}
        for literal in ('LightBeams','FogSupport','ThrashDriver','VideoDriver'):
            searches[literal] = {}
            for encoding in ('ascii','utf-16le'):
                needle = literal.lower().encode(encoding)
                haystack = raw.lower()
                offsets = []
                start = 0
                while (start := haystack.find(needle,start)) != -1:
                    offsets.append(start)
                    start += 1
                searches[literal][encoding] = offsets
        row = {'member': name, 'bytes': len(raw), 'sha256': digest(raw), 'literal_file_offsets': searches}
        if name.lower().endswith('.ini'):
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            parser.read_string(raw.decode('utf-8-sig'))
            row['ini_sections'] = {section: dict(parser[section]) for section in parser.sections()}
        rows.append(row)
    assert sum(row['member'].endswith('/thrash.ini') for row in rows) == 8
    assert all(not hits for row in rows for hits in row['literal_file_offsets']['LightBeams'].values())
    assert all(not hits for row in rows for hits in row['literal_file_offsets']['VideoDriver'].values())
    assert next(row for row in rows if row['member']=='nfs3.ini')['ini_sections']['NFS3']['ThrashDriver'] == 'nglide'
    readme = subprocess.check_output(['7z','x','-so',str(archive),'readme_en.txt'])
    assert digest(readme) == '02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d'
    mentions = [{'line': index, 'text': line} for index,line in enumerate(readme.decode('utf-8-sig').splitlines(),1)
                if 'lightbeams' in line.lower()]
    assert [row['line'] for row in mentions] == [403]
    result = {'kind': 'final-package-driver-config-and-literal-inventory', 'archive_sha256': wanted,
        'members': rows, 'historical_readme_lightbeams_mentions': mentions,
        'limits': ['Case-insensitive ASCII/UTF16LE byte searches only; encoded, compressed, constructed and external strings excluded.',
                   'INI bytes are final packaged defaults, not installed user files or effective runtime settings.',
                   'No literal hit is not proof a feature is absent; intermediate release implementation remains unverified.',
                   'No DLL/configuration API or target execution and no reference-file extraction.']}
    (ROOT/'analysis/evidence/audits/packaged-driver-configuration.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 22 pinned package members, eight driver INIs and bounded historical/final literal inventory')


if __name__ == '__main__':
    main()
