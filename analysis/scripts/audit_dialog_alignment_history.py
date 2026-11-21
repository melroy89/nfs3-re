"""Compare selected named dialog controls across131/140 without rendering."""
import hashlib,json,subprocess
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
SPECS=[
 ('hardkeys','[text]','text','kMenuHARDKEYSEscape001',{'x':('42','35'),'y':('138','173')}),
 ('hardkeys','[text]','text','kMenuHARDKEYSTab001',{'x':('35','32'),'y':('173','208')}),
 ('hardkeys','[text]','text','kMenuHARDKEYSKeypadPl001',{'x':('32','31'),'y':('208','243')}),
 ('hardkeys','[text]','text','kMenuHARDKEYSKeypadMi001',{'x':('31','34'),'y':('243','278')}),
 ('interior','[InteriorBx]',None,None,{'y':('187','147')}),
 ('interior','[slider]','codelink','ZoomSlider',{'x':('227','222'),'y':('400','360')}),
 ('ipx','[selectlist]','codelink','gamelist',{'x':('230','250'),'y':('180','158')}),
 ('loadsave','[Rect]','codelink','DESCRIPTION_BOX',{'x':('400','395'),'y':('176','205')}),
 ('loadsave','[selectlist]','codelink','replays',{'x':('185','183'),'y':('176','158'),'maxvis':('8','10')}),
]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def parse(raw):
    rows=[];current=None
    for line in raw.decode('latin1').splitlines():
        if line.startswith('['):
            if current is not None:rows.append(current)
            current={'section':line,'fields':{}}
        elif current is not None and '='in line:
            k,v=line.split('=',1);assert k not in current['fields'];current['fields'][k]=v
    if current is not None:rows.append(current)
    return rows


def main():
    result={'kind':'static-dialog-alignment-history','versions':{},'selected_changes':[]};all_rows={}
    for version,(ah,_)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        members={};all_rows[version]={}
        for name in ('hardkeys','interior','ipx','loadsave'):
            member=f'fedata/menus/{name}.mnu';raw=subprocess.check_output(['7z','x','-so',str(archive),member]);rows=parse(raw)
            all_rows[version][name]=rows
            members[name]={'member':member,'sha256':sha(raw),'bytes':len(raw),'section_count':len(rows)}
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'members':members}
    for name,section,key,value,expected in SPECS:
        found=[]
        for index,version in enumerate(PINS):
            matches=[r for r in all_rows[version][name]if r['section']==section and(key is None or r['fields'].get(key)==value)]
            assert len(matches)==1,(name,section,key,value)
            row=matches[0]['fields'];assert all(row[k]==pair[index]for k,pair in expected.items());found.append(row)
        result['selected_changes'].append({'menu':name,'section':section,'match_key':key,'match_value':value,
            'changes':{k:{'131':a,'140':b}for k,(a,b)in expected.items()},
            'selected_geometry':[{k:r[k]for k in ('x','y','width','height','maxvis','text','codelink')if k in r}for r in found]})
    result['verified']=['Nine explicitly matched controls in four retained menu assets change authored coordinates/row count as recorded.',
        'Interior view and zoom control move upward40;IPX list moves+20/-22;Load list moves-2/-18 andmaxvis8->10.',
        'Hardkeys label identities are matched by exact symbolic text,not section ordinal across inserted/removed controls.']
    result['limits']=['Selected controls only,not a complete diff of every field or other added/removed button.',
        'Authored coordinates/maxvis do not prove final pixel placement,loaded resources,translation metrics or universal visual alignment.',
        'No implied new control functionality or complete input/renderer equivalence.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/dialog-alignment-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 nine matched controls across four dialogs have pinned authored layout changes')


if __name__=='__main__':main()
