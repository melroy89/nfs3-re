"""Hash-pinned preset selection/data comparison; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-parameter-preset-comparison', 'range_end': 'exclusive', 'binaries': {},
              'limits': ['No preset/game execution.', 'Record field meanings and selector admission remain bounded.']}
    capture = ROOT/'analysis/captures/modern-differences/parameter-preset'
    capture.mkdir(parents=True, exist_ok=True)
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes(); assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        end = 0x41d863 if label == 'original' else 0x41d6e4
        path = capture/f'{label}-0041d620.asm'
        path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', '--start-address=0x41d620',
            f'--stop-address={end}', relative], cwd=ROOT))
        row = {'path': relative, 'sha256': expected, 'start': '0041d620', 'end': f'{end:08x}',
               'bytes_sha256': hashlib.sha256(pe.get_data(0x1d620, end-0x41d620)).hexdigest(),
               'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'conversion_scale_hex': pe.get_data(0x136ce4, 8).hex()}
        if label == 'official_modern':
            data = pe.get_data(0x1d6e4, 256)
            row['preset_table'] = {'address': '0041d6e4', 'size': 256,
                'sha256': hashlib.sha256(data).hexdigest(),
                'words_by_preset_and_16_byte_block': [[list(struct.unpack_from('<8H', data, i*64+j*16))
                                                      for j in range(4)] for i in range(4)]}
        else:
            row['original_scale_tables_hex'] = pe.get_data(0x1a8b0, 24).hex()
        result['binaries'][label] = row
    assert result['binaries']['original']['conversion_scale_hex'] == result['binaries']['official_modern']['conversion_scale_hex']
    (ROOT/'analysis/evidence/audits/original-modern-parameter-preset.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete preset bodies, table bytes and retained conversion scale')


if __name__ == '__main__':
    main()
