"""Static original mutex recovery and Modern repurposed handle-slot witnesses."""
import hashlib
import json
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-instance-recovery-and-handle-role', 'binaries': {},
              'limits': ['No mutex/window/heap API execution.',
                         'Modern imports CreateMutexA; absence of all other mutex uses not established.',
                         'Original fallback metadata pointer and termination-policy writers unqualified.']}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT/relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        get = lambda a,n: pe.get_data(a-0x400000,n)
        imports = {i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT
                   for i in d.imports if i.name}
        spans = [(0x4f91d0,0x4f925f),(0x4b603b,0x4b605d)] if label=='original' else [(0x4a3df2,0x4a3dfd)]
        rows=[]
        for a,b in spans:
            value=get(a,b-a)
            rows.append({'start':f'{a:08x}','exclusive_end':f'{b:08x}',
                         'sha256':hashlib.sha256(value).hexdigest(),'bytes':value.hex()})
        if label=='original':
            assert imports[0x5344a0]=='CreateMutexA'
            assert imports[0x534534]=='GetLastError'
            assert imports[0x534734]=='FindWindowA'
            assert get(0x4f91f1,12)==bytes.fromhex('506a016a002eff15a0445300')
            assert get(0x4f9216,10)==bytes.fromhex('516a002eff1534475300')
            assert get(0x4f9209,5)==bytes.fromhex('3db7000000')
            assert get(0x4f91fd,5)==bytes.fromhex('a3403d9f00')
            assert pe.get_string_at_rva(0x53fe08-0x400000)==b'Need For Speed III'
        else:
            assert imports[0x53448c]=='GetProcessHeap'
            assert get(0x4a3df2,11)==bytes.fromhex('ff158c445300a3403d9f00')
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    (ROOT/'analysis/evidence/audits/instance-recovery-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original mutex/title recovery, Modern heap slot producer, baseline identities')


if __name__=='__main__':
    main()
