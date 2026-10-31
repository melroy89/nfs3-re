"""Authored visible-count comparison; uppercase backups have uncertain provenance."""
import hashlib
import json
import subprocess
from audit_thrash_loader_difference import ROOT
from audit_controller_reset_asset import sections


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    listing=subprocess.check_output(['7z','l','-slt',str(archive)]).decode().splitlines()
    members=[l[7:] for l in listing if l.startswith('Path = fedata/menus/') and l.lower().endswith('.mnu')];assert len(members)==52
    result={'kind':'authored-menu-visible-count-comparison','members':[],'changed':[],'unpaired':[],'backup_only':[]}
    for member in members:
        modern=subprocess.check_output(['7z','x','-so',str(archive),member])
        backup=ROOT/'nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus'/member.split('/')[-1].upper()
        assert backup.is_file();old=backup.read_bytes()
        result['members'].append({'member':member,'modern_sha256':hashlib.sha256(modern).hexdigest(),'backup':str(backup.relative_to(ROOT)),'backup_sha256':hashlib.sha256(old).hexdigest()})
        def index(data):
            rows={}
            for section in sections(data):
                f=section['fields']
                if 'maxvisitem' in f:
                    key=(section['section'],f.get('listname',''))
                    rows.setdefault(key,[]).append(f['maxvisitem'])
            return rows
        a,b=index(old),index(modern)
        for key,values in a.items():
            if key not in b:result['backup_only'].append({'member':member,'section':key[0],'listname':key[1],'backup':values})
        for key,values in b.items():
            if len(values)!=1 or len(a.get(key,[]))!=1:
                result['unpaired'].append({'member':member,'section':key[0],'listname':key[1],'modern':values,'backup':a.get(key,[])});continue
            if a[key]!=values:result['changed'].append({'member':member,'section':key[0],'listname':key[1],'backup':a[key][0],'modern':values[0]})
    result['limits']=['Authored values only; runtime widget counts not measured.','Backup provenance unauthenticated; missing/ambiguous pairs reported.']
    (ROOT/'analysis/evidence/audits/menu-visible-counts.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'menus':len(members),'changed':result['changed'],'unpaired_count':len(result['unpaired']),'backup_only':result['backup_only']},indent=2))


if __name__=='__main__':main()
