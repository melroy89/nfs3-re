"""Read historical setup-menu button routes; no target execution."""
import hashlib,json,subprocess
from audit_thrash_loader_difference import ROOT

PINS={
 '1.1.0':'31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac',
 '1.3.1':'6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934',
 '1.4.0':'8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9',
 'final':'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'}
KEYS=('text','codelink','nextmenu','buttontype')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def buttons(raw):
    result=[];current=None
    for line in raw.decode('latin1').splitlines():
        line=line.strip()
        if line.startswith('['):
            if current is not None:result.append(current)
            current={}if line.lower()=='[button]'else None
        elif current is not None and '='in line:
            key,value=line.split('=',1)
            if key in KEYS:
                assert key not in current
                current[key]=value
    if current is not None:result.append(current)
    return result


def main():
    result={'kind':'static-setup-button-history','versions':{}}
    selected=[]
    for version,pin in PINS.items():
        path=('analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'if version=='final'else
              f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z')
        assert sha((ROOT/path).read_bytes())==pin
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/path),'fedata/menus/setup.mnu'])
        rows=buttons(raw);assert len(rows)==6
        early=version in ('1.1.0','1.3.1')
        expected=({'text':'kMenuOPTIONSCredits001','codelink':'credits','nextmenu':'credits','buttontype':'LR1of2'}if early else
                  {'text':'kMenuMAINOptions001','nextmenu':'options','buttontype':'LR1of2'})
        assert rows[4]==expected
        assert rows[5]['text']=='kMenuSETUPExitGame001'and rows[5]['codelink']=='exitprogram escape'
        selected.append(rows)
        result['versions'][version]={'archive':path,'archive_sha256':pin,'member':'fedata/menus/setup.mnu',
            'member_sha256':sha(raw),'bytes':len(raw),'selected_fields_in_button_file_order':rows}
    assert all(rows[:4]==selected[0][:4]and rows[5]==selected[0][5]for rows in selected)
    result['verified']=[
        'Retained1.1.0 and1.3.1 fifth buttons explicitly name Credits token,codelink and nextmenu.',
        '1.3.1->1.4.0 changes fifth selected route to Options and removes codelink;final retains it.',
        'All four packages have six buttons;selected fields of other five buttons match.',
        'This resolves historical authored Credits presence and the1.4.0 authored Options boundary,not runtime activation.']
    result['limits']=[
        'No1.0.0 package inspected;the claimed first-release introduction remains unverified.',
        'Only four selected button fields;other properties/assets can differ.',
        'File order does not prove pixel placement or selected resource at runtime.',
        'No historical callback registration,translated text,successful descriptor loading or visible Credits/Options screen verified.',
        'No target instructions,DLL/API execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/setup-button-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:early Credits route;131->140 authored Options replacement;final retained')


if __name__=='__main__':main()
