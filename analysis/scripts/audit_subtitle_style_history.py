"""Pin subtitle text replacement against existing Race Results styling."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def sections(raw):
    rows=[];row=None
    for line in raw.decode('latin1').splitlines():
        line=line.strip()
        if line.startswith('[')and line.endswith(']'):
            row={'section':line[1:-1].lower()};rows.append(row)
        elif '='in line and row is not None:
            key,value=line.split('=',1);row[key.strip().lower()]=value.strip()
    return rows


def main():
    prior=json.loads((ROOT/'analysis/evidence/audits/reference-asset-pairs.json').read_text())
    assets={a['normalized_path']:a for a in prior['assets']};archives=dict(prior['archives'])
    for version,(digest,_)in HISTORY.items():archives[version]={'path':f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z','sha256':digest}
    style={'x':'163','y':'113','priority':'4','texttype':'1','color':'2','italic':'0','scale':'0.750000','ypos':'0','align':'0'}
    report={'kind':'static-subtitle-style-history','archives':archives,'shared_style':style,'assets':{},'binaries':{}}
    for source,identity in archives.items():
        archive=ROOT/identity['path'];assert sha(archive.read_bytes())==identity['sha256'];rows=[]
        for name,listname in [('showcase','statsmode'),('compare2','compcat'),('postgame','posttitle')]:
            path=f'fedata/menus/{name}.mnu';member=assets[path][source]['member']if source in ('reference','modern')else path
            raw=subprocess.check_output(['7z','x','-so',str(archive),member])
            if source in ('reference','modern'):assert sha(raw)==assets[path][source]['sha256']
            selected=[r for r in sections(raw)if r.get('listname')==listname]
            texts=[r for r in selected if r['section']=='text']
            if name=='postgame'or source in ('modern','1.5.0'):
                assert len(texts)==1
                assert all(texts[0][k]==v for k,v in style.items())
                assert texts[0]['text']==('kMenuPOSTGAMEracesumm001'if name=='postgame'else'kMenuSHOWCASEStats001')
            else:assert not texts
            if name!='postgame':
                cascades=[r for r in selected if r['section']=='cascade'];assert len(cascades)==1
                assert cascades[0]['notitle']==('1'if source in ('modern','1.5.0')else'0')
            rows.append({'path':path,'member':member,'sha256':sha(raw),'bytes':len(raw),'selected_listname':listname,'controls':selected})
        report['assets'][source]=rows
    fields=[(0x557cc0,3,'texttype',1,0x604f20),(0x557ce0,3,'color',1,0x604f2a),
            (0x557cf0,3,'italic',1,0x604f22),(0x557d00,3,'scale',6,0x604f2c),
            (0x557db0,17,'notitle',1,0x604f24)]
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest;pe=pefile.PE(data=raw);rows=[]
        for va,kind,name,form,destination in fields:
            blob=pe.get_data(va-0x400000,16);w=struct.unpack('<4I',blob)
            assert(w[0],w[2],w[3])==(kind,form,destination)
            assert pe.get_string_at_rva(w[1]-0x400000).decode()==name
            rows.append({'address':f'{va:08x}','name':name,'kind':kind,'form':form,'destination':f'{destination:08x}','entry_offset':destination-0x604ee0,'hex':blob.hex()})
        report['binaries'][label]={'path':relative,'sha256':digest,'field_descriptors':rows}
    assert report['binaries']['original']['field_descriptors']==report['binaries']['official_modern']['field_descriptors']
    report['verified']=['1.4.0->1.5.0 introduces separate list-bound text subtitles and sets old cascades notitle0->1 in both selected menus.',
        'New subtitle styling equals Race Results authored style in nine explicit fields; results style already exists in author-reference/1.4.0.',
        'Text/list binding differs by purpose:statsmode,compcat,posttitle; labels/content are not claimed identical.',
        'Paired EXE field descriptors bind authored texttype/color/italic/scale and cascade notitle to concrete runtime offsets.']
    report['limits']=['No game, font/provider, menu parser or instruction execution; no Ghidra writes.',
        'Author-reference assets not authenticated pristine retail or proven paired to supplied original EXE.',
        'Matching style properties do not independently identify actual font bank/glyphs, localisation, rendered size or all override writes.',
        'notitle property binding is verified; full cascade drawing consumer and complete list/label selection are not qualified here.',
        'Historical boundary is package-level; no new EXE font-selector patch asserted.',
        'MP150-025 has partial package/static support; visual acceptance remains pending.']
    (ROOT/'analysis/evidence/audits/subtitle-style-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:four package snapshots,new text subtitles match nine Race Results style fields;five paired descriptors')


if __name__=='__main__':main()
