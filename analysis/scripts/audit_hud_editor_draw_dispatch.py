"""Bound police-widget hiding investigation at the registered draw callback."""
import hashlib,json,struct
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-hud-editor-draw-dispatch','binaries':{}};images={};captured={}
    spans=[('registered_callback',0x45bcb0,0x45bd18),('draw_dispatch_prefix',0x45ab30,0x45ac29),
           ('cone_stats_arm',0x45b837,0x45b8d0),('tutorial_icon_arm',0x45b8d0,0x45b91a),
           ('slot_classifier',0x47bc20,0x47bc3a),('role_policy_callsite',0x44d8cd,0x44d8e8),
           ('police_policy',0x44c360,0x44c4d1),('racer_policy',0x44c4e0,0x44c601)]
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw);images[label]=pe;get=lambda a,b:pe.get_data(a-0x400000,b-a)
        template=struct.unpack('<32I',get(0x557928,0x5579a8));assert template[11]==0x45bcb0
        table=get(0x45aad0,0x45ab2c);targets=struct.unpack('<23I',table)
        assert targets[6:8]==(0x45b8d0,0x45b837)
        assert get(0x45bcc8,0x45bcd9).hex()=='8b413c89c2be17000000c1fa1ff7fe89d0'
        assert get(0x45bcc3,0x45bcc8).hex()=='e868eeffff'
        captured[label]={name:get(a,b)for name,a,b in spans}
        renderer=get(0x45ab30,0x45b93e)
        result['binaries'][label]={'path':relative,'sha256':digest,'template_callback_slot_2c':f'{template[11]:08x}',
            'jump_table':{'address':'0045aad0','hex':table.hex(),'targets':[f'{x:08x}'for x in targets]},
            'renderer':{'start':'0045ab30','end_exclusive':'0045b93e','bytes':len(renderer),'sha256':sha(renderer)},
            'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                         'sha256':sha(get(a,b)),'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    assert captured['original']==captured['official_modern']
    assert result['binaries']['original']['jump_table']==result['binaries']['official_modern']['jump_table']
    x,y=[p.get_data(0x5ab30,3598)for p in images.values()]
    changed=[f'{0x45ab30+i:08x}'for i,(a,b)in enumerate(zip(x,y))if a!=b]
    assert changed==['0045ae28','0045ae29','0045af5f','0045b4b2','0045b664']
    result['renderer_changed_byte_addresses']=changed
    result['verified']=['Registered HudItem callback0045bcb0 calls0045ab30 before its classifier/outline logic.',
        'Callback computes signed item%23 for later classification; draw dispatcher maps item>=23 to view1 and subtracts23 once, otherwise view0.',
        'Retained23-entry table routes slot6 to0045b8d0 and slot7 to0045b837.',
        'Slot6 calls00482030 and has a bit2 software fallback; slot7 computes a percentage from vehicle+2dc/+2e0, default100 for zero sum.',
        'No new police-role predicate in either retained arm or captured dispatch prefix.',
        'Retained caller0044d8cd invokes shared policy0044c2d0 then chooses0044c360 for nonzero role-local ECX or0044c4e0 otherwise.',
        'Both selected role-policy bodies remain identical; code equality does not prove equal authored input items.']
    result['limits']=['No target, driver, instruction probe, compilation or Ghidra writes.',
        'Earlier callers, active authored items and generic dispatch/admission can suppress registered callbacks.',
        'Complete renderer differs by five bytes outside these captured equal arms; transitive or numeric equivalence is not claimed.',
        'Signed division remainder for negative item IDs is not a normalized0..22 index; ordinary valid menu IDs assumed for slot association.',
        'MP100-048 remains vendor-only; follow live item construction/admission and active menu assets rather than repeating these retained draw arms.']
    (ROOT/'analysis/evidence/audits/hud-editor-draw-dispatch.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: registered draw chain,23-case table and eight retained spans; police hiding unresolved')


if __name__=='__main__':main()
