"""Static1.4.0/1.5.0 optional second-logo-image load and draw linkage."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble
from audit_endpoint_comma_history import HISTORY


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    capture = ROOT/'analysis/captures/modern-differences/logo2-history'
    capture.mkdir(parents=True,exist_ok=True)
    result = {'kind':'historical-optional-logo2-producer-consumer','versions':{},
        'limits':['No target instructions, file APIs, upload or animation execution.',
                  'Static paths require successful helper returns; no uploaded image contents or actual external logo2.qfs file qualified.',
                  'Final1.6.1 uses the separately documented logos.qfs metadata loader; historical logo2 path is not attributed to final.',
                  'Selected-index validity, initialization order and later count/handle mutation are not fully qualified.']}
    tables = []
    for version,(archive_hash,exe_hash) in HISTORY.items():
        relative = f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive = ROOT/relative
        assert sha(archive.read_bytes()) == archive_hash
        raw = subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        assert sha(raw) == exe_hash
        pe = pefile.PE(data=raw)
        def get(start,end):return pe.get_data(start-0x400000,end-start)
        spans = [(0x4a4390,0x4a440d if version=='1.4.0' else 0x4a4424),
                 (0x4a40c0,0x4a4386),
                 (0x4a4410 if version=='1.4.0' else 0x4a4424,0x4a46f0),
                 (0x460478,0x46048e),(0x4601c4,0x4601c9)]
        if version=='1.5.0':spans += [(0x4f91ec,0x4f9204),(0x4f915e,0x4f916a)]
        rows = []
        for start,end in spans:
            data = get(start,end)
            path = capture/f'{version}-{start:08x}.asm'
            path.write_text('\n'.join(disassemble(data,start))+'\n')
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                         'bytes':len(data),'sha256':sha(data),'hex':data.hex(),
                         'assembly':str(path.relative_to(ROOT)),'assembly_sha256':sha(path.read_bytes())})
        assert get(0x460489,0x46048e).hex() == 'e8023f0400'
        table = get(0x55e8dc,0x55e95c);tables.append(table)
        table_rows = list(struct.iter_unpack('<4I',table))
        assert [r[3] for r in table_rows] == [0]*6+[1]*2
        if version=='1.4.0':
            assert pe.get_string_at_rva(0x13cf0c) == b'logo.qfs'
            assert get(0x4a40cd,0x4a40d7).hex() == 'c705901b7a0006000000'
        else:
            assert pe.get_string_at_rva(0x13cf28) == b'logo.qfs'
            assert pe.get_string_at_rva(0x13cf34) == b'logo2.qfs'
            assert get(0x4a4391,0x4a439c).hex() == '31dbf605583a7a0006752a'
            assert get(0x4a43aa,0x4a43b6).hex() == 'b306a3901b7a00b834cf5300'
            assert get(0x4a43bf,0x4a43ce).hex() == 'b308a3941b7a00891dbc1a7a0061c3'
            assert get(0x4a40cd,0x4a40cf).hex() == 'eb08'
            assert get(0x4a45ab,0x4a45b5).hex() == '8b460c8b0485901b7a00'
            imports={e.address:e.name.decode('ascii') for d in pe.DIRECTORY_ENTRY_IMPORT for e in d.imports if e.name}
            assert imports[0x534520] == 'GetFileAttributesA'
        result['versions'][version] = {'archive':relative,'archive_sha256':archive_hash,'member':'nfs3.exe','sha256':exe_hash,
            'spans':rows,'table_0055e8dc':{'hex':table.hex(),'sha256':sha(table),
                'record_stride':16,'rows':table_rows,'fourth_DWORD_role':'uploaded-image index0 or1'},
            'loader_call':'00460489 ->004a4390',
            'animation_target':'004a4410' if version=='1.4.0' else '004a4424'}
    assert tables[0] == tables[1]
    result['checks'] = {'eight_record_table_identical':True,
        'producer':'1.4.0 slot producer writes6 to old count007a1b90;1.5.0 bypasses that store, reuses007a1b90 as first image handle and publishes0/6/8 at007a1abc.',
        'admission':'Mask6 rejects loading. Primary identifier0 prevents second attempt. Primary nonzero gives6; second nonzero gives8.',
        'consumer':'1.5.0 selected index*16 -> record+0c image index ->007a1b90[image index] -> draw helper004d7d90.'}
    (ROOT/'analysis/evidence/audits/logo2-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.4.0/1.5.0 second-image load,0/6/8 count policy, retained records and draw-handle selection')


if __name__=='__main__':main()
