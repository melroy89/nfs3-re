"""Date HUD selector policy simplification, distinct from later asset renaming."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def droplists(raw):
    rows=[];current=None
    for line in raw.decode('latin1').splitlines():
        if line.startswith('['):
            if current is not None:rows.append(current)
            current={}if line=='[droplist]'else None
        elif current is not None and '='in line:
            k,v=line.split('=',1)
            if k in ('codelink','listname','x','y','priority','maxvisitem'):current[k]=v
    if current is not None:rows.append(current)
    return rows


def main():
    result={'kind':'static-hud-selector-history','versions':{}};images={};menus=[]
    op,oh,_=SPECS['original'];raw=(ROOT/op).read_bytes();assert sha(raw)==oh;original=pefile.PE(data=raw)
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a);images[version]=pe
        asset=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/hud.mnu']);rows=droplists(asset);menus.append(rows)
        assert [r['codelink']for r in rows]==(['singlePlayerDefaults','splitScreenDefaults','hotSplitScreenDefaults']if version=='1.3.1'else['singlePlayerDefaults','hotSplitScreenDefaults'])
        if version=='1.3.1':assert get(0x45e960,0x45ea79)==original.get_data(0x5e960,0x119)
        else:
            assert get(0x45e998,0x45e9a1).hex()=='833db0d36f00017421'
            assert get(0x45e9b6,0x45e9c2).hex()=='c705b8886700c2625500eb1f'
            assert get(0x45e9d7,0x45e9e1).hex()=='c705b8886700c8625500'
            for ptr,value in [(0x53a870,b'hotSplitScreenDefaults'),(0x53a844,b'singlePlayerDefaults'),(0x53a85c,b'splitScreenDefaults')]:
                assert pe.get_string_at_rva(ptr-0x400000)==value
            assert bytes.fromhex('b8d36f00')not in get(0x45e998,0x45e9fa)
        spans=[('initializer_prefix',0x45e960,0x45ea79),('callback_flag_consumer',0x44a5cb,0x44a5e5)]
        lists=[{'address':f'{a:08x}','hex':get(a,a+n).hex()}for a,n in [(0x5562c2,6),(0x5562c8,10),(0x5562d2,6)]]
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'hud_menu_sha256':sha(asset),'droplists':rows,
            'lists':lists,'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
             'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    old_rows={r['codelink']:r for r in menus[0]}
    assert all(old_rows[r['codelink']]==r for r in menus[1])
    assert result['versions']['1.3.1']['lists']==result['versions']['1.4.0']['lists']
    assert images['1.3.1'].get_data(0x4a5cb,26)==images['1.4.0'].get_data(0x4a5cb,26)
    result['original_prefix_correspondence']={'path':op,'sha256':oh,'start':'0045e960','end_exclusive':'0045ea79','matches131':True}
    result['policy140']=[{'session_P':'1','suppression_lookup_targets':['singlePlayerDefaults','splitScreenDefaults'],'list_pointer':'005562c8'},
                         {'session_P':'not1','suppression_lookup_targets':['hotSplitScreenDefaults','splitScreenDefaults'],'list_pointer':'005562c2'}]
    result['verified']=['131 initializer prefix matches supplied original,including four-way P/R policy documented in existing HUD report.',
        '140 policy no longer readsR006fd3b8;both P arms write a list pointer and target the opposite retained control plus an absent legacy control for suppression.',
        '140 removes authored splitScreenDefaults control;selected fields of other two controls and all three old list arrays remain identical;later final renaming/zeroing is separate.',
        'Retained callback consumer skips entry+2c callback when entry+5 bit10h set;this is not every display/input path.']
    result['limits']=['Unsuppressed by this block does not mean guaranteed visible:prior flags,lookup success,other callbacks and state lifetime remain unknown.',
        'Complete initializer changes also include shared Credits policy/snapshot repacking;not every byte change is attributed to this release note.',
        'No universal session/race labels,actual menu interaction,target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/hud-selector-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 replaces four-way HUD selector policy with two P arms;legacy control removed,retained fields/lists match,visibility qualified')


if __name__=='__main__':main()
