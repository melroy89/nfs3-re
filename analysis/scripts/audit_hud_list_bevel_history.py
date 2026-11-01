"""Pin list-border queue admission across the advertised 1.4.0->1.5.0 boundary."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    inputs={k:((ROOT/p).read_bytes(),h,{'path':p})for k,(p,h,_)in SPECS.items()}
    for version,(archive_hash,exe_hash)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/rel;assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        inputs[version]=(raw,exe_hash,{'archive':rel,'archive_sha256':archive_hash})
    spans=[('list_admission',0x48479e,0x48483e),('bank_allocation',0x47cbb6,0x47cc37),
           ('border_layout',0x481ede,0x481ef3),('enqueue_eight',0x47fbe0,0x47fca6),
           ('remove_eight',0x47fcb0,0x47fd76),('queue_helpers',0x49bd10,0x49bee2)]
    result={'kind':'static-list-bevel-history','binaries':{}};bodies={}
    for label,(raw,digest,metadata)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        get=lambda a,b:pe.get_data(a-0x400000,b-a)
        bodies[label]={name:get(a,b)for name,a,b in spans}
        branch=get(0x4847bc,0x4847c2)
        expected=0x484941 if label in ('original','1.4.0')else 0x4847e5
        assert branch[:2]==b'\x0f\x85'
        assert 0x4847c2+struct.unpack('<i',branch[2:])[0]==expected
        assert get(0x48479e,0x4847a8).hex()=='83bc0258bc6f00007454'
        assert get(0x4847b5,0x4847bc).hex()=='f605583a7a0002'
        calls=[]
        for name,target in [('enqueue_eight',0x49bd30),('remove_eight',0x49bdc0)]:
            a=next(a for n,a,b in spans if n==name);body=bodies[label][name];sites=[]
            # Decoded instruction listing independently retained below; known helper call offsets.
            for off in [26,49,72,95,118,141,164,187]:
                assert body[off]==0xe8
                assert a+off+5+struct.unpack('<i',body[off+1:off+5])[0]==target
                sites.append(f'{a+off:08x}')
            calls.append({'helper':name,'callee':f'{target:08x}','call_sites':sites})
        result['binaries'][label]={**metadata,'sha256':digest,'software_branch_target':f'{expected:08x}',
            'calls':calls,'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
            'sha256':sha(get(a,b)),'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    for name in bodies['original']:
        if name!='list_admission':assert len({sha(b[name])for b in bodies.values()})==1,name
    original=bodies['original']['list_admission'];modern=bodies['official_modern']['list_admission']
    assert bodies['1.4.0']['list_admission']==original
    assert bodies['1.5.0']['list_admission']==modern
    changed=[f'{0x48479e+i:08x}'for i,(a,b)in enumerate(zip(original,modern))if a!=b]
    assert changed==['004847be','004847bf']
    result['changed_bytes']=changed
    result['verified']=['Renderer bit2 JNE changes target from00484941 to004847e5 in1.4.0->1.5.0 and remains in final.',
        'New target bypasses only background enqueue004847e0 and reaches eight-border-quad enqueue004847f2.',
        'Border bank vertex pointer00791b18/index base00791ad8 belongs to batch00749a38; separate background bank00791ad4/index00791adc belongs to00725748.',
        '0049bd30 appends four indices, optionally removing a prior matching group when signed first index is below batch+4.',
        '0049bdc0 removes the first matching four-index group;0047fcb0 calls it eight times, not a drawing helper.',
        'Five supporting captured spans are byte-identical in all four builds; admission span differs by exactly two bytes.']
    result['limits']=['Static control flow only; no game, software driver, instruction probes, compilation or Ghidra writes.',
        'Bit2 SoftTri attribution follows the existing final renderer-type parser; historical flag producer not independently requalified here.',
        'Visible standard bevel, speeds-list identity, provider handling and every calling context remain untested.',
        'Captured spans have explicit boundaries; no claim that list_admission is a complete enclosing function.',
        'The separate00791ac8 bank removed near00482dc8 is not the00791ad8 bank enqueued here.']
    (ROOT/'analysis/evidence/audits/hud-list-bevel-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four pinned builds; two-byte historical branch retarget admits eight border quads')


if __name__=='__main__':main()
