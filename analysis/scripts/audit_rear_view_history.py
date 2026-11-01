"""Static historical Rear View Detail comparison; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    baseline = json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())
    capture = ROOT/'analysis/captures/modern-differences/rear-view-history'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-rear-view-151-152-comparison', 'versions': {},
        'limits': ['Historical author-hosted identities, not authenticated retail provenance.',
                   'Finite integer-model derivation, not game execution or instruction emulation.',
                   'No rendered mirror quality, x87-state equality or whole-program equivalence claim.']}
    images = {}
    tables = {}
    for version, end, table in [('1.5.1', 0x41d6d8, 0x41d6d8), ('1.5.2', 0x41d6e4, 0x41d6e4)]:
        identity = baseline['packages'][version]
        archive = ROOT/identity['archive']
        assert sha(archive.read_bytes()) == identity['archive_sha256']
        raw = subprocess.check_output(['7z', 'x', '-so', str(archive), 'nfs3.exe'])
        assert sha(raw) == identity['executable_sha256']
        pe = pefile.PE(data=raw)
        images[version] = pe
        binary = capture/f'nfs3-{version}.exe'
        binary.write_bytes(raw)
        table_bytes = pe.get_data(table-0x400000, 256)
        tables[version] = struct.unpack('<128H', table_bytes)
        rows = []
        for start, stop in [(0x41d620, end), (0x41aa60, 0x41aa97),
                            (0x41cdc0, 0x41d1f6), (0x41ba3f, 0x41ba5c)]:
            output = capture/f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={stop}', str(binary.relative_to(ROOT))], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end_exclusive': f'{stop:08x}',
                         'bytes_sha256': sha(pe.get_data(start-0x400000, stop-start)),
                         'assembly': str(output.relative_to(ROOT)), 'assembly_sha256': sha(output.read_bytes())})
        result['versions'][version] = {'archive_sha256': identity['archive_sha256'],
            'executable_sha256': identity['executable_sha256'], 'spans': rows,
            'table_start': f'{table:08x}', 'table_sha256': sha(table_bytes),
            'table_words': list(tables[version])}
    old, new = images['1.5.1'], images['1.5.2']
    assert tables['1.5.1'] == tables['1.5.2']
    assert old.get_data(0x1d626,0x50) == new.get_data(0x1d626,0x50)
    assert old.get_data(0x136ce4,8) == new.get_data(0x136ce4,8)
    assert struct.unpack('<4H', old.get_data(0x1d7c0, 8)) == (150, 100, 40, 80)
    assert old.get_data(0x1d678, 25).hex() == '833dd8d16f000275d1833db0d36f000174c8bec0d74100ebc1'
    assert new.get_data(0x1d678, 40).hex() == '833db0d36f000174d1ba030000002b1528bc6f007ec4a1d8d16f0039d0760289d0c1e00601c6ebb2'
    unchanged = []
    for start, stop in [(0x41aa60, 0x41aa97), (0x41cdc0, 0x41d1f6),
                        (0x41ba3f, 0x41ba5c), (0x552e20, 0x552e44)]:
        assert old.get_data(start-0x400000, stop-start) == new.get_data(start-0x400000, stop-start)
        unchanged.append({'start': f'{start:08x}', 'end_exclusive': f'{stop:08x}'})
    cases = []
    words = tables['1.5.1']
    for selector in range(4):
        for night in range(2):
            for mode1 in range(2):
                offset = selector*32+night*16+mode1*8
                first = list(words[offset:offset+4])
                for detail in range(3):
                    second_old = list((150,100,40,80) if detail == 2 and not mode1 else words[offset+4:offset+8])
                    advance = 0 if mode1 else min(detail, max(3-selector, 0))*32
                    second_new = list(words[offset+4+advance:offset+8+advance])
                    assert len(second_new) == 4
                    cases.append({'selector': selector, 'night': night, 'mode_equals_1': mode1,
                        'rear_detail': detail, 'first_both': first, 'second_151': second_old,
                        'second_152': second_new, 'different': second_old != second_new})
    result['unchanged_selected_spans'] = unchanged
    result['derived_cases'] = cases
    result['different_second_record_cases'] = sum(c['different'] for c in cases)
    assert result['different_second_record_cases'] == 4 and len(cases) == 48
    result['model_scope'] = 'Selectors0..3, Night0/1, mode-equals-1 false/true, Rear View Detail0..2; tuples before WORD<<16 stores.'
    (ROOT/'analysis/evidence/audits/rear-view-151-152.json').write_text(json.dumps(result, indent=2)+'\n')
    print(f'PASS: historical pair and retained table/consumer spans; {result["different_second_record_cases"]}/{len(cases)} derived second-record tuples differ')


if __name__ == '__main__':
    main()
