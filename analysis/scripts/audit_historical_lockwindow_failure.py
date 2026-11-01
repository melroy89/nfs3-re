"""Static1.5.0->1.5.1 lockwindow failure callback comparison; no DLL execution."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble

ARCHIVES = {'1.5.0':'de6cbbbce4b77765f96472aaf8c12a4e245e2abceaf26dd9b84215442b1f4a0f',
            '1.5.1':'c7b66da29ef8cd58c56e27a403bd2889d8a4f0f7cac0873c28a1b4b5a09723de'}
DRIVERS = {'dx5/dx5a':(0x11d4,0x1366,0x1880,0x1891),
           'dx6/dx6a':(0x1240,0x13dd,0x1d90,0x1da1),
           'softtri/softtria':(0x3530,0x36d0,None,None)}


def main():
    result = {'kind':'historical-lockwindow-failure-callback','archives':{},'drivers':{},
              'limits':['Historical driver comparison, not original retail EXE correspondence.',
                        'No DLL, surface lock, callback or failure injection executed.',
                        'Registration admission, complete state lifetime and actual success/failure outcomes remain unqualified.']}
    capture = ROOT/'analysis/captures/modern-differences/lockwindow-history'
    capture.mkdir(parents=True,exist_ok=True)
    for version,expected in ARCHIVES.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/relative
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
        result['archives'][version]={'path':relative,'sha256':expected}
        exe_raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        exe_expected={'1.5.0':'d9db8ead63a9697c4c6c3933e720cd93565f67bd4b264e8bbc0d98d03c236dae',
                      '1.5.1':'4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17'}[version]
        assert hashlib.sha256(exe_raw).hexdigest()==exe_expected
        exe=pefile.PE(data=exe_raw)
        table=struct.unpack('<8I',exe.get_data(0x16afd0,32))
        assert table[5]==0x524550
        assert exe.get_data(0x12472d,13).hex()=='68d0af56006a13ff156cf99e00'
        callback=exe.get_data(0x124550,0x3b)
        assert callback.hex()=='837c240400741b538b1d8044560053ff15b84453005b8b442404a380715600c204008b0d8044560051ff15884553008b442404a380715600c20400'
        imports={i.address:i.name for d in exe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x5344b8]==b'EnterCriticalSection' and imports[0x534588]==b'LeaveCriticalSection'
        exe_spans=[]
        for lo,hi in [(0x524550,0x52458b),(0x52471d,0x524740)]:
            block=exe.get_data(lo-0x400000,hi-lo)
            out=capture/f'{version}-exe-{lo:08x}.asm'
            out.write_text('\n'.join(disassemble(block,lo))+'\n')
            exe_spans.append({'start':f'{lo:08x}','end_exclusive':f'{hi:08x}',
                'bytes_sha256':hashlib.sha256(block).hexdigest(),'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        result['archives'][version]['exe_callback']={'member':'nfs3.exe','sha256':exe_expected,
            'table_0056afd0':[f'{v:08x}' for v in table],'slot_offset':'14','target':'00524550',
            'argument_nonzero':'EnterCriticalSection([00564480])','argument_zero':'LeaveCriticalSection([00564480])',
            'publication':'Then stores raw argument to00567180;RET4','spans':exe_spans}

        for driver,(start,end,helper,helper_end) in DRIVERS.items():
            member=f'drivers/{driver}.dll'
            raw=subprocess.check_output(['7z','x','-so',str(archive),member])
            pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
            assert base==0x60000000
            exports={e.name.decode():e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
            assert exports['_THRASH_lockwindow@0']==start
            row={'member':member,'sha256':hashlib.sha256(raw).hexdigest(),'spans':[]}
            spans=[(start,end)]
            if version=='1.5.1' and helper: spans.append((helper,helper_end))
            if version=='1.5.1':
                copy={'dx5/dx5a':(0x2e26,0x2e45,0x60012888),
                      'dx6/dx6a':(0x36d1,0x36f8,0x6003bcc0),
                      'softtri/softtria':(0x3228,0x3244,0x600400a0)}[driver]
                spans.append(copy[:2])
                assert b'\xbf'+struct.pack('<I',copy[2]) in pe.get_data(copy[0],copy[1]-copy[0])
                row['callback_copy']={'destination':f'{copy[2]:08x}','bytes':32,
                    'consumer_cell_offset':'14','qualification':'Direct bulk-copy writer; full selector dispatch/admission and alternate writes remain separate'}

            for lo,hi in spans:
                code=pe.get_data(lo,hi-lo)
                out=capture/f'{version}-{driver.replace("/","-")}-{lo:08x}.asm'
                out.write_text('\n'.join(disassemble(code,base+lo))+'\n')
                row['spans'].append({'start':f'{base+lo:08x}','end_exclusive':f'{base+hi:08x}',
                    'bytes_sha256':hashlib.sha256(code).hexdigest(),'assembly':str(out.relative_to(ROOT)),
                    'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
            if version=='1.5.1' and helper:
                slot=0x6001289c if driver.startswith('dx5') else 0x6003bcd4
                assert pe.get_data(helper,17)==bytes.fromhex('5389c3a1')+slot.to_bytes(4,'little')+bytes.fromhex('85c0740353ffd05bc3')
            if driver.startswith('dx5'):
                witness=pe.get_data(0x1229,0x11) if version=='1.5.1' else pe.get_data(0x1232,8)
                assert witness.hex()==('85c0740d31c0e84c060000e9ed00000090' if version=='1.5.1' else '85c00f85ec000000')
            elif driver.startswith('dx6'):
                witness=pe.get_data(0x12cc,0x10) if version=='1.5.1' else pe.get_data(0x12d1,11)
                assert witness.hex()==('740e31c0e8bb0a000031c0e9fa000000' if version=='1.5.1' else '740933c081c494000000c3')
            else:
                witness=pe.get_data(0x362f,6)
                assert witness.hex()==('0f858c000000' if version=='1.5.1' else '0f851bffffff')
                if version=='1.5.1': assert pe.get_data(0x36c1,13).hex()=='6a00ff15b4000460e982feffff'
            row['failure_branch_witness_hex']=witness.hex()
            result['drivers'].setdefault(driver,{})[version]=row
    result['finding']='Each inspected nonzero surface-lock-result path adds callback0 before returning through its prior failure continuation; DX5/DX6 use null-guarded register-to-stack adapters.'
    (ROOT/'analysis/evidence/audits/historical-lockwindow-failure.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: two archive hashes, six DLL identities/exports, three changed failure paths and two callback adapters')


if __name__=='__main__':
    main()
