"""Verify original/Modern tier tables and the final EDX/EAX mismatch."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

OLD=[(0x472168,0x6fbc28),(0x472172,0x6fbc2c),(0x472186,0x6fbc1c),
     (0x472190,0x6fbc30),(0x47219a,0x6fbc20),(0x4721a4,0x6fbc24),
     (0x4721ae,0x6fbc3c),(0x47217c,0x791b28)]
NEW=[(0x472e20,0x6fbc28),(0x472e26,0x6fbc2c),(0x472e2c,0x6fbc1c),
     (0x472e32,0x6fbc30),(0x472e38,0x6fbc20),(0x472e3e,0x6fbc24),
     (0x472e44,0x6fbc3c),(0x472e4a,0x6fd1d8)]


def main():
    result={'kind':'graphics-default-tier-tables','binaries':{}}
    suffixes=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        suffixes.append(pe.get_data(0x721b8,56))
        modern=label=='official_modern'
        end=0x472e1d if modern else 0x472f19
        body=pe.get_data(0x472d10-0x400000,end-0x472d10)
        rows=[]
        for va,target in NEW if modern else OLD:
            data=pe.get_data(va-0x400000,6 if modern else 10)
            values=list(data) if modern else list(struct.unpack('<5h',data))
            rows.append({'table':f'{va:08x}','destination':f'{target:08x}',
                         'values':values,'hex':data.hex()})
        row={'path':relative,'sha256':expected,'body_start':'00472d10',
             'body_end_exclusive':f'{end:08x}','body_sha256':hashlib.sha256(body).hexdigest(),
             'tables':rows}
        if modern:
            assert pe.get_data(0x72155,99)==b'\x90'*99
        else:
            assert pe.get_data(0x72155,19)==bytes(19)
        row['old_table_extent']='00472155..004721b8:19 zero bytes plus80 bytes of eight signed-WORD arrays in original;99 NOP bytes in Modern'
        if modern:
            data=pe.get_data(0x472e0f-0x400000,12)
            assert data==bytes.fromhex('0fb691502e4700a3d4d16f00')
            assert pe.get_data(0x472de3-0x400000,5)==bytes.fromhex('e88055fdff')
            assert pe.get_data(0x472e1b-0x400000,2)==bytes.fromhex('61c3')
            assert pe.get_data(0x472e56-0x400000,0xca)==b'\x90'*0xca
            producer=pe.get_data(0x4482e8-0x400000,13)
            assert producer==bytes.fromhex('31c0837e18027c02b001894710')
            getter=pe.get_data(0x448368-0x400000,9)
            assert getter==bytes.fromhex('e8dbffffff8b4010c3')
            descriptor=struct.unpack('<5I',pe.get_data(0x556924-0x400000,20))
            assert descriptor==(0x53a87c,0x5561be,0,0,0x6fd1d4)
            assert pe.get_data(0x53a87c-0x400000,4)==b'fog\0'
            gate=pe.get_data(0x431c1c-0x400000,23)
            assert gate==bytes.fromhex('a1543a7a002305d4d16f00230534925500a3643a7a00c3')
            row['fog_default_chain']={
                'record_producer':'004482e8', 'producer_hex':producer.hex(),
                'menu_record_field_10':'1 iff signed driver record field +18h >= 2, otherwise 0',
                'getter':'00448368','getter_hex':getter.hex(),
                'descriptor':'00556924','token':'fog','selector':'006fd1d4',
                'admission_helper':'00431c1c','admission_hex':gate.hex(),
                'limits':'Requires a valid populated selected record; empty list does not establish initialized field contents.'}
            row['final_unused_edx_table']={'address':'00472e50',
                 'values':list(pe.get_data(0x472e50-0x400000,6)),
                 'load_and_store_hex':data.hex(),
                 'actual_store_source':'EAX from preceding call 00448368, not EDX table load'}
        result['binaries'][label]=row
    assert suffixes[0]==suffixes[1]
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    modern=pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    bindings=[(0x556730,'viewlevel',0x6fbc28),(0x55671c,'hrzlevel',0x6fbc2c),
              (0x5566f4,'cardetail',0x6fbc1c),(0x556708,'sfxlevel',0x6fbc30),
              (0x5566e0,'carlight',0x6fbc20),(0x5566cc,'carchrome',0x6fbc24),
              (0x55676c,'projtex',0x6fbc3c),(0x556564,'mirrorlevel',0x6fd1d8),
              (0x556924,'fog',0x6fd1d4)]
    named=[]
    new_tables={target:list(modern.get_data(table-0x400000,6)) for table,target in NEW}
    for address,key,target in bindings:
        words=struct.unpack('<5I',modern.get_data(address-0x400000,20))
        assert words[2:]==(0,0,target)
        assert modern.get_string_at_rva(words[0]-0x400000).decode('ascii')==key
        ids=[];labels=[]
        for offset in range(8):
            ident=struct.unpack('<H',modern.get_data(words[1]-0x400000+2*offset,2))[0]
            if ident==0:break
            text_offset=struct.unpack_from('<I',english,ident*4)[0]
            ids.append(ident)
            labels.append(english[text_offset:english.index(b'\0',text_offset)].decode('latin1'))
        else:raise AssertionError('unterminated option list')
        row={'descriptor':f'{address:08x}','key':key,'destination':f'{target:08x}',
             'words':[f'{v:08x}' for v in words],'ids':ids,'labels':labels}
        if target in new_tables:
            values=new_tables[target]
            assert all(v<len(labels) for v in values)
            row['table_labels_by_effective_tier']=[labels[v] for v in values]
        named.append(row)
    assert modern.get_data(0x72d11,27).hex()=='8b0da452560083f9057605b905000000f605583a7a00067402d1e9'
    selector=modern.get_data(0x48394,105)
    accessor=modern.get_data(0x48348,41)
    assert selector[:1]==b'\x60' and selector[-2:]==b'\x61\xc3'
    assert accessor.hex()=='a15c82a1003b056082a100720731c0a35c82a10069c014010000053083a100c3e8dbffffff8b4010c3'
    result['named_modern_defaults']={'english_member':'fedata/text/text.eng',
        'english_sha256':hashlib.sha256(english).hexdigest(),'bindings':named,
        'effective_tier':'min(unsigned CPU score,5), then logical shift right1 if renderer mask&6',
        'normal_return_ecx_contract':{'selector':'00448394..004483fd PUSHAD/POPAD',
            'selector_hex':selector.hex(),'record_selector_and_field10_getter':'00448348..00448371 writes no ECX',
            'accessor_hex':accessor.hex()},
        'conditional_cases':[{'score':5,'renderer_mask6_nonzero':masked,'effective_tier':2 if masked else 5,
            'table_labels_before_mode_overrides':{r['key']:r['table_labels_by_effective_tier'][2 if masked else 5]
                for r in named if 'table_labels_by_effective_tier' in r}} for masked in (False,True)],
        'mode_override':'Selected field10 zero forces projtex0 and Z-buffer selector0; nonzero writes Z-buffer selector1. Fog gets raw field10 EAX, not ninth table.',
        'limits':['Derived table labels, not observed settings on this CPU or renderer.',
                  'Requires returning callees with valid stacks, no alias mutation and a valid selected record.',
                  'Other writers/configuration persistence and actual visual quality are outside this mapping.']}
    member='drivers/dx5/dx5a.dll'
    dll_raw=subprocess.check_output(['7z','x','-so',str(archive),member])
    assert hashlib.sha256(dll_raw).hexdigest()=='6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42'
    dll=pefile.PE(data=dll_raw)
    branch=dll.get_data(0x1855,28)
    assert branch.hex()=='83f8037610c7471403000000c7471803000000eb0789471448894718'
    examples=[]
    for q in [0,1,2,3,4,0x7fffffff,0xffffffff]:
        field=3 if q>3 else (q-1)&0xffffffff
        signed=field if field<0x80000000 else field-0x100000000
        selected=int(signed>=2)
        assert selected==int(q>=3)
        examples.append({'unsigned_quotient':q,'field18_hex':f'{field:08x}',
                         'signed_field18':signed,'fog_selector':selected})
    result['dx5_mode_field_to_fog_selector']={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'member':member,'member_sha256':hashlib.sha256(dll_raw).hexdigest(),
        'producer_span':'60001837..60001871','producer_bytes_hex':dll.get_data(0x1837,58).hex(),
        'cap_branch_hex':branch.hex(),
        'quotient':'unsigned60010eb4 / wrap32(width*height*bytes_per_pixel), nonzero denominator required',
        'field18':'Q>3 ->3,otherwise wrap32(Q-1)',
        'derived_selector':'For a valid selected record produced on this callback path,EXE signed field18>=2 iff unsignedQ>=3',
        'instruction_derived_examples':examples,
        'limits':['Arithmetic model, not executed original instructions or renderer observations.',
                  'Does not cover seeded/other-driver records or prove all selected records came through the callback.',
                  'Source60010eb4 ownership and successful buffer allocation are not established.',
                  'DX5 fog-support trial rejects state21 separately; selector1 is not visible fog support.']}
    result['limits']=['Table indexing is version-specific; equal ordinal is not equal CPU capability.',
        'Named options and normal-return ECX preservation are verified; other writers, complete callee lifetimes and visual results remain unqualified.',
        'No target execution, executable changes or Ghidra writes.']
    (ROOT/'analysis/evidence/audits/graphics-default-tables.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original signed-WORD and Modern byte tables; final EDX load/EAX store verified')


if __name__=='__main__':main()
