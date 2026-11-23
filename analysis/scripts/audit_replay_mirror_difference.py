"""Static replay mirror/variant admission witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS=[(0x484450,0x4844c0),(0x422aa0,0x422bd0),
       (0x4844c0,0x484599),(0x482d6b,0x482d8e),
       (0x482f5b,0x482f7f),(0x4c5097,0x4c50af),
       (0x484070,0x4840ae),(0x484260,0x4842de),(0x4c5017,0x4c5031),
       (0x48f7b0,0x48f81b),(0x48f970,0x48fa09),(0x48f550,0x48f69a),
       (0x431800,0x43182d),(0x48d274,0x48d2b1),(0x4bc729,0x4bc77c)]

HISTORICAL_ARCHIVES = {
    '1.3.1': ('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934', 'original'),
    '1.4.0': ('8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9', 'official_modern'),
}


def main():
    capture=ROOT/'analysis/captures/modern-differences/replay-mirror'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-replay-mirror-comparison','range_end':'exclusive','binaries':{},
        'limits':['No replay, input or target execution.','Default F7-to-action chain is static; actual keyboard delivery/rendered mirror unverified.']}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in SPANS:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        assert pe.get_data(0x48f9c8-0x400000,5)==bytes.fromhex('be04410000')
        assert pe.get_data(0x48f9be-0x400000, 5) == bytes.fromhex('b9043f0000')
        assert pe.get_data(0x48f9dd-0x400000, 6) == bytes.fromhex('890dd0c37900')
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    retained_gates = {'004844c0', '00482d6b', '00482f5b'}
    retained_hud_paths = {'00484070', '00484260', '004c5017', '0048f970'}
    retained_f7_paths = {'004c5097', '0048f7b0', '0048f550', '00431800'}
    retained_render_paths = {'0048d274', '004bc729'}
    retained_starts = retained_gates | retained_hud_paths | retained_f7_paths | retained_render_paths
    changed_starts = {'00484450', '00422aa0'}
    span_hashes = {
        label: {row['start']: row['bytes_sha256'] for row in binary['spans']}
        for label, binary in result['binaries'].items()
    }
    for start in retained_starts:
        assert span_hashes['original'][start] == span_hashes['official_modern'][start], start
    for start in changed_starts:
        assert span_hashes['original'][start] != span_hashes['official_modern'][start], start
    result['retained_gate_starts'] = sorted(retained_gates)
    result['retained_hud_path_starts'] = sorted(retained_hud_paths)
    result['retained_f7_path_starts'] = sorted(retained_f7_paths)
    result['retained_render_path_starts'] = sorted(retained_render_paths)
    result['changed_starts'] = sorted(changed_starts)
    release_starts = retained_starts | changed_starts
    result['historical'] = {}
    for version, (digest, baseline) in HISTORICAL_ARCHIVES.items():
        archive = (ROOT / 'analysis/captures/modern-differences/upstream/history'
                   / f'nfs3_modern_patch_v{version}.7z')
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
        binary = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        pe = pefile.PE(data=binary, fast_load=True)
        matches = {}
        for row in result['binaries'][baseline]['spans']:
            if row['start'] in release_starts:
                start = int(row['start'], 16)
                span = pe.get_data(start - pe.OPTIONAL_HEADER.ImageBase,
                                   int(row['end'], 16) - start)
                matches[row['start']] = hashlib.sha256(span).hexdigest()
                assert matches[row['start']] == row['bytes_sha256'], (version, row['start'])
        assert matches.keys() == release_starts
        result['historical'][version] = {
            'archive': str(archive.relative_to(ROOT)), 'archive_sha256': digest,
            'exe_sha256': hashlib.sha256(binary).hexdigest(),
            'matched_baseline': baseline, 'span_hashes': matches,
        }
    result['binding_chain']={'encoded':'00004104','slot':'0079c3cc',
        'shared_action_base':'0079c3a0','action_index':11,'scan_index':'0041',
        'action_builder_identical':True}
    (ROOT/'analysis/evidence/audits/original-modern-replay-mirror.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: replay toggle, eligibility, refresh and input witnesses for both baselines')


if __name__=='__main__':main()
