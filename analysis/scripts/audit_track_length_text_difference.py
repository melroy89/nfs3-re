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
    old_tables=result['baselines']['original']['tables']
    new_tables=result['baselines']['official_modern']['tables']
    assert old_tables[0]['strings']==new_tables[0]['strings']
    assert [value.replace(',', '.') for value in old_tables[1]['strings']]==new_tables[1]['strings']
    assert all(',' in value for value in old_tables[1]['strings'])
    assert old_tables[2]['strings']==new_tables[1]['strings']
    result['string_payload_change']='Second table pointers retained; original decimal commas replaced by dots. Original third-table dot strings match Modern second-table values.'
    a,b=[pe.get_data(0x56318,0x4e8) for pe in images.values()]
    changes=[0x456318+i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert len(changes)==152 and all(0x4565d6<=va<0x456670 for va in changes)
    result['interval']={'start':'00456318','end_exclusive':'00456800','bytes':1256,
        'changed_bytes':152,'changed_addresses':[f'{va:08x}' for va in changes],
        'limit':'Tail comparison only; shared enclosing entry and full widget registration not established.'}
    default=images['official_modern'].get_data(0x8595b,41)
    assert default[:5]==bytes.fromhex('bb03000000')
    destinations=[]
    for offset in range(5,41,6):
        instruction=default[offset:offset+6]
        assert instruction[:2]==bytes.fromhex('891d')
        destinations.append(int.from_bytes(instruction[2:],'little'))
    assert destinations==[0x6fbc68+i*0x1a4 for i in range(6)]
    result['modern_default_selector_producer']={'start':'0048595b','end_exclusive':'00485984',
        'hex':default.hex(),'sha256':hashlib.sha256(default).hexdigest(),
        'value':3,'destinations':[f'{va:08x}' for va in destinations],
        'limit':'Default initializer writes only; later saved settings/editor/aliases not excluded.'}
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_sha=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    languages=[]
    for language in ('eng','ger','fre','spa','ita','swe'):
        member='fedata/text/text.'+language
        data=subprocess.check_output(['7z','x','-so',str(archive),member])
        extent=struct.unpack_from('<I',data)[0]
        assert extent%4==0 and extent<=len(data)
        labels=[]
        for ident in (6,0x78a):
            assert ident*4<extent
            offset=struct.unpack_from('<I',data,ident*4)[0]
            assert extent<=offset<len(data)
            end=data.index(b'\0',offset)
            labels.append({'id':ident,'offset':offset,'hex':data[offset:end].hex(),
                'text_latin1':data[offset:end].decode('latin1')})
        assert labels[1]['text_latin1']=='km'
        languages.append({'member':member,'sha256':hashlib.sha256(data).hexdigest(),
            'bytes':len(data),'table_extent':extent,'labels':labels})
    result['official_unit_assets']={'archive_sha256':archive_sha,'members':languages,
        'limit':'Selected packaged entries validated; no proof of runtime file selection or complete asset parser validation.'}
    result['limits']=['No drawing, language lookup or instruction execution.','Raw selector enum names, valid track indices and runtime localization choice not established; selected official unit strings verified.','Third original table zeroed in Modern; all other readers not excluded.']
    (ROOT/'analysis/evidence/audits/track-length-text-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired formatting tails, retained pointer tables, comma-to-dot payloads, zeroed third and152 localized interval differences')


if __name__=='__main__':main()
