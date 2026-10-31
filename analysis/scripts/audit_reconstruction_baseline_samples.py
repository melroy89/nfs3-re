"""Read-only three-baseline byte/relocation checks for retained reference samples."""
import hashlib,json
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SAMPLES=[(0x485c30,0x485f1b,'3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f'),
         (0x4abd9c,0x4ac027,'27c7ce1baedc6282855c2aadecfdbee768f25db8649f66aa9caea4e94ba9677b'),
         (0x518640,0x51868d,'64b39b42ecef516f64ab5db044fa9028e0591d59af23f14583d393fbc4cd6b2c')]


def main():
    specs={k:(v[0],v[1]) for k,v in SPECS.items()}
    specs['local_analysis']=('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe',
        '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb')
    result={'kind':'three-baseline-reconstruction-sample-identity','binaries':{}}
    relocations=[];constants=[];leaves=[]
    for label,(relative,expected) in specs.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end,wanted in SAMPLES:
            data=pe.get_data(start-0x400000,end-start)
            assert len(data)==end-start and hashlib.sha256(data).hexdigest()==wanted
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                         'bytes':len(data),'sha256':wanted})
            if start==0x485c30:leaves.append(data)
        sites=sorted(e.rva+0x400000 for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries
                     if e.type==3 and 0x485c30<=e.rva+0x400000<0x485f1b)
        assert len(sites)==29;relocations.append(sites)
        data=pe.get_data(0x53dd4c-0x400000,104);assert len(data)==104;constants.append(data)
        result['binaries'][label]={'path':relative,'sha256':expected,'samples':rows,
            'line_leaf_highlow_sites':[f'{a:08x}' for a in sites],
            'tyre_constant_region':{'start':'0053dd4c','end_exclusive':'0053ddb4',
                'bytes':104,'sha256':hashlib.sha256(data).hexdigest()}}
    assert relocations[0]==relocations[1]==relocations[2]
    assert constants[0]==constants[1]==constants[2]
    oracle=ROOT/'analysis/captures/line-boundary-windows/original_00485c30.bin'
    assert oracle.read_bytes()==leaves[0]==leaves[1]==leaves[2]
    result['retained_line_oracle']={'path':str(oracle.relative_to(ROOT)),
        'sha256':hashlib.sha256(oracle.read_bytes()).hexdigest(),
        'verified':'Exact code bytes match all three executable sample bodies; no rerun performed.'}
    result['limits']=['Sample byte identity is not whole-game state, ABI integration or runtime equivalence.',
        'Only the specified tyre constant envelope compared; mutable globals, vehicle layouts, initialization and ambient x87 state require existing contracts.',
        'Historical functional tests reset CW037f; identity does not extend their scope to other control words or games.',
        'No new exports, reconstruction sources, compilation, target probes or Ghidra writes.']
    (ROOT/'analysis/evidence/audits/reconstruction-baseline-samples.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: three sample bodies, 29 leaf relocations and 104-byte tyre constants match all three baselines; retained oracle bytes match')


if __name__=='__main__':main()
