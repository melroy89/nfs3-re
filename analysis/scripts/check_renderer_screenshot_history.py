"""Reproduce eight renderer and screenshot historical investigations without executing target code."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAIRS=[('hud_preview_arrangement_history','hud-preview-arrangement-history'),
       ('gameplay_exit_mode_history','gameplay-exit-mode-history'),
       ('loading_sync_budget_history','loading-sync-budget-history'),
       ('dx7_fog_optin_history','dx7-fog-optin-history'),
       ('fog_mode_enable_history','fog-mode-enable-history'),
       ('menu_fog_context_history','menu-fog-context-history'),
       ('dx6_mode_count_history','dx6-mode-count-history'),
       ('screenshot_depth_local_history','screenshot-depth-local-history')]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    prior_path='analysis/evidence/validation/hud-menu-import-checkpoint.json'
    prior=json.loads((ROOT/prior_path).read_text())
    result={'kind':'eight-renderer-screenshot-history-checkpoint',
        'reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'runner_path':str(Path(__file__).relative_to(ROOT)),'runner_sha256':sha(Path(__file__).read_bytes()),
        'prior_checkpoint':prior_path,'prior_checkpoint_sha256':sha((ROOT/prior_path).read_bytes()),'checks':[]}
    protected=[]
    for row in prior['preserved_artifacts']:
        value=sha((ROOT/row['path']).read_bytes());assert value==row['after_sha256']
        protected.append({'path':row['path'],'before_sha256':value,'matches_prior':True})
    exports=[]
    for row in prior['raw_reference_exports']:
        value=sha((ROOT/row['path']).read_bytes());assert value==row['after_sha256']
        exports.append({'path':row['path'],'before_sha256':value,'matches_prior':True})
    for script,output in PAIRS:
        script=f'analysis/scripts/audit_{script}.py';output=f'analysis/evidence/audits/{output}.json'
        before=sha((ROOT/output).read_bytes())
        for path in [script,output]:
            committed=subprocess.check_output(['git','show',f'HEAD:{path}'],cwd=ROOT)
            assert sha(committed)==sha((ROOT/path).read_bytes())
        row={'command':['python3',script],'script_sha256':sha((ROOT/script).read_bytes()),
             'output':output,'pre_run_output_sha256':before,'script_and_output_match_reviewed_head':True,'runs':[]}
        for index in [1,2]:
            completed=subprocess.run(row['command'],cwd=ROOT,text=True,capture_output=True,timeout=60)
            digest=sha((ROOT/output).read_bytes())
            row['runs'].append({'run':index,'exit_code':completed.returncode,'stdout':completed.stdout,
                                'stderr':completed.stderr,'output_sha256':digest})
            assert completed.returncode==0,(script,completed.stderr)
            assert digest==before,(script,'Evidence changed on reproduction')
        row['repeatable']=True;result['checks'].append(row)
    for row in protected+exports:
        row['after_sha256']=sha((ROOT/row['path']).read_bytes());assert row['after_sha256']==row['before_sha256']
    result['preserved_artifacts']=protected;result['raw_reference_exports']=exports
    result['selected_shared_dependencies']=[{'path':path,'sha256':sha((ROOT/path).read_bytes())}for path in [
        'analysis/scripts/audit_thrash_loader_difference.py','analysis/scripts/audit_dx5_reference_final.py',
        'analysis/scripts/audit_endpoint_comma_history.py',
        'analysis/evidence/audits/reference-asset-pairs.json',
        'analysis/scripts/audit_subtitle_style_history.py',
        'analysis/evidence/audits/dx7-fog-optin-history.json']]
    result['limits']=['Primary-agent16 static reruns, not independent semantic review, runtime, CI or whole-repository qualification.',
        'No target/API/instruction execution, new exports, compilation, reconstruction edits or Ghidra reopening/mutation.',
        'Hashes prove these files match recorded identities, not live GUI state, saved annotation correctness or runtime behavior.',
        'Raw exports compare prior checkpoint hashes, not newly generated exports or freshly parsed original manifests.',
        'Repeatability cannot prove every interpretation or extend the scripts’ stated path/input coverage.',
        'Selected shared dependencies are recorded, not a complete environment/package dependency lock.']
    destination=ROOT/'analysis/evidence/validation/renderer-screenshot-history-checkpoint.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:{2*len(PAIRS)}/{2*len(PAIRS)} runs,{len(PAIRS)} committed evidence outputs reproduced,{len(protected)} protected files and{len(exports)} raw exports unchanged')


if __name__=='__main__':main()
