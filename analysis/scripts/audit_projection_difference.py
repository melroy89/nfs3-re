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
        for start,end in SPANS[label]+[(0x4213b0,0x421441),(0x41bc90,0x41bf26),
                                      (0x422cf0,0x422d9b),(0x422da2,0x422de5),(0x42383f,0x42386b),
                                      (0x4238b0,0x423959),(0x425060,0x4251ef),(0x4251f0,0x425232),
                                      (0x421380,0x4213a1),(0x421450,0x421471),(0x4bc470,0x4bc529),
                                      (0x4349a0,0x4349c1)]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows}
        descriptor=struct.unpack('<5I',pe.get_data(0x156758,20))
        assert descriptor[0]==0x537fdc and descriptor[4]==0x6fbc40
        assert pe.get_string_at_rva(0x137fdc)==b'viewangle'
        expected_ids=[274,275] if label=='original' else [1947,1948,1949,1950]
        assert list(struct.unpack('<'+'H'*(len(expected_ids)+1),pe.get_data(descriptor[1]-0x400000,2*(len(expected_ids)+1))))==expected_ids+[0]
        item['view_angle_setting']={'descriptor':'00556758','words':[f'{v:08x}' for v in descriptor],
            'key':'viewangle','storage':'006fbc40','ordinal_label_ids':expected_ids}
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
        neighborhood=[]
        for address in range(0x5e1000,0x5e1040,4):
            matches=[];offset=0
            while True:
                offset=raw.find(struct.pack('<I',address),offset)
                if offset<0:break
                va=pe.get_rva_from_offset(offset)+0x400000
                assert 0x401000<=va<0x536000
                matches.append({'file_offset':offset,'mapped_literal_va':f'{va:08x}'})
                offset+=1
            neighborhood.append({'address':f'{address:08x}','matches':matches})
        item['source_neighborhood_literal_search']={
            'domain':'Sixteen DWORD-aligned address values005e1000..005e103c, searched as overlapping little-endian literals over complete file.',
            'addresses':neighborhood,'all_matches_in_code_section_address_range':True,
            'limits':'No data-held literal of these exact values found; arbitrary byte-offset bases, arithmetic derivation, relocations to other bases and external writers remain unexcluded.'}

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
    parity=images[0].get_data(0x349a0,33)
    assert parity==images[1].get_data(0x349a0,33)
    assert parity.hex()=='525589e58b1083fa01750489d0eb0231c08b15c4d46f0031d0a34c4e55005d5ac3'
    result['interstage_parity_helper']={'span':'004349a0..004349c1','bytes':33,'bytes_identical':True,
        'sha256':hashlib.sha256(parity).hexdigest(),
        'effect':'EAX=(contextDWORD0==1 ?1:0) XOR rawDWORD006fd4c4; store00554e4c; EDX/EBP restored.',
        'source_exclusion':'No calls and only that single absolute data store in complete helper; no projection-source write.',
        'limits':'Raw XOR does not normalize arbitrary006fd4c4 values to Boolean; whole mirror orientation/output and other intervening callees remain unqualified.'}
    handler=images[0].get_data(0x25060,0x18f)
    assert handler==images[1].get_data(0x25060,0x18f)
    result['retained_type8_handler']={'span':'00425060..004251ef','bytes':399,
        'sha256':hashlib.sha256(handler).hexdigest(),'bytes_identical':True,
        'boundary':'Complete handler through RET004251ee; selected by mode8 in paired dispatcher mapping.',
        'limits':'Instruction equality does not prove equal context state, transitive helpers or ambient x87 state; no missing source capture inferred from the mode label.'}
    init_spans=[]
    for start,end in ((0x422cf0,0x422d9b),(0x422da2,0x422de5),(0x42383f,0x42386b)):
        blob=images[0].get_data(start-0x400000,end-start)
        assert blob==images[1].get_data(start-0x400000,end-start)
        init_spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(blob).hexdigest()})
    result['indexed_slot_initializer_candidate']={'paired_identical_spans':init_spans,
        'ordinary_index_domain':'EBX starts0; local upper bound1 for session006fd3b0==1, otherwise0; loop increments at00423865.',
        'writes':'00422d78/00422d86 clear005e1010+8*EBX and005e1014+8*EBX; ordinary destinations005e1010..005e101c.',
        'exclusion':'These local stores do not initialize source005e1020/2c/30/38 under that domain.',
        'limits':['Intervening callees must preserve loop state; no whole-program index/alias invariant claimed.',
                  'Other indexed writers and actual type8 source producer remain unresolved.']}
    for image in images:
        assert struct.unpack('<2I',image.get_data(0x152f08,8))==(0x5de578,0x5de6ac)
    camera_rows=[]
    for mode in range(1,25):
        pair=struct.unpack('<2I',images[0].get_data(0x152ec8+mode*8,8))
        assert pair==struct.unpack('<2I',images[1].get_data(0x152ec8+mode*8,8))
        spacing=pair[1]-pair[0]
        camera_rows.append({'mode':mode,'slot0':f'{pair[0]:08x}','slot1':f'{pair[1]:08x}',
                            'pair_spacing':spacing,'inferred_pair_end':f'{pair[0]+2*spacing:08x}'})
    ordered=sorted(camera_rows,key=lambda row:row['slot0'])
    assert all(a['inferred_pair_end']==b['slot0'] for a,b in zip(ordered,ordered[1:]))
    assert ordered[0]['slot0']=='005dda10' and ordered[-1]['inferred_pair_end']=='005e1010'
    result['scene_descriptor_pointer_layout']={'table':'00552ec8 modes1..24, twoDWORD pointers each; all paired values identical.',
        'rows':camera_rows,'inferred_packing':'Using within-pair spacing as per-record extent yields contiguous005dda10..005e1010 with no gaps/overlaps.',
        'confidence':'Pointer values/spacing/adjacency verified; treating spacing as complete structure size is inferred, not proved.',
        'limits':'Does not bound arbitrary field writes or establish all types, packing, pointer lifetimes or projection-source producer. Heterogeneous spacing forbids assuming one universal scene-record size.'}
    result['type8_descriptor_availability']={
        'table_row':'00552f08=00552ec8+8*8:005de578,005de6ac; same file-backed pointers in both baselines.',
        'initializer':'Normal mode loop visits1..24; common00422dd8 stores mode number at descriptor+0. Slot loop initializes0 or0/1 according to session.',
        'meaning':'Type8 is not excluded by a null mode-table row or missing ordinary initialization.',
        'limits':'This does not prove actual selection/publication into005e10b0, finalizer reachability, valid vehicle state or missing projection source production.'}
    selected_spans=[]
    for start,end in ((0x4238b0,0x423959),(0x4251f0,0x425232)):
        blob=images[0].get_data(start-0x400000,end-start)
        assert blob==images[1].get_data(start-0x400000,end-start)
        selected_spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(blob).hexdigest()})
    result['type8_selection_witness']={'paired_identical_spans':selected_spans,
        'condition':'004251f0 receives selector00423d90 resultffffffff at00425208.',
        'publication':'00425218 calls004238b0 with requestedEDX8 and EAX=context+0c slot;8 bypasses callback cases3/4/5/6, then0042394d publishes mode-table row8 pointer to005e10b0[slot].',
        'continuation':'00425228 dispatches mode8 through00426450 before exiting this fallback branch.',
        'limits':'Actual selector failure and later finalizer ordering/pointer stability not observed; projection source writer still unresolved.'}
    order_spans=[]
    for start,end in ((0x421380,0x4213a1),(0x421450,0x421471),(0x4bc470,0x4bc529)):
        blob=images[0].get_data(start-0x400000,end-start)
        assert blob==images[1].get_data(start-0x400000,end-start)
        order_spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(blob).hexdigest()})
    result['viewport_stage_order']={'paired_identical_spans':order_spans,
        'stage0':'004bc4a4 calls00421450 withEDX0:00421380 calls004228e0 then004dbde0.',
        'middle':'For admitted input tag0/1,004bc4f3 calls0041bb50 and004bc4fa calls004bc160.',
        'stage2':'004bc509 calls00421450 withEDX2 ->004213b0, which calls004dbde0 before type8 restoration.',
        'limits':'Local call order, not global scheduling; middle callees can mutate source/selection state. Finalized projection may affect later consumers; no rendered-horizon conclusion.'}
    initializer = images[0].get_data(0x23a60,0x4b)
    iterator = images[0].get_data(0x23a20,0x3e)
    assert iterator == images[1].get_data(0x23a20,0x3e)
    mapper = images[0].get_data(0x72300,0x55)
    assert mapper == images[1].get_data(0x72300,0x55)
    camera_values = (0,1,4,3,2,5,6)
    for image in images:
        assert struct.unpack('<7h',image.get_data(0x15629e,14)) == camera_values
    assert initializer == images[1].get_data(0x23a60,0x4b)
    assert initializer[0x19:0x32].hex() == '31c04089148538105e0083f8197d0a4089148538105e00ebf1'
    result['indexed_source_candidate'] = {
        'span':'00423a60..00423aab', 'bytes_identical':True,
        'sha256':hashlib.sha256(initializer).hexdigest(),
        'initial_fill':'EAX starts1, stores indices1..25 at005e1038+4*EAX:005e103c..005e109c inclusive.',
        'excluded_by_initial_fill':['005e1020','005e102c','005e1030','005e1038'],
        'later_store':'00423a9d uses005e103c+4*EDX; EDX derives from00423a20 results.',
        'iterator':{'span':'00423a20..00423a5e','bytes_identical':True,
                    'sha256':hashlib.sha256(iterator).hexdigest(),
                    'reset':'Nonzero input EAX resets scan index to0.',
                    'result':'First nonzero DWORD among006fbbc0,006fbbc4,006fbbc8,006fbbcc, or0; cursor stored at005e10c0.',
                    'qualification':'Bounded four-cell scan requires cursor0..4 on continuation; reset establishes this for the inspected caller absent intervening mutation.'},
        'later_store_alias_indices':{f'{address:08x}':[f'{((address-0x5e103c)//4+k*0x40000000)&0xffffffff:08x}' for k in range(4)]
                                    for address in (0x5e1020,0x5e102c,0x5e1030,0x5e1038)},
        'camera_table_producer':{'span':'00472300..00472355','bytes_identical':True,
            'sha256':hashlib.sha256(mapper).hexdigest(),
            'input_indices':['006fbba8','006fbbac','006fbbb0','006fbbb4'],
            'lookup':'Signed WORD0055629e+2*index, implemented by DWORD load then SAR16; no local index check.',
            'verified_indices_0_through_6':list(camera_values),
            'conditional_exclusion':'Indices0..6 and no intervening table mutation imply outputs0..6; subsequent successor stores cannot alias the four projection source cells.',
            'remaining':'Accepted index extent, alternate writers, startup/call order and type8 source producer remain unresolved.'},
        'limits':['Normal entry/control flow only; alternate interior entries are not excluded.',
                  'Later indexed-store range and callback results remain unresolved; this is not a global no-writer proof.']}
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
    old_defaults=images[0].get_data(0x72d10,0x208)
    new_defaults=images[1].get_data(0x72d10,0x10c)
    assert struct.pack('<I',0x6fbc40) not in old_defaults
    assert images[1].get_data(0x72d92,14).hex()=='31d289154cbc6f00891540bc6f00'
    result['view_angle_default_reset']={
        'original_envelope':'00472d10..00472f18','original_sha256':hashlib.sha256(old_defaults).hexdigest(),
        'modern_envelope':'00472d10..00472e1c','modern_sha256':hashlib.sha256(new_defaults).hexdigest(),
        'modern_write':'00472d92 clears EDX;00472d9a stores0 to006fbc40, selecting Automatic.',
        'original_boundary':'No literal006fbc40 operand in complete original default envelope; computed/transitive writes not excluded.',
        'limits':'This default/reset path is not proof of unconditional startup, saved-value migration or all initialization order.'}
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels={}
    for ident in (274,275,1947,1948,1949,1950):
        offset=struct.unpack_from('<I',english,4*ident)[0]
        labels[str(ident)]=english[offset:english.index(b'\0',offset)].decode('latin1')
    assert list(labels.values())==['Wide','Narrow','Automatic','Narrow (75°)','Normal (90°)','Wide (105°)']
    result['view_angle_labels']={'member':'fedata/text/text.eng','sha256':hashlib.sha256(english).hexdigest(),
        'labels':labels,'limits':'Original IDs decoded with final official Modern English; authenticated original retail labels and intermediate-release lists remain unverified.'}
    (ROOT/'analysis/evidence/audits/original-modern-projection.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: projection baselines, FOV/constants/callers and identical builder')


if __name__=='__main__':main()
