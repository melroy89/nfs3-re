"""Static immediate-release Frame Size descriptor/English-label comparison."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def main():
    a=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']['1.5.3']
    b=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())['packages']['1.6.0']
    specs={'1.5.3':(a['archive'],a['archive_sha256'],a['executable_sha256']),
           '1.6.0':(b['archive_path'],b['archive_sha256'],next(x['sha256'] for x in b['members']if x['member']=='nfs3.exe'))}
    result={'kind':'historical-frame-setting-expansion','versions':{},
            'limits':['Selected descriptor and matching English asset only; not every frame consumer or localization.',
                      'No game/menu/viewport execution or visible camera-shift test.']}
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
        result['versions'][version]={'archive':relative,'archive_sha256':archive_sha,'exe_sha256':exe_sha,
            'descriptor_address':'005567a8','descriptor_dwords':[f'{x:08x}'for x in descriptor],
            'label_list_address':f'{pointer:08x}','word_ids':ids,'labels':labels,
            'text_member':member,'text_sha256':hashlib.sha256(text).hexdigest(),
            'scope':'Descriptor bytes and referenced strings verified; runtime selection and geometry not observed'}
    (ROOT/'analysis/evidence/audits/frame-setting-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.5.3/1.6.0 archives/EXEs; two-to-four descriptor labels with retained selector')


if __name__=='__main__':main()
