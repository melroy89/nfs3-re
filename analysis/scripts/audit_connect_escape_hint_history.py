"""Trace131/140 Connecting notice to added two-line Esc hint; static only."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def texts(raw):
    first=struct.unpack_from('<I',raw)[0];assert first%4==0
    count=first//4;offsets=struct.unpack_from('<'+'I'*count,raw)
    assert offsets[0]==first and all(a<b for a,b in zip(offsets,offsets[1:]))
    rows=[]
    for i,a in enumerate(offsets):
        end=raw.index(0,a);assert end+1==(offsets[i+1]if i+1<count else len(raw))
        rows.append(raw[a:end])
    return rows


def main():
    result={'kind':'static-connect-escape-hint-history','versions':{},'languages':{}};join=[];new_helper=None
    for v,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{v}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        body=get(0x43fdd0,0x43fe44);join.append(body)
        assert get(0x43fdff,0x43fe04).hex()=='b80c000000'
        assert get(0x43fe09,0x43fe0e).hex()==('e8d24d0000'if v=='1.3.1'else'e892ffffff')
        spans=[('join_notice_caller',0x43fdd0,0x43fe44)]
        if v=='1.4.0':
            new_helper=get(0x43fda0,0x43fdcc)
            assert new_helper.hex()=='60bf9010660089fae8a31a0900abb80b000000e8981a0900ab31c05089c389c1b802000000e8b64c000061c3'
            spans.append(('two_line_helper',0x43fda0,0x43fdcc))
            for lang in ('eng','fre','ger','ita','spa','swe'):
                member=f'fedata/text/text.{lang}';data=subprocess.check_output(['7z','x','-so',str(archive),member]);rows=texts(data)
                assert len(rows)==1933
                if lang=='eng':assert rows[11]==b'Press escape to cancel'and rows[12]==b'Connecting...'
                result['languages'][lang]={'member':member,'sha256':sha(data),'entries':len(rows),
                    'hint_index':11,'hint_hex':rows[11].hex(),'hint_latin1_display':rows[11].decode('latin1'),
                    'notice_index':12,'notice_hex':rows[12].hex(),'notice_latin1_display':rows[12].decode('latin1')}
        result['versions'][v]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
             'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    # Only the direct-call displacement changes in the selected complete caller body.
    assert join[0][:0x39]==join[1][:0x39]and join[0][0x3e:]==join[1][0x3e:]
    path,pin,_=SPECS['official_modern'];raw=(ROOT/path).read_bytes();assert sha(raw)==pin
    pe=pefile.PE(data=raw);assert pe.get_data(0x3fda0,44)==new_helper
    result['final_helper']={'path':path,'exe_sha256':pin,'start':'0043fda0','bytes':44,'sha256':sha(new_helper),'matches140':True}
    result['verified']=['131 join notice requests text12 via444be0;140 replaces that call with43fda0,other selected caller bytes retained.',
        'New helper resolves incoming text then index11 into two pointers at00661090,and requests two-line notice through444a80 with zeroed auxiliary inputs.',
        '140 English entries12/11 decode Connecting... and Press escape to cancel;all six language files have complete bounded tables retained.',
        'Official final helper44-byte body matches140;this dates selected hint mechanism to131->140.']
    result['limits']=['No proof Escape actually cancels every connection phase,network state or transport;this is display-request evidence.',
        'No loaded text/font/codepage,rendered visibility or translation-quality validation;Latin1 is reversible display only.',
        '131 package has no matching text assets inspected here;not proof the hint string itself was newly created in140.',
        'Old bytes at43fda0 are not treated as the same helper entry;the paired caller supplies the historical linkage.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/connect-escape-hint-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 Connecting call gains two-line Esc hint;44-byte helper retained final')


if __name__=='__main__':main()
