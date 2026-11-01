"""Reproduce eight HUD, menu and import static investigations without executing target code."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAIRS=[('hud_software_gate_boundary','hud-software-gate-boundary'),
       ('hud_list_bevel_history','hud-list-bevel-history'),
       ('hud_editor_draw_dispatch','hud-editor-draw-dispatch'),
       ('police_editor_asset_admission','police-editor-asset-admission'),
       ('dropdown_priority_history','dropdown-priority-history'),
       ('subtitle_style_history','subtitle-style-history'),
       ('ddraw_import_history','ddraw-import-history'),
       ('menu_callback_selection_history','menu-callback-selection-history')]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    prior_path='analysis/evidence/validation/later-static-mechanisms-checkpoint.json'
    prior=json.loads((ROOT/prior_path).read_text())
    result={'kind':'eight-hud-menu-import-static-checkpoint',
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
        'analysis/evidence/audits/reference-asset-pairs.json']]
    result['limits']=['Primary-agent16 static reruns, not independent semantic review, runtime, CI or whole-repository qualification.',
        'No target/API/instruction execution, new exports, compilation, reconstruction edits or Ghidra reopening/mutation.',
        'Hashes prove these files match recorded identities, not live GUI state, saved annotation correctness or runtime behavior.',
        'Raw exports compare prior checkpoint hashes, not newly generated exports or freshly parsed original manifests.',
        'Repeatability cannot prove every interpretation or extend the scripts’ stated path/input coverage.',
        'Selected shared dependencies are recorded, not a complete environment/package dependency lock.']
    destination=ROOT/'analysis/evidence/validation/hud-menu-import-checkpoint.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:{2*len(PAIRS)}/{2*len(PAIRS)} runs,{len(PAIRS)} committed evidence outputs reproduced,{len(protected)} protected files and{len(exports)} raw exports unchanged')


if __name__=='__main__':main()
