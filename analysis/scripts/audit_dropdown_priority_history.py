"""Static authored dropdown priority boundary and retained draw-loop consumer."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def controls(raw):
    rows=[];row=None
    for line in raw.decode('latin1').splitlines():
        line=line.strip()
        if line.startswith('[')and line.endswith(']'):
            row={'section':line[1:-1].lower()};rows.append(row)
        elif '='in line and row is not None:
            k,v=line.split('=',1);row[k.strip().lower()]=v.strip()
    return [r for r in rows if r['section']in ('droplist','cascade')]


def main():
    prior=json.loads((ROOT/'analysis/evidence/audits/reference-asset-pairs.json').read_text())
    assets={a['normalized_path']:a for a in prior['assets']};archives=dict(prior['archives'])
    for version,(digest,_)in HISTORY.items():archives[version]={'path':f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z','sha256':digest}
    result={'kind':'static-dropdown-priority-history','archives':archives,'assets':{},'binaries':{}};rows={}
    for source,identity in archives.items():
        archive=ROOT/identity['path'];assert sha(archive.read_bytes())==identity['sha256'];rows[source]={};captures=[]
        for name in ('location','opponent'):
            path=f'fedata/menus/{name}.mnu';member=assets[path][source]['member']if source in ('reference','modern')else path
            raw=subprocess.check_output(['7z','x','-so',str(archive),member]);selected=controls(raw)
            if source in ('reference','modern'):assert sha(raw)==assets[path][source]['sha256']
            rows[source][name]={r['listname']:r for r in selected}
            assert len(rows[source][name])==len(selected)
            captures.append({'path':path,'member':member,'sha256':sha(raw),'bytes':len(raw),'controls':selected})
        result['assets'][source]=captures
    for old in ('reference','1.4.0'):
        assert rows[old]['location']['tracks']['priority']=='1'
        assert rows[old]['opponent']['opcars']['priority']=='1'
        assert [rows[old]['location'][k]['priority']for k in ('laps','direction','mirrored','night','weather')]==list('01234')
    for new in ('modern','1.5.0'):
        assert rows[new]['location']['tracks']['priority']=='0'
        assert rows[new]['opponent']['opcars']['priority']=='0'
        assert [rows[new]['location'][k]['priority']for k in ('laps','direction','mirrored','night','weather')]==list('12345')
    for source in rows:
        for menu,top in [('location','tracks'),('opponent','opcars')]:
            r=rows[source][menu][top];assert(r['x'],r['y'],r['maxvisitem'])==('101','69','15'if menu=='location'else'10')
        assert [rows[source]['opponent'][k]['priority']for k in ('ai','oppnumber','traffic')]==list('123')
    captures={}
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest;pe=pefile.PE(data=raw)
        descriptor=pe.get_data(0x157c30,16);words=struct.unpack('<4I',descriptor)
        assert words[0]==1 and words[2:]==(1,0x604eea)
        assert pe.get_string_at_rva(words[1]-0x400000)==b'priority'
        spans=[(0x44a524,0x44a536),(0x44a59c,0x44a5a6),(0x44a5cb,0x44a5e5),(0x44a634,0x44a63a)]
        captures[label]=[pe.get_data(a-0x400000,b-a)for a,b in spans]
        result['binaries'][label]={'path':relative,'sha256':digest,'priority_descriptor':{'address':'00557c30','hex':descriptor.hex(),'form':1,'destination':'00604eea'},
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':data.hex(),'sha256':sha(data),'disassembly':disassemble(data,a)}for(a,b),data in zip(spans,captures[label])]}
    assert captures['original']==captures['official_modern']
    result['verified']=['Selected top dropdown priority changes1->0 across1.4.0->1.5.0, retained final.',
        'Location lower priorities shift0..4->1..5; opponent lower priorities remain1..3.',
        'Shared priority descriptor uses form1/two-byte entry+0a store; named writer contract reuses control-component audit.',
        'Retained draw loop finds max signed priority, selects matching group, calls eligible+2c callbacks and decrements group.',
        'Priority0 is processed after positive groups; selected top x/y/maxvisitem remain unchanged.']
    result['limits']=['No menus, target instructions, rendering, compilation or Ghidra writes.',
        'Author-reference assets are not authenticated pristine retail or independently paired to supplied original EXE.',
        'Callback eligibility, rendering state/depth and provider behaviour limit visual inference; no universal overlap-fix claim.',
        'Other fields also differ, including opponent ypos; priority and keyboard-navigation metadata are distinct.',
        'Historical EXE consumer spans not separately compared; historical boundary applies to pinned authored assets.',
        'Selection-state preparation0044a5a6..0044a5cb differs and is deliberately excluded from retained group-test/callback spans; full loop equivalence is not claimed.',
        'MP150-024 has partial static/package support; runtime acceptance remains pending.']
    (ROOT/'analysis/evidence/audits/dropdown-priority-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:four package snapshots,exact dropdown priority boundary and paired retained draw-group consumers')


if __name__=='__main__':main()
