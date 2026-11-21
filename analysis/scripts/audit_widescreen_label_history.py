"""Check140 Field-of-View label against retained131 setting bindings."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_connect_escape_hint_history import texts
SYMBOLS={1283:'kMenuPSGRAPHWideScre001',1504:'kMenuGRAPHICSWideScre001',1505:'kMenuGRAPHICSwidescre001'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-widescreen-label-history','versions':{}};bindings=[]
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh;pe=pefile.PE(data=raw)
        descriptor=pe.get_data(0x1567a8,20);assert struct.unpack('<5I',descriptor)==(0x538008,0x5561be,0,0,0x6fbc4c)
        choices=pe.get_data(0x1561be,6);assert struct.unpack('<3H',choices)==(229,228,0)
        assert pe.get_string_at_rva(0x138008)==b'widescreen'
        symbols=[]
        for ident,name in SYMBOLS.items():
            ptr=struct.unpack('<I',pe.get_data(0x161c44+4*ident,4))[0]
            assert pe.get_string_at_rva(ptr-0x400000).decode()==name
            symbols.append({'index':ident,'symbol':name,'pointer':f'{ptr:08x}'})
        menu_rows=[]
        for name in ('advgrph.mnu','psgraph.mnu'):
            member='fedata/menus/'+name;data=subprocess.check_output(['7z','x','-so',str(archive),member])
            selected=[line for line in data.decode('latin1').splitlines()if 'widescre' in line.lower()]
            assert 'listname=widescreen'in selected
            menu_rows.append({'member':member,'sha256':sha(data),'selected_fields':selected})
        bindings.append((descriptor,choices,symbols,[r['selected_fields']for r in menu_rows]))
        row={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'descriptor_at_005567a8':descriptor.hex(),
             'choice_words_at_005561be':[229,228,0],'symbol_table_base':'00561c44','symbols':symbols,'menus':menu_rows}
        if version=='1.4.0':
            member='fedata/text/text.eng';data=subprocess.check_output(['7z','x','-so',str(archive),member]);strings=texts(data)
            assert strings[1283]==strings[1504]==b'2:1 Field of View'
            assert strings[1505]==b'2:1 Field of View is...'
            row['english']={'member':member,'sha256':sha(data),'entries':len(strings),
                            'labels':{str(i):strings[i].decode('latin1')for i in (*SYMBOLS,229,228)}}
        result['versions'][version]=row
    assert bindings[0]==bindings[1]
    result['verified']=['131/140 selected menu codelink/text/listname fields,symbol bindings,20-byte descriptor and terminated choice list match.',
        'Both retain keywidescreen,storage006fbc4c,and choice IDs229/228;140 English labels name2:1 Field of View.',
        'This supportsMP140-033 at displayed-label/binding scope,not a new field or changed choices.']
    result['limits']=['No131 English text baseline inspected here;prior Wide Screen wording and exact text-change boundary not proved.',
        'No complete rendering/input consumer comparison;retained descriptor is not proof of unchanged camera semantics.',
        'No loaded-language/font,visible menu,all locales or arbitrary selector-domain validation.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/widescreen-label-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140 Field-of-View labels bind retained131 setting/storage/choices;old wording baseline remains open')


if __name__=='__main__':main()
