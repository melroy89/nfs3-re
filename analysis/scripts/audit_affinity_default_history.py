"""Verify early enabled and final disabled affinity defaults; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    rel='analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z';ah='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac'
    assert sha((ROOT/rel).read_bytes())==ah
    raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);eh='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72';assert sha(raw)==eh
    ini=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.ini']);assert b'SingleProcAffinity=1'in ini
    pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
    assert pe.get_string_at_rva(0x13ee50)==b'SingleProcAffinity'
    assert pe.get_string_at_rva(0x13ee28)==b'NFS3'
    assert pe.get_string_at_rva(0x13fe28)==b'SetProcessAffinityMask'
    assert pe.get_string_at_rva(0x1347ed).upper()==b'KERNEL32.DLL'
    assert get(0x4b55c1,0x4b55c9).hex()=='31d242e827610400'
    assert get(0x4b558d,0x4b5595).hex()=='31c040e803000000'
    assert get(0x4b55a5,0x4b55af).hex()=='50ff150445530050ffd3'
    imports={i.address:i.name.decode()for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
    assert imports[0x534504]=='GetCurrentProcess'and imports[0x534558]=='GetProcAddress'and imports[0x534674]=='GetPrivateProfileIntA'
    assert get(0x4b62ca,0x4b62cf).hex()=='e8e5f2ffff'
    spans=[('option_and_mask_helpers',0x4b558c,0x4b55d6),('resolver',0x4a6e64,0x4a6e8d),('profile_integer_wrapper',0x4fb6f0,0x4fb703),('option_callsite',0x4b62ca,0x4b62cf)]
    result={'kind':'static-affinity-default-history','early':{'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
        'ini_sha256':sha(ini),'ini_text':ini.decode(),'imports':{f'{a:08x}':imports[a]for a in [0x534504,0x534558,0x534674,0x53458c]},
        'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}}
    finalrel,finalhash,_=SPECS['official_modern'];final=(ROOT/finalrel).read_bytes();assert sha(final)==finalhash
    fp=pefile.PE(data=final);body=fp.get_data(0xb559e,0x30)
    assert body[5:7]==b'\x31\xd2'
    assert fp.get_string_at_rva(0x13f608)==b'SingleProcAffinity'
    result['final']={'path':finalrel,'sha256':finalhash,'capture':{'start':'004b559e','end_exclusive':'004b55ce','hex':body.hex(),'sha256':sha(body),'disassembly':disassemble(body,0x4b559e)}}
    result['verified']=['110 shipped INI sets1;option reader independently supplies default1 to profile integer API.',
        'Nonzero reader result calls mask helper1;nonnull resolved SetProcessAffinityMask pointer receives GetCurrentProcess and mask1.',
        'Official final corresponding option path starts default0;existing startup report details final resolution/call.']
    result['limits']=['110 presence,not exact100 introduction or date of later default change.',
        'No affinity API executed or CPU state observed;success,performance and multicore hang repair unverified.',
        'Selected callsite,not whole startup CFG;actual initialization order and resolver/pointer lifetime remain separate.',
        'No target instructions,environment changes or executable/database mutation.']
    (ROOT/'analysis/evidence/audits/affinity-default-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:110 INI and reader default1 reach conditional mask1 request;final reader default0;runtime untested')


if __name__=='__main__':main()
