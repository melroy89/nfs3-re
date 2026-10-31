"""Static paired startup requirement checks; no memory/display API execution."""
import hashlib
import json
import subprocess
import struct
import uuid
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/startup-requirements';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-startup-requirement-comparison','range_end':'exclusive','binaries':{}}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        spans=([(0x4b5f10,0x4b5fee),(0x4b608b,0x4b6097)] if label=='original' else [(0x4b5748,0x4b57c1),(0x4b570c,0x4b5746),(0x4b5c07,0x4b5c11)])
        spans += [(0x4b5e50,0x4b5e9a),(0x4b5ea0,0x4b5f0b),(0x4b6590,0x4b67ac),(0x4b62a0,0x4b6311),(0x4b6320,0x4b6400),(0x4f93f0,0x4f9461),(0x4eb390,0x4eb3bf),(0x4b5860,0x4b58bb),(0x4f4b80,0x4f4ba1),(0x4f2a7d,0x4f2a84),(0x4dfd04,0x4dfd55)]
        spans += [(0x4516a0,0x4516fa if label=='original' else 0x4516f4),(0x4f07d0,0x4f083e)]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm';path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        imports=[{'iat':f'{i.address:08x}','name':i.name.decode(),'dll':d.dll.decode()} for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address in (0x534580,0x534740,0x534754,0x534458,0x534764,0x534500,0x534514,0x534570,0x53458c,0x5344dc,0x534518)]
        item={'path':relative,'sha256':expected,'spans':rows,'imports':imports}
        if label=='official_modern':item['messages']={f'{a:08x}':pe.get_data(a-0x400000,240).split(b'\0')[0].decode() for a in (0x53d27a,0x53d29a,0x53d202)}
        result['binaries'][label]=item
    data=images['original'].get_data(0xf07d0,0x6e);assert data==images['official_modern'].get_data(0xf07d0,0x6e)
    result['identical_disk_geometry_wrapper']={'start':'004f07d0','end':'004f083e','sha256':hashlib.sha256(data).hexdigest()}
    original = images['original']
    assert images['official_modern'].get_data(0xb5e50,0x4a) == b'\x90'*0x4a
    assert original.get_data(0xb5e86,7) == bytes.fromhex('2eff1564475300')
    assert original.get_data(0xb5e8d,5) == bytes.fromhex('e8ebcb0300')
    result['removed_corruption_diagnostic'] = {'entry': '004b5e50', 'end_exclusive': '004b5e9a',
        'modern_same_address': '74 NOP bytes; not proof all diagnostic behavior disappeared',
        'tables': {}, 'message_flags': '00000031', 'input': 'EAX unchecked table index',
        'post_dialog_call': '004f2a7d; clears EAX then calls004dfd04',
        'limit': 'Termination route includes indirect callbacks; complete nonreturn guarantee not established.'}
    for va in (0x4b55c8,0x4b55e0):
        pointers = struct.unpack('<6I', original.get_data(va-0x400000,24))
        result['removed_corruption_diagnostic']['tables'][f'{va:08x}'] = [
            {'index': i, 'pointer': f'{address:08x}',
             'text_latin1': original.get_string_at_rva(address-0x400000).decode('latin1')}
            for i,address in enumerate(pointers)]
    assert images['official_modern'].get_data(0xb5ea0,0x6b) == b'\x90'*0x6b
    assert original.get_data(0xf4b80,0x21) == images['official_modern'].get_data(0xf4b80,0x21)
    assert original.get_data(0xb60f3,5) == bytes.fromhex('e8a8fdffff')
    result['removed_texture_resource_log'] = {'entry': '004b5ea0', 'end_exclusive': '004b5f0b',
        'modern_same_address': '107 NOP bytes', 'original_setup_call': '004b60f3',
        'input_eax': 'selector; value6 adds descriptor+74h', 'input_edx': 'unchecked language-table index',
        'descriptor_primary_field': '70h', 'threshold_signed': 2097152,
        'stream': '00566f72', 'format_va': '0053fde0',
        'format': original.get_string_at_rva(0x13fde0).decode('ascii'),
        'formatter_adapter': '004f4b80..004f4ba1 identical across both baselines', 'tables': {},
        'limit': 'Diagnostic output only; descriptor units, stream destination and observed write success not established.'}
    for va in (0x4b55f8,0x4b5610):
        pointers = struct.unpack('<6I', original.get_data(va-0x400000,24))
        result['removed_texture_resource_log']['tables'][f'{va:08x}'] = [
            {'index': i, 'pointer': f'{address:08x}',
             'text_latin1': original.get_string_at_rva(address-0x400000).decode('latin1')}
            for i,address in enumerate(pointers)]
    assert images['official_modern'].get_data(0xb6590,0x21c) == b'\x90'*0x21c
    assert original.get_data(0xb5872,9) == bytes.fromhex('e8190d000083f8057d')
    result['removed_directdraw_probe'] = {'entry': '004b6590', 'end_exclusive': '004b67ac',
        'modern_same_address': '540 NOP bytes', 'caller_call': '004b5872',
        'caller_required_signed_minimum': 5, 'library': original.get_string_at_rva(0x13fefc).decode(),
        'export': original.get_string_at_rva(0x13ff08).decode(),
        'queried_identifiers': {f'{va:08x}': str(uuid.UUID(bytes_le=original.get_data(va-0x400000,16)))
                               for va in (0x56b928,0x56b938)},
        'diagnostic_table': [],
        'result_paths': {'0': 'OS-query/platform guard, library/export/create failure or intermediate method failure',
                         '1': 'First queried interface not obtained', '3': 'Surface queried interface not obtained',
                         '5': 'Final interface obtained and success cleanup completed'},
        'limit': 'Static path tags, not a complete installed DirectX version detector or runtime result.'}
    for i,va in enumerate(struct.unpack('<6I',original.get_data(0xb5580,24))):
        result['removed_directdraw_probe']['diagnostic_table'].append({
            'index': i, 'pointer': f'{va:08x}',
            'text_latin1': original.get_string_at_rva(va-0x400000).decode('latin1')})
    for start,end in ((0x4b62a0,0x4b6311),(0x4b6320,0x4b6400)):
        assert images['official_modern'].get_data(start-0x400000,end-start) == b'\x90'*(end-start)
    encoded = original.get_data(0x15fdc0,6)
    decoded = bytes((b+13)&255 for b in encoded)
    assert decoded == b'remote'
    assert original.get_string_at_rva(0xb5688) == b'C:NFS3.EXE'
    assert original.get_data(0xa3d67,5) == bytes.fromhex('e8b4250100')
    assert original.get_data(0xf9440,7) == bytes.fromhex('2eff1518455300')
    assert any(i.address == 0x534518 and i.name == b'GetDriveTypeA' for d in original.DIRECTORY_ENTRY_IMPORT for i in d.imports)
    result['removed_install_media_admission'] = {
        'prefix_helper': '004b62a0..004b6311', 'admission_helper': '004b6320..004b6400',
        'startup_call': '004a3d67', 'encoded_prefix_hex': encoded.hex(),
        'decoded_prefix': decoded.decode(), 'prefix_input_va': '007a26b4', 'compare_limit': 6,
        'drive_probe_iat': '00534518', 'accepted_drive_type_literal': 5,
        'filename_template': 'C:NFS3.EXE', 'drive_indices': '0..25 inclusive',
        'install_filename': original.get_string_at_rva(0x13fe30).decode(), 'tables': {},
        'limits': ['File/path helper004f9390 and resource helper004f0330 not fully reconstructed.',
                   'The template is drive-relative, not a proven root-absolute executable path.',
                   'No media, drive, file or game operation executed.']}
    for table in (0x4b5694,0x4b56ac):
        result['removed_install_media_admission']['tables'][f'{table:08x}'] = [
            {'index': i, 'pointer': f'{va:08x}',
             'text_latin1': original.get_string_at_rva(va-0x400000).decode('latin1')}
            for i,va in enumerate(struct.unpack('<6I',original.get_data(table-0x400000,24)))]
    result['limits']=['No memory, disk, desktop, dialog or target API execution.','Memory fields described by exact offsets; no complete API structure/type reconstruction.','Current-directory helper, API failures and diagnostic termination internals are not fully audited here.','No release-note attribution inferred solely from a changed startup routine.']
    (ROOT/'analysis/evidence/audits/original-modern-startup-requirements.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: startup requirement counterparts, caller witnesses, imports and messages')


if __name__=='__main__':main()
