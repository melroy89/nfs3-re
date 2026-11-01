"""Verify the two-binary DDRAW static-import removal release boundary."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def inventory(raw):
    pe=pefile.PE(data=raw)
    def table(attribute):
        return [{'dll':d.dll.decode('ascii'),'symbols':[{'name':i.name.decode('ascii')if i.name else None,
                'ordinal':i.ordinal,'iat_va':f'{i.address:08x}'}for i in d.imports]}
                for d in getattr(pe,attribute,[])]
    return {'machine':f'{pe.FILE_HEADER.Machine:04x}','image_base':f'{pe.OPTIONAL_HEADER.ImageBase:08x}',
            'imports':table('DIRECTORY_ENTRY_IMPORT'),'delay_imports':table('DIRECTORY_ENTRY_DELAY_IMPORT'),
            'delay_directory':{'rva':pe.OPTIONAL_HEADER.DATA_DIRECTORY[13].VirtualAddress,
                               'size':pe.OPTIONAL_HEADER.DATA_DIRECTORY[13].Size}}


def main():
    dll_pins={'1.4.0':'67764a56917fd93fffb847968f2cf90cff7c0fd8ab812d99403bfa88ef0208d3',
              '1.5.0':'bea4abc9ff9b3e54ed304d2fd05d6be7005e1933b209e5a3975da4f897b67fab'}
    report={'kind':'static-ddraw-import-removal-history','history':{},'supplied_exe_baselines':{}}
    for version,(archive_hash,exe_hash)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==archive_hash;rows=[]
        for member,digest in [('nfs3.exe',exe_hash),('drivers/glide3x/voodoo2a.dll',dll_pins[version])]:
            raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==digest
            inv=inventory(raw);ddraw=[d for d in inv['imports']if d['dll'].casefold()=='ddraw.dll']
            if version=='1.4.0':assert len(ddraw)==1 and [s['name']for s in ddraw[0]['symbols']]==['DirectDrawCreate']
            else:assert not ddraw
            assert inv['delay_directory']=={'rva':0,'size':0}and not inv['delay_imports']
            rows.append({'member':member,'sha256':digest,'bytes':len(raw),**inv})
        report['history'][version]={'archive':rel,'archive_sha256':archive_hash,'members':rows}
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest;inv=inventory(raw)
        dd=[d for d in inv['imports']if d['dll'].casefold()=='ddraw.dll']
        assert bool(dd)==(label=='original')
        report['supplied_exe_baselines'][label]={'path':relative,'sha256':digest,**inv}
    archive_rel='analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    archive=ROOT/archive_rel;archive_hash='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    assert sha(archive.read_bytes())==archive_hash
    member='drivers/glide3x/voodoo2a.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member])
    digest='f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b';assert sha(raw)==digest
    inv=inventory(raw);assert not[d for d in inv['imports']+inv['delay_imports']if d['dll'].casefold()=='ddraw.dll']
    report['final_glide']={'archive':archive_rel,'archive_sha256':archive_hash,'member':member,'sha256':digest,**inv}
    report['verified']=['Both named1.4.0 binaries statically import DDRAW.dll!DirectDrawCreate; both named1.5.0 binaries omit that descriptor.',
        'Neither historical member has a nonzero delay-import directory; no migration into PE delay imports in this pair.',
        'Supplied original EXE imports DDRAW;official final EXE and selected final Glide driver omit that static import.',
        'MP150-045 is bounded-static supported for named package members and exact release boundary.']
    report['limits']=['Static parsed PE tables only; no OS loader, DLL/API, target instructions or Ghidra changes.',
        'Import removal does not establish absence of conditional dynamic loading, DirectDraw use or transitive dependencies.',
        'Selected drivers/glide3x/voodoo2a.dll is not every driver variant or an authenticated retail driver baseline.',
        'Existing dynamic lookup investigation remains the authority for selected resolver behaviour and lifetime limits.',
        'Author-hosted release labels/hashes identify inspected artifacts, not publisher signatures or full development history.']
    (ROOT/'analysis/evidence/audits/ddraw-import-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:both historical binaries remove DDRAW static imports140->150;final snapshots corroborate')


if __name__=='__main__':main()
