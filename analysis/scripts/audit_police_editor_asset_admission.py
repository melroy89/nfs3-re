"""Bind role-specific HUD editor omissions to named slots and registered code."""
import hashlib,json,re,struct,subprocess
from collections import Counter
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def items(raw):
    result=[];section=None;current={}
    for line in raw.decode('latin1').splitlines()+['[END]']:
        line=line.strip()
        if line.startswith('[')and line.endswith(']'):
            if section=='huditem':
                assert 'item'in current;result.append(int(current['item']))
            section=line[1:-1].lower();current={}
        elif '='in line:
            key,value=line.split('=',1);current[key.strip().lower()]=value.strip()
    return result


def main():
    prior_path=ROOT/'analysis/evidence/audits/reference-asset-pairs.json'
    prior=json.loads(prior_path.read_text());assets={a['normalized_path']:a for a in prior['assets']}
    archive_pins={'reference':'374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127',
                  'modern':'c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'}
    for key,digest in archive_pins.items():assert sha((ROOT/prior['archives'][key]['path']).read_bytes())==digest
    expected={'ps1pcop':[6,7],'ps1prace':[],'ps2p1c2r':[6,7],
              'ps2p1r2c':[29,30],'ps2p2c':[6,7,29,30],'ps2p2r':[]}
    report={'kind':'static-police-editor-authored-admission','inventory_sha256':sha(prior_path.read_bytes()),
            'archives':prior['archives'],'menus':[],'binaries':{}}
    for name,removed in expected.items():
        path=f'fedata/menus/{name}.mnu';row={'path':path};ids={}
        for source in ('reference','modern'):
            entry=assets[path][source];raw=subprocess.check_output(['7z','x','-so',str(ROOT/prior['archives'][source]['path']),entry['member']])
            assert sha(raw)==entry['sha256'];ids[source]=items(raw)
            assert len(ids[source])==len(set(ids[source]))
            row[source]={'member':entry['member'],'sha256':sha(raw),'bytes':len(raw),'HudItem_ids':ids[source]}
        assert sorted((Counter(ids['reference'])-Counter(ids['modern'])).elements())==removed
        assert not(Counter(ids['modern'])-Counter(ids['reference']))
        row['removed_HudItem_ids']=removed;row['added_HudItem_ids']=[];report['menus'].append(row)
    early_rel='analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    early_archive=ROOT/early_rel
    early_hash='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac'
    assert sha(early_archive.read_bytes())==early_hash
    early_rows=[]
    for menu in report['menus']:
        member=menu['path'];raw=subprocess.check_output(['7z','x','-so',str(early_archive),member])
        ids=items(raw);assert ids==menu['modern']['HudItem_ids']
        early_rows.append({'member':member,'sha256':sha(raw),'bytes':len(raw),'HudItem_ids':ids,
                           'byte_identical_final':sha(raw)==menu['modern']['sha256']})
    report['early_history']={'version':'1.1.0','archive':early_rel,'archive_sha256':early_hash,
        'menus':early_rows,'conclusion':'All six early authored item-ID sequences already match final; no1.0.0 artifact checked.'}
    for label,(relative,digest,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest;pe=pefile.PE(data=raw);rows=[]
        for i,name in enumerate(['ps1prace','ps1pcop','ps2p2r','ps2p2c','ps2p1c2r','ps2p1r2c']):
            va=0x555df8+i*24;body=pe.get_data(va-0x400000,24);words=struct.unpack('<6I',body)
            assert pe.get_string_at_rva(words[0]-0x400000).decode()==name
            assert words[1:]==(0,0,0x44de80,0x44dfd0,0)
            rows.append({'address':f'{va:08x}','name':name,'hex':body.hex()})
        body=pe.get_data(0x4de80,0x14b)
        report['binaries'][label]={'path':relative,'sha256':digest,'registered_pages':rows,
            'shared_initializer':{'start':'0044de80','end_exclusive':'0044dfcb','bytes':len(body),'sha256':sha(body),'hex':body.hex()}}
    assert report['binaries']['original']['registered_pages']==report['binaries']['official_modern']['registered_pages']
    assert report['binaries']['original']['shared_initializer']==report['binaries']['official_modern']['shared_initializer']
    report['verified']=['Modern authored menus remove precisely slot6/7 for police views, including29/30=view1 slots6/7.',
        'Racer single/split menus retain those item IDs; mixed-role menus retain the racer view items.',
        'All six same-name page callback registrations and shared331-byte initializer are retained original/final.',
        'Named slot association and item-to-view dispatch reuse the linked rectangle/draw audits; unchanged draw cases need not be deleted to omit authored items.']
    report['limits']=['Static archive records and selected EXE linkage only; active installation, file loading and visible editor behaviour not executed.',
        'Author-hosted reference assets are not authenticated pristine retail or proven paired to supplied original EXE.',
        'Same authored item-ID policy is verified by1.1.0; exact1.0.0 introduction and generic parser/input routes remain unverified.',
        'Other menu property/layout differences are not classified as this widget omission.',
        'MP100-048 has partial package/static support; no new executable police-role gate is asserted.']
    (ROOT/'analysis/evidence/audits/police-editor-asset-admission.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: six paired menus plus1.1.0 item-ID history, exact police-only removals and retained EXE bindings')


if __name__=='__main__':main()
