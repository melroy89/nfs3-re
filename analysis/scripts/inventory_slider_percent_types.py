"""Inventory selected installed slider definition blocks; no parser/game execution."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--game-dir',type=Path,required=True);root=p.parse_args().game_dir
    files=[]
    for folder in ('FEDATA/MENUS','fedata_org/menus'):
        for path in sorted((root/folder).iterdir()):
            if path.name.lower() not in ('audio.mnu','advgrph.mnu','cedbasic.mnu'):continue
            raw=path.read_bytes();blocks=[];current=None
            for number,line in enumerate(raw.decode('latin1').splitlines(),1):
                line=line.strip()
                if line.startswith('[') and line.endswith(']'):
                    if current and 'percenttype' in current:blocks.append(current)
                    current={'section':line,'line':number}
                elif current is not None and '=' in line:
                    k,v=line.split('=',1)
                    if k.lower() in ('codelink','percenttype','slidertype','snap','r0_step','r1_step','r2_step'):current[k.lower()]=v
            if current and 'percenttype' in current:blocks.append(current)
            files.append({'path':str(path.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),'blocks':blocks})
    assert files
    by_path={f['path']:f for f in files}
    comparisons=[]
    for name in ('advgrph','audio','cedbasic'):
        installed=by_path[f'FEDATA/MENUS/{name}.mnu']
        upper=by_path[f'fedata_org/menus/{name.upper()}.MNU']
        lower=by_path[f'fedata_org/menus/{name}.mnu']
        old={b['codelink']:b for b in upper['blocks']}
        new={b['codelink']:b for b in installed['blocks']}
        comparisons.append({'installed':installed['path'],'uppercase_backup':upper['path'],
            'lowercase_backup':lower['path'],'lowercase_backup_identical_to_installed':lower['sha256']==installed['sha256'],
            'matching_codelinks':[{'codelink':k,'backup_percenttype':old[k]['percenttype'],
                                  'installed_percenttype':new[k]['percenttype']} for k in sorted(old.keys() & new.keys())],
            'installed_only_codelinks':sorted(new.keys()-old.keys()),'backup_only_codelinks':sorted(old.keys()-new.keys())})
    out=Path(__file__).resolve().parents[1]/'evidence/inventories/installed-slider-percent-types.json'
    out.write_text(json.dumps({'scope':'Selected installed/local backup menu text only; not authenticated package provenance or parser execution.','files':files,'selected_comparisons':comparisons},indent=2)+'\n')
    print(f'PASS: {len(files)} selected files, slider blocks retained with source lines')


if __name__=='__main__':main()
