"""Compare the pause-title asset record without loading or rendering the game."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    result={'kind':'pause-title-asset-comparison','files':{}}
    for label,relative in (('official_modern','analysis/captures/modern-differences/upstream/package/fedata/menus/pause.mnu'),('local_uppercase_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/PAUSE.MNU')):
        data=(ROOT/relative).read_bytes()
        if label=='official_modern':assert data==subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/pause.mnu'])
        sections=[];current=None
        for number,line in enumerate(data.decode('latin1').splitlines(),1):
            if line.startswith('['):
                current={'section':line,'line':number,'fields':{}};sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);current['fields'][key]=value
        selected=[s for s in sections if s['fields'].get('codelink')=='pstitle']
        assert len(selected)==1 and selected[0]['section']=='[text]'
        result['files'][label]={'path':relative,'sha256':hashlib.sha256(data).hexdigest(),'title':selected[0]}
    old=result['files']['local_uppercase_backup']['title']['fields'];new=result['files']['official_modern']['title']['fields']
    changed={k:{'backup':old[k],'official':new[k]} for k in old.keys()&new.keys() if old[k]!=new[k]}
    assert changed=={'y':{'backup':'14','official':'9'}}
    assert old['x']==new['x']=='320' and old['align']==new['align']=='2'
    result['changed_common_fields']=changed
    result['backup_fields_absent_from_official']={k:old[k] for k in sorted(old.keys()-new.keys())}
    result['limits']=['No code, render, input or target execution.','Unauthenticated backup provenance; official final asset does not verify release introduction.','Omitted legacy fields and other menu records are not qualified by a title-coordinate comparison.']
    (ROOT/'analysis/evidence/inventories/pause-title-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned official member, title y14 to9, shared x320/align2 and omitted fields')


if __name__=='__main__':main()
