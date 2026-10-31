"""Paired HUD initializer and version-specific defaults-list selection."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'hud-settings-initializer-policy-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/hud-settings-policy'
    capture.mkdir(parents=True,exist_ok=True);bodies=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);start,end=0x45e960,0x45f07c
        body=pe.get_data(start-0x400000,end-start);bodies.append(body)
        path=capture/f'{label}.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
            f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
        registration=pe.get_data(0x555ea0-0x400000,24)
        assert struct.unpack('<6I',registration)==(0x537cf8,0,0,0x45e960,0x45f160,0x45f4c0)
        assert pe.get_data(0x537cf8-0x400000,4)==b'hud\0'
        strings={f'{a:08x}':pe.get_data(a-0x400000,32).split(b'\0')[0].decode('ascii')
                 for a in ([0x53a844,0x53a84c,0x53a864,0x53a878] if label=='original' else [0x53a844,0x53a850])}
        result['binaries'][label]={'path':relative,'sha256':expected,
            'start':f'{start:08x}','end_exclusive':f'{end:08x}','span_bytes':len(body),
            'span_sha256':hashlib.sha256(body).hexdigest(),'assembly':str(path.relative_to(ROOT)),
            'hud_registration_hex':registration.hex(),'strings':strings,
            'list_words':{f'{a:08x}':list(struct.unpack('<'+str(n)+'H',pe.get_data(a-0x400000,n*2)))
                          for a,n in [(0x5562c2,3),(0x5562c8,5),(0x5562d2,3)]}}
        if label=='official_modern':
            assert pe.get_data(0x45e9e8-0x400000,0x8c)==b'\x90'*0x8c
            assert pe.get_data(0x45e9e1-0x400000,7)==bytes.fromhex('31d2e991000000')
    old,new=bodies
    changed=[0x45e960+i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    assert len(changed)==242 and all(0x45e980<=a<0x45ea74 for a in changed)
    assert old[:0x20]==new[:0x20] and old[0x114:]==new[0x114:]
    consumer=[]
    for label,(relative,_,_) in SPECS.items():
        pe=pefile.PE(str(ROOT/relative))
        data=pe.get_data(0x44a5cb-0x400000,26);consumer.append(data)
    assert consumer[0]==consumer[1]==bytes.fromhex('837b2c007414f6430510750e9889c289d8ff532c85c0740289c7')
    result['flag_consumer']={'start':'0044a5cb','end_exclusive':'0044a5e5',
        'identical_hex':consumer[0].hex(),'effect':'Entry byte +5 bit 10h skips this +2ch callback dispatch.'}
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    official=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/hud.mnu'])
    result['hud_assets']={}
    for name,relative in [
        ('official_modern','analysis/captures/modern-differences/upstream/package/fedata/menus/hud.mnu'),
        ('uppercase_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/HUD.MNU'),
        ('lowercase_backup','nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/menus/hud.mnu')]:
        data=(ROOT/relative).read_bytes()
        if name=='official_modern':assert data==official
        sections=[];current=None
        for line in data.decode('latin1').splitlines():
            if line.startswith('['):
                current={'type':line.strip('[]'),'fields':{}};sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);current['fields'][key]=value
        selected=[s for s in sections if s['type']=='droplist']
        result['hud_assets'][name]={'path':relative,'sha256':hashlib.sha256(data).hexdigest(),
            'equals_official':data==official,'droplists':selected,
            'provenance':'Archive member verified' if name=='official_modern' else 'Local backup, not authenticated as retail or paired to supplied original executable'}
    assert [s['fields']['codelink'] for s in result['hud_assets']['official_modern']['droplists']]==['forsingle','forsplit']
    assert [s['fields']['codelink'] for s in result['hud_assets']['uppercase_backup']['droplists']]==['singlePlayerDefaults','splitScreenDefaults','hotSplitScreenDefaults']
    assert result['hud_assets']['lowercase_backup']['equals_official']
    pe=pefile.PE(str(ROOT/SPECS['official_modern'][0]))
    result['modern_list_descriptors']={}
    for va,token,table in [(0x5567bc,0x53a85c,0x5562c2),(0x556938,0x53a86c,0x5562c8)]:
        words=struct.unpack('<5I',pe.get_data(va-0x400000,20))
        assert words==(token,table,0,0,0x678900)
        result['modern_list_descriptors'][f'{va:08x}']={'words':[f'{x:08x}' for x in words],
            'name':pe.get_data(token-0x400000,20).split(b'\0')[0].decode('ascii')}
    result['changed_bytes']=len(changed)
    result['limits']=['Initializer code beyond selected policy is byte-identical, not full transitive behavior equivalence.',
        'Numeric session/mode meanings, widget flag consumers, pointer lifetimes and actual menu behavior require linked evidence.',
        'No target execution, Ghidra edits or reconstruction changes.']
    (ROOT/'analysis/evidence/audits/hud-settings-policy.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: complete {len(old)}-byte initializer; 242 changed bytes confined to policy block')


if __name__=='__main__':main()
