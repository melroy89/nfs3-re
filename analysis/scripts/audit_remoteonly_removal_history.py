"""Date removal of the selected RemoteOnly INI reader; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-remoteonly-removal-history','versions':{}}
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        ini=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.ini']);pe=pefile.PE(data=raw)
        get=lambda a,b:pe.get_data(a-0x400000,b-a);old=version=='1.3.1'
        assert raw.lower().count(b'remoteonly')==int(old)
        assert (b'RemoteOnly=0' in ini)==old
        assert get(0x472b38,0x472b3d).hex()==('e863370400'if old else'b800000000')
        assert get(0x472b43,0x472b48).hex()=='a354bb6f00'
        if old:
            assert pe.get_string_at_rva(0x13edf8)==b'NFS3'
            assert pe.get_string_at_rva(0x13ee4c)==b'RemoteOnly'
            assert get(0x4b62a0,0x4b62c1).hex()=='555352bdf8ed5300bb4cee530031d2e83c54040085c07405b8010000005a5b5dc3'
            imports={i.address:i.name for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
            assert imports[0x534674]==b'GetPrivateProfileIntA'
            assert get(0x4fb702,0x4fb713).hex()=='683c267a00525355ff15744653005a59c3'
        else:assert get(0x4b62a0,0x4b62c1)==b'\x90'*33
        spans=[('config_tail',0x472b38,0x472b48),('reader_or_nops',0x4b62a0,0x4b62c1),('integer_profile_wrapper',0x4fb6f0,0x4fb713)]
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'ini':{'member':'nfs3.ini','sha256':sha(ini),'text':ini.decode()},
            'remoteonly_ascii_count':raw.lower().count(b'remoteonly'),
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    result['verified']=['131 reads NFS3/RemoteOnly integer with caller default0 via shared override/profile wrapper;normalizes any nonzero to1.',
        '140 substitutes MOV EAX,0 for caller CALL,retains store to006fbb54,NOP-fills reader and removes checked ASCII key and shipped INI entry.']
    result['limits']=['Local reader removal,not exhaustive computed-name or field-writer coverage.',
        'Shared override helper4fb734 and parser4f0430 not fully qualified here;caller default0 need not be API fallback0 on every route.',
        'Does not prove the vendor adjective useless,all startup outcomes,or actual media/network effects.',
        'No game/API/target instructions executed;no executable or database edits.']
    (ROOT/'analysis/evidence/audits/remoteonly-removal-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:RemoteOnly selected reader and shipped INI entry removed131 to140;gate becomes literal0')


if __name__=='__main__':main()
