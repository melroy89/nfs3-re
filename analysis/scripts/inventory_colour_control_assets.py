"""Compare selected colour widget records; no rendering or retail provenance claim."""
import hashlib
import json
import subprocess
from audit_thrash_loader_difference import ROOT


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    result={'kind':'colour-control-asset-comparison','files':{}}
    for label,relative in [('official_modern','analysis/captures/modern-differences/upstream/package/fedata/menus/car1.mnu'),('local_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/CAR1.MNU')]:
        raw=(ROOT/relative).read_bytes()
        if label=='official_modern':assert raw==subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/car1.mnu'])
        records=[];record=None
        for number,line in enumerate(raw.decode('latin1').splitlines(),1):
            if line.startswith('['):record={'section':line,'line':number,'fields':{}};records.append(record)
            elif record is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);record['fields'][key]=value
        selected={r['fields']['codelink']:r for r in records if r['fields'].get('codelink') in ('CAR_COLOR_SELECT_P1','COLOR_EDIT')}
        assert len(selected)==2
        result['files'][label]={'path':relative,'sha256':hashlib.sha256(raw).hexdigest(),'records':selected}
    comparisons={}
    for name in ('CAR_COLOR_SELECT_P1','COLOR_EDIT'):
        old=result['files']['local_backup']['records'][name]['fields'];new=result['files']['official_modern']['records'][name]['fields']
        comparisons[name]={'changed_common_fields':{k:{'backup':old[k],'official':new[k]} for k in sorted(old.keys()&new.keys()) if old[k]!=new[k]},'backup_only_fields':{k:old[k] for k in sorted(old.keys()-new.keys())},'official_only_fields':{k:new[k] for k in sorted(new.keys()-old.keys())}}
    assert comparisons['COLOR_EDIT']['changed_common_fields']=={}
    assert comparisons['CAR_COLOR_SELECT_P1']['changed_common_fields']=={'x':{'backup':'128','official':'126'},'y':{'backup':'208','official':'220'}}
    result['comparisons']=comparisons
    result['limits']=['Official final asset versus local backup; original retail provenance and historical introduction unverified.','Authored coordinates only; runtime widget padding, layout defaults, hit testing and rendered position untested.','Two distinct widgets; no inferred identity between colour-wheel handler and car-colour dropdown.']
    (ROOT/'analysis/evidence/inventories/colour-control-assets.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: distinct colour widgets, dropdown x/y move, unchanged common wheel fields')


if __name__=='__main__':main()
