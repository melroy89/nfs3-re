"""Static early/final loading-artwork tiling correspondence."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.1.0.7z'
    archive_hash='31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac'
    assert sha(archive.read_bytes())==archive_hash
    early=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    assert sha(early)=='59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'
    rel,digest,_=SPECS['official_modern'];raw=(ROOT/rel).read_bytes();assert sha(raw)==digest
    images=[pefile.PE(data=b)for b in [early,raw]];bodies=[p.get_data(0x94cb0,748)for p in images]
    changed=[0x494cb0+i for i,(a,b)in enumerate(zip(*bodies))if a!=b]
    assert changed==[0x494d11,0x494d1a,0x494ebc,0x494f0d,0x494f22,0x494f37,0x494f4c,0x494f61,0x494f70]
    rows=[]
    for p,body,label in zip(images,bodies,['modern_1.1.0','official_final']):
        assert p.get_data(0x94d23,5).hex()=='ba00010000'
        assert p.get_data(0x94d3e,10).hex()=='b903000000bb02000000'
        rows.append({'label':label,'sha256':sha(early if label=='modern_1.1.0'else raw),
                     'capture':{'start':'00494cb0','end_exclusive':'00494f9c','sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,0x494cb0)}})
    reads=[]
    for site in [0x494d11,0x494d1a]:
        addresses=[struct.unpack('<I',p.get_data(site-0x400000,4))[0]for p in images]
        values=[p.get_data(a-0x400000,4)for p,a in zip(images,addresses)];assert values[0]==values[1]
        reads.append({'operand':f'{site:08x}','addresses':[f'{a:08x}'for a in addresses],'identical_binary32_hex':values[0].hex()})
    calls=[]
    for p in images:
        b=p.get_data(0x94ebb,5);assert b[0]==0xe8
        calls.append(f'{0x494ec0+int.from_bytes(b[1:],"little",signed=True):08x}')
    assert calls==['00494c60','00494c5c']
    result={'kind':'static-loading-artwork-early-final-history','archive':str(archive.relative_to(ROOT)),
        'archive_sha256':archive_hash,'final_path':rel,'binaries':rows,'changed_bytes':[f'{a:08x}'for a in changed],
        'scale_reads':reads,'changed_call_targets':calls,
        'verified':['Early1.1.0 already requests256-square extent and3x2 grid as in final.',
            'Complete748-byte envelopes differ at only nine bytes: two scale-read addresses, six progress-state store addresses and one relative-call displacement.',
            'Both scale-read constants match at their versioned addresses; store-address identity/lifetime is not assumed.'],
        'limits':['No raster, asset, renderer, game or extracted instruction execution.',
            'An envelope may include padding; bytes retained through00494f9c do not redefine recovered function boundaries.',
            'Original300-versus-Modern6 iteration evidence is in linked prior loading-artwork audit; this checks early/final correspondence.',
            'Changed callee00494c60->00494c5c and relocated progress stores are recorded, not transitively proven equivalent here.',
            'Better image quality, sprite seam fixes, actual allocations/uploads, performance and1.0.0 introduction unverified.']}
    (ROOT/'analysis/evidence/audits/loading-tile-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: early/final256 extent and3x2 grid; nine differing bytes classified with equal scale constants')


if __name__=='__main__':main()
