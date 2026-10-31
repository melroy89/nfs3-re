"""Compare an unlisted front-end key handler by shared callback binding and instruction envelope."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'scope': 'Paired callback at004651e0; raw key tokens and component updates only', 'baselines': {}}
    images = {}
    bodies = {}
    for label,(relative,wanted,_) in SPECS.items():
        path = ROOT/relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == wanted
        pe = pefile.PE(data=raw)
        images[label] = pe
        code = pe.get_data(0x651e0,269)
        bodies[label] = code
        assert pe.get_data(0x157a34,4) == struct.pack('<I',0x4651e0)
        assert struct.unpack('<d',pe.get_data(0x13ab6c,8))[0] == 0.4
        assert struct.unpack('<f',pe.get_data(0x13ab74,4))[0] == 10.0
        out['baselines'][label] = {'path': relative, 'sha256': wanted,
            'entry': '004651e0', 'end_exclusive': '004652ed', 'bytes': len(code),
            'body_sha256': hashlib.sha256(code).hexdigest(), 'hex': code.hex(),
            'disassembly': subprocess.check_output(['objdump','-d','-Mintel',
                '--start-address=0x4651e0','--stop-address=0x4652ed',str(path)],text=True),
            'callback_pointer_slot': '00557a34'}
    old,new = bodies['original'],bodies['official_modern']
    changed = [0x4651e0+i for i,(a,b) in enumerate(zip(old,new)) if a != b]
    assert len(changed) == 52 and all(0x465218 <= va < 0x465271 for va in changed)
    for label,positive,negative in [('original',0x40000000,0xc0000000),('official_modern',0x3f800000,0xbf800000)]:
        pe = images[label]
        assert pe.get_data(0x65218,5) == b'\xb8'+struct.pack('<I',positive)
        assert pe.get_data(0x6522c,5) == b'\xba'+struct.pack('<I',negative)
    assert old[0x91:] == new[0x91:]  # Shared continuation starts00465271.
    gate = images['original'].get_data(0x4a660,29)
    assert gate == images['official_modern'].get_data(0x4a660,29)
    assert images['official_modern'].get_data(0x6523f,22) == bytes.fromhex(
        'd90554896700d9e0d95dfcd90558896700d9e0d95df8')
    assert images['original'].get_data(0x65241,5) == bytes.fromhex('b902000000')
    assert images['official_modern'].get_data(0x651ec,2) == bytes.fromhex('31c9')
    assert images['official_modern'].get_data(0x652e6,2) == bytes.fromhex('89c8')
    out['difference'] = {'changed_addresses': [f'{va:08x}' for va in changed],
        'token_4b00_delta': {'original': 2.0, 'modern': 1.0},
        'token_4d00_delta': {'original': -2.0, 'modern': -1.0},
        'token_0020': 'Modern local deltas are negative current components at00678954/00678958 before common addition.',
        'token_0020_return': {'original': 2, 'modern': 0},
        'shared_continuation': '00465271..004652ed', 'gate_body_sha256': hashlib.sha256(gate).hexdigest(),
        'gate_body_hex': gate.hex(),
        'limit': 'Finite/nontrapping cancellation argument only; InteriorBx binding established; physical axes and runtime input not established.'}
    interval_start,interval_end = 0x464fca,0x4654c0
    interval_rows = []
    interval_changes = []
    for label,pe in images.items():
        data = pe.get_data(interval_start-0x400000,interval_end-interval_start)
        interval_rows.append({'baseline': label, 'sha256': hashlib.sha256(data).hexdigest()})
        interval_changes.append(data)
    assert [interval_start+i for i,(a,b) in enumerate(zip(*interval_changes)) if a!=b] == changed
    out['outside_function_interval'] = {'start': f'{interval_start:08x}', 'end_exclusive': f'{interval_end:08x}',
        'bytes': interval_end-interval_start, 'changed_bytes': len(changed), 'identities': interval_rows,
        'scope': 'All52 changed bytes in this1270-byte uncovered interval are in the paired key handler.'}
    bindings = {}
    for label,pe in images.items():
        ident,name,template = struct.unpack('<3I',pe.get_data(0x157bec,12))
        assert (ident,template) == (33,0x557a04)
        assert pe.get_string_at_rva(name-0x400000) == b'InteriorBx'
        assert pe.get_data(template-0x400000+0x30,4) == struct.pack('<I',0x4651e0)
        assert pe.get_data(template-0x400000+0x2c,4) == struct.pack('<I',0x464fd0)
        update = pe.get_data(0x6501a,0x45)
        bindings[label] = {'registry_row': '00557bec', 'type_id': ident, 'token': 'InteriorBx',
            'token_va': f'{name:08x}', 'template': f'{template:08x}', 'key_callback_offset': '30h',
            'update_callback_offset': '2ch', 'update_callback': '00464fd0',
            'update_prefix': {'start': '0046501a', 'end_exclusive': '0046505f',
                'sha256': hashlib.sha256(update).hexdigest(), 'hex': update.hex(),
                'scope': 'FILD signed state0055a43c/0055a440, add component pair, call004dfd56 twice, FISTP back.'}}
    assert bindings['original']['update_prefix']['hex'] == bindings['official_modern']['update_prefix']['hex']
    templates = {}
    for label,pe in images.items():
        interior = pe.get_data(0x157a04,64)
        compass = pe.get_data(0x157a44,64)
        row = struct.unpack('<3I',pe.get_data(0x157bf8,12))
        assert row == (34,0x538460,0x557a44)
        assert pe.get_string_at_rva(0x138460) == b'Compass'
        assert struct.unpack_from('<I',compass,4)[0] == (0 if label == 'original' else 0x200)
        templates[label] = {'interior_template_hex': interior.hex(),
            'compass_registry_row': '00557bf8', 'compass_template': '00557a44',
            'compass_template_hex': compass.hex(),
            'compass_offset_04': struct.unpack_from('<I',compass,4)[0]}
    assert templates['original']['interior_template_hex'] == templates['official_modern']['interior_template_hex']
    compass_old = bytes.fromhex(templates['original']['compass_template_hex'])
    compass_new = bytes.fromhex(templates['official_modern']['compass_template_hex'])
    assert [i for i,(a,b) in enumerate(zip(compass_old,compass_new)) if a != b] == [5]
    out['adjacent_templates'] = {'baselines': templates,
        'limit': 'The changed DWORD at00557a48 belongs to Compass, not InteriorBx. Meaning of mask0200h and downstream consumers unresolved.'}
    compass_callbacks = []
    for start,end in [(0x457460,0x4575a0),(0x4575a0,0x457616),
                      (0x457620,0x45762a),(0x457630,0x45766d),(0x457670,0x457675)]:
        paired = {label: pe.get_data(start-0x400000,end-start) for label,pe in images.items()}
        assert paired['original'] == paired['official_modern']
        compass_callbacks.append({'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
            'bytes': end-start, 'sha256': hashlib.sha256(paired['original']).hexdigest(),
            'hex': paired['original'].hex()})
    out['compass_retained_callbacks'] = {'paired_bodies': compass_callbacks,
        'total_bytes': sum(row['bytes'] for row in compass_callbacks),
        'limit': 'Five complete callback envelopes match; initialization callback00457680 and generic dispatcher/constructor not qualified.'}
    copy_bodies = {label: pe.get_data(0x49060,120) for label,pe in images.items()}
    assert copy_bodies['original'] == copy_bodies['official_modern']
    assert bytes.fromhex('b9bc000000') in copy_bodies['original']
    out['template_copy'] = {'entry': '00449060', 'end_exclusive': '004490d8',
        'bytes': 120, 'sha256': hashlib.sha256(copy_bodies['original']).hexdigest(),
        'hex': copy_bodies['original'].hex(), 'copy_bytes': 188,
        'runtime_base': '00604ee0', 'runtime_stride': 188,
        'compass_runtime_bit_address': '00604ee0 + 188*entry_index + 4',
        'limit': 'Copies188 bytes from selected registry template;64-byte adjacent-prefix witnesses do not establish complete source object sizes or later field overwrites.'}
    copied_sources = []
    for start in (0x557a04,0x557a44):
        paired = {label: pe.get_data(start-0x400000,188) for label,pe in images.items()}
        offsets = [i for i,(a,b) in enumerate(zip(paired['original'],paired['official_modern'])) if a != b]
        assert offsets == [0x557a49-start]
        copied_sources.append({'source': f'{start:08x}', 'bytes': 188,
            'baselines': {label: {'hex': data.hex(), 'sha256': hashlib.sha256(data).hexdigest()}
                          for label,data in paired.items()},
            'changed_offsets': offsets, 'changed_source_va': '00557a49'})
    out['overlapping_copy_sources'] = {'sources': copied_sources,
        'limit': 'Changed source byte enters InteriorBx runtime offset45h and Compass offset05h on this copy path; later overwrites/consumers and intended source schema unresolved.'}
    initializers = {label: pe.get_data(0x65370,324) for label,pe in images.items()}
    assert initializers['original'] == initializers['official_modern']
    assert initializers['original'][14:19] == bytes.fromhex('a198476600')
    out['interior_initializer'] = {'entry': '00465370', 'end_exclusive': '004654b4',
        'bytes': 324, 'sha256': hashlib.sha256(initializers['original']).hexdigest(),
        'hex': initializers['original'].hex(),
        'limit': 'Identical initializer overwrites incoming EAX with global00664798 before using it; no direct runtime-entry+45h overwrite established. Called helpers/global aliases not fully traced.'}
    dispatch = {}
    for label,start,end in [('original',0x44a335,0x44a439),('official_modern',0x44a339,0x44a436)]:
        data = images[label].get_data(start-0x400000,end-start)
        assert images[label].get_data(0x4a428,7) == bytes.fromhex('83fb02750231db')
        dispatch[label] = {'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
            'hex': data.hex(), 'sha256': hashlib.sha256(data).hexdigest(),
            'disassembly': subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',str(ROOT/SPECS[label][0])],text=True)}
    out['selected_entry_dispatch_suffix'] = {'baselines': dispatch,
        'token_0020_exposed_return': {'original': 0, 'official_modern': 0},
        'limit': 'Conditional on selected InteriorBx callback reaching admitted token0020h path; no full dispatcher equivalence, indirect caller coverage or runtime event delivery established.'}
    archive = ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_sha == 'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    members = []
    for member,wanted in [('fedata/menus/interior.mnu','376be73730fd40f53e43fbc4ce14e95747d4675b72ef9437cb1f4cf7f58125dd'),
                          ('fedata/menus/credits1.mnu','4441df58ec7b8a88fc9aa04f6b2537ac49f5df2d9d095acf89577329195cb0c7')]:
        raw = subprocess.check_output(['7z','x','-so',str(archive),member])
        assert hashlib.sha256(raw).hexdigest() == wanted
        lines = raw.decode('latin1').splitlines()
        index = next(i for i,line in enumerate(lines) if line.lower() == '[interiorbx]')
        block = []
        for line in lines[index+1:]:
            if line.startswith('['):
                break
            if line.strip():
                block.append(line)
        members.append({'member': member, 'sha256': wanted, 'tag': lines[index], 'properties': block})
    out['interior_widget_binding'] = {'exe_bindings': bindings, 'archive_sha256': archive_sha,
        'selected_menu_members': members,
        'limit': 'Named widget and shared per-update dataflow verified; rendered rotation and actual key-event delivery untested.'}
    inventories = {}
    for name in ('original','modern'):
        path = ROOT/f'analysis/captures/modern-differences/functions-{name}.json'
        raw = path.read_bytes()
        inventory = json.loads(raw)
        covering = [row['entry'] for row in inventory['functions']
                    if any(int(a,16)<=0x4651e0<int(b,16) for a,b in row['ranges'])]
        assert not covering
        inventories[name] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
            'executable_sha256': inventory['executable_sha256'], 'covering_entries': covering}
    out['saved_inventory_boundary'] = inventories
    out['limits'] = ['Missing saved function object does not make the instructions padding.',
        'InteriorBx registry/template/menu binding established; selected-entry return normalization established; full table schema, other callers and rendered behavior remain incomplete.',
        'Identical updater prefix calls changed helper004dfd56; see original-modern-slider-percentage.md for rounding/exception differences.',
        'No game, key event, instruction probe, C export/compilation or Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/control-component-key-difference.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: shared callback, paired269-byte envelopes,52 changed bytes, step/reset witnesses and inventory gap')


if __name__ == '__main__':
    main()
