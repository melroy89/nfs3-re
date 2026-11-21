"""Retain DX6 selector15h branches at the140/150 menu-context boundary."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior_path=ROOT/'analysis/evidence/audits/menu-fog-context-history.json'
    prior=json.loads(prior_path.read_text())
    result={'kind':'static-dx6-fog-selector-history','prior_evidence_sha256':sha(prior_path.read_bytes()),'versions':{}}
    retained=[]
    spans=[('dispatcher_prefix',0x60003310,0x60003345),
           ('selector15_routes',0x6000373e,0x600038b2),
           ('raw_state_wrapper',0x60006950,0x60006991)]
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'drivers/dx6/dx6a.dll'])
        assert sha(raw)==prior['versions'][version]['dx6']['sha256']
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        assert any(e.name==b'_THRASH_setstate@8'and e.address==0x3310 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        table_entry=0x60003f0c+0x15*4
        assert struct.unpack('<I',get(table_entry,table_entry+4))[0]==0x6000373e
        assert get(0x6000333e,0x60003345).hex()=='ff24bd0c3f0060'
        assert get(0x6000373e,0x60003753).hex()=='83fb0475626a016a1c891db4bc0360892d5c4b0160'
        assert get(0x60003872,0x6000387e).hex()=='3bdd751b556a1ce8d2300000'
        assert get(0x60006988,0x60006991).hex()=='ff5158f7d81bc040c3'
        blobs=[get(a,b)for _,a,b in spans];retained.append(blobs)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'drivers/dx6/dx6a.dll',
            'sha256':sha(raw),'exe_sha256_from_history':eh,'selector15_table_entry':f'{table_entry:08x}',
            'selector15_target':'6000373e','captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'sha256':sha(get(a,b)),'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert retained[0]==retained[1]
    result['verified']=[
        'Both exports dispatch selector15h through table60003f0c to6000373e;selected code ranges identical.',
        'Payload4 stores mode4,clears60014b5c,and requests raw states1c=1,23=1,22/26/24/25 from global parameters.',
        'Payload0 requests raw state1c=0 and clears60014b5c;payload1 requests1c=1 and stores1 there.',
        'Raw wrapper60006950 can invoke setup/flush helpers,then calls object600150a0 vtable+58 with state/value.',
        'Wrapper normalizes zero callback result to1 and nonzero to0;selector branches set success register regardless of these individual results.',
        'Previously verified menu effective0 versus old supported4 reaches different selected provider branches when cache permits forwarding.']
    result['limits']=[
        'No actual DLL/API execution,rendering,compiler,instruction probe or Ghidra write.',
        'Raw state IDs retained without asserting a fully verified external COM/API identity or complete specification.',
        'Setup/flush helpers,object provenance,device acceptance,cache/lifetime and all other selector values remain separately qualified.',
        'No direct menu-car or taillight-specific draw linkage;MP150-033 remains vendor-only.',
        'Identical selected branches do not establish whole DLL data/resource or runtime equivalence.']
    (ROOT/'analysis/evidence/audits/dx6-fog-selector-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140/150 DX6 selector15 routes identical;payload4/0 raw-state request difference retained')


if __name__=='__main__':main()
