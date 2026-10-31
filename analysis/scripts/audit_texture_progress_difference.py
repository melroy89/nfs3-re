"""Compare indexed-texture progress arithmetic without executing game code."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-texture-progress-comparison', 'range_end': 'exclusive', 'binaries': {}}
    images = {}
    capture = ROOT / 'analysis/captures/modern-differences/texture-progress'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        rows = []
        for start, end in [(0x41db10, 0x41dbb4), (0x4ea654, 0x4ea658), (0x4ea658, 0x4ea665)]:
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        values = [struct.unpack('<f', pe.get_data(a-0x400000, 4))[0] for a in (0x41db20, 0x41db27, 0x536d1c)]
        assert values == ([15.0, 43.0, 15.0] if label == 'original' else [81.0, 14.0, 81.0])
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows, 'fallback_step_start_budget': values}
    for start, end in [(0x4ea654, 0x4ea658), (0x4ea658, 0x4ea665), (0x41db31, 0x41db77), (0x41dba7, 0x41dbb4)]:
        a,b = [p.get_data(start-0x400000,end-start) for p in images.values()]
        assert a == b
    result['limits'] = ['Static only; no visible progress, duration or renderer acceptance tested.', 'Budget/count division and each accumulator update round through binary32 under ambient x87 state.', 'Skipped null entries and abort paths can prevent the nominal endpoint.']
    (ROOT / 'analysis/evidence/audits/original-modern-texture-progress.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: indexed-texture progress constants, complete paired bodies and collection helpers')


if __name__ == '__main__':
    main()
