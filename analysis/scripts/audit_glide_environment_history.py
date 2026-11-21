"""Date selected hardcoded Glide environment requests; static only."""
import hashlib,json,subprocess,struct
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-glide-environment-history','versions':{}};images={}
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);images[version]=(raw,pe)
        spans=[('hardcoded_request_block',0x4f8953,0x4f8a51),('environment_adapter_prefix',0x4f8b50,0x4f8bc3)]if version=='1.3.1'else[('replacement_setup_prefix',0x4f8a50,0x4f8a84)]
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':pe.get_data(a-0x400000,b-a).hex(),
                'sha256':sha(pe.get_data(a-0x400000,b-a)),'disassembly':disassemble(pe.get_data(a-0x400000,b-a),a)}for n,a,b in spans]}
    old,pe=images['1.3.1'];new,_=images['1.4.0']
    specs=[(0x4f8958,0x54d7b0,''),(0x4f8969,0x54d7c0,''),(0x4f897f,0x54d7dc,'1'),
        (0x4f8993,0x54d7f4,'1.0'),(0x4f89a7,0x54d800,'1.0'),(0x4f89bb,0x54d80c,'1.0'),(0x4f89cf,0x54d818,'1.0'),
        (0x4f89e3,0x54d824,'1'),(0x4f89f7,0x54d834,'1.0'),(0x4f8a0b,0x54d844,'1.0'),(0x4f8a1f,0x54d854,'1.0'),(0x4f8a33,0x54d864,'1.0'),(0x4f8a47,0x54d870,'1')]
    rows=[]
    for site,address,value in specs:
        assert pe.get_data(site-0x400000,5)==b'\xb8'+struct.pack('<I',address)
        value_address={'':0x54d7ac,'1':0x54d7d8,'1.0':0x54d7f0}[value]
        assert pe.get_data(site-0x400000-5,5)==b'\xba'+struct.pack('<I',value_address)
        call=site+(7 if site in (0x4f8958,0x4f8969)else 5)
        op=pe.get_data(call-0x400000,5);assert op[0]==0xe8 and call+5+struct.unpack('<i',op[1:])[0]==0x4f8b50
        name=pe.get_string_at_rva(address-0x400000).decode();assert name.encode()not in new
        rows.append({'name':name,'value_literal':value,'name_load':f'{site:08x}','name_address':f'{address:08x}','ascii_occurrences131':old.count(name.encode()),'ascii_occurrences140':0})
    for address,value in [(0x54d7ac,b''),(0x54d7d8,b'1'),(0x54d7f0,b'1.0')]:assert pe.get_string_at_rva(address-0x400000)==value
    imports={i.address:i.name for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
    assert imports[0x5345dc]==b'SetEnvironmentVariableA'
    assert pe.get_data(0xf8ba1,7).hex()=='2eff15dc455300'
    result['selected_old_requests']=rows
    result['limits']=['Selected131 setup block and absence of13 named ASCII literals in140;not exhaustive computed-name/environment-write exclusion.',
        'Empty value literal can become NULL in adapter;environment-existing/overwrite flags and CRT bookkeeping affect outcomes.',
        'Replacement prefix omits these local requests but complete caller correspondence,all legacy paths and inherited/provider environment remain unqualified.',
        'No API/environment/target instruction execution or executable/database mutation.']
    (ROOT/'analysis/evidence/audits/glide-environment-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:13 named hardcoded131 Glide setup requests absent as ASCII literals140;adapter API bound,full exclusion unclaimed')


if __name__=='__main__':main()
