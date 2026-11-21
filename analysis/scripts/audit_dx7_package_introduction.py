"""Verify DX7 package introduction without loading the provider."""
import configparser,hashlib,io,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dx7-package-introduction','versions':{}}
    for version,(ah,_)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        listing=subprocess.check_output(['7z','l','-slt',str(archive)],text=True)
        paths=[line[7:].replace('\\','/')for line in listing.splitlines()if line.startswith('Path = ')]
        selected=sorted(p for p in paths if p.lower().startswith('drivers/dx7/'))
        row={'archive':rel,'archive_sha256':ah,'dx7_members':selected}
        if version=='1.4.0':assert selected==[]
        else:
            assert selected==['drivers/dx7/dx7a.dll','drivers/dx7/thrash.ini']
            members={p:subprocess.check_output(['7z','x','-so',str(archive),p])for p in selected}
            row['members']=[{'member':p,'bytes':len(raw),'sha256':sha(raw)}for p,raw in members.items()]
            cp=configparser.ConfigParser();cp.read_file(io.StringIO(members['drivers/dx7/thrash.ini'].decode('utf-8-sig')))
            row['thrash_options']=dict(cp['THRASH'])
            assert row['thrash_options']=={'file':'dx7a.dll','type':'d3d','fogsupport':'0','directdrawlagfix':'1'}
            raw=members['drivers/dx7/dx7a.dll'];pe=pefile.PE(data=raw)
            row['pe']={'machine':hex(pe.FILE_HEADER.Machine),'image_base':hex(pe.OPTIONAL_HEADER.ImageBase),
                'exports':[{'name':e.name.decode()if e.name else None,'ordinal':e.ordinal,'rva':f'{e.address:08x}'}for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]}
            assert pe.FILE_HEADER.Machine==0x14c
            assert any(e.name==b'_THRASH_setstate@8'for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        result['versions'][version]=row
    result['verified']=['No drivers/dx7 members in retained140 archive;150 adds dx7a.dll plus thrash.ini.',
        '150 INI selects the bundled DLL with typed3d,FogSupport0,DirectDrawLagFix1;PE is i386 with THRASH exports.']
    result['limits']=['Package contents only;no installed DLL selection,successful loading,device acceptance or rendered output.',
        'No proof of Motor City Online source lineage or disabled dithering from inclusion/config alone.',
        'Absence is scoped to drivers/dx7 archive paths,not every possible renamed binary or earlier external distribution.',
        'No DLL/API/target instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/dx7-package-introduction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140->150 adds configured i386 DX7 provider package;source lineage/runtime unverified')


if __name__=='__main__':main()
