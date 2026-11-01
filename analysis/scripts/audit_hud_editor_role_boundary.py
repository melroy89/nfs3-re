"""Bound unresolved police-widget claim by exact retained code and nonzero presets."""
import hashlib,json,struct,subprocess,re
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    capture=ROOT/'analysis/captures/modern-differences/hud-editor-role-boundary'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'bounded-unresolved-hud-editor-police-widget-review','binaries':{},
        'claim':'MP100-048 Cone Stats/Tutorial Icon hidden for cops',
        'conclusion':'Not established by checked callbacks, template/rectangle loader or nonzero preset records; work remains.',
        'limits':['Static selected-route inspection, not editor execution or all-admission-path coverage.',
                  'Author-hosted reference assets are not authenticated pristine retail or proved paired to supplied original EXE.',
                  'Nonzero rectangle records do not prove visibility; retained method bytes do not prove equal inputs/assets.',
                  'Archive omission does not prove installed-file deletion or runtime unreachability.']}
    images={};blobs={}
    spans=[(0x44d4c0,0x44d669),(0x45ca90,0x45cb46),(0x45cb50,0x45cb55)]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[];blobs[label]=[]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_text('\n'.join(disassemble(data,start))+'\n')
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','bytes':len(data),
                         'sha256':sha(data),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':sha(path.read_bytes())})
        callback=pe.get_data(0x155db0,24)
        assert struct.unpack('<6I',callback)==(0x537c9c,0,0,0x44d4c0,0x44d670,0)
        assert pe.get_string_at_rva(0x137c9c)==b'pshud'
        registration=pe.get_data(0x157bd8,12)
        assert struct.unpack('<3I',registration)==(0x538444,0x557928,32)
        assert pe.get_string_at_rva(0x138444)==b'HudItem'
        template=pe.get_data(0x157928,128)
        assert struct.unpack_from('<I',template,0x24)[0]==0x45ca90
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'pshud_callback_row_hex':callback.hex(),'huditem_registration_hex':registration.hex(),
            'huditem_template_128_bytes_sha256':sha(template)}
    assert blobs['original']==blobs['official_modern']
    assert result['binaries']['original']['huditem_template_128_bytes_sha256']==result['binaries']['official_modern']['huditem_template_128_bytes_sha256']
    prior=json.loads((ROOT/'analysis/evidence/audits/reference-asset-pairs.json').read_text())
    assets={row['normalized_path']:row for row in prior['assets']}
    selected={}
    archive=ROOT/prior['archives']['reference']['path'];assert sha(archive.read_bytes())==prior['archives']['reference']['sha256']
    for key in ('fedata/menus/pshudpos.mnu','gamedata/dashhud/edef.pos'):
        entry=assets[key]['reference'];raw=subprocess.check_output(['7z','x','-so',str(archive),entry['member']])
        assert sha(raw)==entry['sha256']
        selected[key]={'member':entry['member'],'sha256':sha(raw)}
        if key.endswith('.mnu'):
            ids=[int(x)for x in re.findall(r'^item=(\d+)\s*$',raw.decode('latin1'),re.M)]
            assert len(ids)==17 and set(ids)==set(range(17))
            selected[key]['HudItem_item_values_in_order']=ids
            selected[key]['final_package_status']=assets[key]['status']
        else:
            lines=[line for line in raw.decode('latin1').splitlines() if ':' in line];assert len(lines)==138
            picked=[]
            for profile in range(6):
                for slot in (6,7):
                    line=lines[profile*23+slot];name,coords=line.split(':',1)
                    assert name.endswith('TutorIcon' if slot==6 else 'ConeStats')
                    values=[float(x)for x in re.findall(r'-?\d*\.?\d+',coords)]
                    assert len(values)==4 and any(values)
                    picked.append({'profile':profile,'slot':slot,'name':name,'coordinates':values})
            selected[key]['named_records']=picked
    table=images['official_modern'].get_data(0x13eb20,0x900);records=[]
    for profile in range(6):
        for slot in (6,7):
            offset=profile*384+slot*16;data=table[offset:offset+16]
            assert any(data)
            records.append({'profile':profile,'slot':slot,'source_va':f'{0x53eb20+offset:08x}',
                            'raw_hex':data.hex(),'raw_binary32_values':struct.unpack('<4f',data)})
    result['reference_archive']={'path':str(archive.relative_to(ROOT)),'sha256':sha(archive.read_bytes()),'assets':selected}
    result['modern_embedded_records']={'table':'0053eb20','table_sha256':sha(table),'records':records,
        'meaning_limit':'Slot association reuses common POS order and verified initializer layout; raw pair ordering is not presented as final pixel coordinates.'}
    result['next_required_evidence']='Locate actual editor item-list construction/admission for slot6/7 and police-role variants, then trace draw/input flags; qualify active assets and runtime separately.'
    (ROOT/'analysis/evidence/audits/hud-editor-role-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: retained route/template bytes and nonzero named preset records; MP100-048 remains unverified')


if __name__=='__main__':main()
