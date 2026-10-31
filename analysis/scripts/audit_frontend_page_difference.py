"""Compare frontend page switch extension and selected record/resource; no execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-frontend-page-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No rendering, decompression or target execution.', 'Record 75 selection at runtime not proven.']}
    capture = ROOT/'analysis/captures/modern-differences/frontend-page'; capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x441cb0, 0x44236c), (0x437820, 0x4378b6)]
        if label == 'official_modern':
            spans += [(0x4f1f58, 0x4f1f88), (0x4f26a0, 0x4f270e), (0x4f2710, 0x4f2736)]
        spans += [(0x44240c, 0x442448)]
        spans += [(0x4ef1e0, 0x4ef26f), (0x4f2620, 0x4f269f), (0x4f2560, 0x4f261b),
                  (0x5102a4, 0x5102ef), (0x5102f0, 0x5103ff), (0x510400, 0x510416)]
        rows = []
        for start, end in spans:
            path = capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}',
                f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        row = {'path': relative, 'sha256': expected, 'spans': rows,
               'switch_table_first_five': [f'{a:08x}' for a in struct.unpack('<5I', pe.get_data(0x41c90,20))],
               'record_75_words': [f'{a:08x}' for a in struct.unpack('<4I',pe.get_data(0x155c08,16))]}
        records = [struct.unpack('<4I',pe.get_data(0x155758+16*i,16)) for i in range(77)]
        sentinel = next(i for i, words in enumerate(records) if words[1] == 0)
        assert sentinel == 76
        row['first_zero_offset4_sentinel_index'] = sentinel
        row['last_text_page_and_sentinel'] = {str(i): [f'{x:08x}' for x in records[i]] for i in (74,75,76)}
        row['page_table_0_through_sentinel_sha256'] = hashlib.sha256(pe.get_data(0x155758,77*16)).hexdigest()
        if label == 'official_modern':
            row['resource_loader_imports'] = {f'{i.address:08x}': i.name.decode()
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                if i.address in (0x53453c, 0x534540, 0x534570)}
            resources = []
            for t in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                for n in t.directory.entries:
                    if t.id == 10 and str(n.name) == 'ABOUT.QFS':
                        for lang in n.directory.entries:
                            data = lang.data.struct
                            payload = pe.get_data(data.OffsetToData, data.Size)
                            assert payload[:2] == bytes.fromhex('10fb')
                            resources.append({'type': 10, 'name': str(n.name), 'language': lang.id,
                                'rva': f'{data.OffsetToData:08x}', 'size': data.Size,
                                'sha256': hashlib.sha256(payload).hexdigest(),
                                'first_32_bytes_hex': payload[:32].hex(),
                                'header_declared_unpacked_size': int.from_bytes(payload[2:5], 'big')})
            assert len(resources) == 1
            row['about_resource'] = resources[0]
            row['sixth_switch_target'] = f'{struct.unpack("<I",pe.get_data(0x41ca4,4))[0]:08x}'
            row['strings'] = {f'{a:08x}': pe.get_data(a-0x400000,40).split(b'\0')[0].decode('ascii') for a in (0x53f7d4,0x53f7e0)}
        result['binaries'][label] = row
    result['identical_dependency_ranges'] = []
    for start, end in ((0x4ef1e0, 0x4ef26f), (0x4f2620, 0x4f269f), (0x4f2560, 0x4f261b),
                       (0x5102a4, 0x5102ef), (0x5102f0, 0x5103ff), (0x510400, 0x510416)):
        pair = [p.get_data(start-0x400000, end-start) for p in images]
        assert pair[0] == pair[1]
        result['identical_dependency_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}'})
    bodies = [p.get_data(0x41cb0,0x44236c-0x441cb0) for p in images]
    changes = [0x441cb0+i for i,(a,b) in enumerate(zip(*bodies)) if a!=b]
    assert changes == [0x441d03]
    result['main_body_changed_addresses'] = [f'{a:08x}' for a in changes]
    assert result['binaries']['original']['switch_table_first_five'] == result['binaries']['official_modern']['switch_table_first_five']
    assert result['binaries']['official_modern']['sixth_switch_target'] == '00437820'
    (ROOT/'analysis/evidence/audits/original-modern-frontend-page.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baselines, one-byte main-body delta, retained five targets, new resource record')


if __name__ == '__main__':
    main()
