"""Date selected shared speech path/fallback and Swedish codes110->120."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'),
          '1.2.0':('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003')}
    result={'kind':'static-speech-language-history','versions':{}}
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a);old=version=='1.1.0'
        start,end=(0x4a6f0c,0x4a6f2d)if old else(0x4a6f04,0x4a6f6e)
        spans=[('complete_path_initializer',start,end)]
        if not old:
            spans += [('directory_predicate',0x4a38f0,0x4a3911),('find_terminator',0x4f9390,0x4f9399),('copy_string',0x4f939c,0x4f93a6)]
            assert get(0x4a6f4a,0x4a6f4f).hex()=='e8a1c9ffff'
            assert get(0x4a6f65,0x4a6f6d).hex()=='31c9890d74277a00'
            assert get(0x4a38f0,0x4a38f9).hex()=='515250ff1520455300'
            slots={i.address:i.name for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name};assert slots[0x534520]==b'GetFileAttributesA'
        letters=[]
        for table in [0x409ff0,0x412950]:
            ptrs=struct.unpack('<7I',get(table,table+28));values=[p.get_string_at_rva(v-0x400000).decode('ascii')for v in ptrs]
            assert values==(['E','G','F','S','I','E','E']if old else['E','G','F','S','I','W','E']);letters.append({'address':f'{table:08x}','letters':values,'pointers':[f'{v:08x}'for v in ptrs]})
        selector=0x6fbb4c if old else 0x7a2774
        for site in [0x40a1a6,0x413794]:assert get(site,site+5)==b'\xa1'+struct.pack('<I',selector)
        names=[];rva=0x13ec2c
        for index in range(24):
            text=p.get_string_at_rva(rva);assert len(text)+1<=128
            names.append({'index':index,'destination':f'{0x7a27b4+128*index:08x}','text':text.decode('ascii')});rva+=len(text)+1
        assert names[7]['text']==('.\\GameData\\Audio\\Speech\\English\\'if old else'.\\GameData\\Audio\\Speech\\')
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'selected_consumer_selector':f'{selector:08x}','letter_tables':letters,'initialized24_path_slots':names,'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    result['limits']=['Selected110 initializer only copies path literals;not whole-program absence of every fallback.',
        '120 caches selector007a2774;final007a2764 and helper register contracts must not be substituted.',
        'Directory false includes missing,nondirectory and API failure;English/files are not rechecked here.',
        'No playback,crash-free outcome,asset provenance,all consumers or lifetime/concurrency proof.',
        'No target/API/instruction execution or binary/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/speech-language-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:110->120 selected speech fallback/cache and two Swedish E->W tables dated;audio behavior unverified')


if __name__=='__main__':main()
