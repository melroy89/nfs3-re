"""Static original -fpuerrors startup removal; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    capture = ROOT/'analysis/captures/modern-differences/startup-fpuerrors'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-startup-fpuerrors-comparison', 'binaries': {},
              'limits': ['No target instructions or floating-point exceptions executed.',
                         'Guard initialization, other helper callers and subsequent control-word writes not exhaustively traced.']}
    helper_images = []
    for label in ('original', 'official_modern'):
        relative, expected, _ = SPECS[label]
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        pointer = struct.unpack('<I', pe.get_data(0x15eb34+25*4,4))[0]
        name = pe.get_string_at_rva(pointer-0x400000).decode('ascii')
        row = {'path': relative, 'sha256': expected, 'slot25': name, 'spans': []}
        for start,end in [(0x4a3d05,0x4a3d4a),(0x4f7c90,0x4f7cdc)]:
            output = capture/f'{label}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            row['spans'].append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(output.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        helper_images.append(pe.get_data(0xf7c90,0x4c))
        if label == 'original':
            assert name == '-fpuerrors'
            assert pe.get_data(0xa3d05,9).hex() == 'f6052feb550002743c'
            calls = []
            for offset,mask in enumerate((4,2,1,8,16)):
                start = 0x4a3d0e+12*offset
                code = pe.get_data(start-0x400000,12)
                assert code[:7] == b'\xba'+struct.pack('<I',mask)+b'\x31\xc0'
                assert code[7] == 0xe8
                assert start+12+struct.unpack('<i',code[8:])[0] == 0x4f7c90
                calls.append({'setup':f'{start:08x}','value_eax':0,'mask_edx':mask,'target':'004f7c90'})
            row['calls'] = calls
        else:
            assert name == ''
            assert pe.get_data(0xa3d05,0x45) == b'\x90'*0x45
        result['binaries'][label] = row
    assert helper_images[0] == helper_images[1]
    assert helper_images[0][0x1e:0x2f].hex() == '85d2741c89d08b3424f7d021da21f009d0'
    result['helper'] = {'bytes_identical':True,'guard':'BYTE005644c0 nonzero',
        'contract':'EAX newbits, EDX mask; CW=(oldCW & ~mask)|(newbits & mask); returns zero-extended rereadCW; guardfalse returns0',
        'startup_effect':'Clear lowfive maskbits001f, in order4,2,1,8,10hex; preserve precision-maskbit0020, precision-control and rounding bits',
        'limitation':'No claim about persistent exception policy after later FINIT/FLDCW paths'}
    (ROOT/'analysis/evidence/audits/startup-fpuerrors-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original switch/gate/five calls, Modern removal, retained helper equality')


if __name__ == '__main__':
    main()
