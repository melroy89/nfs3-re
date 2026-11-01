"""Static race-dialog ordinal remap and1.1.0->1.2.0 introduction boundary."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble
from audit_mode_capacity_history import HISTORY


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    inputs={label:((ROOT/rel).read_bytes(),digest,rel) for label,(rel,digest,_) in SPECS.items()}
    archives={}
    for version in ['1.1.0','1.2.0']:
        ah,eh=HISTORY[version][:2];rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/rel;assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        inputs[version]=(raw,eh,rel+'!nfs3.exe');archives[version]={'path':rel,'sha256':ah}
    result={'kind':'static-race-dialog-preselection','archives':archives,'binaries':{}};helpers={}
    for label,(raw,digest,path) in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        descriptor=struct.unpack('<5I',get(0x556528,0x55653c))
        assert descriptor==(0x537d28,0x556214,0x55621e,0,0x6fd3b8)
        assert pe.get_string_at_rva(0x137d28)==b'racetype'
        ids=list(struct.unpack('<5H',get(0x556214,0x55621e)));assert ids==[213,214,215,220,0]
        assert get(0x452ced,0x452cf1).hex()=='85f67407'
        assert get(0x452cf6,0x452cfb).hex()=='eb0231c050'
        spans=[(0x452bd0,0x452d32),(0x45dab0,0x45dac9)]
        encoded=get(0x452cf1,0x452cf6)
        if label in ['original','1.1.0']:
            assert encoded.hex()=='a1b8d36f00';helper=None
        else:
            assert encoded[0]==0xe8
            helper=0x452cf6+int.from_bytes(encoded[1:],'little',signed=True)
            assert helper==(0x448558 if label=='1.2.0'else 0x4728e0)
            body=get(helper,helper+19);helpers[label]=body
            assert body.hex()=='a1b8d36f003c037503b001c33c017502b003c3'
            spans.append((helper,helper+19))
        result['binaries'][label]={'path':path,'sha256':digest,'race_type_label_ids':ids,
            'descriptor_words':[f'{v:08x}'for v in descriptor],'remap_helper':f'{helper:08x}'if helper else None,
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    assert helpers['1.2.0']==helpers['official_modern']
    old,new=[bytes.fromhex(result['binaries'][k]['captures'][0]['hex']) for k in ['original','official_modern']]
    assert [0x452bd0+i for i,(a,b) in enumerate(zip(old,new)) if a!=b]==[0x452cf1,0x452cf2,0x452cf3,0x452cf4]
    result['original_final_builder_changed_bytes']=['00452cf1','00452cf2','00452cf3','00452cf4']
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha(archive.read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng']);labels={}
    for ident in [213,214,215,220,198]:
        offset=struct.unpack_from('<I',english,ident*4)[0];labels[str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    assert labels=={'213':'Single Race','214':'Tournament','215':'Knockout','220':'Hot Pursuit','198':'Cancel'}
    result['english']={'member':'fedata/text/text.eng','sha256':sha(english),'labels':labels}
    result['ordinary_C0_orders']={'race_setting':['Single Race','Tournament','Knockout','Hot Pursuit'],
        'constructed_dialog':['Single Race','Hot Pursuit','Knockout','Tournament','Cancel']}
    result['derived_full_dword_examples']=[{'input':f'{value:08x}','output':f'{(value&0xffffff00)|(1 if value&255==3 else 3 if value&255==1 else value&255):08x}'}for value in [0,1,2,3,4,0x101,0x103]]
    result['limits']=['No game, dialog, input, resource lookup or extracted instruction execution.',
        'Choice-order interpretation is scoped to local C=0 unrestricted construction; alternate restricted/session paths remain separate.',
        'Official final English text decodes unchanged numeric IDs; original/early language provenance unverified.',
        'Helper swaps only AL values1/3, preserving upper24 bits; arbitrary invalid states are not normalized or range checked.',
        'Actual dialog focus, input callback effects and full caller/global lifetime remain unverified.',
        'Original004728e0 is unrelated timestamp-reading code, not an old version of the new remap helper.']
    (ROOT/'analysis/evidence/audits/race-dialog-preselection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:four pinned builds, shared race descriptor/labels, early120 remap boundary and identical final19-byte helper')


if __name__=='__main__':main()
