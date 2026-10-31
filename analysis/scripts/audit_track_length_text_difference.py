"""Static track-length formatting tail comparison; no renderer execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result={'kind':'static-track-length-formatting-comparison','baselines':{}}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe
        end=0x456664 if label=='original' else 0x45663a
        data=pe.get_data(0x565d6,end-0x4565d6)
        tables=[]
        for va in (0x559644,0x559668,0x55968c):
            blob=pe.get_data(va-0x400000,36); pointers=struct.unpack('<9I',blob)
            tables.append({'va':f'{va:08x}','hex':blob.hex(),
                'strings':[pe.get_string_at_rva(x-0x400000).decode('ascii') if x else None for x in pointers]})
        result['baselines'][label]={'path':relative,'sha256':expected,
            'tail_start':'004565d6','tail_end_exclusive':f'{end:08x}',
            'tail_hex':data.hex(),'tail_sha256':hashlib.sha256(data).hexdigest(),
            'disassembly':subprocess.check_output(['objdump','-d','-Mintel','--start-address=0x4565d6',f'--stop-address={end}',str(ROOT/relative)],text=True),
            'tables':tables,'formats':{f'{va:08x}':pe.get_string_at_rva(va-0x400000).decode('ascii') for va in (0x539a78,0x539a80,0x538d7c)}}
    for va in (0x559644,0x559668):
        assert images['original'].get_data(va-0x400000,36)==images['official_modern'].get_data(va-0x400000,36)
    assert images['official_modern'].get_data(0x15968c,36)==b'\0'*36
    assert [row['strings'] for row in result['baselines']['original']['tables'][:2]] == [row['strings'] for row in result['baselines']['official_modern']['tables'][:2]]
    a,b=[pe.get_data(0x56318,0x4e8) for pe in images.values()]
    changes=[0x456318+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert len(changes)==152 and all(0x4565d6<=va<0x456670 for va in changes)
    result['interval']={'start':'00456318','end_exclusive':'00456800','bytes':1256,
        'changed_bytes':152,'changed_addresses':[f'{va:08x}' for va in changes],
        'limit':'Tail comparison only; shared enclosing entry and full widget registration not established.'}
    result['limits']=['No drawing, language lookup or instruction execution.','Selector/unit semantics, valid track indices and complete localization not established.','Third original table zeroed in Modern; all other readers not excluded.']
    (ROOT/'analysis/evidence/audits/track-length-text-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired formatting tails, retained two tables, zeroed third and152 localized interval differences')


if __name__=='__main__':main()
