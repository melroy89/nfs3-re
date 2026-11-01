"""Static historical car-detail budget and wheel tick sources; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble
from audit_endpoint_comma_history import HISTORY


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    capture = ROOT/'analysis/captures/modern-differences/vehicle-detail-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-vehicle-detail-release-boundary', 'binaries': {},
        'limits': ['No rendering, instruction or game execution.',
                   'Local detail/tick mechanisms do not prove all wheels rotate in mirror or split-screen.',
                   'Model availability, classifier outputs, budget state, x87 state and complete object lifetime remain conditional.']}
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert sha(raw) == expected
        images[label] = (raw, {'path': relative, 'sha256': expected})
    for version, (archive_hash, executable_hash) in HISTORY.items():
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive = ROOT/relative
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        assert sha(raw) == executable_hash
        images[version] = (raw, {'archive': relative, 'archive_sha256': archive_hash,
                                'member': 'nfs3.exe', 'sha256': executable_hash})
    common = [(0x4bb5d0,0x4bba07), (0x4bbad0,0x4bbb94), (0x4bb4c0,0x4bb5ce),
              (0x4bae00,0x4bb10f), (0x4bb200,0x4bb495)]
    ends = {'original':0x4bbcb4, '1.4.0':0x4bbcb4, '1.5.0':0x4bbcd5, 'official_modern':0x4bbce3}
    witnesses = {}
    for label, (raw, identity) in images.items():
        pe = pefile.PE(data=raw)
        def get(start,end):
            return pe.get_data(start-0x400000,end-start)
        spans = common+[(0x4bbba0,ends[label]), (0x4b9140,0x4b9280), (0x4b9280,0x4b93bf)]
        witnesses[label] = {}
        rows = []
        for start,end in spans:
            data = get(start,end);witnesses[label][start] = data
            path = capture/f'{label}-{start:08x}.asm'
            path.write_text('\n'.join(disassemble(data,start))+'\n')
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                         'bytes':len(data),'sha256':sha(data),'assembly':str(path.relative_to(ROOT)),
                         'assembly_sha256':sha(path.read_bytes())})
        descriptor = struct.unpack('<5I',get(0x5566f4,0x556708))
        assert descriptor == (0x537fa4,0x55623a,0,0,0x6fbc1c)
        assert get(0x537fa4,0x537fae) == b'cardetail\0'
        assert struct.unpack('<4H',get(0x55623a,0x556242)) == (187,186,185,0)
        tables = get(0x4bb498,0x4bb4b8)
        assert struct.unpack('<8I',tables) == (0x4bb53e,0x4bb549,0x4bb554,0x4bb55f,
                                             0x4bb576,0x4bb576,0x4bb576,0x4bb581)
        result['binaries'][label] = {**identity,'spans':rows,
            'car_detail_descriptor':[f'{v:08x}' for v in descriptor],
            'label_ids':[187,186,185], 'dispatch_table_hex':tables.hex(),
            'threshold_table_hex':get(0x55fdf4,0x55fe24).hex(),
            'threshold_rows':list(struct.iter_unpack('<4f',get(0x55fdf4,0x55fe24))),
            'context_scale_binary64':struct.unpack('<2d',get(0x540130,0x540140))}
    for start,_ in common:
        assert len({w[start] for w in witnesses.values()}) == 1
    assert witnesses['original'][0x4bbba0] == witnesses['1.4.0'][0x4bbba0]
    # Complete 1.5.0 gate, absent in the original/1.4.0 unconditional call site.
    gate = witnesses['1.5.0'][0x4bbba0][0x4b:0x5b]
    assert gate.hex() == '833d1cbc6f0000740789f0e8d5feffff'
    for start,load in ((0x4b9140,0x4b9157),(0x4b9280,0x4b9296)):
        assert witnesses['original'][start] == witnesses['1.4.0'][start]
        assert witnesses['1.5.0'][start] == witnesses['official_modern'][start]
        old,new = witnesses['1.4.0'][start],witnesses['1.5.0'][start]
        changed = [start+i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
        assert changed == list(range(load+1,load+5))
    archive = ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha(archive.read_bytes()) == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english = subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels = []
    for ident in (187,186,185):
        offset = struct.unpack_from('<I',english,ident*4)[0]
        labels.append(english[offset:english.index(b'\0',offset)].decode('latin1'))
    assert labels == ['High','Medium','Low']
    result['label_evidence'] = {'archive_sha256':sha(archive.read_bytes()),
        'member':'fedata/text/text.eng','sha256':sha(english),'ids':[187,186,185],'labels':labels}
    result['checks'] = {'common_complete_bodies_identical': [f'{a:08x}' for a,_ in common],
        'original_dispatcher_identical_140':True, '150_budget_gate_hex':gate.hex(),
        '150_predicate':'006fbc1c != 0; High0 skips entire004bbad0, Medium1/Low2 admit',
        '150_wheel_helpers_identical_final':True,
        'wheel_tick_change':'0055fe28 global snapshot -> object+8c0 in both helpers',
        'thresholds_140_150_final_identical':len({result['binaries'][k]['threshold_table_hex']
            for k in ('1.4.0','1.5.0','official_modern')})==1}
    assert result['checks']['thresholds_140_150_final_identical']
    (ROOT/'analysis/evidence/audits/vehicle-detail-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired historical detail gate, unchanged classifier/render bodies and wheel tick-source boundary')


if __name__ == '__main__':
    main()
