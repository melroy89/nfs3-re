"""Pin selected local legacy-style DLL candidates; no provenance/behavior inference."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT

GAME='nfs3_decomp.rep/Electronic Arts/Need For Speed III/'
LOCAL=[('legacy_voodoo',GAME+'VOODOO2A.DLL','f65f00e6fa6a5a67e11ff38d661b3d493474d0e075c9183a7b244b1143cea88e'),
       ('legacy_d3d',GAME+'D3DA.DLL','ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02'),
       ('setup_d3d',GAME+'3dSetup/D3DA.DLL','988cae4d164aa7872f433a1afca10791a76162d2a2272feda623fc92ddb02bb3')]


def inspect(raw):
    pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
    exports={e.name.decode() if e.name else '#'+str(e.ordinal):
             {'ordinal':e.ordinal,'va':f'{base+e.address:08x}'}
             for e in pe.DIRECTORY_ENTRY_EXPORT.symbols}
    imports={d.dll.decode():[i.name.decode() if i.name else '#'+str(i.ordinal) for i in d.imports]
             for d in pe.DIRECTORY_ENTRY_IMPORT}
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'image_base':f'{base:08x}','exports':exports,'imports':imports}


def symbols(row):
    return {dll.lower()+'!'+name for dll,names in row['imports'].items() for name in names}


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    expected='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
    out={'kind':'selected-local-dll-counterpart-candidates','archive_sha256':expected,'files':{}}
    for label,relative,wanted in LOCAL:
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==wanted
        out['files'][label]={'path':relative,**inspect(raw),
            'provenance':'Local legacy-style candidate; not authenticated as retail or paired to supplied original executable.'}
    for label,member in [('modern_voodoo','drivers/glide3x/voodoo2a.dll'),('modern_dx5','drivers/dx5/dx5a.dll'),('packaged_sound','eacsnd.dll')]:
        raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        installed=ROOT/GAME/member;assert installed.read_bytes()==raw
        out['files'][label]={'path':str(installed.relative_to(ROOT)),'archive_member':member,
            **inspect(raw),'provenance':'Byte-identical to member in pinned official archive.'}
    pairs=[]
    for a,b in [('legacy_voodoo','modern_voodoo'),('legacy_d3d','modern_dx5'),('setup_d3d','modern_dx5')]:
        old,new=[out['files'][k] for k in (a,b)]
        assert len(old['exports'])==len(new['exports'])==34 and set(old['exports'])==set(new['exports'])
        pairs.append({'candidate':a,'modern':b,'same_export_names':True,'export_name_count':34,
            'old_only_static_imports':sorted(symbols(old)-symbols(new)),
            'modern_only_static_imports':sorted(symbols(new)-symbols(old)),
            'limit':'Shared export surface and role candidate only; no matched function, API-version, data-layout or rendering equivalence claim.'})
    out['candidate_pairs']=pairs
    out['sound_local_match']={'path':GAME+'eacsnd.dll','archive_member':'eacsnd.dll',
        'sha256':out['files']['packaged_sound']['sha256'],
        'conclusion':'This local sound DLL is not a distinct older comparison baseline.'}
    out['limits']=['Selected file identities/interfaces only; other original installation media/backups not searched.',
        'Static imports omit dynamic resolution and do not prove executed dependency use.',
        'Local legacy-style files lack independent original-retail or executable-pair provenance.',
        'No DLL loading, game/probe execution, executable or Ghidra edits.']
    (ROOT/'analysis/evidence/audits/legacy-dll-candidates.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: three distinct local candidate hashes, matching34-name export surfaces, official member identities and local sound match')


if __name__=='__main__':main()
