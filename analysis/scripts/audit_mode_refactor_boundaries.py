"""Static depth narrowing and later descriptor-source release boundaries."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble
from audit_endpoint_comma_history import HISTORY


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    specs=dict(HISTORY)
    specs['1.6.0']=('9e1bb8f034026f6f2641417d59f46203f787771394767ca4c6ae4474e4324bb8','9fd80c4cdc9827f190698f28aa93f1182218d7c557898fb2653abfc4148c7a72')
    inputs={};metadata={}
    for version,(ah,eh)in specs.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        inputs[version]=raw;metadata[version]={'archive':rel,'archive_sha256':ah,'sha256':eh}
    rel,digest,_=SPECS['official_modern'];raw=(ROOT/rel).read_bytes();assert sha(raw)==digest
    inputs['1.6.1']=raw;metadata['1.6.1']={'path':rel,'sha256':digest}
    result={'kind':'static-mode-refactor-release-boundaries','versions':{}};bodies={};helpers={}
    for version,raw in inputs.items():
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        if version=='1.4.0':
            spans=[(0x4bed90,0x4bee72)]
            assert get(0x4bedfe,0x4bee03).hex()=='83f9107c60'
        else:
            spans=[(0x4bed90,0x4bedca if version=='1.6.1'else 0x4bedcb),
                   (0x4bedcc,0x4bee5e if version=='1.6.1'else 0x4bee5f),(0x4bee60,0x4beea3)]
            helpers[version]=get(0x4bee60,0x4beea3)
            assert get(0x4bee8e,0x4bee9d).hex()=='8b460883f820740583f8107502b301'
            for site in [0x4bed99,0x4beddd]:
                assert get(site,site+(5 if version=='1.6.1'else 6)).hex()==('a15c3a7a00'if version=='1.6.1'else'ff1580f99e00')
        bodies[version]=[get(a,b)for a,b in spans]
        result['versions'][version]={**metadata[version],'captures':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
             'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    assert bodies['1.5.0']==bodies['1.6.0']
    assert helpers['1.5.0']==helpers['1.6.0']==helpers['1.6.1']
    # Prior pinned early evidence provides the precise comparison bytes, not just an old conclusion.
    prior=ROOT/'analysis/evidence/audits/mode-admission-history.json'
    evidence=json.loads(prior.read_text())
    early=bytes.fromhex(evidence['binaries']['1.1.0']['captures'][0]['hex'])
    assert sha(early)==evidence['binaries']['1.1.0']['captures'][0]['sha256']
    assert bodies['1.4.0'][0]==early
    result['prior_early_evidence']={'path':str(prior.relative_to(ROOT)),'sha256':sha(prior.read_bytes()),
        'early_110_enumerator_equals_fresh140':True}
    result['verified']=['Depth signed>=16 remains in1.4.0;1.5.0 uses new67-byte helper admitting only16/32.',
        '1.5.0/1.6.0 enumerator, nearest-mode search and eligibility helper bodies are identical.',
        '1.6.0->1.6.1 replaces two about-slot calls with cached-descriptor reads; eligibility helper unchanged.',
        'The surrounding bodies are repacked and nearest-search epilogue stores saved EAX before restoring ESP in final; not only an in-place operand substitution.']
    result['limits']=['No game, provider, callback, instruction probe or API execution.',
        'Fresh historical archives pin140/150/160; early110 bytes reused from hash-retained prior evidence, not re-extracted here.',
        'Code equality is not descriptor-state/callback equivalence; cached-pointer validity and provider side effects remain separate.',
        'No measured speedup, advertised depth support, actual mode choice or full nearest-search machine-state equivalence claim.',
        'Only selected complete bodies/release pairs; not every renderer or texture-loading consumer.']
    (ROOT/'analysis/evidence/audits/mode-refactor-boundaries.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140->150 depth narrowing;150/160 body equality;160->161 two descriptor-cache substitutions with retained eligibility')


if __name__=='__main__':main()
