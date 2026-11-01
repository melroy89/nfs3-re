"""Static split of fog formula selection from ordinary enable state in152."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior_path=ROOT/'analysis/evidence/audits/dx7-fog-optin-history.json';prior=json.loads(prior_path.read_text())
    inputs={}
    for version,row in prior['versions'].items():
        archive=ROOT/row['archive'];assert sha(archive.read_bytes())==row['archive_sha256']
        digest=next(m['sha256']for m in row['members']if m['member']=='nfs3.exe')
        inputs[version]=(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']),digest,{'archive':row['archive'],'archive_sha256':row['archive_sha256']})
    path,digest,_=SPECS['official_modern'];inputs['final']=((ROOT/path).read_bytes(),digest,{'path':path})
    report={'kind':'static-fog-mode-enable-history','prior_evidence_sha256':sha(prior_path.read_bytes()),'binaries':{}};bodies={}
    for label,(raw,digest,identity)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        spans=[('gate',0x431c20,0x431c40)]if label=='1.5.1'else[('gate',0x431c1c,0x431c33),('mode_setup',0x431c34,0x431c4d)]
        spans += [('setup_callsite',0x4c4e40,0x4c4e75),('scene_restore',0x431b40,0x431bb4),('state_dispatch',0x431900,0x431a99)]
        bodies[label]={n:get(a,b)for n,a,b in spans}
        if label=='1.5.1':assert get(0x4c4e64,0x4c4e6b).hex()=='eb0f9090909090'
        else:
            assert get(0x4c4e64,0x4c4e6b).hex()=='e8cbcdf6ffeb0a'
            assert get(0x431c34,0x431c4d).hex()=='833d543a7a0000740fb815000000ba04000000e8b4fcffffc3'
        assert get(0x431b89,0x431b99).hex()=='b8150000008b15643a7a00e867fdffff'
        report['binaries'][label]={**identity,'sha256':digest,'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
            'hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    for n in ('gate','mode_setup','setup_callsite'):assert bodies['1.5.2'][n]==bodies['final'][n]
    for n in ('scene_restore','state_dispatch'):assert bodies['1.5.1'][n]==bodies['1.5.2'][n]==bodies['final'][n]
    old=bodies['1.5.1']['gate'];new=bodies['1.5.2']['gate']
    assert old[:17]==new[:17]
    assert old[17:].hex()=='85c07405b804000000a3643a7a00c3'
    assert new[17:].hex()=='a3643a7a00c3'
    # Whole driver identity is established by prior audit; retain selected raw provider branches here.
    source=prior['versions']['1.5.2'];archive=ROOT/source['archive']
    raw=subprocess.check_output(['7z','x','-so',str(archive),'drivers/dx7/dx7a.dll'])
    assert sha(raw)=='8f3ed9676611d65f40b5dde537aab5813d2e2a854c08fdf3b08b7d19a7a25d5e'
    pe=pefile.PE(data=raw);index=pe.get_data(0x6aec+0x15,1)[0]
    target=struct.unpack('<I',pe.get_data(0x6a34+4*index,4))[0];assert(index,target)==(19,0x60004c44)
    assert any(e.name==b'_THRASH_setstate@8'and e.address==0x3ca0 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
    spans=[('dispatch',0x60003ca0,0x60003d64),('value4_route',0x60004c44,0x60004ca9),('values0_1_routes',0x60004d81,0x60004df4)]
    report['dx7_provider']={'member':'drivers/dx7/dx7a.dll','sha256':sha(raw),'state15_table_index':index,'state15_target':f'{target:08x}',
        'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':pe.get_data(a-0x60000000,b-a).hex(),
         'sha256':sha(pe.get_data(a-0x60000000,b-a)),'disassembly':disassemble(pe.get_data(a-0x60000000,b-a),a)}for n,a,b in spans]}
    report['derived_masks']=[{'support':s,'option':o,'context':c,'intersection':s&o&c,'151_effective':4 if s&o&c else 0,'152_effective':s&o&c}
        for s,o,c in [(1,1,1),(1,0,1),(1,1,0),(1,2,1),(4,4,4)]]
    report['verified']=['151 maps nonzero intersection to4;152/final publish raw support&option&context intersection at007a3a64.',
        '152 adds supported-only state15h,value4 setup request before checked gameplay loop,retained final.',
        'Retained scene restore submits effective gate to state15h;ordinary normalized1 inputs therefore submit1 instead of4.',
        'DX7 table routes selector15h to60004c44;value4 configures mode state while0/1 take distinct disable/enable branches.',
        'This connects the previously verified configuration opt-in to a historical EXE/provider-contract change.']
    report['limits']=['Static selected routes/derived masks only;no game,DLL,API,instruction probe,compilation or Ghidra writes.',
        'No authoritative complete Thrash107 specification or all-provider version negotiation established.',
        'Provider branch guards,render-state call returns,device lifetime,other state values and rendered fog remain unverified.',
        'Intersection is bitwise;do not replace arbitrary nonzero inputs with logical booleans without producer constraints.',
        'Cache suppression can avoid repeated provider requests;API calls are not guaranteed on every source invocation.']
    (ROOT/'analysis/evidence/audits/fog-mode-enable-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:151->152 raw effective mask plus separate state15/value4 setup;final retained and DX7 dispatch linked')


if __name__=='__main__':main()
