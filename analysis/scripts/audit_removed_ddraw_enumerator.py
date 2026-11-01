"""Static removed legacy DirectDraw enumeration wrapper/adapter."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-removed-DirectDraw-enumeration-adapter','binaries':{}}
    for label,(path,digest,_) in SPECS.items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        spans=[(0x4ebae0,0x4ebaf0),(0x4ed904,0x4edbc0),(0x533e80,0x533e86)]
        imports={e.address:e.name.decode() for lib in pe.DIRECTORY_ENTRY_IMPORT for e in lib.imports if e.name}
        wrapper=pe.get_data(0xebae0,16);adapter=pe.get_data(0xedb80,55)
        if label=='original':
            assert imports[0x53466c]=='DirectDrawEnumerateA'
            assert wrapper.hex()=='5152506880db4e00e8938304005a59c3'
            assert pe.get_data(0xeb420,16)==bytes(16)
            assert adapter[-3:]==bytes.fromhex('c21000')
        else:
            assert wrapper==b'\x90'*16 and pe.get_data(0xedb80,64)==b'\x90'*64
            assert 'DirectDrawEnumerateA' not in imports.values()
        candidates=[]
        for section in pe.sections:
            if not section.Characteristics&0x20000000:continue
            code=section.get_data();base=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
            for offset in range(len(code)-4):
                if code[offset]==0xe8 and (base+offset+5+struct.unpack_from('<i',code,offset+1)[0])&0xffffffff==0x4ebae0:
                    candidates.append(f'{base+offset:08x}')
        assert not candidates
        result['binaries'][label]={'path':path,'sha256':digest,
            'direct_e8_wrapper_candidates':candidates,
            'wrapper_pointer_occurrences':raw.count((0x4ebae0).to_bytes(4,'little')),
            'adapter_pointer_occurrences':raw.count((0x4edb80).to_bytes(4,'little')),
            'template_004eb420':pe.get_data(0xeb420,16).hex(),
            'spans':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}',
                      'sha256':sha(pe.get_data(a-0x400000,b-a)),
                      'bytes_hex':pe.get_data(a-0x400000,b-a).hex(),
                      'disassembly':disassemble(pe.get_data(a-0x400000,b-a),a)} for a,b in spans]}
    old,new=[pefile.PE(str(ROOT/SPECS[label][0])) for label in ('original','official_modern')]
    assert old.get_data(0xed904,0x27c)==new.get_data(0xed904,0x27c)
    result['adapter_contract']={'original_entry':'004edb80','body_end_exclusive':'004edbb7',
        'stack_arguments':['GUID pointer','description pointer','driver-name pointer','callback/context pointer'],
        'forwarded_registers':{'EAX':'GUID pointer, or local16-byte zero copy if null',
            'EDX':'description pointer','EBX':'driver-name pointer','ECX':'called callback/context pointer'},
        'return':'EAX1 after callback normal return; RET16; callback return discarded',
        'local_preservation':'EBX/ESI/EDI saved and restored; ECX/EDX/flags not preserved by this body',
        'assumptions':'DF0, valid caller stack and pointers, callback returns with expected register ABI; no retained local GUID pointer beyond call'}
    result['partition']={'unchanged':'004ed904..004edb80,636 bytes',
                         'removed':'004edb80..004edbc0,64 bytes including55-byte body and9-byte alignment'}
    result['limits']=['No target/API execution; no original reachability or visible device-list effect established.',
        'No directE8 candidates and literal-pointer counts are bounded encoding searches, not exclusion of computed/indirect calls.',
        'Static import removal does not exclude dynamically resolved enumeration elsewhere.',
        'Callback/context interpretation follows this wrapper; not a general signature for other DirectDraw callbacks.']
    (ROOT/'analysis/evidence/audits/removed-ddraw-enumerator.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: removed16-byte wrapper/55-byte adapter,64-byte NOP span and unchanged636-byte preceding interval')


if __name__=='__main__':main()
