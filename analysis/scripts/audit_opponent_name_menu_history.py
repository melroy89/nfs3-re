"""Compare historical HUD presets and distinguish settings from gameplay Name geometry."""
import hashlib,json,subprocess,struct
import pefile
from audit_dx5_reference_final import disassemble
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dialog_alignment_history import parse


def main():
    result={'kind':'static-opponent-name-menu-history','versions':{}};geometry=[];consumers=[];producers=[];tables=[];callers=[]
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==ah
        member='fedata/menus/hud.mnu';raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member])
        exe=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert hashlib.sha256(exe).hexdigest()==eh
        pe=pefile.PE(data=exe);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        words=struct.unpack('<5I',get(0x556848,0x55685c))
        assert words[4]==0x6fbc54 and pe.get_string_at_rva(words[0]-0x400000)==b'opponentName'
        branch=get(0x483e49,0x483ec8);consumers.append(branch)
        assert get(0x483e57,0x483e61).hex()=='83bc0254bc6f00007467'
        assert get(0x483ec3,0x483ec8).hex()=='e828590000'
        assert get(0x485694,0x485699).hex()=='be00055400'
        init=get(0x485680,0x4856c5);scale=get(0x480910,0x4809f7);convert_address=0x4f9404 if version=='1.3.1'else 0x4f9418;convert=get(convert_address,convert_address+29)
        producers.append((init,scale,convert))
        callers.append((get(0x484c10,0x484c5d),get(0x4897f0,0x4898a4)))
        assert get(0x484c43,0x484c48).hex()=='e8c8bcffff'
        assert get(0x484c33,0x484c39).hex()=='837ddc177d14'
        assert get(0x484c50,0x484c56).hex()=='837de0027d07'
        table=get(0x540500,0x540980);assert len(table)==1152;tables.append(table)
        slot12=[list(struct.unpack('<4H',get(0x540500+i*192+96,0x540500+i*192+104)))for i in range(6)]
        expected=[[400,953,600,993],[0,0,0,0],[400,453,600,493],[0,0,0,0],[400,953,600,993],[0,0,0,0]]if version=='1.3.1'else[[400,156,600,196],[0,0,0,0],[400,121,600,161],[0,0,0,0],[400,621,600,661],[0,0,0,0]]
        assert slot12==expected
        rows=[r for r in parse(raw)if r['fields'].get('codelink','').startswith(('opponentNameButton','opponentNameCascade'))]
        assert len(rows)==12
        selected={r['fields']['codelink']:{k:r['fields'][k]for k in ['x','y','listname','text']}for r in rows}
        assert len(selected)==12;geometry.append(selected)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,
            'member_sha256':hashlib.sha256(raw).hexdigest(),'preset_table':{'start':'00540500','bytes':1152,'sha256':hashlib.sha256(table).hexdigest(),'hex':table.hex()},'slot12_source_words':slot12,'producer_captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':hashlib.sha256(get(a,b)).hexdigest(),'disassembly':disassemble(get(a,b),a)}for n,a,b in [('preset_copy',0x485680,0x4856c5),('word_to_float',convert_address,convert_address+29),('slot_scaler',0x480910,0x4809f7),('all_slot_call_loop',0x484c10,0x484c5d),('text_draw_adapter',0x4897f0,0x4898a4)]],'matched_controls':selected,'exe_sha256':eh,'name_descriptor_words':list(words),
            'gameplay_consumer':{'start':'00483e49','end_exclusive':'00483ec8','bytes':127,
                'sha256':hashlib.sha256(branch).hexdigest(),'hex':branch.hex(),'disassembly':disassemble(branch,0x483e49)}}
    assert geometry[0]==geometry[1] and consumers[0]==consumers[1] and producers[0][1:]==producers[1][1:] and callers[0]==callers[1]
    assert [0x485680+i for i,(a,b)in enumerate(zip(producers[0][0],producers[1][0]))if a!=b]==[0x4856ab,0x4856b7]
    assert producers[0][2].hex()=='83ec04890424db0424c70424e8030000da3424d91c248b042483c404c3'
    changes=[]
    for profile in range(6):
        for slot in range(24):
            offset=profile*192+slot*8
            a=list(struct.unpack_from('<4H',tables[0],offset));b=list(struct.unpack_from('<4H',tables[1],offset))
            if a!=b:changes.append({'profile':profile,'slot':slot,'address':f'{0x540500+offset:08x}','131':a,'140':b})
    assert len(changes)==14
    assert sorted(set(r['slot']for r in changes))==[3,6,12,15]
    result['complete_preset_comparison']={'profiles':6,'slots_per_profile':24,'records':144,'changed_records':14,'unchanged_records':130,'changed_words':sum(a!=b for x in changes for a,b in zip(x['131'],x['140'])),'changes':changes,'scope':'Entire1152-byte table only;not all HUD initialization or all executable differences.'}
    result['scaler_changed_byte_addresses']=[f'{0x480910+i:08x}'for i,(a,b)in enumerate(zip(producers[0][1],producers[1][1]))if a!=b]
    result['gameplay_contract']={'profile_gate':'006fbc50+group*348h+role*1a4h+4','name_storage':'006fbc54','draw_call':'00483ec3 ->004897f0','geometry_reads':['0074981c+localIndex*170h','00749820+localIndex*170h','00749818+localIndex*170h'],'slot':12,'source':'00540500+profile*192+slot*8;WORD pairs converted/1000 and swapped into profile rectangle','scaler_call':'00484c43 loops slots0..22 for local indices0/1,including12;entry/later mutations unresolved.','draw_adapter':'004897f0..004898a4 retained180bytes,RET24;alignment and lower text helpers remain conditional.','remaining':'Full initializer admission,later writes,lower text ABI and mirror-relative final placement unresolved.'}
    result['verified']='127-byte Name consumer also identical131/140;all12 matched Opponent Name settings button/cascade controls retain x,y,listname and text token131/140.'
    result['limits']=['These are HUD settings controls,not the gameplay overlay;this neither proves nor disproves MP140-071.',
        'Slot12 preset/scaler/consumer linked;local scaler loop linked;full initializer admission,later geometry writes and lower text ABI unresolved;no rendered position observed.',
        'Not a complete asset-field comparison;other fields and unrelated controls can differ.',
        'No target execution or executable/database changes.']
    (ROOT/'analysis/evidence/audits/opponent-name-menu-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:12 Opponent Name settings controls retain selected geometry/bindings;gameplay relocation unresolved')


if __name__=='__main__':main()
