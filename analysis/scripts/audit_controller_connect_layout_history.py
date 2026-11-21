"""Compare authored Controller/Connect layouts120->130 and reset131->140."""
import hashlib,json,subprocess
from audit_thrash_loader_difference import ROOT
from audit_dialog_alignment_history import parse
from audit_screenshot_counter_history import PINS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.2.0':'151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b',
          '1.3.0':'93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
          **{v:p[0]for v,p in PINS.items()}}
    result={'kind':'static-controller-connect-layout-history','versions':{}};menus={}
    for version,ah in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel;assert sha(archive.read_bytes())==ah
        menus[version]={};members={}
        for name in (('control1','connect','pscntl1')if version in ['1.2.0','1.3.0']else('control1',)):
            member=f'fedata/menus/{name}.mnu';raw=subprocess.check_output(['7z','x','-so',str(archive),member]);rows=parse(raw);menus[version][name]=rows
            members[name]={'member':member,'sha256':sha(raw),'bytes':len(raw),'section_count':len(rows),'buttons':[r['fields']for r in rows if r['section']=='[button]']}
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'members':members}
    def buttons(version,name):return {r['fields']['text']:r['fields']for r in menus[version][name]if r['section']=='[button]'}
    controller=[]
    for ordinal,token in enumerate(['DeadZone','ForceFee','AudioFee','Function','Predefin','ResetToD'],1):
        key='kMenuCONTROL1'+token+'001';a,b=[buttons(v,'control1')[key]for v in ['1.2.0','1.3.0']]
        assert a['ypos']==str(ordinal+1)and b['ypos']==str(ordinal)
        assert all(a.get(k)==b.get(k)for k in ['text','codelink','nextmenu','buttontype','x','y','align'])
        controller.append({'text':key,'120_ypos':a['ypos'],'130_ypos':b['ypos']})
    connect=[]
    for link,old,new in [('racenet',1,5),('ipx',2,2),('tcp',3,1),('modem',4,3),('serial',5,4)]:
        pair=[]
        for version,index in [('1.2.0',old),('1.3.0',new)]:
            row=[r for r in buttons(version,'connect').values()if r.get('codelink')==link];assert len(row)==1
            assert row[0]['ypos']==str(index);pair.append(row[0])
        assert all(pair[0][k]==pair[1][k]for k in ['text','codelink','nextmenu','buttontype'])
        assert 'x'in pair[0]and'y'in pair[0]and'x'not in pair[1]and'y'not in pair[1]
        connect.append({'codelink':link,'120_ypos':old,'130_ypos':new,'120_xy':[pair[0]['x'],pair[0]['y']],'130_xy':'omitted;parser defaults not established'})
    reset={v:buttons(v,'control1')['kMenuCONTROL1ResetToD001']['ypos']for v in pins};assert reset=={'1.2.0':'7','1.3.0':'6','1.3.1':'6','1.4.0':'7'}
    def without_demo(rows):return [{'section':r['section'],'fields':{k:v for k,v in r['fields'].items()if k not in ['EnableForDemo','EnableForE3Demo']}}for r in rows]
    assert without_demo(menus['1.2.0']['pscntl1'])==without_demo(menus['1.3.0']['pscntl1'])
    result.update({'controller_tab_changes':controller,'connect_tab_changes':connect,'reset_ypos_history':reset,'split_screen_control':{'menu':'pscntl1','equal_after_removing_demo_fields':True},'limits':[
        'Authored metadata,not rendered pixels or complete parser/default/runtime selection proof.',
        'Connect order and omitted coordinates do not prove identical executable protocol behavior.',
        'Demo-field removal has no interpreted runtime effect here;split-screen negative comparison is restricted to parsed records.',
        'No target,UI,API,instruction execution or executable/Ghidra changes.']})
    (ROOT/'analysis/evidence/audits/controller-connect-layout-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:120->130 Controller/Connect tab changes;131->140 reset6->7;split-screen geometry retained')


if __name__=='__main__':main()
