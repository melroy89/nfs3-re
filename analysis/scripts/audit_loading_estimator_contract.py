"""Static loading estimator branches with exact ordinary arithmetic examples."""
import hashlib,json
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def ordinary(requested,now,last,start,target,previous):
    """Only exact finite examples below; not an x87 instruction emulator."""
    if requested!=100 and ((now-last)&0xffffffff)<=50:return None
    elapsed=(now-start)&0xffffffff
    if elapsed<target:
        percentage=elapsed*100/target
        if percentage<=requested:return percentage
    return min(requested,previous+5)


def main():
    relative,digest,_=SPECS['official_modern'];raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
    pe=pefile.PE(data=raw)
    def get(a,b):return pe.get_data(a-0x400000,b-a)
    body=get(0x490134,0x4901c3)
    checks=[(0x490143,'81fb0000c8427410'),(0x490151,'83f8327705'),
        (0x490156,'31c048eb61'),(0x490163,'3b05ac277a007322'),
        (0x490180,'dfe0d91c249e77058b1c24eb21'),
        (0x49018d,'d905a8277a00c704240000a040d80424'),
        (0x4901a3,'dfe0d91c249e73038b1c24'),
        (0x4901ae,'891da8277a00890da4277a0089d8')]
    for address,encoded in checks:assert get(address,address+len(bytes.fromhex(encoded))).hex()==encoded
    cases=[dict(requested=50,now=1000,last=900,start=0,target=4000,previous=0,expected=25),
        dict(requested=100,now=1000,last=999,start=0,target=4000,previous=80,expected=25),
        dict(requested=10,now=1000,last=900,start=0,target=4000,previous=30,expected=10),
        dict(requested=50,now=1000,last=950,start=0,target=4000,previous=0,expected=None),
        dict(requested=100,now=1000,last=1000,start=0,target=0,previous=0,expected=5)]
    for case in cases:
        args={k:v for k,v in case.items()if k!='expected'};assert ordinary(**args)==case['expected']
    result={'kind':'static-loading-estimator-contract','path':relative,'sha256':digest,
        'capture':{'start':'00490134','end_exclusive':'004901c3','sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,0x490134)},
        'exact_ordinary_derived_examples':cases,
        'verified':['Exact100.0 bits bypass ordinary unsigned elapsed<=50ms rejection.',
            'Rejected call returnsffffffffh without the two final progress/timestamp stores.',
            'Time-percentage<=requested branch bypasses previous+5 calculation.',
            'Otherwise prior+5 is compared to request; ordered prior+5>=request retains request, else stores computed candidate.',
            'Both accepted branches store output bits to007a27a8 and now to007a27a4.'],
        'limits':['Static instructions and mathematical examples, not executed game/probe/API observations.',
            'Model is deliberately scoped to finite exact-fitting cases; no x87 precision, exceptions, status, NaN, signed zero or general wrap emulator.',
            'Time-gate subtraction/comparison is unsigned32; percentage conversion uses signed FILD/FIDIV after low32 IMUL.',
            'Normal configured target<=10000 and unsigned elapsed<target bound the ordinary percentage numerator; arbitrary corrupted state not qualified.',
            'Prior paired progress/caller/reset/clock evidence is linked by the report, not independently re-audited here.',
            'No measured smoothness, frame rate, monotonicity invariant, loading speed or1.0.0 introduction proof.']}
    (ROOT/'analysis/evidence/audits/loading-estimator-contract.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:143-byte estimator, throttle/time/fallback branches and five exact ordinary derived examples')


if __name__=='__main__':main()
