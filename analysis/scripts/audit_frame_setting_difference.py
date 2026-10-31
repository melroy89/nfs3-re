"""Resolve Frame Size list, selector storage and official labels without execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-frame-size-setting-comparison','range_end':'exclusive','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/frame-setting';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        words=struct.unpack('<5I',pe.get_data(0x1567a8,20));assert words[0]==0x538008 and words[4]==0x6fbc4c
        assert pe.get_data(words[0]-0x400000,32).split(b'\0')[0]==b'widescreen'
        ids=[]
        for i in range(16):
            value=struct.unpack('<H',pe.get_data(words[1]-0x400000+2*i,2))[0]
            if not value:break
            ids.append(value)
        assert ids==([229,228] if label=='original' else [1951,1952,1953,1954])
        spans=[(0x442c80,0x442cdc)]
        if label=='official_modern':spans += [(0x4624a0,0x4624df),(0x462633,0x462663)]
        rows=[]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'descriptor_005567a8_words':[f'{x:08x}' for x in words],'list_ids':ids,'spans':rows}
        if label=='official_modern':
            assert pe.get_data(0x62661,2)==bytes.fromhex('8902')
            assert int.from_bytes(pe.get_data(0x156ed8,4),'little')==0x4624a0
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels={}
    for ident in (228,229,1283,1504,1505,1951,1952,1953,1954):
        offset=struct.unpack_from('<I',english,4*ident)[0];assert 0<=offset<len(english)
        end=english.index(b'\0',offset)
        labels[str(ident)]={'offset':offset,'text':english[offset:end].decode('latin1')}
    result['label_symbol_ids']={}
    for ident,expected_name in ((1283,'kMenuPSGRAPHWideScre001'),(1504,'kMenuGRAPHICSWideScre001'),(1505,'kMenuGRAPHICSwidescre001')):
        pointer=struct.unpack('<I',pe.get_data(0x161c44+4*ident,4))[0]
        name=pe.get_data(pointer-0x400000,80).split(b'\0')[0].decode()
        assert name==expected_name
        result['label_symbol_ids'][name]=ident
    result['official_english']={'member':'fedata/text/text.eng','sha256':hashlib.sha256(english).hexdigest(),'labels':labels}
    result['official_menu_fields']=[]
    for name in ('advgrph.mnu','psgraph.mnu'):
        data=subprocess.check_output(['7z','x','-so',str(archive),f'fedata/menus/{name}'])
        fields=[{'line':i,'field':line} for i,line in enumerate(data.decode('latin1').splitlines(),1) if line in ('listname=widescreen','text=kMenuGRAPHICSWideScre001','text=kMenuGRAPHICSwidescre001','text=kMenuPSGRAPHWideScre001')]
        result['official_menu_fields'].append({'member':f'fedata/menus/{name}','sha256':hashlib.sha256(data).hexdigest(),'fields':fields})
    result['limits']=['No UI selection, rendering or target execution.','Matched lookup path and accepted-write spans are partial function witnesses.','Original choice IDs are decoded using official Modern English here; original retail language provenance is not established.']
    (ROOT/'analysis/evidence/audits/original-modern-frame-setting.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: two-to-four choice expansion, Frame Size labels, selector and DWORD write')


if __name__=='__main__':main()
