"""Check DX6 quad attribute handling against selector15h flag writes."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    prior_path=ROOT/'analysis/evidence/audits/dx6-fog-selector-history.json'
    prior=json.loads(prior_path.read_text())
    result={'kind':'static-dx6-quad-fog-flag-history','prior_evidence_sha256':sha(prior_path.read_bytes()),'versions':{}}
    spans=[('quad_export',0x60001570,0x600015c5),('quad_copy_and_indices',0x60005f90,0x6000623f)]
    copies=[(0x60005ffb,'8b5714895614'),(0x60006089,'8b4714894614'),
            (0x60006117,'8b4714894614'),(0x600061a6,'8b4714894614')]
    retained=[]
    for version,(ah,_)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'drivers/dx6/dx6a.dll'])
        assert sha(raw)==prior['versions'][version]['sha256']
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        assert any(e.name==b'_THRASH_drawquad@16'and e.address==0x1570 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        assert get(0x600015b8,0x600015bd).hex()=='e8d3490000'
        for a,copy in copies:
            assert get(a,a+9).hex()=='a15c4b016085c07508'
            assert get(a+9,a+15).hex()==copy
            assert get(a+15,a+17).hex()=='eb31'
        blobs=[get(a,b)for _,a,b in spans];retained.append(blobs)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'drivers/dx6/dx6a.dll','sha256':sha(raw),
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
             'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert retained[0]==retained[1]
    result['flag_checks']=[{'start':f'{a:08x}','zero_flag_action':'copy source DWORD+14h to destination+14h',
                           'nonzero_flag_action':'calculate float expression,convert via60007e00,lookup byte,and store byte shifted24 at destination+14h'}for a,_ in copies]
    result['verified']=[
        'Both140/150 quad exports conditionally call60005f90 after an orientation/sign test;checked bodies identical.',
        'Four vertex paths read60014b5c;zero copies source+14h unchanged,nonzero replaces destination+14h with lookup-byte<<24.',
        'Prior selector audit proves both payload4 and0 clear60014b5c,so these requests alone do not select different vertex-attribute branches.',
        'Raw state1Ch requests still differ between4 and0;do not conflate device-state change with CPU-side vertex rewriting.']
    result['limits']=[
        'Only selected quad path;not all primitive exports,menu-car reachability or device draw lifetime.',
        'Calls/other writes may change the flag between setup and submission;no global immutability claim.',
        'No complete external vertex schema or lookup-domain/exceptional-x87 semantics established here.',
        'No taillight-specific vertex values,rendered outcome,DLL/API execution,instruction probes,compilation or Ghidra writes.']
    (ROOT/'analysis/evidence/audits/dx6-quad-fog-flag-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: retained DX6 quad flag branches;payload4/0 both select copy under unchanged-flag premise')


if __name__=='__main__':main()
