"""Static camera choice/default mapping; no game or camera execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-camera-slot-defaults','binaries':{}}
    converters=[]
    for label,(relative,digest,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        labels=list(struct.unpack('<8H',get(0x55628e,0x55629e)))
        modes=list(struct.unpack('<7H',get(0x55629e,0x5562ac)))
        assert labels==[193,147,150,149,148,151,152,0] and modes==[0,1,4,3,2,5,6]
        descriptors=[]
        for i in range(4):
            address=0x556c1c+20*i;words=struct.unpack('<5I',get(address,address+20))
            assert words==(0x5382cc+8*i,0x55628e,0,0,0x6fbba8+4*i)
            token=pe.get_string_at_rva(words[0]-0x400000).decode()
            assert token==f'camera{i+1}'
            descriptors.append({'address':f'{address:08x}','token':token,'words':[f'{w:08x}' for w in words]})
        converter=get(0x472300,0x472355);converters.append(converter)
        for i,site in enumerate([0x472308,0x47231c,0x472330,0x472344]):
            assert get(site,site+10).hex()=='8b04459c625500c1f810'
        if label=='original':
            spans=[(0x472413,0x47247b),(0x4b56d0,0x4b56e0),(0x472300,0x472355)]
            assert get(0x47241a,0x47241f).hex()=='bb03000000'
            assert get(0x472425,0x47242a).hex()=='ba01000000'
            assert get(0x472454,0x472460).hex()=='8915a8bb6f00891db0bb6f00'
            assert get(0x472460,0x472467).hex()=='31f6b902000000'
            assert get(0x47246c,0x472472).hex()=='8935b4bb6f00'
            assert get(0x472475,0x47247b).hex()=='890dacbb6f00'
            assert get(0x4b56d0,0x4b56e0).hex()=='51525589e52eff15684553005d5a59c3'
            imports={entry.address:entry.name for dll in pe.DIRECTORY_ENTRY_IMPORT for entry in dll.imports if entry.name}
            assert imports[0x534568]==b'GetTickCount'
            defaults=[1,2,3,0]
        else:
            spans=[(0x472298,0x4722c7),(0x472300,0x472355)]
            assert get(0x472298,0x4722c7).hex()=='31c0a3b0bb6f00a3b4bb6f00b001a3ccd16f00a3acbb6f00b003a3a8bb6f00a3b8bb6f00a3bcbb6f00e83a000000c3'
            defaults=[3,1,0,0]
        result['binaries'][label]={'path':relative,'sha256':digest,'descriptors':descriptors,
            'label_ids':labels,'mode_ids':modes,'default_ordinals':defaults,
            'derived_default_label_ids':[labels[i] for i in defaults],
            'derived_default_mode_ids':[modes[i] for i in defaults],
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                         'sha256':sha(get(a,b)),'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)} for a,b in spans]}
    assert converters[0]==converters[1]
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha(archive.read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels={}
    for ident in [193,147,150,149,148,151,152]:
        offset=struct.unpack_from('<I',english,4*ident)[0]
        labels[str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    assert [labels[str(i)] for i in [193,147,150,149]]==['None','In Car','Roof Cam','Heli Cam']
    menu=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/camera.mnu'])
    assert all(('listname=camera'+str(i)).encode() in menu for i in range(1,5))
    result['assets']={'english_sha256':sha(english),'labels':labels,'camera_menu_sha256':sha(menu),
                      'camera_menu_lists':['camera1','camera2','camera3','camera4']}
    result['limits']=['Static initial/default-writing paths, not actual saved-user settings or complete later writer coverage.',
        'Original EDX is explicitly saved around GetTickCount; EBX retention assumes the normal32-bit Windows API callee-preserved ABI, not arbitrary hooked behavior.',
        'Official final English labels decode shared numeric IDs; original retail language provenance remains unverified.',
        'None is a list label/mapped mode0, not a new proof of camera-cycle admission or absence of other camera modes.',
        'No camera/game/instruction execution or rendered acceptance;1.0.0 introduction and actual restoration through the UI untested.',
        'Converter reads overlapping DWORDs then SAR16; a portable WORD implementation may match values but not the full read footprint.']
    (ROOT/'analysis/evidence/audits/camera-defaults-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four paired descriptors, original/Modern default writes, retained85-byte converter and named choice mappings')


if __name__=='__main__':main()
