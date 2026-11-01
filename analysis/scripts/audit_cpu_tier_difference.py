"""Hash-pinned CPU tier producer/consumer witnesses; no target execution."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4f1ea0,0x4f1eea),(0x4f1ef0, 0x4f209d), (0x472d89, 0x472dfa), (0x49616c, 0x4961ab)],
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
            assert struct.unpack('<d',pe.get_data(0x14c9b0,8))[0] == -8.0
            assert pe.get_data(0xf1ebe,11) == bytes.fromhex('dd1c24dc1c24dfe09e770a')
            assert pe.get_data(0xf1ed3,13) == bytes.fromhex('dd0424dc0db0c95400d95c2408')
            assert pe.get_data(0xf20de,2)==bytes.fromhex('0f31')
            assert pe.get_data(0xf20fc,2)==bytes.fromhex('0f31')
            assert pe.get_data(0xf219d,2)==bytes.fromhex('f7fb')
        item = {'path':relative,'sha256':expected,'spans':rows}
        if label == 'official_modern':
            item['six_byte_default_tables'] = {f'{va:08x}':list(pe.get_data(va-0x400000,6))
                for va in range(0x472e20,0x472e56,6)}
            item['family_warning'] = pe.get_data(0x53d231-0x400000,150).split(b'\0')[0].decode('ascii')
        if label == 'original':
            callers = [0x4f1fed,0x4f1fff,0x4f2011,0x4f2025,0x4f2037,0x4f2052,0x4f2064]
            for va in callers:
                encoded = pe.get_data(va-0x400000,5)
                assert encoded[0] == 0xe8 and va+5+int.from_bytes(encoded[1:],'little',signed=True) == 0x4f1ea0
            item['scaled_difference_helper'] = {
                'start': '004f1ea0', 'end_exclusive': '004f1eea', 'bytes': 74,
                'callers_in_estimator': [f'{va:08x}' for va in callers],
                'inputs': 'EAX,EDX DWORDs; one binary32 stack scale; RET4',
                'delta': 'Low32 EAX-EDX interpreted signed for FILD',
                'rounding': 'Product stored to binary32 then binary64 before comparing0 to binary64 copy.',
                'negative_ordered_product': 'Reload binary64 product, multiply by-8, store/reload binary32 for ST0 return.',
                'other_product': 'Reload initial binary32 product for ST0 return; includes unordered compare on nontrapping path.',
                'limit': 'Static arithmetic/caller contract; benchmark accuracy, units and runtime CW/inputs unverified.'}
        result['binaries'][label] = item
    original=pefile.PE(str(ROOT/SPECS['original'][0]))
    assert original.get_data(0xf2076,14).hex()=='69ff40420f0089f8893da4525600'
    assert original.get_data(0x72dab,12).hex()=='89c2be40420f00c1fa1ff7fe'
    assert original.get_data(0x96175,8).hex()=='81fb406bed077d07'
    assert original.get_data(0x96198,19).hex()=='813da4525600406bed077d07c7457e01000000'
    examples=[]
    for n in (166,200,266,267,2147,2148,2200,3000,4000,4294,4295,5000):
        bits=(n*1000000)&0xffffffff
        signed=bits if bits<0x80000000 else bits-0x100000000
        quotient=abs(signed)//1000000
        if signed<0:quotient=-quotient
        tier=sum(quotient>threshold for threshold in (166,200,233,266))
        movie=1 if signed<133000000 else (2 if signed<200000000 else 3)
        examples.append({'hypothetical_pre_multiply_integer':n,'stored_global_hex':f'{bits:08x}',
            'stored_global_signed':signed,'signed_division_quotient':quotient,
            'default_tier_before_renderer_adjustment':tier,'movie_conversion_selector':movie,
            'movie_local_field_forced_one':signed<133000000})
    assert (2147*1000000)<=0x7fffffff<(2148*1000000)
    assert next(r for r in examples if r['hypothetical_pre_multiply_integer']==2200)['default_tier_before_renderer_adjustment']==0
    assert next(r for r in examples if r['hypothetical_pre_multiply_integer']==5000)['default_tier_before_renderer_adjustment']==4
    result['original_signed_wrap_consequence']={
        'producer':'004f2076 IMUL EDI,EDI,1000000; EAX/global receive low32 bits, overflow flags not tested in this tail.',
        'graphics_consumer':'00472dab sign extends returned EAX into EDX:EAX; IDIV1000000; signed threshold ladder166/200/233/266.',
        'graphics_admission':'Capability branch00472d99..00472da6 can bypass estimator and retain initial tier4.',
        'movie_consumer':'00496175 signed133000000/200000000 thresholds; below133000000 also forces local+7e to1.',
        'first_signed_boundary_for_nonnegative_integer_input':2148,
        'examples':examples,'limits':['Arithmetic derivation, not executing estimator/CPUID/movie/game instructions.',
            'Pre-multiply integers are hypothetical inputs; not measured CPU MHz or proof the complete calibration produces them.',
            'Negative values select the lowest <=166 class, not a literal assignment of166 to the global.',
            'Multiple modulo2^32 wraps mean not every larger input selects the lowest tier.']}
    out = ROOT/'analysis/evidence/audits/original-modern-cpu-tier.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: CPU tier baseline identities, producer/consumer spans and tables')


if __name__ == '__main__':
    main()
