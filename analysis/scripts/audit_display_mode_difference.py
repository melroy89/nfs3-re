"""Static original/Modern display-mode enumerator and menu-list witnesses.

Requires pefile/GNU objdump; no game, driver or instruction execution.
"""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = {
    'original': [(0x4bed90, 0x4bee72), (0x448210, 0x4482e8), (0x517610, 0x51788d),
                 (0x472d10, 0x472f19), (0x4483a0, 0x4483fe), (0x4bef50, 0x4bf10f), (0x44b1a0,0x44b206),
                 (0x4482f0,0x44832c),(0x448330,0x448394),(0x4a3418,0x4a3427)],
    'official_modern': [(0x4bed90, 0x4beeb0), (0x448210, 0x448345), (0x4beeb0, 0x4bef9d),
                        (0x448394, 0x448425), (0x472d10, 0x472e1d),
                        (0x472aac, 0x472aeb), (0x4f9140, 0x4f915e), (0x44b1a0,0x44b206), (0x448348,0x44837c), (0x4bef9d,0x4befcd),
                        (0x4a3408,0x4a3417)],
}


def main():
    capture = ROOT/'analysis/captures/modern-differences/display-modes'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-display-mode-comparison', 'range_end': 'exclusive',
        'binaries': {}, 'limits': ['Driver-provided records were not executed or mutated.',
            'Menu count boundary is not a proved reachable storage fault.',
            'Driver DLL enumeration limits and actual UI behavior remain untested.']}
    images=[]
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        images.append(pe)
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
    preparation=[images[0].get_data(0xbf022,47),images[0].get_data(0xbf0d7,47),images[1].get_data(0xbef9d,47)]
    normalized=[]
    for data in preparation:
        assert data[18]==0xe8
        normalized.append(data[:19]+b'\x00'*4+data[23:])
    assert normalized[0]==normalized[1]==normalized[2]
    assert images[1].get_data(0xbefcc,1)==b'\xc3'
    assert images[0].get_data(0xbf060,4)==bytes.fromhex('85c07473')
    assert images[1].get_data(0xbef2a,4)==bytes.fromhex('85c07466')
    assert images[0].get_data(0xbefe3,5)==bytes.fromhex('83f9027e07')
    assert images[1].get_data(0xbeefd,5)==bytes.fromhex('83fa027605')
    result['mode_application_followup']={'original_failure_gate':'004bf060','modern_failure_gate':'004bef2a',
        'preparation_original_regions':['004bf022..004bf051','004bf0d7..004bf106'],
        'preparation_modern_helper':'004bef9d..004befcd',
        'comparison':'47 preparation bytes identical after normalizing sole direct CALL displacement; Modern adds RET.',
        'field14_cap':'original signed <=2; Modern unsigned <=2',
        'limits':'No rollback or runtime mode-switch equivalence established.'}
    selected_accessors=images[1].get_data(0x48348,52)
    assert selected_accessors==bytes.fromhex('a15c82a1003b056082a100720731c0a35c82a10069c014010000053083a100c3e8dbffffff8b4010c3909090e8cfffffff8b00c3')
    result['selected_record_accessors']={'selector':'00448348','field10_accessor':'00448368',
        'field0_accessor':'00448374','record_stride':276,'index':'00a1825c','count':'00a18260',
        'base':'00a18330','limits':'Unsigned index normalization does not reject an empty list; original counterparts are mapped below without result-equivalence claims.'}
    for pe,site,target,apply in [(images[0],0x4a3418,0x4482f0,0x4bef50),
                                  (images[1],0x4a3408,0x448374,0x4beeb0)]:
        body=pe.get_data(site-0x400000,15)
        assert body[0]==0xe8 and site+5+int.from_bytes(body[1:5],'little',signed=True)==target
        assert body[5:10].hex()=='a3c4fe5500'
        assert body[10]==0xe8 and site+15+int.from_bytes(body[11:15],'little',signed=True)==apply
    assert images[0].get_data(0x482f5,5).hex()=='e8c6ffffff'
    assert images[0].get_data(0x48305,2).hex()=='7c08'
    result['accessor_counterparts']={
        'field0':{'original':'004482f0..0044832c','modern':'00448374..0044837c',
            'caller_original':'004a3418','caller_modern':'004a3408',
            'shared_handoff':'Store EAX to0055fec4, then call version-specific mode application with EAX still live.',
            'original':'Calls list initializer004482c0 unconditionally, then signed index<count check and field0 load.',
            'modern':'Calls unsigned cached-record selector00448348 and reads field0, without calling list initializer.'},
        'field10':{'original':'00448330 full record copy plus caller offset10 read',
                   'modern':'00448368 direct selected-record field10 load',
                   'existing_evidence':'original-modern-graphics-menu-transition.md#mode-copy-field-correspondence-is-now-established'},
        'limits':['Maps local functional counterparts through actual callers/field offsets, not same-address guesses.',
                  'No source-record equality, complete initialization order or runtime mode equivalence.',
                  'Original signed check can admit a negative index when it is below a normal positive count; Modern unsigned check rejects it for ordinary small counts.',
                  'Both local index-normalization policies can still read record0 when count0.']}
    original_recovery,modern_recovery=[p.get_data(0x4b1a0,102) for p in images]
    assert [i for i,(a,b) in enumerate(zip(original_recovery,modern_recovery)) if a!=b]==[0x46,0x47]
    assert original_recovery[0x45:0x4a]==bytes.fromhex('e8663d0700')
    assert modern_recovery[0x45:0x4a]==bytes.fromhex('e8c63c0700')
    result['recovery_call']={'instruction':'0044b1e5','original_target':'004bef50',
        'modern_target':'004beeb0','input_eax':1,'limits':'Caller does not check application return; no runtime recovery test.'}
    modern=images[1]
    raw=(ROOT/SPECS['official_modern'][0]).read_bytes()
    needle=bytes.fromhex('6082a100');positions=[];cursor=0
    while True:
        offset=raw.find(needle,cursor)
        if offset<0:break
        positions.append(modern.get_rva_from_offset(offset)+0x400000);cursor=offset+1
    assert positions==[0x448232,0x448265,0x448283,0x448326,0x44834f,0x44837d,0x4483d4]
    assert modern.get_data(0x48281,6).hex()=='ff056082a100'
    assert modern.get_data(0x48320,24).hex()=='575131c039056082a1007516bf6482a100b933000000f3ab'
    assert modern.get_data(0x48297,9).hex()=='b94500000031c0f3ab'
    bss=next(s for s in modern.sections if s.Name.rstrip(b'\0')==b'.bss')
    reloc=next(s for s in modern.sections if s.Name.rstrip(b'\0')==b'.reloc')
    assert (bss.VirtualAddress,bss.Misc_VirtualSize,bss.SizeOfRawData,bss.PointerToRawData)==(0x16e000,0,0x4b1000,0)
    end=0x400000+bss.VirtualAddress+bss.SizeOfRawData
    assert end==0xa1f000==0x400000+reloc.VirtualAddress
    assert 0xa18330+100*276==0xa1ef00 and 0xa18330+101*276==end+20
    result['count_cache_storage_boundary']={
        'exact_count_address_operands':[f'{address:08x}' for address in positions],
        'direct_writer':'00448281 increments count; no direct zero-reset literal store in this complete file scan.',
        'initializer':'00448320 tests count0; only then clears51 DWORDs of labels and enumerates. It does not directly reset count.',
        'label_clear_range':['00a18264','00a18330'],
        'bss_header':{'start':'0056e000','virtual_size':0,'raw_size':bss.SizeOfRawData,'raw_pointer':0,'size_field_end':'00a1f000','characteristics':f'{bss.Characteristics:08x}'},
        'next_section':{'name':'.reloc','start':f'{0x400000+reloc.VirtualAddress:08x}','characteristics':f'{reloc.Characteristics:08x}'},
        'conditional_append_101':{'pre_count':100,'insertion_index':100,'record_start':'00a1ef00','record_end_exclusive':'00a1f014',
            'clear_DWORDs':69,'bytes_beyond_bss_size_field_extent':20},
        'limits':['Literal-operand scan excludes computed/bulk/alias/external reset paths and does not prove immutable lifetime.',
                  'VirtualSize0/raw-pointer0 are retained; raw-size metadata is not file-backed BSS bytes or a runtime mapping observation.',
                  '101st unique admitted append is a conditional local path, not an observed provider list or execution.',
                  'Section-boundary crossing is arithmetic evidence, not an observed overwrite/fault or proof of OS mapping/protection/discard behavior.',
                  'Do not silently change JA to JAE in a reconstruction; expose the selected compatibility policy.']}
    output = ROOT/'analysis/evidence/audits/original-modern-display-modes.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: original/Modern identity and enumerator/menu instruction captures')


if __name__ == '__main__':
    main()
