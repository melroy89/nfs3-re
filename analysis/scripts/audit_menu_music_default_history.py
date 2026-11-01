"""Pin original/early/final menu-music defaults and their versioned labels."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    assert sha(archive.read_bytes())=='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac'
    early=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    assert sha(early)=='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'
    inputs={key:((ROOT/relative).read_bytes(),digest,relative) for key,(relative,digest,_) in SPECS.items()}
    inputs['modern_1.1.0']=(early,sha(early),str(archive.relative_to(ROOT))+'!nfs3.exe')
    result={'kind':'static-menu-music-default-history','binaries':{}}
    bodies={}
    for key,(raw,digest,path) in inputs.items():
        assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        descriptor=struct.unpack('<5I',get(0x556bf4,0x556c08))
        assert descriptor[0]==0x5382b4 and descriptor[4]==0x6fbbec
        assert pe.get_string_at_rva(0x1382b4)==b'menutunes'
        labels=[]
        for i in range(16):
            ident=struct.unpack('<H',pe.get_data(descriptor[1]-0x400000+2*i,2))[0]
            if ident==0:break
            labels.append(ident)
        expected=([1946,1944,1945]+list(range(467,474))) if key=='official_modern' else [466]+list(range(467,474))
        assert labels==expected
        a,b=(0x472248,0x472295) if key=='official_modern' else (0x4725be,0x472611)
        body=get(a,b);bodies[key]=body
        if key=='original':
            assert get(0x4725de,0x4725e0).hex()=='89fa'
            assert get(0x4725fe,0x472600).hex()=='31fa'
            assert get(0x472605,0x47260b).hex()=='8915ecbb6f00'
            setting=0
        elif key=='modern_1.1.0':
            assert get(0x4725cd,0x4725d2).hex()=='b802000000'
            assert get(0x472605,0x47260b).hex()=='a3ecbb6f0090'
            setting=2
        else:
            assert get(a,a+12).hex()=='31c0a3e4bb6f00a3ecbb6f00'
            setting=0
        result['binaries'][key]={'path':path,'sha256':digest,'default_selector':setting,
            'descriptor':[f'{v:08x}' for v in descriptor],'label_ids':labels,'default_label_id':labels[setting],
            'capture':{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(body),
                       'hex':body.hex(),'disassembly':disassemble(body,a)}}
    differences=[0x4725be+i for i,(old,new) in enumerate(zip(bodies['original'],bodies['modern_1.1.0'])) if old!=new]
    assert differences==[0x472605,0x472606,0x472607,0x472608,0x472609,0x47260a]
    result['original_early_changed_bytes']=[f'{a:08x}' for a in differences]
    final_archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha(final_archive.read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(final_archive),'fedata/text/text.eng'])
    result['label_source']={'archive':str(final_archive.relative_to(ROOT)),'member':'fedata/text/text.eng','sha256':sha(english),'labels':{}}
    for ident in [466,468,1946]:
        offset=struct.unpack_from('<I',english,4*ident)[0]
        result['label_source']['labels'][str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    assert result['label_source']['labels']=={'466':'Random','468':'Romulus 3','1946':'Random (All)'}
    result['limits']=['No game, music, instruction or API execution; audible playback and actual saved settings untested.',
        '1.1.0 is early surviving evidence; no1.0.0 introduction-date proof or exact later default-change date.',
        'Label strings decoded from official final English resource, not authenticated original/early language files.',
        'Captured default-writing blocks do not establish every caller, reset admission, persistence override or later writer.',
        'Final Random (All) selector membership and cycling are separately audited; label is not proof every track is included.']
    (ROOT/'analysis/evidence/audits/menu-music-default-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original0/early2/final0 defaults, six-byte early patch and versioned menu label bindings')


if __name__=='__main__':main()
