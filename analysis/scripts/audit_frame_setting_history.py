"""Static immediate-release Frame Size descriptor/English-label comparison."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble


def main():
    a=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']['1.5.3']
    b=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())['packages']['1.6.0']
    specs={'1.5.3':(a['archive'],a['archive_sha256'],a['executable_sha256']),
           '1.6.0':(b['archive_path'],b['archive_sha256'],next(x['sha256'] for x in b['members']if x['member']=='nfs3.exe'))}
    result={'kind':'historical-frame-setting-expansion','versions':{},
            'limits':['Selected descriptor and matching English asset only; not every frame consumer or localization.',
                      'No game/menu/viewport execution or visible camera-shift test.']}
    constructor_hashes={}
    header_routes=[]
    capture=ROOT/'analysis/captures/modern-differences/frame-setting-history'
    capture.mkdir(parents=True,exist_ok=True)
    for version,(relative,archive_sha,exe_sha) in specs.items():
        archive=ROOT/relative
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==archive_sha
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        assert hashlib.sha256(raw).hexdigest()==exe_sha
        pe=pefile.PE(data=raw)
        descriptor=struct.unpack('<5I',pe.get_data(0x1567a8,20))
        assert descriptor[0]==0x538008 and descriptor[2:]==(0,0,0x6fbc4c)
        assert pe.get_string_at_rva(0x138008)==b'widescreen'
        pointer=descriptor[1];ids=[]
        for i in range(8):
            value=struct.unpack('<H',pe.get_data(pointer-0x400000+i*2,2))[0]
            if not value:break
            ids.append(value)
        assert ids==([1932,1933] if version=='1.5.3' else [1951,1952,1953,1954])
        member='fedata/text/text.eng'
        text=subprocess.check_output(['7z','x','-so',str(archive),member])
        first=struct.unpack_from('<I',text)[0];assert first%4==0 and first<len(text)
        labels=[]
        for index in ids:
            assert index*4<first
            offset=struct.unpack_from('<I',text,index*4)[0]
            assert first<=offset<len(text)
            labels.append(text[offset:text.index(0,offset)].decode('ascii'))
        assert labels==(['Full','2:1'] if version=='1.5.3' else ['Full, Centered','Full, Shifted','2:1, Centered','2:1, Shifted'])
        spans=[]
        ranges=[(0x4be5e0,0x4be850),(0x4be874,0x4be88d)] if version=='1.5.3' else [(0x4be5e0,0x4be85a),(0x4be89c,0x4be8b5)]
        ranges.extend([(0x472aac,0x472aeb),(0x4723f0,0x472402),(0x472d10,0x472e1d)])
        for lo,hi in ranges:
            code=pe.get_data(lo-0x400000,hi-lo)
            out=capture/f'{version}-{lo:08x}.asm'
            out.write_text('\n'.join(disassemble(code,lo))+'\n')
            spans.append({'start':f'{lo:08x}','end_exclusive':f'{hi:08x}',
                'bytes_sha256':hashlib.sha256(code).hexdigest(),'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        if version=='1.5.3':
            assert pe.get_data(0xbe622,19).hex()=='833d4cbc6f0000740a833db0d36f0001740146'
            assert pe.get_data(0xbe65a,5).hex()=='d1fb035dd8'
        else:
            assert pe.get_data(0xbe622,15).hex()=='833db0d36f000174068b354cbc6f00'
            assert pe.get_data(0xbe640,6).hex()=='f7c602000000'
            assert pe.get_data(0xbe65a,6).hex()=='f7c601000000'
        header=pe.get_data(0x15e8a0,12)
        expected_version=5 if version=='1.5.3' else 6
        assert struct.unpack('<3I',header)==(0x20f0,expected_version,0)
        assert pe.get_data(0x72ac2,2)==bytes([0x3c,expected_version])
        assert pe.get_data(0x72ad7,5).hex()=='e834020000'
        assert pe.get_data(0x72d92,8).hex()=='31d289154cbc6f00'
        header_routes.append(pe.get_data(0x72aac,0x3f))
        constructor_hashes[version]=spans[0]['bytes_sha256']
        result['versions'][version]={'archive':relative,'archive_sha256':archive_sha,'exe_sha256':exe_sha,
            'descriptor_address':'005567a8','descriptor_dwords':[f'{x:08x}'for x in descriptor],
            'label_list_address':f'{pointer:08x}','word_ids':ids,'labels':labels,
            'text_member':member,'text_sha256':hashlib.sha256(text).hexdigest(),
            'constructor_spans':spans,
            'configuration_header':{'file_backed_template_hex':header.hex(),'minimum_version_byte':expected_version,
                'rejected_version':'00472ad2 header refresh then00472ad7 display defaults plusHUD/sound groups',
                'frame_default':'00472d92 clearsEDX;00472d94 stores0 at006fbc4c'},
            'scope':'Descriptor bytes and referenced strings verified; runtime selection and geometry not observed'}
    assert [0x472aac+i for i,(a,b) in enumerate(zip(*header_routes)) if a!=b]==[0x472ac3]
    relative,expected,_=SPECS['official_modern']
    final_raw=(ROOT/relative).read_bytes();assert hashlib.sha256(final_raw).hexdigest()==expected
    final=pefile.PE(data=final_raw)
    final_constructor=hashlib.sha256(final.get_data(0xbe5e0,0x27a)).hexdigest()
    assert final_constructor==constructor_hashes['1.6.0']
    result['final_constructor_correspondence']={'path':relative,'sha256':expected,
        'range':'004be5e0..004be85a','bytes':634,'bytes_sha256':final_constructor,'identical_to_160':True,
        'limits':'Local constructor bytes only; dimensions/helpers/state and rendered outcome can differ'}
    (ROOT/'analysis/evidence/audits/frame-setting-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.5.3/1.6.0 archives/EXEs; two-to-four descriptor labels with retained selector')


if __name__=='__main__':main()
