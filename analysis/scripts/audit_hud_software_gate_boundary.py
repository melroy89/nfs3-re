"""Bound a negative SoftTri-bevel lead using paired complete branch spans."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble
from audit_endpoint_comma_history import HISTORY


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    inputs={label:((ROOT/rel).read_bytes(),digest,{'path':rel})for label,(rel,digest,_)in SPECS.items()}
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        inputs[version]=(raw,eh,{'archive':rel,'archive_sha256':ah})
    result={'kind':'static-hud-software-gate-boundary','binaries':{}};bodies=[]
    for label,(raw,digest,metadata)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);rows=[];pair=[]
        for start,end,branch in [(0x482051,0x4820ac,0x52),(0x48213e,0x482173,0x2c)]:
            body=pe.get_data(start-0x400000,end-start);pair.append(body)
            assert body[:9]==bytes.fromhex('f605583a7a000275')+bytes([branch])
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':sha(body),
                         'hex':body.hex(),'disassembly':disassemble(body,start)})
        bodies.append(pair);result['binaries'][label]={**metadata,'sha256':digest,'captures':rows}
    assert all(pair==bodies[0]for pair in bodies)
    result['verified']=['The two selected renderer-byte bit2/JNE branch spans are identical across original,140,150 and final.',
        'Each skips its captured fall-through work when bit2 is set; no local gate removal in the claimed140->150 pair.',
        'This does not establish that these spans alone own the advertised opponent/speeds-list bevel.']
    result['limits']=['No game, renderer, input, callback or extracted instruction execution.',
        'Only two selected91/53-byte branch spans, not complete enclosing routines or every software-renderer path.',
        'Identical instructions may consume changed globals, vertices, texture data or provider implementations.',
        'Final s-type bit2 association uses prior loader evidence; no universal cross-version flag meaning inferred.',
        'MP150-017 remains unverified; required follow-up is actual list-frame dispatch/resource/provider linkage, not another assertion that nearby geometry changes fix it.']
    (ROOT/'analysis/evidence/audits/hud-software-gate-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:two complete branch spans identical in four pinned builds;SoftTri-bevel attribution remains unverified')


if __name__=='__main__':main()
