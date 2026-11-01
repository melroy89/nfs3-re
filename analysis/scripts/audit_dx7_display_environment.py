"""Static DX7 display-env caller and selected consumer1.6.0/1.6.1."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def main():
    baseline=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())
    result={'kind':'dx7-display-environment-comparison','versions':{},
        'limits':['No getenv/atoi, driver/API or target execution.','Black-polygon attribution, full callback/state lifecycle and visible results unresolved.']}
    capture=ROOT/'analysis/captures/modern-differences/dx7-display-environment';capture.mkdir(parents=True,exist_ok=True)
    consumers=[]
    for version in ('1.6.0','1.6.1'):
        package=baseline['packages'][version];archive=ROOT/package['archive_path']
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==package['archive_sha256']
        member='drivers/dx7/dx7a.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        expected=next(r['sha256']for r in package['members']if r['member']==member)
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        assert pe.get_string_at_rva(0x151ac)==b'THRASH_DISPLAY'
        imports={i.address:i.name for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x60015058]==b'getenv' and imports[0x60015070]==b'atoi'
        end=0x600020b6 if version=='1.6.0' else 0x600020a0
        rows=[]
        for lo,hi in [(0x60002060,end),(0x600020c0,0x600021e7)]:
            code=pe.get_data(lo-0x60000000,hi-lo);out=capture/f'{version}-{lo:08x}.asm'
            out.write_text('\n'.join(disassemble(code,lo))+'\n')
            rows.append({'start':f'{lo:08x}','end_exclusive':f'{hi:08x}','bytes_sha256':hashlib.sha256(code).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        consumers.append(pe.get_data(0x20c0,0x127))
        if version=='1.6.0':
            assert pe.get_data(0x20aa,10).hex()=='8b44240050e80c000000'
            assert pe.get_data(0x2071,10).hex()=='c70560ab056001000000'
        else:
            assert pe.get_data(0x208a,20).hex()=='85c0740a50ff157050016083c40450e822000000'
        result['versions'][version]={'archive_sha256':package['archive_sha256'],'member':member,'sha256':expected,'spans':rows}
    assert consumers[0]==consumers[1]
    result['facts']={'common_admission':'Signed600170bc<0 and either6007b864 or6007b880 nonzero',
        'missing_environment':'160 passes entryECX savedbyPUSHECX;161 passes getenvNULL=0',
        'present_environment':'Both passatoi result',
        'removed_local_store':'160 writesDWORD1 to6005ab60 before callbackguard;161 omitsit',
        'consumer':'Complete295-byte600020c0..600021e7 identical;validsignedindexselectsentry,invalidfallsbackto0;thenothercallbacks/setup',
        'limits':'EntryECX is not proved initialized by callers;fallback0 does not prove valid firstentry or side-effect-free selection'}
    (ROOT/'analysis/evidence/audits/dx7-display-environment.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned DX7 pairs, env argument paths, removed store and identical complete selection consumer')


if __name__=='__main__':main()
