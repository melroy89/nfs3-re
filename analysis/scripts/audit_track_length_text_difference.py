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
        'limit':'Complete formatting helper00456590 paired by direct call004566a5; full widget registration remains unresolved.'}
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
    readme=ROOT/'analysis/captures/modern-differences/upstream/package/readme_en.txt'
    readme_bytes=readme.read_bytes()
    readme_sha=hashlib.sha256(readme_bytes).hexdigest()
    assert readme_sha=='02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d'
    claim=readme_bytes.decode('latin1').splitlines()[315]
    assert claim=='- Length of a track in the track info is displayed in units, which is choosed in the HUD of the 1st player.'
    result['catalog_route']={'id':'MP140-032','readme_sha256':readme_sha,
        'line':316,'source_claim':claim,'support':'partial static',
        'limit':'First profile cell, selector branches and official unit labels verified; live first-player bank selection, visible output and v1.4.0 introduction not verified.'}
    full_helpers={}
    for label,pe in images.items():
        end=0x456664 if label=='original' else 0x45663a
        data=pe.get_data(0x56590,end-0x456590)
        call=pe.get_data(0x566a5,5)
        assert call[0]==0xe8 and 0x4566aa+int.from_bytes(call[1:],'little',signed=True)==0x456590
        assert data[:11]==bytes.fromhex('53515256575589e583ec50')
        full_helpers[label]={'entry':'00456590','end_exclusive':f'{end:08x}',
            'bytes':len(data),'hex':data.hex(),'sha256':hashlib.sha256(data).hexdigest(),
            'shared_direct_callsite':'004566a5','call_hex':call.hex()}
    assert images['original'].get_data(0x56590,70)==images['official_modern'].get_data(0x56590,70)
    result['complete_formatting_helpers']={'baselines':full_helpers,
        'shared_prefix_bytes':70,'limit':'Complete local helper envelopes and direct caller verified; broader owner registration, valid indices and drawing semantics remain separate.'}
    routes={}
    for label,pe in images.items():
        assert struct.unpack('<3I',pe.get_data(0x157a9c,12))==(4,0x538360,0x556df0)
        assert pe.get_string_at_rva(0x138360)==b'image'
        assert pe.get_data(0x156e1c,4)==struct.pack('<I',0x460100)
        assert pe.get_string_at_rva(0x13a954)==b'glow'
        prefix=pe.get_data(0x60100,0x29)
        wrapper=pe.get_data(0x56670,0x189)
        routes[label]={'registry_row':'00557a9c','type':4,'name':'image','template':'00556df0',
            'update_slot':'00556e1c','update_target':'00460100','codelink':'glow',
            'dispatch_prefix_hex':prefix.hex(),'wrapper_entry':'00456670',
            'wrapper_end_exclusive':'004567f9','wrapper_hex':wrapper.hex(),
            'wrapper_sha256':hashlib.sha256(wrapper).hexdigest()}
    assert routes['original']['dispatch_prefix_hex']==routes['official_modern']['dispatch_prefix_hex']
    assert routes['original']['wrapper_hex']==routes['official_modern']['wrapper_hex']
    result['image_glow_route']={'baselines':routes,
        'gate':'00559c60 must be0 and006fd4ac must equal00677d8c before call00456590',
        'limit':'Static registry/codelink/wrapper chain; actual menu instance loading and runtime invocation untested.'}
    menu_routes=[]
    for member in ('fedata/menus/location.mnu','fedata/menus/trkinfo.mnu'):
        data=subprocess.check_output(['7z','x','-so',str(archive),member])
        local=ROOT/'analysis/captures/modern-differences/upstream/package'/member
        assert local.read_bytes()==data
        sections=[];current=None
        for line in data.decode('latin1').splitlines():
            if line.startswith('['):
                current={'section':line.strip('[]'),'fields':{}};sections.append(current)
            elif current is not None and '=' in line and not line.startswith(';'):
                key,value=line.split('=',1);current['fields'][key]=value
        selected=[row for row in sections if row['fields'].get('nextmenu')=='trkinfo' or row['fields'].get('codelink')=='glow']
        assert len(selected)==1
        assert selected[0]['section']==('button' if member.endswith('location.mnu') else 'image')
        menu_routes.append({'member':member,'sha256':hashlib.sha256(data).hexdigest(),
            'selected_sections':selected,'matches_retained_local_copy':True})
    result['official_track_info_menu_route']={'members':menu_routes,
        'limit':'Authored menu route and image binding; parser/runtime selection, navigation and rendering untested.'}
    result['limits']=['No drawing, language lookup or instruction execution.','Raw selector enum names, valid track indices and runtime localization choice not established; selected official unit strings verified.','Third original table zeroed in Modern; all other readers not excluded.']
    (ROOT/'analysis/evidence/audits/track-length-text-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired formatting tails, retained pointer tables, comma-to-dot payloads, zeroed third and152 localized interval differences')


if __name__=='__main__':main()
