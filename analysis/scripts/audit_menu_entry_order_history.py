"""Link selected authored control reorder to retained menu ordinal traversal."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dialog_alignment_history import parse
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-menu-entry-order-history','versions':{}};retained=[];orders={}
    spans=[('loader',0x449510,0x449891),('template_copy',0x449060,0x4490d8),
           ('previous',0x449f30,0x44a0b5),('next',0x44a0c0,0x44a23b)]
    controls=('[button]','[selectlist]','[droplist]','[slider]','[cascade]')
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh;pe=pefile.PE(data=raw)
        get=lambda a,b:pe.get_data(a-0x400000,b-a)
        retained.append([get(a,b)for _,a,b in spans])
        assert get(0x44a1fe,0x44a203).hex()=='66f7c20113'
        assert get(0x4496e4,0x4496f6).hex()=='8d4a0189c289c8890dac0b6600e86af9ffff'
        templates=[]
        for row,code,name,template,flags in [(0x557aa8,5,b'button',0x556e40,0x800),(0x557acc,21,b'selectlist',0x556ff8,0x200 if version=='1.3.1'else 0)]:
            values=struct.unpack('<3I',get(row,row+12));assert values[0]==code and values[2]==template
            assert pe.get_string_at_rva(values[1]-0x400000)==name
            actual=struct.unpack('<H',get(template+4,template+6))[0];assert actual==flags
            templates.append({'class':name.decode(),'row':f'{row:08x}','template':f'{template:08x}','flags':actual,'clear_navigation_skip_mask1301':actual&0x1301==0})
        members={};orders[version]={}
        for menu in ('loadsave','ipx'):
            member=f'fedata/menus/{menu}.mnu';data=subprocess.check_output(['7z','x','-so',str(archive),member]);rows=parse(data)
            seq=[{'section_ordinal_zero_based':i,'section':r['section'],
                  'identity':r['fields'].get('codelink')or r['fields'].get('text')or r['fields'].get('listname')}
                 for i,r in enumerate(rows)if r['section']in controls]
            orders[version][menu]=seq;members[menu]={'member':member,'sha256':sha(data),'authored_control_order':seq}
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'menus':members,'templates':templates,
            'unchanged_code':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b))}for n,a,b in spans],
            'ordinal_append_witness':{'start':'004496d6','end_exclusive':'004496f8','hex':get(0x4496d6,0x4496f8).hex(),
                                      'disassembly':disassemble(get(0x4496d6,0x4496f8),0x4496d6)}}
    assert retained[0]==retained[1]
    def position(v,menu,identity):
        matches=[r['section_ordinal_zero_based']for r in orders[v][menu]if r['identity']==identity]
        assert len(matches)==1;return matches[0]
    assert position('1.3.1','loadsave','escape CANCEL_LOAD_OPTIONS')<position('1.3.1','loadsave','replays')
    assert position('1.4.0','loadsave','replays')<position('1.4.0','loadsave','escape CANCEL_LOAD_OPTIONS')
    for key in ('joingame','refreshlist'):
        assert position('1.3.1','ipx','gamelist')<position('1.3.1','ipx',key)
        assert position('1.4.0','ipx',key)<position('1.4.0','ipx','gamelist')
    result['verified']=['Load replays versus Back/Cancel and IPX gamelist versus Join/Refresh reverse relative authored section order131->140.',
        'Retained loader increments00660bac for parsed section then copies template into00604ee0+ordinal*bc;selected selectors traverse indexed records.',
        'Button template800 clears skip mask in both;selectlist template200->0 removes a bit tested by retained navigation mask1301;runtime writes/race-now policy remain qualified.',
        'This is a concrete order-producing asset/code candidate forMP140-015,not an observed keyboard traversal.']
    result['limits']=['Source section ordinals are not actual global runtime indices;loading,base indices,parser success and appended menus remain conditional.',
        'Template flags are initial values,not proof every actual control remains selectable or receives a key.',
        'No all-menu order correctness,mouse/focus effects or live keyboard/UI test established.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/menu-entry-order-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 Load/IPX authored control reorders link to retained indexed loader/selectors;runtime admission qualified')


if __name__=='__main__':main()
