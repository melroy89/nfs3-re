"""Static paired HSV keyboard callback; no instruction or UI execution."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha,disassemble,intervals
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'static-colour-wheel-keyboard-callback','binaries':{}};bodies=[];images=[]
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw);images.append(pe);body=pe.get_data(0x3ec40,831);bodies.append(body)
        record=struct.unpack('<3I',pe.get_data(0x157b60,12));assert record[1]==0x557834
        assert pe.get_string_at_rva(record[0]-0x400000)==b'colorwheel'
        assert struct.unpack('<I',pe.get_data(0x157834+0x30,4))[0]==0x43ec40
        result['binaries'][label]={'path':path,'sha256':digest,'widget_row':'00557b60',
            'template':'00557834','input_callback':'0043ec40',
            'start':'0043ec40','end_exclusive':'0043ef7f','bytes':831,
            'body_sha256':sha(body),'bytes_hex':body.hex(),'disassembly':disassemble(body,0x43ec40)}
    old,new=bodies
    assert old[:0xa3]==new[:0xa3]
    assert old[0x1e4:0x2be]==new[0x1e4:0x2be]
    count=sum(a!=b for a,b in zip(old,new));assert count==369
    assert images[1].get_data(0x3ebb5,11)==b'\x90'*11
    for lo,hi in [(0x43ebc0,0x43ec40),(0x43ef7f,0x43f220)]:
        assert images[0].get_data(lo-0x400000,hi-lo)==images[1].get_data(lo-0x400000,hi-lo)
    assert sum(x!=y for x,y in zip(*[pe.get_data(0x3ebb5,11) for pe in images]))==11
    result['outside_partition']={'interval':'0043ebb5..0043f220','changed_bytes':380,
        'parts':[{'range':'0043ebb5..0043ebc0','changed':11,'role':'old mouse handler last3 bytes and alignment8'},
                 {'range':'0043ebc0..0043ec40','changed':0,'role':'retained wheel callback/adjacent code'},
                 {'range':'0043ec40..0043ef7f','changed':369,'role':'complete keyboard handler'},
                 {'range':'0043ef7f..0043f220','changed':0,'role':'retained remainder'}]}
    result['changed_bytes']=count;result['changed_runs']=intervals(old,new,0x43ec40)
    result['key_actions']=[{'key':'4800h','field':'+48h','delta':10},
        {'key':'5000h','field':'+48h','delta':-10},{'key':'4b00h','field':'+44h','delta':10},
        {'key':'4d00h','field':'+44h','delta':-10},{'key':'4900h','field':'+40h','delta':-10},
        {'key':'5100h','field':'+40h','delta':10}]
    result['ordinary_domain']='For incoming fields0..255,old/new adjusted value agrees; Modern skips endpoint stores and sound at bounds.'
    result['sound_changes']={'arrows':'Old no local sound;Modern successful field store -> shared0043ef62 selectsID0 then004181d0',
        'escape_enter':'Old ID0/EDX127 before action;Modern action first,then shared0043ef69 selectsID1',
        'tab':'Existing0043ef09 sound request immediateID1->0; positioning geometry retained'}
    result['limits']=['Static code/registration comparison,not executed target,UI,sound or maintainedC validation.',
        'Ordinary-field equivalence is conditional on0..255; invalid/out-of-range behaviour differs.',
        'Input dispatch and transitive helper/register/state lifetime and audible outcome remain separate.',
        'No field-to-hue/saturation/value names inferred solely from offsets.']
    (ROOT/'analysis/evidence/audits/colour-keyboard-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: bound831-byte colour-wheel keyboard callback;369 differences; retained dispatch/Tab geometry')


if __name__=='__main__':main()
