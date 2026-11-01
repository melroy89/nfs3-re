"""Static role-linked HUD preview image coordinate history."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_subtitle_style_history import sections


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior=json.loads((ROOT/'analysis/evidence/audits/reference-asset-pairs.json').read_text())
    asset=next(a for a in prior['assets']if a['normalized_path']=='fedata/menus/hud.mnu')
    archives=dict(prior['archives'])
    for version,(digest,_)in HISTORY.items():archives[version]={'path':f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z','sha256':digest}
    report={'kind':'static-hud-preview-arrangement-history','archives':archives,'snapshots':{},'property_bindings':{}};images={}
    for source,identity in archives.items():
        archive=ROOT/identity['path'];assert sha(archive.read_bytes())==identity['sha256']
        member=asset[source]['member']if source in ('reference','modern')else'fedata/menus/hud.mnu'
        raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        if source in ('reference','modern'):assert sha(raw)==asset[source]['sha256']
        rows=[r for r in sections(raw)if r['section']=='image'and'codelink'in r]
        image_map={r['codelink']:r for r in rows};assert len(rows)==len(image_map)==(36 if source=='reference' else 38)
        images[source]=image_map
        report['snapshots'][source]={'member':member,'sha256':sha(raw),'bytes':len(raw),'linked_images':rows}
    assert images['1.4.0'].keys()==images['1.5.0'].keys()==images['modern'].keys()
    expected={'screen':((300,157),(270,157)), 'oppnImage2':((160,128),(148,145)),
        'drpmImage2':((219,124),(219,125)), 'arpmImage2':((219,124),(210,120)),
        'mrpmImage2':((219,124),(210,120)), 'amphImage2':((65,124),(70,120)),
        'akphImage2':((65,124),(70,120)), 'timeImage2':((2,121),(2,122)),
        'splitImage2':((286,121),(283,122)), 'opplImage2':((10,165),(10,177)),
        'mapImage2':((267,151),(261,165)), 'copRadarImage2':((10,132),(10,146)),
        'oppcImage2':((10,165),(10,174))}
    changed=[]
    for link,old in images['1.4.0'].items():
        new=images['1.5.0'][link];a=tuple(int(old[k])for k in ('x','y'));b=tuple(int(new[k])for k in ('x','y'))
        if a!=b:
            assert expected[link]==(a,b)
            final=images['modern'][link];assert tuple(int(final[k])for k in ('x','y'))==b
            assert old['image']==new['image']==final['image']
            changed.append({'codelink':link,'old_xy':a,'new_xy':b,'delta':[b[i]-a[i]for i in (0,1)],'retained_image_alias':new['image']})
    assert set(c['codelink']for c in changed)==set(expected);report['historical_coordinate_changes']=changed
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest;pe=pefile.PE(data=raw);rows=[]
        for va,name,destination in [(0x557c10,'x',0x604ee6),(0x557c20,'y',0x604ee8)]:
            blob=pe.get_data(va-0x400000,16);w=struct.unpack('<4I',blob)
            assert(w[0],w[2],w[3])==(1,1,destination)
            assert pe.get_string_at_rva(w[1]-0x400000).decode()==name
            rows.append({'address':f'{va:08x}','name':name,'kind':1,'form':1,'destination':f'{destination:08x}','hex':blob.hex()})
        report['property_bindings'][label]={'path':relative,'sha256':digest,'descriptors':rows}
    assert report['property_bindings']['original']['descriptors']==report['property_bindings']['official_modern']['descriptors']
    report['verified']=['Exactly13 linked-image coordinate pairs change140->150,with same38 linked controls and no ID renumbering.',
        'All13 changed pairs are retained in final;their image aliases are unchanged.',
        'Shared x/y property rows bind authored coordinates to form1 destinations entry+6/+8 in both EXEs.',
        'Only authored coordinate changes are classified here;other HUD policy/navigation changes are separate.']
    report['limits']=['No target, menu parser, instruction probes, compilation or Ghidra writes.',
        'Final screen pixels, runtime overwrites, parent transforms, loaded image identity and visual quality remain unverified.',
        'Codelink suffix2 is reported literally;not independently assigned to player2 or a role.',
        'Unchanged image aliases do not prove unchanged asset payloads.',
        'Author-reference assets not authenticated pristine retail or proven paired to supplied original EXE.',
        'MP150-020 has partial package/static support;arranged well is not a quantitative acceptance result.']
    (ROOT/'analysis/evidence/audits/hud-preview-arrangement-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:13 exact preview coordinate changes140->150,retained final;38 linked images and paired x/y bindings')


if __name__=='__main__':main()
