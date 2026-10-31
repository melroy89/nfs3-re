"""Static window-key translator/table comparison; no OS or instruction execution."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    out={'kind':'static-window-key-translation-comparison','baselines':{}}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe
        end=0x4ccc67 if label=='original' else 0x4ccaf6
        data=pe.get_data(0xccaa0,end-0x4ccaa0)
        out['baselines'][label]={'path':relative,'sha256':expected,'entry':'004ccaa0',
            'end_exclusive':f'{end:08x}','bytes':len(data),'hex':data.hex(),
            'body_sha256':hashlib.sha256(data).hexdigest(),
            'disassembly':subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x4ccaa0',f'--stop-address={end}',str(ROOT/relative)],text=True)}
    modern=images['official_modern'];tables=[]
    for start,end in [(0x4ccaf8,0x4ccb54),(0x4ccb54,0x4ccb84)]:
        data=modern.get_data(start-0x400000,end-start)
        pairs=list(struct.iter_unpack('<HH',data));assert pairs[-1]==(0,0)
        assert all(key and value for key,value in pairs[:-1])
        tables.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
            'hex':data.hex(),'sha256':hashlib.sha256(data).hexdigest(),
            'entries':[{'input':f'{key:04x}','output':f'{value:04x}'} for key,value in pairs[:-1]]})
    assert len(tables[0]['entries'])==22 and len(tables[1]['entries'])==11
    imports={i.address:i.name.decode() for d in modern.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
    assert imports[0x534744]=='GetKeyState'
    assert modern.get_data(0xccac8,19)==bytes.fromhex('6890000000ff1544475300a801740431c0eb19')
    assert {'input':'006c','output':'5300'} in tables[1]['entries']
    assert images['original'].get_data(0xccb2e,13)==bytes.fromhex('83fa700f84d800000031c05dc3')
    out['modern_tables']=tables
    out['numlock_gate']={'import_iat':'00534744','import':'GetKeyState','argument':144,
        'tested_mask':1,'behavior':'Primary table first; on miss, set toggle bit returns0; clear bit scans keypad table.',
        'register_dependency':'EDX key reused after GetKeyState without local save; provider preservation not established.'}
    out['old_key_006c_path']=['004ccab5','004ccac4','004ccb13','004ccb1e','004ccb2e','004ccb37 -> EAX0']
    a,b=[pe.get_data(0xccaf6,142) for pe in images.values()]
    changed=sum(x!=y for x,y in zip(a,b));assert changed==116
    out['outside_interval']={'start':'004ccaf6','end_exclusive':'004ccb84','bytes':142,
        'changed_bytes':116,'modern_partition':'2 NOP bytes +92-byte primary table +48-byte keypad table'}
    callers=[]
    for start,end,role in [(0x4cd020,0x4cd0dd,'Complete key-down callback with repeat enqueue'),
                           (0x4cd5b9,0x4cd5d3,'Message-loop translate/zero-result branch')]:
        paired={label:pe.get_data(start-0x400000,end-start) for label,pe in images.items()}
        assert paired['original']==paired['official_modern']
        data=paired['original']
        callers.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','role':role,
            'hex':data.hex(),'sha256':hashlib.sha256(data).hexdigest()})
    for site in (0x4cd0a9,0x4cd5bf):
        data=modern.get_data(site-0x400000,5)
        assert data[0]==0xe8 and site+5+int.from_bytes(data[1:],'little',signed=True)==0x4ccaa0
    out['retained_callers']={'bodies':callers,'direct_sites':['004cd0a9','004cd5bf'],
        'queue_call':'004cd0ca ->004cc8e0',
        'limit':'Windows-message to queue route verified; ECX repeat count live across translator/GetKeyState path, provider preservation not established. Physical delivery and consumer lifecycle remain untested.'}
    out['limits']=['Static mapping/branch evidence only; no keyboard, OS, game or instruction probes.',
        'No exhaustive original/Modern input equivalence claim; actual message routing, Num Lock provider result and EDX preservation remain dependencies.',
        'Table DWORDs are data, not instructions or function pointers.']
    (ROOT/'analysis/evidence/audits/window-key-translation-difference.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: complete key translator bodies,22/11 table entries, NumLock gate and116 interval differences')


if __name__=='__main__':main()
