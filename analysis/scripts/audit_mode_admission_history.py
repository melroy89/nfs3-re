"""Static early mode budget bypass and depth-admission distinction."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    ah='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac';assert sha(archive.read_bytes())==ah
    early=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    eh='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72';assert sha(early)==eh
    inputs={key:((ROOT/rel).read_bytes(),digest,rel)for key,(rel,digest,_)in SPECS.items()}
    inputs['1.1.0']=(early,eh,str(archive.relative_to(ROOT))+'!nfs3.exe')
    result={'kind':'static-mode-admission-history','archive_sha256':ah,'binaries':{}}
    for label,(raw,digest,path)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        spans=[(0x4bee60,0x4beea3)]if label=='official_modern'else[(0x4bed90,0x4bee72)]
        if label=='1.1.0':
            assert get(0x4bede6,0x4bedfe).hex()=='89f869c06400000031d2f7fb83f87c7c6c3db20000007f65'
            assert get(0x4bedfe,0x4bee03).hex()=='83f9107c60'
            assert get(0x4bee10,0x4bee32)==b'\xeb\x20'+b'\x90'*32
        result['binaries'][label]={'path':path,'sha256':digest,'captures':[
            {'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
             'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    examples=[]
    for width,height,depth in [(1920,1440,16),(1024,768,24),(1024,768,32),(320,240,16)]:
        ratio=100*width//height
        examples.append({'width':width,'height':height,'depth':depth,
            'original_with_8MiB_budget':3*width==4*height and depth in [15,16] and 8*1024*1024>=4*width*height,
            'early_110':124<=ratio<=178 and depth>=16,
            'final_161':124<=ratio<=178 and depth in [16,32]})
    assert examples[0]['early_110'] and not examples[0]['original_with_8MiB_budget']
    assert examples[1]['early_110'] and not examples[1]['final_161']
    result['ordinary_derived_examples']=examples
    result['example_premises']='Positive fitting dimensions, flags bit0 set/bit1 clear and signed record+14>=2; other provider/menu gates unmodeled.'
    result['limits']=['No driver, mode callback, game, API or extracted instruction execution.',
        'Early signed depth>=16 is an EXE predicate, not proof of24-bit/64-bit provider support.',
        'Original budget producer/constants and final callback/storage limits reuse linked prior audits.',
        'Examples model only these eligibility predicates, not actual advertised/selected/displayed modes.',
        'No universal maximum resolution removal or local640x480 minimum; backend, arithmetic and allocation limits remain.',
        '1.1.0 proves early presence, not1.0.0 introduction; exact later depth-narrowing date unestablished.']
    (ROOT/'analysis/evidence/audits/mode-admission-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:early budget bypass and signeddepth>=16; three-version gates with four ordinary derived examples')


if __name__=='__main__':main()
