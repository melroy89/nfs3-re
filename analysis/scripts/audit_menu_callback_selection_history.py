"""Static complete callback-loop comparison: none sentinel and index width."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def signed16(value):
    value&=65535
    return value-65536 if value>=32768 else value


def main():
    pins={'1.3.1':('6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934','199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664'),
          '1.4.0':HISTORY['1.4.0']}
    inputs={k:((ROOT/p).read_bytes(),h,{'path':p})for k,(p,h,_)in SPECS.items()}
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        inputs[version]=(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']),eh,{'archive':rel,'archive_sha256':ah})
    report={'kind':'static-menu-callback-selection-history','binaries':{}};bodies={};queries=[]
    old=bytes.fromhex('8b4616c1f8108945f48b4618c1f8108945f88b45f40345f839c27507b801000000eb0231c0')
    new=bytes.fromhex('668b461a6683f8647412660346180fbfc039c27507b801000000eb0931c0eb059090909090')
    for label,(raw,digest,identity)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        body=get(0x44a4f0,0x44a65b);bodies[label]=body;query=get(0x44a440,0x44a469);queries.append(query)
        assert get(0x44a5a6,0x44a5cb)==(old if label in ('original','1.3.1')else new)
        assert get(0x44a5cb,0x44a5df).hex()=='837b2c007414f6430510750e9889c289d8ff532c'
        report['binaries'][label]={**identity,'sha256':digest,'captures':[
            {'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),'hex':get(a,b).hex(),
             'disassembly':disassemble(get(a,b),a)}for name,a,b in [('callback_loop',0x44a4f0,0x44a65b),('selected_entry_query',0x44a440,0x44a469)]]}
    assert bodies['original']==bodies['1.3.1']and bodies['official_modern']==bodies['1.4.0']
    assert all(q==queries[0]for q in queries)
    changed=[f'{0x44a4f0+i:08x}'for i,(a,b)in enumerate(zip(bodies['original'],bodies['official_modern']))if a!=b]
    assert changed==[f'{a:08x}'for a in range(0x44a5a6,0x44a5cb)]
    samples=[]
    for start,selection,index in [(5,2,7),(5,2,8),(5,100,105),(32760,10,-32766),(-32760,-10,32766)]:
        start=signed16(start);selection=signed16(selection);index=signed16(index)
        original=start+selection;modern=signed16(start+selection)
        samples.append({'start_signed16':start,'selection_signed16':selection,'entry_index_signed16':index,
            'original_sum':original,'modern_sum':modern,'original_flag':int(index==original),
            'modern_flag':int(selection!=100 and index==modern),
            'evidence':'Derived scalar arithmetic only; not executed original instructions or proven reachable menu state.'})
    report['changed_byte_addresses']=changed;report['derived_cases']=samples
    report['verified']=['Complete363-byte loop differs only in37-byte selection preparation,including five final NOP bytes excluded from saved function ranges.',
        'All complete loop bytes match original->1.3.1 and1.4.0->final for these four pinned builds.',
        'Original selected flag compares entry index with signext16(start)+signext16(selection) in32bits.',
        'Modern first treats selection WORD100 as none,otherwise compares with signext16((start+selection)mod65536).',
        'Retained callback gate passes computed0/1 through CWDE/MOV EDX,EAX with entry in EAX to[entry+2c].',
        'Retained selected-entry query already returns-1 for selection100 in all four builds; it otherwise retains32-bit summation.']
    report['limits']=['Static byte/control-flow and derived arithmetic only; no target instructions, menu, API or Ghidra writes.',
        'Callback state and consumers can change after dispatch; whole flags/register/local-stack equivalence is not claimed.',
        'Scalar boundary cases do not establish valid menu records, array bounds or runtime reachability.',
        'No universal original UI bug or particular release-note attribution inferred from this independent mechanism.',
        'Selection query and callback now share sentinel policy but are not numerically equivalent for16-bit sum overflow.']
    (ROOT/'analysis/evidence/audits/menu-callback-selection-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:four pinned complete loops,131->140 sentinel/width change,retained query and derived scalar cases')


if __name__=='__main__':main()
