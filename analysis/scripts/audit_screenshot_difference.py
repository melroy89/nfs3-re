"""Hash-pinned static witnesses for original/Modern screenshot paths.

Requires pefile and GNU objdump; does not run the game or probe instructions.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4c5243,0x4c5281),(0x4c546e,0x4c548e),(0x4eb1c0,0x4eb1c8),(0x451810, 0x451836), (0x452410, 0x452420),
        (0x4c4490, 0x4c45c7), (0x4b6520, 0x4b6588), (0x4eb160, 0x4eb1c0),
        (0x4eafc0, 0x4eb153), (0x5040b8, 0x504133)],
    'official_modern': [(0x4c5243,0x4c5281),(0x4c546e,0x4c548e),(0x4eb1c0,0x4eb1c8),(0x4ccb84, 0x4ccc40), (0x4cdc50, 0x4cdcbb),
        (0x4c4480, 0x4c45cb), (0x4e3078, 0x4e3248), (0x4b5680, 0x4b5696),
        (0x4f1f58, 0x4f1f88), (0x4f1fb0, 0x4f1fc9)],
}
STRINGS = {'original': [0x5401d8, 0x53feb0, 0x53fef4],
           'official_modern': [0x53f7f4, 0x53f804, 0x53f6cc, 0x53f7e8]}


def main():
    capture = ROOT/'analysis/captures/modern-differences/screenshots'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-screenshot-path-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['No screenshot or target instructions executed.',
            'Spans are instruction witnesses, not a complete interprocedural graph.',
            'Same-address regions do not imply function correspondence.']}
    images={}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data);images[label]=pe
        rows = []
        for start, end in SPANS[label]:
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = capture/f'{label}-{start:08x}.asm'
            output.write_text(text)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        strings = {f'{va:08x}': pe.get_data(va-0x400000, 180).split(b'\0')[0].decode('ascii')
                   for va in STRINGS[label]}
        result['binaries'][label] = {'path': relative, 'sha256': expected,
            'spans': rows, 'strings': strings}
        if label == 'official_modern':
            resources = []
            for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                for name in kind.directory.entries:
                    if name.name and str(name.name) == 'SNAP.WAV':
                        for language in name.directory.entries:
                            entry = language.data.struct
                            blob = pe.get_data(entry.OffsetToData, entry.Size)
                            assert kind.id == 10 and blob[:4] == b'RIFF' and blob[8:12] == b'WAVE'
                            resources.append({'type': kind.id, 'name': str(name.name),
                                'language': language.id, 'rva': f'{entry.OffsetToData:08x}',
                                'size': entry.Size, 'sha256': hashlib.sha256(blob).hexdigest()})
            assert len(resources) == 1
            result['binaries'][label]['sound_resource'] = resources
            result['binaries'][label]['sound_imports'] = {f'{i.address:08x}': i.name.decode()
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                if i.name and i.address in [0x53453c,0x534540,0x534570,0x534668]}
    old,new=images['original'],images['official_modern']
    assert old.get_data(0xeb1c0,8)==new.get_data(0xeb1c0,8)==bytes.fromhex('0fb68018485600c3')
    assert new.get_data(0xc524e,51)==b'\x90'*51
    assert sum(a!=b for a,b in zip(old.get_data(0xc524e,51),new.get_data(0xc524e,51)))==51
    assert old.get_data(0xc5255,5).hex()=='b838000000'
    assert old.get_data(0xc5263,5).hex()=='b819000000'
    assert old.get_data(0xc5271,5).hex()=='bf01000000'
    assert old.get_data(0xc5477,13).hex()=='85ff7409e810f0ffff31ffeb0a'
    assert new.get_data(0xc5477,15).hex()=='a1a0367d00e8ff71ffffe8faefffff'
    result['race_loop_capture_branch']={'removed_poll':'004c5243..004c5276',
        'poll_admission':'signed006fd3b0<2 OR signed006fd3a0>1',
        'key_bytes':['00564850(index38h)','00564831(index19h)'],
        'latch':'Both nonzero -> EDI1; no local key-edge detection',
        'original_draw_gate':'When007d3674==0,EDI nonzero ->004c4490 thenEDI0; else004bc680',
        'modern_draw_gate':'When007d3674==0,call004bc680 then004c4480',
        'outside_interval':'004c524e..004c5281,51 NOP-replaced bytes; begins inside originalCMP004c524c operand',
        'limits':'No complete-loop cadence, physical key delivery, captured frame identity or successful write established.'}
    output = ROOT/'analysis/evidence/audits/original-modern-screenshots.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: both input hashes and original/Modern screenshot instruction captures')


if __name__ == '__main__':
    main()
