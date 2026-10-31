"""Compare slideshow navigation, binding and deferred refresh witnesses, offline."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-slideshow-navigation-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/slideshow-navigation'
    capture.mkdir(parents=True, exist_ok=True)
    images = []
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw); images.append(pe)
        spans = [(0x453840, 0x453859), (0x453860, 0x45393e), (0x453c00, 0x453eee), (0x453ed7, 0x453eec), (0x453ef0, 0x453f48)] if label == 'original' else [(0x453850, 0x453863), (0x453864, 0x45393d), (0x453c00, 0x453eee), (0x453ed7, 0x453eee), (0x453ef0, 0x453f58)]
        spans += [(0x4d6390,0x4d66ea),(0x44aa30, 0x44aac9), (0x44a9e0, 0x44aa21), (0x44ab40, 0x44ac7c),
                  (0x44b6c8, 0x44b707), (0x44b7a7, 0x44b7ec), (0x44b30b, 0x44b382)]
        if label=='official_modern':spans += [(0x451810,0x45182d),(0x451830,0x45183d),(0x4d6459,0x4d64a5),(0x4dafe6,0x4daffc)]
        rows = []
        for start, end in spans:
            path = capture / f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel', f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT))
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}', 'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(), 'assembly': str(path.relative_to(ROOT)), 'assembly_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        out['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows,
            'tokens': {f'{a:08x}': pe.get_data(a-0x400000, 32).split(b'\0')[0].decode() for a in (0x5397a4, 0x5397b0)},
            'slides_registration_row_00555f90_hex': pe.get_data(0x155f90, 24).hex(),
            'action_switch_0044b208_hex': pe.get_data(0x4b208, 32).hex()}
        assert int.from_bytes(pe.get_data(0x4b21c, 4), 'little') == 0x44b7a7
    old,new=images
    start,end=0x453c00,0x453eee
    a,b=[pe.get_data(start-0x400000,end-start) for pe in images]
    changed=[start+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    regions=[(0x453c00,0x453c47),(0x453e64,0x453e6b),(0x453e91,0x453e98),(0x453ebc,0x453ec6),(0x453ee3,0x453eee)]
    assert all(any(lo<=address<hi for lo,hi in regions) for address in changed)
    for site,slot in [(0x453e66,1),(0x453e93,2),(0x453ec1,0)]:
        for pe,target in [(old,0x4d6390),(new,0x451810)]:
            data=pe.get_data(site-0x400000,5);assert data[0]==0xe8
            assert site+5+int.from_bytes(data[1:],'little',signed=True)==target
    assert new.get_data(0x51812,3)==bytes.fromhex('0fb6ca')
    assert new.get_data(0x51831,5)==bytes.fromhex('bf70476600')
    out['complete_refresh_envelope']={'start':f'{start:08x}','end_exclusive':f'{end:08x}','changed_addresses':[f'{v:08x}' for v in changed],'covering_regions':[[f'{lo:08x}',f'{hi:08x}'] for lo,hi in regions],'boundary':'Original initializer/refresh versus Modern binding wrapper plus separate refresh; includes original post-return alignment.'}
    out['refresh_resource_slots']={'wrapper':'00451810','base':'00664770','index':'zero-extended DL','slideshow_slots':{'00453e66':1,'00453e93':2,'00453ec1':0},'reset':'00451830 clears12 bytes','limits':'Complete creator/resource lifetime and all shared-slot users unresolved.'}
    common = [p.get_data(0x5386d, 0x453931-0x45386d) for p in images]
    assert common[0] == common[1]
    creator=[pe.get_data(0xd6390,0x35a) for pe in images];assert creator[0]==creator[1]
    out['retained_resource_creator']={'start':'004d6390','end_exclusive':'004d66ea','length':0x35a,'sha256':hashlib.sha256(creator[0]).hexdigest(),'conditional_allocation_call':'004d6601 -> slot009ef968','shared_update_call':'004d6654 -> slot009ef964','condition':'Saved prior-index EDX argument is nonzero: skip allocation branch.'}
    pe=images[1];section=pe.sections[0];base=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress;code=pe.get_data(section.VirtualAddress,section.SizeOfRawData)
    out['slot_helper_direct_call_scan']={}
    for target,expected_sites in [(0x451810,[0x453e66,0x453e93,0x453ec1]),(0x451830,[0x4daff2])]:
        sites=[base+i for i in range(len(code)-4) if code[i]==0xe8 and base+i+5+int.from_bytes(code[i+1:i+5],'little',signed=True)==target]
        assert sites==expected_sites
        out['slot_helper_direct_call_scan'][f'{target:08x}']={'sites':[f'{v:08x}' for v in sites],'scope':'Every-byte E8/rel32 scan of official code section; excludes indirect references and other sections.'}
    counter_refs=[base+i for i in range(len(code)-3) if code[i:i+4]==bytes.fromhex('7c476600')]
    assert counter_refs==[0x45385b,0x453933,0x453ee4,0x453f43]
    assert pe.get_data(0x53f0d,2)==bytes.fromhex('7e32')
    assert pe.get_data(0x53f41,7)==bytes.fromhex('833d7c47660000')
    section=next(s for s in pe.sections if s.Name.startswith(b'.bss'))
    assert section.PointerToRawData==0 and section.IMAGE_SCN_CNT_UNINITIALIZED_DATA
    assert section.VirtualAddress<=0x26477c<section.VirtualAddress+section.SizeOfRawData
    out['counter_storage_and_references']={'slots_half_open':['00664770','0066477c'],'counter_half_open':['0066477c','00664780'],'section':'.bss','raw_pointer':section.PointerToRawData,'absolute_address_operand_candidates':[f'{v:08x}' for v in counter_refs],'scan_scope':'Literal address bytes in official code section; known instructions corroborated. Excludes computed aliases.','periodic_gate':'JLE00453f41 reaches counter test even when timing interval is not exceeded.','reset':'00451830 clears slots only, excludes counter.'}
    out['retained_previous_core'] = {'start': '0045386d', 'end': '00453931', 'sha256': hashlib.sha256(common[0]).hexdigest()}
    out['retained_action9_path_ranges'] = []
    for start, end in ((0x44aa30, 0x44aac9), (0x44a9e0, 0x44aa21), (0x44ab40, 0x44ac7c), (0x44b6c8, 0x44b707), (0x44b7a7, 0x44b7ec)):
        pair = [p.get_data(start-0x400000, end-start) for p in images]
        assert pair[0] == pair[1]
        out['retained_action9_path_ranges'].append({'start': f'{start:08x}', 'end': f'{end:08x}', 'sha256': hashlib.sha256(pair[0]).hexdigest()})
    archive = ROOT / 'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    relative = 'analysis/captures/modern-differences/upstream/package/fedata/menus/slides.mnu'
    raw = (ROOT/relative).read_bytes()
    assert raw == subprocess.check_output(['7z', 'x', '-so', str(archive), 'fedata/menus/slides.mnu'])
    out['official_arrow_asset'] = {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'fields': [{'line': i, 'field': line} for i, line in enumerate(raw.decode('latin1').splitlines(), 1) if line.startswith(('codelink=keyleft ', 'codelink=keyright '))]}
    out['limits'] = ['No input, filesystem, renderer or target execution.', 'Binding/refresh snippets are explicitly partial; complete refresh routine and resources not validated.', 'Action9 path is traced conditionally; shared counter aliases, pending-menu overrides and complete callback admission remain separate.']
    (ROOT/'analysis/evidence/audits/original-modern-slideshow-navigation.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: explicit callback counterparts, retained previous core, deferred-refresh witnesses')


if __name__ == '__main__':
    main()
