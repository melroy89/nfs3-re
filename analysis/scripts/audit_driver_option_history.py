"""Static early filename/@device parser and adjacent driver-key rename."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    specs={
      '1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'),
      '1.3.1':('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664'),
      '1.4.0':('8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9','7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d')}
    result={'kind':'static-driver-option-history','versions':{}}
    for version,(ah,eh)in specs.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/relative
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        if version=='1.4.0':start,end,key_operand,default_operand=0x4b5a23,0x4b5a50,0x4b5a33,0x4b5a38
        else:start,end,key_operand,default_operand=0x4b5748,0x4b5775,0x4b5758,0x4b575d
        keyptr=struct.unpack('<I',get(key_operand,key_operand+4))[0]
        defaultptr=struct.unpack('<I',get(default_operand,default_operand+4))[0]
        key=pe.get_string_at_rva(keyptr-0x400000).decode();default=pe.get_string_at_rva(defaultptr-0x400000).decode()
        assert key==('ThrashDriver'if version=='1.4.0'else'VideoDriver')
        spans=[(start,end)]
        if version=='1.1.0':
            assert default=='dx5'
            spans.extend([(0x4b57d4,0x4b586b),(0x4fb704,0x4fb719),(0x4b5775,0x4b579f)])
            assert get(0x4b57dd,0x4b57e2).hex()=='bf743a7a00'
            assert get(0x4b581a,0x4b5828).hex()=='b82e646c6c3947fc7401ab31c0aa'
            assert get(0x4b5847,0x4b586a).hex()=='807eff40751d803e307218803e39771368bcfd5500688cd6530056e8e1ac030083c40c'
            assert pe.get_string_at_rva(0x13d68c)==b'%d'
            imports={e.address:e.name for d in pe.DIRECTORY_ENTRY_IMPORT for e in d.imports if e.name}
            assert imports[0x53458c]==b'LoadLibraryA'
            assert imports[0x534678]==b'GetPrivateProfileStringA'
        result['versions'][version]={'archive':relative,'archive_sha256':ah,'sha256':eh,
            'key':key,'key_pointer':f'{keyptr:08x}','default':default,
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    result['early_contract']={'source':'ESI byte-string; empty returns without local state updates',
        'path_destination':'007a3a74; prepend .\\ unless source starts .\\ or ./; normalize slash during copy',
        'suffix':'Append .dll if last four copied bytes differ; @ terminates copied filename',
        'device':'If consumed delimiter was@ and next byte is0..9, scan%d into0055fdbc; otherwise no local device write',
        'classification':'Basename first byte d/v/s/other writes6/4/1/0 to007a3a54',
        'loader':'LoadLibraryA receives parsed007a3a74 path at004b5775..004b5780'}
    result['limits']=['No parser, game, DLL, INI or extracted instruction execution; normal filename assumptions only.',
        'No1.0.0 predecessor or predefined alias implementation; early presence does not independently prove all1.1.0 introduction claims.',
        'Read-helper success, input normalizer, scanf overflow/failure, long/short strings and provider/device acceptance not fully qualified.',
        'No key-alias retry in captured branch; no whole-program alias absence claim.',
        'Final uses different driver-directory/type/fog/device storage contracts; do not transfer early field meanings by address.']
    (ROOT/'analysis/evidence/audits/driver-option-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:early filename/@device parser,live INI key131->140 rename and three pinned setting branches')


if __name__=='__main__':main()
