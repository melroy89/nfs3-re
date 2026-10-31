"""Hash-pinned CPU tier producer/consumer witnesses; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4f1ef0, 0x4f209d), (0x472d89, 0x472dfa), (0x49616c, 0x4961ab)],
    'official_modern': [(0x4f1c70, 0x4f1e9e), (0x50ea85, 0x50eaa7),
        (0x472d10, 0x472e1d), (0x49616f, 0x4961ab), (0x4a3e07, 0x4a3e0c)],
}


def main():
    capture = ROOT/'analysis/captures/modern-differences/cpu-tier'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-cpu-tier-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['No CPUID, benchmark, game or target instruction execution.',
        'Same-address global changes meaning; not a measured host CPU rating.',
        'Legacy/extended CPUID paths and complete tier consumers remain bounded.']}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        rows = []
        selected=SPANS[label]+[(0x4f1ff0,0x4f22b0),(0x4f20b0,0x4f216d),(0x4f2170,0x4f21bd),(0x4f21c0,0x4f22af)]
        for start, end in selected:
            out = capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        removed=pe.get_data(0xf1ff0,0x2c0)
        if label=='official_modern':assert set(removed)=={0x90}
        else:
            assert pe.get_data(0xf20de,2)==bytes.fromhex('0f31')
            assert pe.get_data(0xf20fc,2)==bytes.fromhex('0f31')
            assert pe.get_data(0xf219d,2)==bytes.fromhex('f7fb')
        item = {'path':relative,'sha256':expected,'spans':rows}
        if label == 'official_modern':
            item['six_byte_default_tables'] = {f'{va:08x}':list(pe.get_data(va-0x400000,6))
                for va in range(0x472e20,0x472e56,6)}
            item['family_warning'] = pe.get_data(0x53d231-0x400000,150).split(b'\0')[0].decode('ascii')
        result['binaries'][label] = item
    out = ROOT/'analysis/evidence/audits/original-modern-cpu-tier.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: CPU tier baseline identities, producer/consumer spans and tables')


if __name__ == '__main__':
    main()
