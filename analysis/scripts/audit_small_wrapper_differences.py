"""Hash-pinned static comparison of music-override and shell-open wrappers."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'small-wrapper-static-comparison', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/small-wrappers'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        imports = {i.address: i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534480] == 'ShellExecuteA'
        assert imports[0x53454c] == 'GetModuleHandleA'
        assert pe.get_data(0x136c30, 5) == b'open\0'
        spans = [(0x410460, 0x4104a1), (0x4104b0, 0x4104ee), (0x418cc0, 0x418ceb)]
        rows = []
        blobs[label] = []
        for a, b in spans:
            data = pe.get_data(a - 0x400000, b - a)
            blobs[label].append(data)
            path = capture / f'{label}-{a:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={a}', f'--stop-address={b}', relative], cwd=ROOT))
            rows.append({'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'imports': {'00534480': imports[0x534480], '0053454c': imports[0x53454c]}}
    for index, address in [(0, 0x410479), (1, 0x4104cf)]:
        a, b = blobs['original'][index], blobs['official_modern'][index]
        differences = [i for i, pair in enumerate(zip(a, b)) if pair[0] != pair[1]]
        start = [0x410460, 0x4104b0][index]
        assert differences == [address - start]
        assert a[address - start] == 6 and b[address - start] == 8
    old, new = blobs['original'][2], blobs['official_modern'][2]
    assert old[0x13:0x22] == bytes.fromhex('2eff154c455300502eff1580445300')
    assert new[0x0e:0x1c] == bytes.fromhex('6a00ff158044530031c0405a59c3')
    result['limits'] = ['Static inspection only; no shell invocation or audio playback.',
        'Original language-resource provenance and all caller effects remain outside this audit.']
    (ROOT / 'analysis/evidence/audits/small-wrapper-differences.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: two isolated 6-to-8 music comparisons and shell owner/call/return sequences')


if __name__ == '__main__':
    main()
