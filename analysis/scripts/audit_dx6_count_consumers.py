"""Link historical DX6 count adjustment to inclusive EXE consumers."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior_path=ROOT/'analysis/evidence/audits/dx6-mode-count-history.json';prior=json.loads(prior_path.read_text())
    assert prior['layout']['record_bytes']==40 and prior['layout']['insert_helper_limit']==100
    assert prior['layout']['published_table_base']=='6003f000'and prior['layout']['insertion_base']=='6003f028'
    assert prior['layout']['explicit_zeroing']=={'start':'6003f028','bytes':4000,'excludes_leading_record':True}
    result={'kind':'static-dx6-count-consumers','prior_evidence_sha256':sha(prior_path.read_bytes()),'versions':{}}
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        if version=='1.4.0':
            spans=[('enumeration',0x4bed90,0x4bee72)]
            assert get(0x4beda4,0x4bedb8).hex()=='be010000008945fc8b45fc3b703c0f8fb1000000'
        else:
            spans=[('enumeration',0x4bed90,0x4bedcb),('nearest_search',0x4bedcc,0x4bee5f),
                   ('eligibility',0x4bee60,0x4beea3),('application_prefix',0x4bef50,0x4befc2),
                   ('application_index_gate',0x4befc2,0x4befdb)]
            assert get(0x4bedaa,0x4bedb3).hex()=='4183c6283b4df87f14'
            assert get(0x4bedb3,0x4bedc7).hex()=='89f0e8a600000085c074ec89c889f2ff55fcebe3'
            assert get(0x4bedf0,0x4bee04).hex()=='4183c6283b4df07f5589f0e86000000085c074ec'
            assert get(0x4bee67,0x4bee78).hex()=='8a4610a801742fa802752b837e14027c25'
            assert get(0x4bee4e,0x4bee56).hex()=='89d885c07502b001'
            assert get(0x4befce,0x4befd2).hex()=='39d37e09'
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                         'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    rows=[];base=int(prior['layout']['insertion_base'],16);clear_end=base+4000
    for n in (0,3,99,100):
        extra=base+n*40;inside=extra+40<=clear_end
        rows.append({'inserted_records':n,'reported_count_150':n+1,'last_visited_public_index':n+1,
            'extra_record_address':f'{extra:08x}','inside_explicit_clear_arena':inside,
            'zero_extra_rejected_before_callback':True if inside else None,
            'premise':'Fresh clear;only retained insertion/replacement writes;no alias or external table mutations;not a runtime observation.'})
    result['conditional_derived_extents']=rows
    result['verified']=['Both checked historical scans start at1 and use signed greater-than exit,so indexcount is included.',
        '150 enumeration and nearest lookup share eligibility helper;flags bit0-clear exits before geometry division.',
        'For0<=N<100 under retained insertion-only lifecycle,extra public indexN+1 is zeroed insertion slotN and receives no enumeration callback.',
        'AtN100 extra index101 lies beyond explicit4000-byte cleared insertion arena;that static zero-slot proof no longer applies.',
        'Nearest lookup retains fallback index1 without proof it passed eligibility.',
        '150 direct application admits changed index1..count inclusively,while same-current path skips that count gate;no eligibility-helper call is established there.']
    result['limits']=['No game,driver,mode API,instruction probe,compilation or Ghidra writes.',
        'Conditional arena proof excludes external/aliased record mutation and malformed counter state;complete lifetime remains unknown.',
        'Beyond explicit clear does not prove outside mapped memory,corruption or a runtime fault.',
        'No all-input switch safety or complete mode-list equivalence claimed;150 also changes depth admission and collector ABI.',
        'This explains selected consumer implications,not a universal missing-last-resolution fix or rendered provider acceptance.']
    (ROOT/'analysis/evidence/audits/dx6-count-consumers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:inclusive scans and150 early zero-slot rejection;conditionalN<100 arena proof,capacity/switch limits retained')


if __name__=='__main__':main()
