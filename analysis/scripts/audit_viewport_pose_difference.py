"""Static viewport camera-selection comparison; no target execution."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-viewport-pose-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No camera/game execution.', 'Normal-return restoration only; no synchronization proved.']}
    capture = ROOT/'analysis/captures/modern-differences/viewport-pose'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        spans = [(0x4228e0, 0x4229bb if label == 'original' else 0x4229b9), (0x422850, 0x4228df)]
        spans += [(0x42387c, 0x4238a5), (0x421708, 0x42172c)]
        spans += [(0x4223c0, 0x422512), (0x422520, 0x422604)]
        if label == 'original':
            spans += [(0x42649c, 0x4264be), (0x4264c0, 0x4264ec)]
        if label == 'official_modern':
            spans += [(0x42649c, 0x4264be), (0x4264c0, 0x4264ec),
                      (0x472298, 0x4722ab), (0x45da2d, 0x45da37)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}',
                f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    assert result['binaries']['original']['spans'][1]['bytes_sha256'] == result['binaries']['official_modern']['spans'][1]['bytes_sha256']
    result['pose_finalizer_identical'] = True
    modern = pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    result['snapshot_call_targets'] = {}
    for site, target in ((0x42389a, 0x42649c), (0x421718, 0x4264c0)):
        data = modern.get_data(site-0x400000, 5)
        assert data[0] == 0xe8 and site+5+int.from_bytes(data[1:], 'little', signed=True) == target
        result['snapshot_call_targets'][f'{site:08x}'] = f'{target:08x}'
    result['identical_pose_callees'] = []
    for index in (4, 5):
        pair = [result['binaries'][k]['spans'][index] for k in ('original', 'official_modern')]
        assert pair[0]['bytes_sha256'] == pair[1]['bytes_sha256']
        result['identical_pose_callees'].append(pair[0]['start'])
    pe=pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    words=struct.unpack('<5I',pe.get_data(0x556550-0x400000,20))
    assert words==(0x53772c,0x5563aa,0,0,0x6fd1cc)
    assert pe.get_data(0x53772c-0x400000,16).split(b'\0')[0]==b'rearcamera'
    choices=struct.unpack('<3H',pe.get_data(0x5563aa-0x400000,6));assert choices==(1939,1940,0)
    labels={}
    for ident,expected in [(1938,'Rear View From'),(1939,'Active Camera'),(1940,'In Car Camera')]:
        offset=struct.unpack('<I',pe.get_data(0x53d310-0x400000+4*(ident-0x788),4))[0]
        value=pe.get_data(0x53d310-0x400000+offset,80).split(b'\0')[0].decode('ascii')
        assert value==expected;labels[str(ident)]=value
    result['modern_rear_camera_binding']={'descriptor':'00556550',
        'words':[f'{w:08x}' for w in words],'name':'rearcamera','selection_cell':'006fd1cc',
        'choice_ids':list(choices),'embedded_fallback_labels':labels,
        'limit':'Names identify authored choices, not observed camera pose or complete input dispatch.'}
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    result['rear_camera_menu_assets']={}
    for name,relative in [
        ('official_modern','analysis/captures/modern-differences/upstream/package/fedata/menus/camera.mnu'),
        ('uppercase_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/CAMERA.MNU')]:
        data=(ROOT/relative).read_bytes()
        if name=='official_modern':assert data==subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/camera.mnu'])
        sections=[];current=None
        for line in data.decode('latin1').splitlines():
            if line.startswith('['):
                current={'section':line.strip('[]'),'fields':{}};sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);current['fields'][key]=value
        selected=[s for s in sections if s['fields'].get('listname')=='rearcamera']
        assert len(selected)==(2 if name=='official_modern' else 0)
        result['rear_camera_menu_assets'][name]={'path':relative,'sha256':hashlib.sha256(data).hexdigest(),
            'items':selected,'provenance':'Pinned archive member' if name=='official_modern' else 'Local backup, not authenticated as retail or paired to supplied original executable'}
    (ROOT/'analysis/evidence/audits/original-modern-viewport-pose.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete wrapper bodies and identical pose finalizer')


if __name__ == '__main__':
    main()
