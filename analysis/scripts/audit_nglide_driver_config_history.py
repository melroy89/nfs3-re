"""Compare131/140 nGlide configuration and packaged general-driver bytes; static only."""
import hashlib,json,subprocess,configparser,io
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-nglide-driver-config-history','versions':{}};settings=[]
    for version,(ah,_)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        listing=subprocess.check_output(['7z','l','-slt',str(archive)],text=True)
        paths=[line[7:].replace('\\','/')for line in listing.splitlines()if line.startswith('Path = ')]
        member='drivers/nglide/thrash.ini';raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read_file(io.StringIO(raw.decode()))
        old=version=='1.3.1';assert cfg['THRASH']['File']==('nglide.dll'if old else'voodoo2a.dll')
        assert dict(cfg['THRASH'])=={'File':'nglide.dll'if old else'voodoo2a.dll','Type':'voodoo','FogSupport':'1','LightBeams':'1'}
        section='NGLIDE'if old else'ENV';expected={'Resolution':'0','Aspect':'0','Refresh':'0','Vsync':'1','Gamma':'5','Splash':'0'}
        values=dict(cfg[section]);assert values==(expected if old else{'NGLIDE_'+k.upper():v for k,v in expected.items()})
        settings.append([values[k if old else'NGLIDE_'+k.upper()]for k in expected])
        driver='drivers/nglide/'+cfg['THRASH']['File'];blob=subprocess.check_output(['7z','x','-so',str(archive),driver]);pe=pefile.PE(data=blob)
        assert pe.FILE_HEADER.Machine==0x14c
        siblings=[]
        if not old:
            assert 'drivers/nglide/nglide.dll'not in paths
            for name in ['dgvoodoo','glide3x']:
                path=f'drivers/{name}/voodoo2a.dll';other=subprocess.check_output(['7z','x','-so',str(archive),path]);assert other==blob
                siblings.append({'member':path,'sha256':sha(other),'equal_bytes':True})
        hardware_paths=sorted(p for p in paths if p.startswith('drivers/glide3x/'))
        hardware={'paths':hardware_paths}
        if old:assert not hardware_paths
        else:
            assert hardware_paths==['drivers/glide3x/thrash.ini','drivers/glide3x/voodoo2a.dll']
            hwini=subprocess.check_output(['7z','x','-so',str(archive),'drivers/glide3x/thrash.ini'])
            hwcfg=configparser.ConfigParser();hwcfg.optionxform=str;hwcfg.read_file(io.StringIO(hwini.decode()))
            assert dict(hwcfg['THRASH'])==dict(cfg['THRASH'])
            assert dict(hwcfg['ENV'])=={'FX_GLIDE_NO_SPLASH':'1'}
            hardware.update({'config_sha256':sha(hwini),'config_text':hwini.decode(),'provider_glide3x_dll_packaged_here':False})
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'config':{'member':member,'sha256':sha(raw),'text':raw.decode()},
            'hardware_glide3x_directory':hardware,'driver':{'member':driver,'bytes':len(blob),'sha256':sha(blob),'machine':'014c','matching_siblings':siblings}}
    assert settings[0]==settings[1]
    result['verified']=['131 special nglide.dll path becomes140 voodoo2a.dll;140 bytes equal dgvoodoo/glide3x sibling drivers.',
        'Six NGLIDE key/value pairs move to ENV with NGLIDE_ uppercase prefixes;values and selected THRASH capability keys retained.']
    result['limits']=['Packaged configuration/bytes,not successful installation,selection,provider loading or effective settings.',
        '140 adds separate glide3x directory/config but no glide3x.dll inside it;real Voodoo hardware/provider compatibility not tested.',
        'Whole driver implementations,ABI/source ancestry and every replacement of old special-adapter behavior unverified.',
        'Inherited environment and OS/provider precedence may affect outcomes;no target/API/environment execution or binary/database changes.']
    (ROOT/'analysis/evidence/audits/nglide-driver-config-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:nGlide special-to-general configured driver switch and six ENV key migrations131 to140;three140 driver copies identical')


if __name__=='__main__':main()
