"""Exclude HUD settings-control geometry as evidence for the gameplay name move."""
import hashlib,json,subprocess
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dialog_alignment_history import parse


def main():
    result={'kind':'static-opponent-name-menu-history','versions':{}};geometry=[]
    for version,(ah,_)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==ah
        member='fedata/menus/hud.mnu';raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member])
        rows=[r for r in parse(raw)if r['fields'].get('codelink','').startswith(('opponentNameButton','opponentNameCascade'))]
        assert len(rows)==12
        selected={r['fields']['codelink']:{k:r['fields'][k]for k in ['x','y','listname','text']}for r in rows}
        assert len(selected)==12;geometry.append(selected)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,
            'member_sha256':hashlib.sha256(raw).hexdigest(),'matched_controls':selected}
    assert geometry[0]==geometry[1]
    result['verified']='All12 matched Opponent Name settings button/cascade controls retain x,y,listname and text token131/140.'
    result['limits']=['These are HUD settings controls,not the gameplay overlay;this neither proves nor disproves MP140-071.',
        'Gameplay rectangle/default production and named renderer submissions still need linkage;no rendered position observed.',
        'Not a complete asset-field comparison;other fields and unrelated controls can differ.',
        'No target execution or executable/database changes.']
    (ROOT/'analysis/evidence/audits/opponent-name-menu-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:12 Opponent Name settings controls retain selected geometry/bindings;gameplay relocation unresolved')


if __name__=='__main__':main()
