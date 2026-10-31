"""Static FOV/projection comparison; no rendering or instruction execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

LEGACY=[(0x4fd280,0x4fd2a8),(0x4fd2b0,0x4fd3eb),(0x4fd3f0,0x4fd420),(0x4fd420,0x4fd482)]

SPANS={'original':LEGACY+[(0x4dbcc0,0x4dbd97),(0x4becd0,0x4bed69),(0x4bf260,0x4bf370)],
       'official_modern':[(0x4dbc48,0x4dbd35),(0x4becd0,0x4bed69),
                          (0x4bf260,0x4bf370),(0x4be748,0x4be74d)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/projection'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-projection-comparison','range_end':'exclusive','binaries':{},
        'limits':['No render/game/instruction execution.','Formula summaries do not claim bit-exact libm/x87 equivalence.']}
    bodies={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in SPANS[label]+[(0x4213b0,0x421441),(0x41bc90,0x41bf26)]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows}
        centre_refs=[]
        for address in (0x564434,0x564438):
            needle=struct.pack('<I',address);offset=0;hits=[]
            while True:
                offset=raw.find(needle,offset)
                if offset<0:break
                hits.append({'file_offset':offset,'mapped_operand_va':f'{pe.get_rva_from_offset(offset)+0x400000:08x}'})
                offset+=1
            expected_hits=({'00564434':['0042141c','004fd28f','004fd2cd','004fd440'],
                            '00564438':['0042142c','004fd2a2','004fd2e7','004fd460']}[f'{address:08x}']
                           if label=='original' else [])
            assert [h['mapped_operand_va'] for h in hits]==expected_hits
            centre_refs.append({'address':f'{address:08x}','matches':hits})
        bss=next(section for section in pe.sections if section.Name.startswith(b'.bss'))
        assert bss.PointerToRawData==0 and bss.Characteristics==0xc0000080 and bss.Misc_VirtualSize==0
        source_rows=[]
        for address,expected_count in [(0x5e1020,1),(0x5e102c,1),(0x5e1030,1),(0x5e1038,3)]:
            assert bss.VirtualAddress<=address-0x400000<bss.VirtualAddress+bss.SizeOfRawData
            off=0;matches=[]
            while True:
                off=raw.find(struct.pack('<I',address),off)
                if off<0:break
                matches.append({'operand_va':f'{pe.get_rva_from_offset(off)+0x400000:08x}',
                    'file_offset':off,'preceding_bytes_hex':raw[max(0,off-4):off].hex()})
                off+=1
            assert len(matches)==expected_count
            source_rows.append({'source_address':f'{address:08x}','literal_matches':matches})
        item['conditional_projection_source_storage']={'section':'.bss','virtual_size':bss.Misc_VirtualSize,
            'declared_size':bss.SizeOfRawData,'raw_offset':0,'characteristics':'c0000080',
            'file_backed_initial_values':'not established; do not interpret file offset0 as these values',
            'expected_loader_zero_fill_confidence':'inferred, not measured', 'sources':source_rows,
            'limits':['Noncanonical PE size fields; expected uninitialized storage contract, not a live loader observation.',
                      'Literal search does not recover bulk-copy, computed or alias writers; source production remains unresolved.']}
        item['absolute_centre_address_inventory']={'method':'Overlapping four-byte little-endian literal search over complete executable file; matches are operand locations, not instruction entries.',
            'addresses':centre_refs,'limits':['Does not detect computed addresses, aliases, encoded pointers, external modules or runtime-generated code.']}

        if label=='official_modern':
            item['float_constants']={f'{va:08x}':{'hex':pe.get_data(va-0x400000,4).hex(),
                'value':struct.unpack('<f',pe.get_data(va-0x400000,4))[0]}
                for va in [0x5401c0,0x5401c4,0x5401c8,0x53f420,0x5401cc,0x5401d0,0x5401d4]}
        if label=='official_modern':
            item['removed_legacy_ranges']=[]
            for start,end in LEGACY:
                blob=pe.get_data(start-0x400000,end-start)
                assert blob==b'\x90'*(end-start)
                item['removed_legacy_ranges'].append({'start':f'{start:08x}',
                    'end':f'{end:08x}','all_nop':True,'sha256':hashlib.sha256(blob).hexdigest()})
        result['binaries'][label]=item
        bodies[label]=pe.get_data(0x4bf260-0x400000,0x110)
    images=[pefile.PE(str(ROOT/SPECS[label][0])) for label in ('original','official_modern')]
    old,new=[pe.get_data(0x213b0,0x91) for pe in images]
    changed=[0x4213b0+i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    assert all(0x4213d4<=v<0x421430 for v in changed)
    for address in (0x56443c,0x564440,0x564434,0x564438):
        assert b'\xa3'+struct.pack('<I',address) in old
        assert struct.pack('<I',address) not in new
    result['viewport_finalizer']={'start':'004213b0','end_exclusive':'00421441','envelope_bytes':145,'changed_addresses':[f'{v:08x}' for v in changed],'changed_region':['004213d4','00421430'],'condition':'Nonzero context-index table pointer whose DWORD0 equals8','retained_float_pairs':[['005e1020','0056009c'],['005e102c','005600a4'],['005e1030','005600a8'],['005e1038','005600a0']],'removed_dword_pairs':[['005e10a0','0056443c'],['005e1034','00564440'],['005e1024','00564434'],['005e1028','00564438']],'limits':'Conditional local stores only; no complete visual or x87 state equivalence.'}
    assert bodies['original']==bodies['official_modern']
    assert images[0].get_data(0x1bc90,0x296)==images[1].get_data(0x1bc90,0x296)
    assert images[0].get_data(0x1401c0,4)==images[1].get_data(0x1401c0,4)==struct.pack('<f',0.5)
    result['retained_float_centre_chain']={
        'builder':'004bf260..004bf370','half_constant':'005401c0=0.5',
        'centre_stores':['004bf2a0 ->005600a4','004bf2a6 ->005600a8'],
        'half_extent_stores':['004bf284 ->005600ac','004bf28a ->005600b0'],
        'consumer':'0041bc90..0041bf26','consumer_bytes_identical':True,
        'local_projection':'0041be02..0041be39: scale*inverseZ*component + centre',
        'limits':['Producer and consumer identity is not equality of upstream dimensions/angles or rendered horizon.','Half-width reload and live extended half-height have distinct spill schedules.']}
    modern = images[1]
    for va,encoded in ((0x4dbc6e,'d8d1dfe09e7602'),(0x4dbc75,'d9c9ddd8'),
                       (0x4dbc7f,'d8d1dfe09e7302'),(0x4dbc86,'d9c9ddd8'),
                       (0x4dbc8a,'d91dccfe5500c3')):
        assert modern.get_data(va-0x400000,len(bytes.fromhex(encoded))).hex() == encoded
    assert struct.unpack('<f',modern.get_data(0x1401d0,4))[0] == 90.0
    assert struct.unpack('<f',modern.get_data(0x1401d4,4))[0] == 107.0
    unordered_ah = 0x45  # C3/C2/C0 mapped to ZF/PF/CF by FNSTSW AX; SAHF.
    cf = unordered_ah & 1
    zf = (unordered_ah >> 6) & 1
    lower_jump = bool(cf or zf)
    upper_jump = not bool(cf)
    assert (cf,zf) == (1,1) and lower_jump and not upper_jump
    result['modern_fov_clamp_contract'] = {
        'helper': '004dbc48..004dbc91', 'lower': 90.0, 'upper': 107.0,
        'lower_branch': 'JBE004dbc77: unordered takes jump and discards lower bound, retaining candidate.',
        'upper_branch': 'JAE004dbc88: unordered does not jump; FXCH/FSTP discards candidate, retaining107.',
        'conditional_unordered_result': '107.0 stored at0055fecc if both comparisons are unordered and execute without trapping.',
        'eax_residue': 'Upper16 entry EAX retained; low16 is second FNSTSW snapshot, not a scalar result.',
        'local_cw': 'No FLDCW/FINIT; computation and exceptions depend on ambient control state.',
        'limit': 'Symbolic branch/stack trace only; no NaN/zero-dimension instruction probe or game call.'}
    result['projection_builder_272_bytes_identical']=True
    (ROOT/'analysis/evidence/audits/original-modern-projection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: projection baselines, FOV/constants/callers and identical builder')


if __name__=='__main__':main()
