"""Static witnesses for seven previously unreferenced changed Modern entries."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = [(0x426290,0x426295),(0x42c700,0x42c7e6),
         (0x45d7ad,0x45d837),(0x4f915e,0x4f916a),
         (0x517784,0x51778a),(0x524290,0x5242ed),
         (0x533e86,0x533e93),(0x537340,0x537348)]


def main():
    result = {'kind': 'small-entry-boundary-and-argument-comparison', 'binaries': {}}
    capture = ROOT/'analysis/captures/modern-differences/remaining-small-entries'
    capture.mkdir(parents=True,exist_ok=True)
    blobs = {}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        spans={}
        rows=[]
        for start,end in SPANS:
            data=pe.get_data(start-0x400000,end-start)
            assert len(data)==end-start
            spans[start]=data
            row={'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                 'sha256':hashlib.sha256(data).hexdigest(),'hex':data.hex()}
            if start!=0x537340:
                path=capture/f'{label}-{start:08x}.asm'
                path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                    f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
                row['assembly']=str(path.relative_to(ROOT))
            rows.append(row)
        blobs[label]=spans
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
        if label=='official_modern':
            imports=[i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                     if i.address==0x534520]
            assert imports==['GetFileAttributesA']
            message=pe.get_data(0x53d2f2-0x400000,128).split(b'\0')[0]
            assert message==b'DDRAW.DLL is not imported.'
            result['modern_import_00534520']=imports[0]
            result['modern_message_0053d2f2']=message.decode()
    old,new=blobs['original'],blobs['official_modern']
    assert old[0x426290]==bytes.fromhex('5589e55dc3')
    assert new[0x426290]==b'\xc3'+b'\x90'*4
    a,b=old[0x42c700],new[0x42c700]
    assert a[:0x1a]==b[:0x1a] and a[0x1f:]==b[0x1f:]
    assert a[0x1a:0x1f]==bytes.fromhex('ba00009642')
    assert b[0x1a:0x1f]==bytes.fromhex('ba0000c042')
    assert struct.unpack('<d',old[0x537340])[0]==15.0
    assert struct.unpack('<d',new[0x537340])[0]==3.8
    assert old[0x45d7ad][0]==0xc3 and new[0x45d7ad][0]==0x60
    assert old[0x45d7ad][1:0x85]==new[0x45d7ad][1:0x85]
    assert old[0x45d7ad][0x85:]==bytes.fromhex('b803000000')
    assert new[0x45d7ad][0x85:0x87]==bytes.fromhex('61c3')
    assert new[0x4f915e]==bytes.fromhex('515250ff15204553005a59c3')
    assert new[0x517784]==bytes.fromhex('a3b4327a00c3')
    a,b=old[0x524290],new[0x524290]
    assert a[:0x4e]==b[:0x4e] and a[0x53:]==b[0x53:]
    assert a[0x4e:0x53]==bytes.fromhex('e80df7f7ff')
    assert b[0x4e:0x53]==bytes.fromhex('e8cdfaf7ff')
    assert new[0x533e86]==bytes.fromhex('b8f2d25300e87c18f8ffc20c00')
    result['limits']=['No target execution or Ghidra changes.',
        'Modern metadata does not establish original function counterparts.',
        'Caller coverage, full callee semantics and runtime effects remain unverified.']
    (ROOT/'analysis/evidence/audits/remaining-small-entries.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print('PASS: seven small entries plus referenced progress data verified')


if __name__=='__main__':main()
