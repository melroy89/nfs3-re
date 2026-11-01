"""Reproduce eight selected static audits and check protected artifact identity."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAIRS=[('nglide_config_history','nglide-config-history'),
       ('menu_music_default_history','menu-music-default-history'),
       ('cabin_extent_history','cabin-extent-history'),
       ('camera_defaults_difference','camera-defaults-difference'),
       ('map_zoom_default_history','map-zoom-default-history'),
       ('opponent_hud_defaults','opponent-hud-defaults'),
       ('police_list_spacing','police-list-spacing'),
       ('intensity_color_contract','intensity-color-contract')]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    prior_path='analysis/evidence/validation/five-static-mechanisms-checkpoint.json'
    prior=json.loads((ROOT/prior_path).read_text())
    protected=[]
    for row in prior['preserved_artifacts']:
        value=sha((ROOT/row['path']).read_bytes());assert value==row['after_sha256']
        protected.append({'path':row['path'],'before_sha256':value,'matches_prior':True})
    exports=[]
    for row in prior['raw_reference_exports']:
        value=sha((ROOT/row['path']).read_bytes());assert value==row['sha256']
        exports.append({'path':row['path'],'before_sha256':value,'matches_prior':True})
    result={'kind':'eight-recent-static-mechanisms-checkpoint',
        'reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'prior_checkpoint':prior_path,'prior_checkpoint_sha256':sha((ROOT/prior_path).read_bytes()),'checks':[]}
    for script,output in PAIRS:
        script=f'analysis/scripts/audit_{script}.py';output=f'analysis/evidence/audits/{output}.json'
        before=sha((ROOT/output).read_bytes())
        row={'command':['python3',script],'script_sha256':sha((ROOT/script).read_bytes()),
             'output':output,'pre_run_output_sha256':before,'runs':[]}
        for index in [1,2]:
            completed=subprocess.run(row['command'],cwd=ROOT,text=True,capture_output=True,timeout=60)
            digest=sha((ROOT/output).read_bytes())
            row['runs'].append({'run':index,'exit_code':completed.returncode,'stdout':completed.stdout,
                                'stderr':completed.stderr,'output_sha256':digest})
            assert completed.returncode==0,(script,completed.stderr)
            assert digest==before,(script,'Evidence changed on reproduction')
        row['repeatable']=True;row['matches_pre_run_output']=True;result['checks'].append(row)
    for row in protected+exports:
        row['after_sha256']=sha((ROOT/row['path']).read_bytes());assert row['after_sha256']==row['before_sha256']
    result['preserved_artifacts']=protected;result['raw_reference_exports']=exports
    result['shared_dependencies']=[{'path':path,'sha256':sha((ROOT/path).read_bytes())} for path in [
        'analysis/scripts/audit_thrash_loader_difference.py','analysis/scripts/audit_dx5_reference_final.py',
        'analysis/evidence/audits/language-fallback-history.json']]
    result['limits']=['Primary-agent reruns of eight selected static audits, not independent semantic review, runtime, CI or whole-repository validation.',
        'No target/API/instruction execution, new exports, compilation, reconstruction edits or Ghidra database reopening/mutation.',
        'Hashes establish file identity across this checkpoint and prior record, not live GUI state or correctness of every annotation.',
        'Raw export identity is compared against prior checkpoint hashes; exports were not regenerated and original export manifests were not freshly parsed.',
        'Repeatability does not prove every semantic interpretation or extend the selected input/path coverage.']
    destination=ROOT/'analysis/evidence/validation/recent-static-mechanisms-checkpoint.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:16/16 audit runs,8 unchanged evidence outputs,{len(protected)} protected files and{len(exports)} raw exports unchanged')


if __name__=='__main__':main()
