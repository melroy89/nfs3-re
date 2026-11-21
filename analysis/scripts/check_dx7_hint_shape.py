"""Reproduce five DX7, hint, label and shape investigations without executing target code."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAIRS=[('dx7_package_introduction','dx7-package-introduction'),
       ('dx7_dither_requests','dx7-dither-requests'),
       ('connect_escape_hint_history','connect-escape-hint-history'),
       ('widescreen_label_history','widescreen-label-history'),
       ('map_marker_shape_history','map-marker-shape-history')]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    prior_path='analysis/evidence/validation/renderer-menu-counter-followup-checkpoint.json'
    prior=json.loads((ROOT/prior_path).read_text())
    result={'kind':'five-dx7-hint-shape-checkpoint',
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
        'analysis/scripts/audit_endpoint_comma_history.py','analysis/scripts/audit_screenshot_counter_history.py',
        'analysis/captures/modern-differences/dx7-api-headers/d3dtypes.h',
        'analysis/captures/modern-differences/dx7-api-headers/d3d.h',
        'nfs3_decomp.rep/Electronic Arts/Need For Speed III/gamedata_org/DashHud/HUD98.FSH']]
    result['limits']=['Primary-agent10 static reruns, not independent semantic review, runtime, CI or whole-repository qualification.',
        'No target/API/instruction execution, new exports, compilation, reconstruction edits or Ghidra reopening/mutation.',
        'Hashes prove these files match recorded identities, not live GUI state, saved annotation correctness or runtime behavior.',
        'Raw exports compare prior checkpoint hashes, not newly generated exports or freshly parsed original manifests.',
        'Repeatability cannot prove every interpretation or extend the scripts’ stated path/input coverage.',
        'Selected shared dependencies are recorded, not a complete environment/package dependency lock.']
    destination=ROOT/'analysis/evidence/validation/dx7-hint-shape-checkpoint.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:{2*len(PAIRS)}/{2*len(PAIRS)} runs,{len(PAIRS)} committed evidence outputs reproduced,{len(protected)} protected files and{len(exports)} raw exports unchanged')


if __name__=='__main__':main()
