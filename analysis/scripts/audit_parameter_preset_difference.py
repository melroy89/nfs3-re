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
            factors = struct.unpack('<6i', pe.get_data(0x1a8b0,24))
            assert factors == (49152,26869,19660,65536,36044,26214)
            pattern = bytes.fromhex('f7eac1e210c1e81011d0')
            body = pe.get_data(0x1d620,end-0x41d620)
            sites = [0x41d620+i for i in range(len(body)) if body.startswith(pattern,i)]
            assert sites == [0x41d66b,0x41d688,0x41d6a5,0x41d6bf,0x41d6d7,0x41d6ef,
                             0x41d722,0x41d73f,0x41d75c,0x41d776,0x41d78e,0x41d7a6]
            constants = [(0x41d662,440),(0x41d683,60),(0x41d6a0,92),
                         (0x41d6b6,500),(0x41d6d2,110),(0x41d6ea,150),
                         (0x41d719,440),(0x41d73a,60),(0x41d757,92),
                         (0x41d76d,500),(0x41d789,110),(0x41d7a1,150)]
            for va,n in constants:
                assert pe.get_data(va-0x400000,5) == b'\xb8'+struct.pack('<I',n<<16)
            row['original_exact_integer_arithmetic'] = {
                'multiply_sequence_sites': [f'{x:08x}' for x in sites],
                'factors_nonzero_006fd4c8': list(factors[:3]),
                'factors_zero_006fd4c8': list(factors[3:]),
                'formula': 'wrap32(N * signed_factor); N=440,60,92 for mode1, otherwise500,110,150',
                'derivation': 'All constants=N<<16; signed64 product low16=0, so SHR carry bit15=0; joined high/low halves equal low32(product arithmetic-shift16).',
                'scope': 'Mathematical consequence of asserted instructions; not original-instruction execution.'}

        result['binaries'][label] = row
    assert result['binaries']['original']['conversion_scale_hex'] == result['binaries']['official_modern']['conversion_scale_hex']
    old_factors = result['binaries']['original']['original_exact_integer_arithmetic']
    table = result['binaries']['official_modern']['preset_table']['words_by_preset_and_16_byte_block']
    table_bytes = b''.join(struct.pack('<8H',*block) for preset in table for block in preset)
    comparisons=[]
    for selector in range(4):
        for alternate in (False,True):
            factors = old_factors['factors_nonzero_006fd4c8' if alternate else 'factors_zero_006fd4c8']
            factor=factors[max(0,selector-1)]
            for mode1 in (False,True):
                constants=(440,60,92) if mode1 else (500,110,150)
                known=[(n*factor)&0xffffffff for n in constants]
                if selector==0: known=[known[0]]*3
                for aux in range(4):
                    start=selector*64+(32 if alternate else 0)+(16 if mode1 else 0)
                    advance=0 if mode1 else min(aux,max(0,3-selector))*64
                    sources=[start,start+8+advance]
                    new=[list(struct.unpack_from('<4H',table_bytes,x)) for x in sources]
                    comparisons.append({'selector':selector,'nonzero_006fd4c8':alternate,
                        'mode_equals1':mode1,'auxiliary_006fd1d8':aux,
                        'original_known_fields_28_38_3c': [known,known if mode1 else None],
                        'modern_source_offsets':sources,
                        'modern_words_24_28_38_3c':new,
                        'known_field_differences':sum(a != (b<<16) for i,record in enumerate(new)
                            if i==0 or mode1 for a,b in zip(known,record[1:]))})
    result['derived_integer_comparisons'] = {
        'kind':'mathematical evaluation of asserted static formulas and table; no target execution',
        'scope':'selectors0..3, both flag/mode branches, auxiliary representatives0..3; original untouched fields are null, not zero',
        'cases':comparisons,
        'cases_with_known_field_differences':sum(x['known_field_differences']>0 for x in comparisons)}

    assert len(comparisons)==64
    assert result['derived_integer_comparisons']['cases_with_known_field_differences']==48
    (ROOT/'analysis/evidence/audits/original-modern-parameter-preset.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: baselines, complete preset bodies, table bytes and retained conversion scale')


if __name__ == '__main__':
    main()
