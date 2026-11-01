"""Static installer records, early INI RemoteOnly and final zero gate."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    ah='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac';assert sha(archive.read_bytes())==ah
    early=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    eh='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72';assert sha(early)==eh
    inputs={key:((ROOT/rel).read_bytes(),digest,rel)for key,(rel,digest,_)in SPECS.items()}
    inputs['1.1.0']=(early,eh,str(archive.relative_to(ROOT))+'!nfs3.exe')
    result={'kind':'static-install-settings-history','early_archive_sha256':ah,'binaries':{}}
    for label,(raw,digest,path)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        if label=='original':
            assert pe.get_string_at_rva(0x13dc40)==b'install.win'
            spans=[(0x4a6e10,0x4a6f61),(0x472b38,0x472b48)]
        elif label=='1.1.0':
            assert b'install.win' not in raw and raw.lower().count(b'install.win')==1
            assert b'RENDITION not yet supported (INSTALL.WIN)\0' in raw
            for address,value in [(0x53ee28,b'NFS3'),(0x53ee30,b'Language'),(0x53ee7c,b'RemoteOnly'),(0x53eaf0,b'english')]:
                assert pe.get_string_at_rva(address-0x400000)==value
            assert get(0x4b62a0,0x4b62c1).hex()=='555352bd28ee5300bb7cee530031d2e83c54040085c07405b8010000005a5b5dc3'
            assert get(0x472b38,0x472b3d).hex()=='e863370400'
            assert get(0x472b43,0x472b48).hex()=='a354bb6f00'
            imports={e.address:e.name.decode()for dll in pe.DIRECTORY_ENTRY_IMPORT for e in dll.imports if e.name}
            assert imports[0x534674]=='GetPrivateProfileIntA' and imports[0x534678]=='GetPrivateProfileStringA'
            spans=[(0x4b62a0,0x4b62c1),(0x4fb6f0,0x4fb703),(0x4fb704,0x4fb719),
                   (0x4a6eb0,0x4a6f0a),(0x472b38,0x472b48)]
        else:
            assert b'install.win' not in raw.lower() and b'remoteonly' not in raw.lower()
            assert get(0x472b1d,0x472b2b).hex()=='31c9890d0cd56f00890d54bb6f00'
            assert get(0x4b62a0,0x4b62c1)==b'\x90'*33
            spans=[(0x4a6e68,0x4a6ec1),(0x472b1d,0x472b2b),(0x4b62a0,0x4b62c1)]
        result['binaries'][label]={'path':path,'sha256':digest,
            'case_insensitive_ascii_literal_counts':{key:raw.lower().count(key.encode())for key in ['install.win','remoteonly']},
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    result['verified']=['Original processed install.win records feed language and remote-prefix source buffers; prior producer/consumer audits provide full linkage.',
        'Early1.1.0 reads NFS3/RemoteOnly with integer default0; zero returns0, any nonzero returns1; config tail publishes EAX to006fbb54.',
        'Early1.1.0 reads NFS3/Language through the string-profile API with english default and capacity8; both wrappers use filename buffer007a263c.',
        'Final config tail explicitly stores0 to006fbb54; early RemoteOnly helper span is NOPs and key literal absent.',
        'Literal absence is a bounded ASCII search, not proof about computed names or every external file access.']
    result['limits']=['No installer file, INI, API, game or extracted instruction execution.',
        'Original source-file validity/read failures, early actual filename-buffer initialization and every later field writer not revalidated here.',
        'RemoteOnly is a setting name; external media/audio effects, multiplayer meanings and successful startup remain unverified.',
        '1.0.0 introduction and exact later removal release remain unestablished.',
        'No whole-program file-access exclusion follows from changed local readers or missing strings.']
    (ROOT/'analysis/evidence/audits/install-settings-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:original install records,early INI RemoteOnly/Language API bindings and final literal-zero gate')


if __name__=='__main__':main()
