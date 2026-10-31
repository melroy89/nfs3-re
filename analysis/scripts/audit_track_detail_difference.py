"""Static track-chain detail selection and removed next-block classification."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-track-detail-comparison', 'range_end': 'exclusive', 'binaries': {}}
    images = {}
    capture = ROOT / 'analysis/captures/modern-differences/track-detail'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        spans = []
        for start, end in [(0x41cdc0, 0x41d210 if label == 'original' else 0x41d1f6), (0x41aa60, 0x41aaab if label == 'original' else 0x41aa97), (0x431c20, 0x431c25), (0x41d900, 0x41d953), (0x41da24, 0x41da33)]:
            data = pe.get_data(start - 0x400000, end - start)
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            spans.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        table = struct.unpack('<9I', pe.get_data(0x152e20, 36))
        assert table == (1, 0, 150, 2, 2, 100, 3, 4, 50)
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': spans, 'file_backed_table_00552e20': [list(table[i:i+3]) for i in range(0, 9, 3)]}
    old, new = [images[k] for k in ('original', 'official_modern')]
    result['identical_ranges'] = []
    for start, end in [(0x41cdc0, 0x41ce96), (0x41cf0a, 0x41d1ef), (0x41d900, 0x41d953), (0x41da24, 0x41da33)]:
        a, b = [p.get_data(start - 0x400000, end - start) for p in (old, new)]
        assert a == b
        result['identical_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(a).hexdigest()})
    a, b = [p.get_data(0x1cdc0, 0x42f) for p in (old, new)]
    changed = [0x41cdc0+i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert len(changed) == 115 and min(changed) == 0x41ce97 and max(changed) == 0x41cf09
    assert new.get_data(0x1cec8, 0x42) == b'\x90' * 0x42
    assert old.get_data(0x31c20, 5) == bytes.fromhex('5589e55dc3')
    result['changed_byte_count'] = len(changed)
    result['changed_addresses'] = [f'{n:08x}' for n in changed]
    result['limits'] = ['Static only; no rendered output or instruction execution.', 'File-backed table is not proof of its later runtime contents.', 'No complete layout, transitive helper equivalence or historical release attribution.']
    (ROOT / 'analysis/evidence/audits/original-modern-track-detail.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: paired track-chain bodies, detail table, changed classifier and removed next-block call')


if __name__ == '__main__':
    main()
