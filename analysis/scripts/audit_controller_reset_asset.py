"""Compare reset-button authored fields; backup is not authenticated retail."""
import hashlib
import json
import subprocess
from audit_thrash_loader_difference import ROOT


def sections(data):
    rows=[];current=None
    for line in data.decode('latin1').splitlines():
        if line.startswith('['):
            current={'section':line,'fields':{}};rows.append(current)
        elif current is not None and '=' in line:
            k,v=line.split('=',1);current['fields'][k]=v
    return rows


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    oldpath='nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/CONTROL1.MNU'
    old=(ROOT/oldpath).read_bytes();new=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/control1.mnu'])
    result={'kind':'controller-reset-authored-position','inputs':{}}
    for label,data,path,pos in [('backup',old,oldpath,'7'),('official_modern',new,'fedata/menus/control1.mnu','8')]:
        matches=[r for r in sections(data) if r['fields'].get('text')=='kMenuCONTROL1ResetToD001']
        assert len(matches)==1
        row=matches[0];assert row['section']=='[button]'
        assert all(row['fields'][k]==v for k,v in {'codelink':'reset','buttontype':'tab','ypos':pos}.items())
        result['inputs'][label]={'path_or_member':path,'sha256':hashlib.sha256(data).hexdigest(),'reset_section':row}
    result['limits']=['Local backup provenance is not authenticated retail.','Authored ypos 7 to8; runtime placement and parser semantics not tested.']
    (ROOT/'analysis/evidence/audits/controller-reset-asset.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: controller reset button paired authored fields and ypos7 to8')


if __name__=='__main__':main()
