"""Static early coefficient halving versus later fitted-width cache rewrite."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    historical=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']
    specs={
        '1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'),
        '1.5.3':('0f92afacbbc179500ede3d7e22107999f3d4ad9ff0a41feb8cd00ef65559ec64',historical['1.5.3']['executable_sha256']),
        '1.6.0':('9e1bb8f034026f6f2641417d59f46203f787771394767ca4c6ae4474e4324bb8','9fd80c4cdc9827f190698f28aa93f1182218d7c557898fb2653abfc4148c7a72')}
    inputs={key:((ROOT/rel).read_bytes(),digest,rel)for key,(rel,digest,_)in SPECS.items()}
    archives={}
    for version,(ah,eh)in specs.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        inputs[version]=(raw,eh,rel+'!nfs3.exe');archives[version]={'path':rel,'sha256':ah}
    result={'kind':'static-border-thickness-history','archives':archives,'binaries':{}};bodies={};updaters={}
    for label,(raw,digest,path)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        early=label in ['original','1.1.0','1.5.3']
        start,end=0x47f650,(0x47fbdc if early else 0x47f98c)
        body=get(start,end);bodies[label]=body
        coeff=get(0x53b4f8,0x53b4fc);scale=get(0x53b4fc,0x53b500)
        assert coeff==struct.pack('<f',4 if label=='original'else 2)
        assert scale==struct.pack('<f',1/640)
        spans=[(start,end)]
        if early:assert get(0x47f65a,0x47f66c).hex()=='db05c8da7c00d80df8b45300d80dfcb45300'
        else:
            spans.append((0x47f9a4,0x47f9bd));updaters[label]=get(0x47f9a4,0x47f9bd)
            assert updaters[label].hex()=='db0548277a00d80df8b45300d80dfcb45300db1dd0fe5500c3'
        result['binaries'][label]={'path':path,'sha256':digest,'coefficient_bits':coeff.hex(),'scale_bits':scale.hex(),
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    assert bodies['original']==bodies['1.1.0']==bodies['1.5.3']
    assert bodies['1.6.0']==bodies['official_modern'] and updaters['1.6.0']==updaters['official_modern']
    result['verified']=['Original/1.1.0/1.5.3 complete1420-byte builders are identical; early change is coefficient4->2.',
        '1.5.3->1.6.0 replaces repeated mode-width calculations with cached fitted-reference-width thickness.',
        '1.6.0 builder and25-byte updater are retained byte-for-byte in final.']
    result['limits']=['No game, border, x87 instruction or renderer execution.',
        'Coefficient halving before FISTP does not establish integer or visible half-thickness.',
        'Mode/reference-width publication and builder destinations/UV schedules reuse linked prior audits.',
        'Actual rounding, input width/state freshness, cached-update lifecycle, wrapper effects and rendering remain unverified.',
        '1.1.0 proves early presence, not1.0.0 introduction; no whole-game comparison completion claim.']
    (ROOT/'analysis/evidence/audits/border-thickness-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original/early/153 identical builders with4->2 coefficient;160 fitted-width cache rewrite retained in final')


if __name__=='__main__':main()
