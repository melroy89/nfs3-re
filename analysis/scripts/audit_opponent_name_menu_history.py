"""Exclude HUD settings-control geometry as evidence for the gameplay name move."""
import hashlib,json,subprocess,struct
import pefile
from audit_dx5_reference_final import disassemble
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dialog_alignment_history import parse


def main():
    result={'kind':'static-opponent-name-menu-history','versions':{}};geometry=[];consumers=[]
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
        rows=[r for r in parse(raw)if r['fields'].get('codelink','').startswith(('opponentNameButton','opponentNameCascade'))]
        assert len(rows)==12
        selected={r['fields']['codelink']:{k:r['fields'][k]for k in ['x','y','listname','text']}for r in rows}
        assert len(selected)==12;geometry.append(selected)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,
            'member_sha256':hashlib.sha256(raw).hexdigest(),'matched_controls':selected,'exe_sha256':eh,'name_descriptor_words':list(words),
            'gameplay_consumer':{'start':'00483e49','end_exclusive':'00483ec8','bytes':127,
                'sha256':hashlib.sha256(branch).hexdigest(),'hex':branch.hex(),'disassembly':disassemble(branch,0x483e49)}}
    assert geometry[0]==geometry[1] and consumers[0]==consumers[1]
    result['gameplay_contract']={'profile_gate':'006fbc50+group*348h+role*1a4h+4','name_storage':'006fbc54','draw_call':'00483ec3 ->004897f0','geometry_reads':['0074981c+view*170h','00749820+view*170h','00749818+view*170h'],'remaining':'Geometry producer,callee ABI and mirror-relative placement unresolved.'}
    result['verified']='127-byte Name consumer also identical131/140;all12 matched Opponent Name settings button/cascade controls retain x,y,listname and text token131/140.'
    result['limits']=['These are HUD settings controls,not the gameplay overlay;this neither proves nor disproves MP140-071.',
        'Named profile gate and draw call linked;gameplay rectangle/default producer and renderer ABI still unresolved;no rendered position observed.',
        'Not a complete asset-field comparison;other fields and unrelated controls can differ.',
        'No target execution or executable/database changes.']
    (ROOT/'analysis/evidence/audits/opponent-name-menu-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:12 Opponent Name settings controls retain selected geometry/bindings;gameplay relocation unresolved')


if __name__=='__main__':main()
