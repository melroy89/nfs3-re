"""Identify original DDE code beneath a Modern outside-function NOP span."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'removed-original-dde-code-region','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/removed-dde'
    capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        spans=[]
        for start,end in [(0x4900b0,0x490106),(0x490110,0x490133),
                          (0x490140,0x4902ee),(0x4902f0,0x49042c),
                          (0x4901c3,0x490430)]:
            data=pe.get_data(start-0x400000,end-start)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
            if label=='official_modern' and start==0x4901c3:
                assert data==b'\x90'*(end-start)
        imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT
                 for i in d.imports if i.name}
        dde=sorted(name for name in imports.values() if name.startswith('Dde'))
        assert len(dde)==7
        row={'path':relative,'sha256':expected,'spans':spans,'dde_imports':dde}
        references={}
        for target in (0x4900b0,0x490110,0x490140,0x4902f0):
            relative_hits=[]
            for section in pe.sections:
                if not section.Characteristics & 0x20000000:continue
                data=section.get_data()
                base=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
                for offset in range(len(data)-4):
                    opcode=data[offset]
                    if opcode not in (0xe8,0xe9):continue
                    dest=(base+offset+5+struct.unpack_from('<i',data,offset+1)[0]) & 0xffffffff
                    if dest==target:
                        relative_hits.append({'va':f'{base+offset:08x}',
                                              'opcode':f'{opcode:02x}'})
            absolute_hits=[]
            position=0
            while True:
                offset=raw.find(struct.pack('<I',target),position)
                if offset<0:break
                absolute_hits.append(f'{pe.OPTIONAL_HEADER.ImageBase+pe.get_rva_from_offset(offset):08x}')
                position=offset+1
            expected_relative=([{'va':'004900f4','opcode':'e8'},
                                {'va':'0049012b','opcode':'e8'}]
                               if label=='official_modern' and target==0x4900b0 else [])
            expected_absolute=['004900cb'] if label=='original' and target==0x4902f0 else []
            assert relative_hits==expected_relative and absolute_hits==expected_absolute
            references[f'{target:08x}']={'rel32_byte_candidates':relative_hits,
                                       'absolute_address_encodings':absolute_hits}
        row['entry_reference_search']={
            'scope':'E8/E9 rel32 byte candidates across executable sections; absolute DWORD encodings across all file bytes',
            'results':references,
            'limits':'Not an instruction-boundary or reachability proof. Excludes computed/relative-table aliases, interior entries, external callers and runtime-generated pointers.'}
        if label=='original':
            expected_thunks={0x533eb6:'DdeQueryStringA',0x533ebc:'DdeClientTransaction',
                0x533ec2:'DdeGetLastError',0x533ec8:'DdeConnect',
                0x533ece:'DdeCreateStringHandleA',0x533ed4:'DdeUninitialize',
                0x533eda:'DdeInitializeA'}
            row['import_thunks']={}
            for va,name in expected_thunks.items():
                data=pe.get_data(va-0x400000,6)
                assert data[:2]==b'\xff\x25'
                slot=struct.unpack('<I',data[2:])[0];assert imports[slot]==name
                row['import_thunks'][f'{va:08x}']={'iat':f'{slot:08x}','name':name}
            strings={0x53bb90:'NETSCAPE',0x53bb9c:'IExplore',0x53bba8:'WWW_OpenURL',
                     0x53bbb4:'"',0x53bbb8:',,0xFFFFFFFF,0,,,NETREPORT',0x53bbd4:'NETREPORT'}
            for va,value in strings.items():
                assert pe.get_data(va-0x400000,128).split(b'\0')[0]==value.encode()
            row['strings']={f'{va:08x}':s for va,s in strings.items()}
            assert pe.get_data(0x4900ca-0x400000,5)==bytes.fromhex('68f0024900')
        result['binaries'][label]=row
    result['limits']=['No target execution or Ghidra writes.',
        'Original caller reachability and user-visible activation not established.',
        'Retained imports do not prove Modern executes DDE; removed body does not prove all browser opening disappeared.',
        'Outside span begins within an original branch operand; it is not a function boundary.']
    (ROOT/'analysis/evidence/audits/removed-dde-region.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original DDE bodies/imports/strings and 621-byte Modern NOP span verified')


if __name__=='__main__':main()
