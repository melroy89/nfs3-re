"""Static demo-startup branch witnesses; no target execution or field-name inference."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind':'removed-demo-startup-branches','binaries':{},
              'limits':['Raw storage effects, not verified menu/gameplay meaning.',
                        'No runtime demo launch; other writers and flag producers not exhaustive.']}
    capture = ROOT/'analysis/captures/modern-differences/demo-startup'
    capture.mkdir(parents=True,exist_ok=True)
    for label in ('original','official_modern'):
        relative,expected,_ = SPECS[label]
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        switches = {}
        for i in (20,21):
            pointer = struct.unpack('<I',pe.get_data(0x15eb34+4*i,4))[0]
            switches[str(i)] = pe.get_string_at_rva(pointer-0x400000).decode('ascii')
        start,end = 0x4a3b3d,0x4a3d05
        code = pe.get_data(start-0x400000,end-start)
        out = capture/f'{label}-{start:08x}.asm'
        out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
        row = {'path':relative,'sha256':expected,'switches':switches,
               'span':{'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                       'bytes_sha256':hashlib.sha256(code).hexdigest(),
                       'assembly':str(out.relative_to(ROOT)),
                       'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}}
        if label == 'original':
            assert switches == {'20':'-e3demo','21':'-msdemo'}
            assert pe.get_data(0xa3b3d,13).hex() == 'f6052eeb5500200f84d8000000'
            assert pe.get_data(0xa3c22,13).hex() == 'f6052eeb5500100f84d6000000'
            assert pe.get_data(0xa3c07,9).hex() == '31c066891d0a625500'
            assert pe.get_data(0xa3c1c,6).hex() == '66a31e625500'
            assert pe.get_data(0xa3bcd-1,7).hex() == '66890db4625500'
            assert pe.get_data(0xa3bd3,7).hex() == '66890db6625500'
            assert pe.get_data(0xa3cae,14).hex() == '66891db662550066891db8625500'
            assert pe.get_data(0xa3cd0,5).hex() == 'b801000000'
            assert pe.get_data(0xa3ce4,6).hex() == '66a31e625500'
        else:
            assert switches == {'20':'','21':''}
            assert code == b'\x90'*(end-start)
        result['binaries'][label] = row
    result['branch_order'] = ['bit21/msdemo at004a3b3d','bit20/e3demo at004a3c22']
    result['differing_word_stores'] = {
        '005562b6':{'msdemo':1,'e3demo':0},
        '0055621e':{'msdemo':0,'e3demo':1}}
    result['common_raw_effects'] = {
        '0055b041..0055b049_exclusive':'32 33 34 38 3b 3f 40 38',
        '00554f50':'DWORD0',
        '00556382':'clear18bytes through004e0640; subsequentlyWORD00556388=1',
        'WORD1':['005562b4','0055628a','00556224','00556208','00556262'],
        'WORD0':['005562b8','00556220','00556222','00556264','0055637c','0055620a','00556286','00556288']}
    result['precedence'] = 'When both flagbits are set, e3demo branch executes after msdemo and overwrites both differing WORDs; no early exclusive-branch dispatch.'
    (ROOT/'analysis/evidence/audits/removed-demo-startup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: switch slots, independent ordered gates, selected differing stores and456-byte Modern NOP replacement')


if __name__ == '__main__':
    main()
