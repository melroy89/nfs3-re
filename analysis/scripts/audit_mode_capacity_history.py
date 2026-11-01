"""Static EXE menu-capacity release history, including inclusive label consumers."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble

HISTORY = {
    '1.1.0': ('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac',
              '59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72',
              51,0xa18398,0xa18400,104,0x898),
    '1.2.0': ('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b',
              '4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003',
              101,0xa18254,0xa18320,204,0x8ca),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    capture = ROOT/'analysis/captures/modern-differences/mode-capacity-history'
    capture.mkdir(parents=True,exist_ok=True)
    output = {'kind':'historical-exe-mode-menu-capacity','versions':{},
        'limits':['No target instructions, display enumeration or UI execution.',
                  '1.0.0 artifact not inspected; 1.1.0 establishes an early retained mechanism, not its first introduction.',
                  'Local append capacity and inclusive label routing do not establish provider supply, actual list length or complete memory lifetime.',
                  'Counts, strides and products assume ordinary initialized nonnegative counts without intervening alias mutation.']}
    bodies = {}
    for version,(archive_hash,exe_hash,cap,labels,records,clear,upper) in HISTORY.items():
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive = ROOT/relative
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        assert sha(raw) == exe_hash
        pe = pefile.PE(data=raw)
        def get(start,end):return pe.get_data(start-0x400000,end-start)
        spans = [(0x448210,0x4482b9),(0x4482c0,0x4482e8),
                 (0x4d17b0,0x4d17ca),(0x448400,0x448423)]
        rows = []
        for start,end in spans:
            data = get(start,end)
            bodies[version,start] = data
            path = capture/f'{version}-{start:08x}.asm'
            path.write_text('\n'.join(disassemble(data,start))+'\n')
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                         'bytes':len(data),'sha256':sha(data),'hex':data.hex(),
                         'assembly':str(path.relative_to(ROOT)),'assembly_sha256':sha(path.read_bytes())})
        assert get(0x448235,0x44823e) == bytes.fromhex('833d18925500')+bytes([cap])+bytes.fromhex('7d75')
        assert struct.unpack('<I',get(0x44822c,0x448230))[0] == records
        assert struct.unpack('<I',get(0x4482af,0x4482b3))[0] == labels
        assert struct.unpack('<I',get(0x4482c7,0x4482cb))[0] == labels
        assert struct.unpack('<I',get(0x4482d2,0x4482d6))[0] == clear
        assert get(0x4482cb,0x4482d1).hex() == '891518925500'
        assert get(0x4d17b4,0x4d17bb).hex() == '3d660800007c0f'
        assert get(0x4d17bb,0x4d17c2) == b'\x3d'+struct.pack('<I',upper)+b'\x7f\x08'
        assert upper-0x866+1 == cap
        assert clear == 2*(cap+1)
        assert records-labels == clear
        assert struct.unpack('<I',get(0x448419,0x44841d))[0] == records
        descriptor = struct.unpack('<5I',get(0x5566b8,0x5566cc))
        assert descriptor == (0x537f84,labels,0,0,0x6fbc14)
        assert pe.get_string_at_rva(0x137f84) == b'winsize'
        output['versions'][version] = {'archive':relative,'archive_sha256':archive_hash,'member':'nfs3.exe','sha256':exe_hash,
            'spans':rows,'count':'00559218','signed_reject_count_at_least':cap,
            'record_base':f'{records:08x}','record_stride':276,'label_base':f'{labels:08x}',
            'label_clear_bytes':clear,'cleared_WORD_slots':cap+1,
            'inclusive_dynamic_label_ids':[f'{0x866:04x}',f'{upper:04x}'],
            'descriptor_005566b8':[f'{v:08x}' for v in descriptor],
            'descriptor_key':pe.get_string_at_rva(0x137f84).decode('ascii')}
    # Only the bank addresses and signed comparison immediate differ in the complete collector pair.
    normalized = []
    for version in HISTORY:
        data = bytearray(bodies[version,0x448210])
        for offset,size in [(0x1c,4),(0x2b,1),(0x9f,4)]:data[offset:offset+size]=b'\0'*size
        normalized.append(data)
    assert normalized[0] == normalized[1]
    orig_path,orig_hash,_ = SPECS['original']
    original = (ROOT/orig_path).read_bytes()
    assert sha(original) == orig_hash
    pe = pefile.PE(data=original)
    guard = pe.get_data(0x48235,9)
    assert guard.hex() == '833d18925500147d75'
    assert pe.get_data(0x482af,4) == struct.pack('<I',0x5591ec)
    assert pe.get_data(0x482c7,4) == struct.pack('<I',0x5591ec)
    output['original_guard'] = {'path':orig_path,'sha256':orig_hash,
        'start':'00448235','hex':guard.hex(),'signed_reject_count_at_least':20,
        'label_base':'005591ec'}
    output['checks'] = {'complete_historical_collector_equal_after_only_address_and_capacity_normalization':True,
        'labels_consumer_matches_capacity':True,'cleared_label_slots_include_one_extra_WORD':True,
        'comparison':'Original local cap20; early1.1.0 cap51;1.2.0 cap101. Headlines50/100 are not exact local caps.'}
    (ROOT/'analysis/evidence/audits/mode-capacity-history.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS: pinned1.1.0/1.2.0 local51/101 append guards, label ranges, initialization and record consumers')


if __name__ == '__main__':main()
