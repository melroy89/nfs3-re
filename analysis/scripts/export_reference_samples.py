"""Export only the three readiness samples, twice, from an isolated saved snapshot.

Requires installed Ghidra 12.1.4/JDK21; creates reference files, not maintained C.
No game execution, instruction probes, C compilation, linking or installation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import time

ENTRIES = ('00485c30', '004abd9c', '00518640')
DB = Path('nfs3_decomp.rep/idata/f9/~00000f9f.db/db.3144.gbf')
EXE = Path('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe')
DB_SHA = '00b157c74363b3d10efd1138c537d7127f7bbf7cd97dfbf52dc4ccbb86fa2c5a'
EXE_SHA = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, help='Exact saved Git commit')
    parser.add_argument('--ghidra', type=Path, required=True)
    parser.add_argument('--java-home', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    baseline = subprocess.check_output(['git', 'rev-parse', args.baseline + '^{commit}'], cwd=repo, text=True).strip()
    if sha(repo / DB) != DB_SHA or sha(repo / EXE) != EXE_SHA:
        raise SystemExit('Working baseline fingerprint mismatch')
    ghidra = args.ghidra.resolve()
    script = repo / 'analysis/scripts/ghidra/ExportReferenceSample.java'
    tools = {str(p.relative_to(ghidra)): sha(p) for p in (
        ghidra / 'Ghidra/Features/Decompiler/lib/Decompiler.jar',
        ghidra / 'Ghidra/Features/Decompiler/lib/Decompiler-src.zip',
        ghidra / 'Ghidra/Features/Decompiler/os/linux_x86_64/decompile',
    )}
    config = {
        'ghidra_version': '12.1.4 PUBLIC', 'language': 'x86:LE:32:default', 'compiler_spec': 'windows',
        'exporter': 'ghidra.app.util.exporter.CppExporter',
        'options': {'create_header': True, 'create_c': True, 'emit_types': False,
                    'emit_referenced_globals': True, 'exclude_tags': True, 'tag_filter': '',
                    'comment_style': 'CStyle', 'warning_comments': True,
                    'defaults': 'new DecompileOptions() in pinned installed JAR',
                    'decompile_timeout_seconds': 30, 'entry_process_deadline_seconds': 120},
        'tool_hashes': tools, 'runner_java_sha256': sha(script),
        'runner_python_sha256': sha(Path(__file__).resolve()),
        'locale': 'C.UTF-8', 'timezone': 'UTC', 'newline': 'LF',
    }
    options_digest = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    root = repo / 'analysis/captures/reference-exports' / baseline / options_digest
    if root.exists():
        raise SystemExit('Refusing to overwrite prior runs: ' + str(root))
    root.mkdir(parents=True)
    write_json(root / 'configuration.json', config)
    identity = {'git_commit': baseline, 'executable_sha256': EXE_SHA, 'database_path': str(DB),
                'database_sha256': DB_SHA, 'options_digest': options_digest}
    env = dict(os.environ, JAVA_HOME=str(args.java_home), LC_ALL='C.UTF-8', LANG='C.UTF-8', TZ='UTC')
    manifests = []
    with tempfile.TemporaryDirectory(prefix='nfs3-reference-export-') as temp:
        work = Path(temp)
        archive = work / 'baseline.tar'
        with archive.open('wb') as stream:
            subprocess.run(['git', 'archive', '--format=tar', baseline], cwd=repo, stdout=stream, check=True)
        identity['git_archive_sha256'] = sha(archive)
        for run_number in (1, 2):
            snapshot = work / ('project-' + str(run_number))
            snapshot.mkdir()
            with tarfile.open(archive) as package:
                package.extractall(snapshot, filter='data')
            if sha(snapshot / DB) != DB_SHA or sha(snapshot / EXE) != EXE_SHA:
                raise RuntimeError('Archived baseline mismatch')
            output = root / ('run-' + str(run_number))
            output.mkdir()
            manifest = {'schema': 1, 'run': run_number, 'baseline': dict(identity), 'configuration': config,
                        'selection': list(ENTRIES), 'attempts': [],
                        'exclusions': {'local_count': 4130, 'external_count': 207,
                            'rule': 'All saved local entries except the three selected VAs, plus all external entries',
                            'local_inventory_sha256': '94b4ca701df43c7106503e0b6ce40fb590c5b3d920ac62900444fed4af8716d7'}}
            java_version = subprocess.run([str(args.java_home / 'bin/java'), '-version'], capture_output=True, text=True, check=True)
            manifest['java_version'] = java_version.stderr.strip()
            for entry in ENTRIES:
                log = output / (entry + '.log')
                command = [str(ghidra / 'support/analyzeHeadless'), str(snapshot),
                    'nfs3_decomp/Electronic Arts/Need For Speed III', '-process', 'nfs3.exe',
                    '-readOnly', '-noanalysis', '-scriptPath', str(script.parent),
                    '-postScript', script.name, entry, str(output)]
                attempt = {'entry': entry, 'process_deadline_seconds': 120, 'log': log.name}
                start = time.monotonic()
                try:
                    with log.open('w') as stream:
                        completed = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=120)
                    attempt['process_exit_code'] = completed.returncode
                except subprocess.TimeoutExpired:
                    attempt.update(status='timeout', failure='Headless process exceeded 120 seconds')
                result = output / (entry + '.result.json')
                if result.exists():
                    attempt['export_result'] = json.loads(result.read_text())
                    if 'status' not in attempt:
                        attempt['status'] = attempt['export_result']['status'] if attempt['process_exit_code'] == 0 else 'failure'
                elif 'status' not in attempt:
                    attempt.update(status='failure', failure='No result ledger produced; inspect headless log')
                attempt['elapsed_seconds'] = time.monotonic() - start
                attempt['log_sha256'] = sha(log)
                attempt['headless_diagnostics'] = [line for line in log.read_text().splitlines() if 'WARN ' in line or 'ERROR ' in line]
                manifest['attempts'].append(attempt)
                write_json(output / 'manifest.json', manifest)
                print('run', run_number, entry, attempt['status'], flush=True)
            manifest['isolated_database_unchanged'] = sha(snapshot / DB) == DB_SHA
            manifest['counts'] = {status: sum(a['status'] == status for a in manifest['attempts'])
                                  for status in ('success', 'failure', 'timeout', 'cancelled')}
            write_json(output / 'manifest.json', manifest)
            manifests.append(manifest)
    comparisons = []
    for entry in ENTRIES:
        for suffix in ('.c', '.h', '.options.xml'):
            a, b = [root / ('run-' + str(run)) / (entry + suffix) for run in (1, 2)]
            comparisons.append({'file': entry + suffix, 'run_1_sha256': sha(a) if a.exists() else None,
                                'run_2_sha256': sha(b) if b.exists() else None,
                                'identical': a.exists() and b.exists() and a.read_bytes() == b.read_bytes()})
    comparison = {'baseline': identity, 'files': comparisons,
                  'all_outputs_identical': all(row['identical'] for row in comparisons),
                  'all_exports_successful': all(a['status'] == 'success' for m in manifests for a in m['attempts']),
                  'source_executable_unchanged': sha(repo / EXE) == EXE_SHA,
                  'source_database_unchanged': sha(repo / DB) == DB_SHA}
    write_json(root / 'comparison.json', comparison)
    print('RESULT_ROOT', root, flush=True)
    print('SUMMARY', json.dumps({k: v for k, v in comparison.items() if k not in ('baseline', 'files')}), flush=True)


if __name__ == '__main__':
    main()
