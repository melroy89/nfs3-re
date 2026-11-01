"""Static original low-address startup read/handler witnesses; no fault execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind':'startup-low-address-path','binaries':{},
              'limits':['No memory fault, exception filter or target instruction executed.',
                        'Full exception dispatcher, global consumers and intended OS/debugger policy unresolved.']}
    capture = ROOT/'analysis/captures/modern-differences/startup-low-address'
    capture.mkdir(parents=True,exist_ok=True)
    for label in ('original','official_modern'):
        relative,expected,_ = SPECS[label]
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        row = {'path':relative,'sha256':expected,'spans':[],
               'metadata_0055e8cd_hex':pe.get_data(0x15e8cd,12).hex()}
        for start,end in [(0x4a39f0,0x4a3a10),(0x4a3ad9,0x4a3b3d),
                          (0x4f7af8,0x4f7b1a),(0x4f7b7d,0x4f7ba7)]:
            out = capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            row['spans'].append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        assert pe.get_data(0x15e8c0,4) == bytes(4)
        assert pe.get_data(0x1643fc,4) == bytes(4)
        if label == 'original':
            assert pe.get_data(0xa3ae7,7).hex() == 'b8900100008a00'
            assert pe.get_data(0xa3afd,11).hex() == '8d45c0502eff151c465300'
            assert pe.get_data(0xa3b08,18).hex() == '85c07507b801000000eb0231c0a3c0e85500'
            assert pe.get_data(0xa3b1a,10).hex() == 'b801000000e859400500'
            assert struct.unpack('<I',pe.get_data(0x15e8cf,4))[0] == 0x4a3afd
            assert any(i.address==0x53461c and i.name==b'UnhandledExceptionFilter'
                       for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports)
            row['facts'] = {'read':'004a3ae7 MOV EAX,190;004a3aec MOV AL,[EAX]',
                'handler':'004a3afd passes addressEBP-40h to importedUnhandledExceptionFilter',
                'publication':'0055e8c0=1 if filter returns0,otherwise0',
                'resume':'004a3b1a EAX1 ->runtime entry004f7b7d, which pops multiple registers before testing result',
                'following_publication':'004a3b2d storesDWORD1 at005643fc',
                'frame':'004a3a00/03/08 installs frame via004f7af8 with metadata0055e8cd; first recorded target004a3afd'}
        else:
            assert pe.get_data(0xa3ad9,0x64) == b'\x90'*0x64
            assert struct.unpack('<I',pe.get_data(0x15e8cf,4))[0] == 0x4a3f7d
            row['facts'] = {'replacement':'004a3ad9..004a3b3d all100NOP bytes',
                            'metadata_first_target':'004a3f7d instead of004a3afd'}
        result['binaries'][label] = row
    (ROOT/'analysis/evidence/audits/startup-low-address-path.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baseline hashes, low-address read, filter/result publication and Modern removal')


if __name__ == '__main__':
    main()
