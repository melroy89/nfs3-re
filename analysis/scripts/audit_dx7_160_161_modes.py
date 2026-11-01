"""Static historical DX7 mode policy comparison; no DLL execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def main():
    baseline = json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())
    capture = ROOT/'analysis/captures/modern-differences/dx7-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-dx7-160-161-mode-policy', 'range_end': 'exclusive', 'versions': {}}
    images = {}
    for version in ('1.6.0', '1.6.1'):
        package = baseline['packages'][version]
        archive = ROOT/package['archive_path']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == package['archive_sha256']
        member = 'drivers/dx7/dx7a.dll'
        raw = subprocess.check_output(['7z','x','-so',str(archive),member])
        expected = next(row for row in package['members'] if row['member'] == member)
        assert hashlib.sha256(raw).hexdigest() == expected['sha256']
        pe = pefile.PE(data=raw); images[version] = pe
        binary = capture/f'dx7-{version}.dll'; binary.write_bytes(raw)
        pointer_site = 0x1161 if version == '1.6.0' else 0x1150
        assert pe.get_data(pointer_site,10).hex() == 'c70500c80f6050720160'
        spans = ([(0x60002544,0x600025a7),(0x60002710,0x600027d5)] if version == '1.6.0'
                 else [(0x60002578,0x600025ec),(0x600025ec,0x600026d2),(0x600026d4,0x6000276d)])
        spans += [(0x60000000+pointer_site,0x60000000+pointer_site+10)]
        rows = []
        for start,end in spans:
            body = pe.get_data(start-0x60000000,end-start)
            output = capture/f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                         'sha256':hashlib.sha256(body).hexdigest(), 'assembly':str(output.relative_to(ROOT)),
                         'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        result['versions'][version] = {'archive_sha256':package['archive_sha256'],
            'member':member,'sha256':expected['sha256'],'spans':rows}
    old,new = images['1.6.0'],images['1.6.1']
    for offset,value in ((0x28,640),(0x2c,480),(0x30,16),(0x34,4),(0x38,1),(0x3c,3),(0x40,2)):
        at = 0x2555 + ((offset-0x28)//4)*7
        assert old.get_data(at,7) == b'\xc7\x42'+bytes([offset])+value.to_bytes(4,'little')
    assert old.get_data(0x2586,10).hex() == 'c705fcc70f6002000000'
    assert old.get_data(0x2765,14).hex() == '390775e7395f0475e2394f0875dd'
    assert new.get_data(0x25b2,25).hex() == 'b9e803000031c08b3d00c80f60f3abc705fcc70f6000000000'
    assert new.get_data(0x26fe,15).hex() == 'b903000000f3a77444770489c2ebda'
    result['paired_mechanisms'] = {
        'table_identity':'Both about exports publish60017250 through600fc800; candidate records use28h stride.',
        'older_seed':'Writes640/480/16 at table+28/+2c/+30 before interface enumeration; count initialized2 including reserved index0.',
        'newer_seed':'Zero table/count; only reviewed admitted callback candidates inserted, then reserved-index count increment.',
        'older_order':'Callback scans existing records for exact width/height/input-depth match or first empty record; new records append in arrival order.',
        'newer_order':'Binary unsigned lexicographic width/height/resulting-depth insertion with shifting; equal-key metadata replaced.'}
    result['limits'] = ['Author-hosted1.6.0/1.6.1 DLL pair, not original retail EXE/DLL correspondence.',
        'Older seed is a bounded setup witness; callbacks and newer insertion are complete captured bodies.',
        'No full API support guarantee, later-writer exclusion, display enumeration or rendered outcome tested.',
        'No DLL loading or executable/database mutation.']
    (ROOT/'analysis/evidence/audits/dx7-160-161-mode-policy.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned historical DX7 pair, removed fixed mode seed and changed insertion policy')


if __name__ == '__main__':
    main()
