"""Static original/Modern display-mode enumerator and menu-list witnesses.

Requires pefile/GNU objdump; no game, driver or instruction execution.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4bed90, 0x4bee72), (0x448210, 0x4482e8)],
    'official_modern': [(0x4bed90, 0x4beeb0), (0x448210, 0x448345)],
}


def main():
    capture = ROOT/'analysis/captures/modern-differences/display-modes'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-display-mode-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['Driver-provided records were not executed or mutated.',
            'Menu count boundary is not a proved reachable storage fault.',
            'Driver DLL enumeration limits and actual UI behavior remain untested.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        rows = []
        for start, end in SPANS[label]:
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            output = capture/f'{label}-{start:08x}.asm'
            output.write_text(text)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly': str(output.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    output = ROOT/'analysis/evidence/audits/original-modern-display-modes.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: original/Modern identity and enumerator/menu instruction captures')


if __name__ == '__main__':
    main()
