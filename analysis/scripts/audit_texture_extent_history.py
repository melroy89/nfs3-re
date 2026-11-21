"""Date selected track extent and AllowHugeTextures changes140->150->151."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={**HISTORY,'1.5.1':('c7b66da29ef8cd58c56e27a403bd2889d8a4f0f7cac0873c28a1b4b5a09723de','4f7064a3fefa1a2598c95fbf72f3aee999360e3bf4d2d285f5e4c969ae2c8a17')}
    result={'kind':'static-texture-extent-history','versions':{}}
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel;assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        ini=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.ini']);p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a)
        spans=[('track_caller',0x41db67,0x41db8b),('square_builder_prefix',0x49cea0,{'1.4.0':0x49cece,'1.5.0':0x49cec6,'1.5.1':0x49cec4}[version])]
        literal=b'AllowHugeTextures\0';assert (literal in raw)==(version=='1.5.1')
        if version=='1.5.1':
            assert get(0x41dbb4,0x41dbbf).hex()=='8b1d8c277a00e9c1640b00'
            assert get(0x41db7b,0x41db80).hex()=='bb80000000'
            assert get(0x41db86,0x41db8b).hex()=='e829000000'
            assert p.get_string_at_rva(0x13edc0)==b'AllowHugeTextures'
            assert get(0x4b56c2,0x4b56c9).hex()=='bbc0ed530031d2'
            assert get(0x4b56ce,0x4b56e3).hex()=='31c983f803770288c1b800010000d3e0a38c277a00'
            spans += [('track_wrapper',0x41dbb4,0x41dbbf),('setting_read_and_extent',0x4b56c2,0x4b56e3)]
            assert b'AllowHugeTextures=0'in ini
        else:
            assert get(0x41db7b,0x41db80).hex()==('bb80000000'if version=='1.4.0'else'bb00010000')
            assert get(0x41db86,0x41db8b).hex()=='e8f5640b00'
            assert b'AllowHugeTextures'not in ini
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'ini_sha256':sha(ini),'ascii_setting_literal_present':literal in raw,'ini_setting_lines':[l for l in ini.decode().splitlines()if'AllowHugeTextures'in l],
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    result['verified']=[
        'Selected track branch passes immediate128 in140 and256 in150 to004d4080.',
        '151 restores caller immediate128 but retargets to wrapper0041dbb4,which replacesEBX with007a278c and tail-jumps004d4080;caller immediate is not effective extent.',
        '151 adds checked ASCII key and packaged default0;reader defaultEDX0,mapping0..3->256..2048,unsigned out-of-range->256.',
        '150 square builder retains fixed256 threshold and dimension-pass-through branch;151 uses configured-global halving prefix.']
    result['limits']=[
        'Selected caller/prefix/date evidence only;reuse original/final report for broader producers/reduction,not complete historical function equivalence.',
        'Absent literal does not exclude other/computed configuration or all larger texture routes;150 pass-through branch prevents a universal256 cap claim.',
        'No beta package inspected;MP150-013 beta-only claim is not verified by these release builds.',
        'Driver acceptance,allocation/upload,asset dimensions,visual output and all later writes unverified.',
        'No target/API/instruction execution,compilation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/texture-extent-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140->150 track128->256;151 wrapper overrides stale128 with configured extent;beta/runtime claims unverified')


if __name__=='__main__':main()
