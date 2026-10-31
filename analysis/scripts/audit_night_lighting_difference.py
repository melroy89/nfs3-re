"""Static paired night-lighting admission and retained execution body."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/night-lighting';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-night-lighting-comparison','range_end':'exclusive','binaries':{}};images={}
    spans=[(0x41c670,0x41c9e4),(0x4bbde0,0x4bbe3a),(0x41d04e,0x41d06d),
           (0x4bc470,0x4bc529),(0x4bc717,0x4bc777),(0x4bc237,0x4bc2a2),
           (0x41b9b0,0x41bac2),(0x41cdc0,0x41cdd1)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['original_same_address_row_00556564']=[f'{v:08x}' for v in struct.unpack('<5I',images['original'].get_data(0x156564,20))]
    modern=images['official_modern']
    descriptor=struct.unpack('<5I',modern.get_data(0x156564,20))
    assert descriptor==(0x537720,0x55623a,0,0,0x6fd1d8)
    assert modern.get_data(descriptor[0]-0x400000,32).split(b'\0')[0]==b'mirrorlevel'
    assert struct.unpack('<4H',modern.get_data(0x15623a,8))==(187,186,185,0)
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels={}
    for ident in (187,186,185,1937):
        offset=struct.unpack_from('<I',english,ident*4)[0];labels[str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    assert [labels[str(n)] for n in (187,186,185,1937)]==['High','Medium','Low','Rear View Detail']
    result['modern_mirror_option']={'descriptor_00556564':[f'{v:08x}' for v in descriptor],'label_ids':[187,186,185],'english_sha256':hashlib.sha256(english).hexdigest(),'labels':labels}
    result['official_menus']=[]
    for name in ('graphics.mnu','psgraph.mnu'):
        data=subprocess.check_output(['7z','x','-so',str(archive),f'fedata/menus/{name}'])
        fields=[{'line':i,'text':line} for i,line in enumerate(data.decode('latin1').splitlines(),1) if line in ('listname=mirrorlevel','text=str_1937')]
        assert fields
        result['official_menus'].append({'member':f'fedata/menus/{name}','sha256':hashlib.sha256(data).hexdigest(),'fields':fields})
    result['mirror_pass_descriptors']={}
    for label,pe in images.items():
        rows=[]
        for address,name,storage in [(0x556870,b'mirror',0x6fbc5c),(0x556910,b'mirrorcop',0x6fbe00)]:
            row=struct.unpack('<5I',pe.get_data(address-0x400000,20))
            assert row[4]==storage
            assert pe.get_data(row[0]-0x400000,32).split(b'\0')[0]==name
            rows.append({'address':f'{address:08x}','name':name.decode(),'words':[f'{v:08x}' for v in row]})
        result['mirror_pass_descriptors'][label]=rows
    # Exact register-forwarding witnesses, independently bound to both baselines.
    for pe in images.values():
        for address,hexbytes in [(0x4bc475,'89c6'),(0x4bc481,'8935143d7a00'),
                                 (0x4bc767,'b801000000'),(0x41cdc9,'89c6'),
                                 (0x41d066,'89f0')]:
            expected=bytes.fromhex(hexbytes)
            assert pe.get_data(address-0x400000,len(expected))==expected
    result['identical_ranges']=[]
    for start,end in [(0x41c670,0x41c684),(0x41c6cc,0x41c9e4),(0x4bbde0,0x4bbe3a),(0x41d04e,0x41d06d),(0x4bc470,0x4bc529),(0x4bc717,0x4bc777),(0x41cdc0,0x41cdd1)]:
        data=images['original'].get_data(start-0x400000,end-start);assert data==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest()})
    result['limits']=['No graphics, night race or instruction execution.','Tag1 is the optional mirror-setting-gated render pass; full camera construction and rendered output remain unresolved.','Identical body does not establish transitive numeric, allocation or rendered equivalence.']
    (ROOT/'analysis/evidence/audits/original-modern-night-lighting.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: night-lighting counterparts, bounded gate delta, retained body and arena helper')


if __name__=='__main__':main()
