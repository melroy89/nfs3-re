"""Date selected screenshot counter/storage/format changes; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble
PINS={
 '1.3.1':('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664'),
 '1.4.0':('8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9','7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-screenshot-counter-history','versions':{}};copies=[]
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        old=version=='1.3.1';a,b=(0x4c44f9,0x4c4531)if old else(0x4e31cc,0x4e31f7)
        if old:
            assert get(a,a+7).hex()=='8b0df800560041'
            assert get(0x4c4514,0x4c451a).hex()=='890df8005600'
        else:assert get(a,a+12).hex()=='31c040f00fc105e0d16f0040'
        fmt=pe.get_string_at_rva(0x1401d8).decode();assert fmt==('%s\\nfs3_%02d.tga'if old else'nfs3_%04d.%s')
        counter=0x5600f8 if old else 0x6fd1e0;inside=0x6fbb40<=counter and counter+4<=0x6fbb40+0x20f0
        assert inside==(not old)
        spans=[('counter_loop',a,b),('config_save_copy_and_request',0x472869,0x4728c3)]
        copies.append(get(0x472869,0x4728c3))
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,
            'format_at_005401d8':fmt,'counter':f'{counter:08x}','inside_config_save_extent':inside,
            'captures':[{'name':n,'start':f'{s:08x}','end_exclusive':f'{e:08x}','hex':get(s,e).hex(),
             'sha256':sha(get(s,e)),'disassembly':disassemble(get(s,e),s)}for n,s,e in spans]}
    assert copies[0]==copies[1]
    result['verified']=[
        '131 selected loop increments005600f8 ordinarily;140 loop uses LOCK XADD006fd1e0 then increments returned old value.',
        'Only140 selected counter lies within config base006fbb40,size20f0;save copy/request suffix identical.',
        'Shared format address changes from path-prefixed two-digit TGA to four-digit extension-parametrized form.',
        'This dates selected counter relocation/atomicity/format changes to131->140,consistent withMP140-055.']
    result['limits']=[
        'No all-writer/alias analysis or proof original had no other persistence route.',
        'No actual saved bytes,cross-launch game result,full startup/default lifetime or immediate save-after-capture guarantee.',
        'Minimum formatting width does not cap the counter;collision selection is not filename reservation.',
        'No target instructions,file APIs,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/screenshot-counter-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 counter moves into serialized config extent,becomes atomic,and adopts new filename format')


if __name__=='__main__':main()
