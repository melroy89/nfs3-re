"""Static early diagnostic flag change; no dialog or handler execution."""
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
    inputs={label:((ROOT/rel).read_bytes(),digest,rel)for label,(rel,digest,_)in SPECS.items()}
    inputs['1.1.0']=(early,eh,str(archive.relative_to(ROOT))+'!nfs3.exe')
    result={'kind':'static-diagnostic-dialog-history','archive_sha256':ah,'binaries':{}};bodies={}
    for label,(raw,digest,path)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw)
        body=pe.get_data(0x1010,520);bodies[label]=body
        expected=0x11031 if label=='original'else 0x51011
        assert pe.get_data(0x1195,5)==b'\x68'+expected.to_bytes(4,'little')
        assert pe.get_string_at_rva(0x136030)==b'Abort message:'
        call=pe.get_data(0x11a6,7);assert call.hex()=='2eff1564475300'
        imports={e.address:e.name for dll in pe.DIRECTORY_ENTRY_IMPORT for e in dll.imports if e.name}
        assert imports[0x534764]==b'MessageBoxA'
        result['binaries'][label]={'path':path,'sha256':digest,'messagebox_flags':f'{expected:08x}',
            'caption':'Abort message:','caption_address':'00536030','messagebox_iat':'00534764',
            'capture':{'start':'00401010','end_exclusive':'00401218','sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,0x401010)}}
    assert bodies['1.1.0']==bodies['official_modern']
    changes=[0x401010+i for i,(a,b)in enumerate(zip(bodies['original'],bodies['official_modern']))if a!=b]
    assert changes==[0x401196,0x401198];result['changed_byte_addresses']=[f'{a:08x}'for a in changes]
    result['limits']=['No game, abort handler, MessageBox API or extracted instruction execution.',
        'Early1.1.0 proves presence, not1.0.0 introduction or all error dialogs.',
        'Flag names/Windows semantics reuse the prior primary-source interpretation; no window stacking or usability result measured.',
        'Original SYSTEMMODAL already requests topmost style; added explicit TOPMOST does not prove original was obscured.',
        'Identical body/caption does not prove equal globals, formatter/callback state, handler admission or termination behavior.']
    (ROOT/'analysis/evidence/audits/diagnostic-dialog-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:three pinned520-byte handlers,early/final equality,only two flag bytes changed and retained caption/API binding')


if __name__=='__main__':main()
