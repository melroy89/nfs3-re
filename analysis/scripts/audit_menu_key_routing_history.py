"""Date known keyboard-routing changes; distinguish unchanged selection algorithms."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-menu-key-routing-history','versions':{}};common=[]
    op,oh,_=SPECS['original'];raw=(ROOT/op).read_bytes();assert sha(raw)==oh;original=pefile.PE(data=raw)
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh;pe=pefile.PE(data=raw)
        get=lambda a,b:pe.get_data(a-0x400000,b-a);old=version=='1.3.1'
        spans=[('dispatcher',0x44a2d0,0x44a439 if old else 0x44a436),
               ('previous_selection',0x449f30,0x44a0b5),('next_selection',0x44a0c0,0x44a23b),
               ('lobby_key_handler',0x441700,0x4417ef),('named_action_scan',0x44a240,0x44a2c9 if old else 0x44a2c2)]
        common.append([get(a,b)for n,a,b in spans[1:4]])
        if old:assert get(0x44a2d0,0x44a439)==original.get_data(0x4a2d0,0x169)
        else:
            assert get(0x44a2e9,0x44a2f5).hex()=='6683fe0974266683fe1b7420'
            assert get(0x44a3a0,0x44a3a9).hex()=='e8d37b0a007532eb57'
            shift=get(0x4f1f78,0x4f1f9c)
            assert shift.hex()=='b010eb06b011eb02b01251520fb6c050ff15384753006685c00f9cc00fb6c085c05a59c3'
            assert any(i.address==0x534738 and i.name==b'GetAsyncKeyState'for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports)
            spans.append(('modifier_entry_shared_tail',0x4f1f78,0x4f1f9c))
            names={f'{a:08x}':pe.get_string_at_rva(a-0x400000).decode()for a in (0x53be28,0x53be2e,0x53be36,0x53be3e)}
            assert list(names.values())==['keyup','keydown','keyleft','keyright']
            result['named_tokens140']=names
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
             'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert common[0]==common[1]
    fp,fh,_=SPECS['official_modern'];fr=(ROOT/fp).read_bytes();assert sha(fr)==fh
    final=pefile.PE(data=fr);assert final.get_data(0xf1fcc,36)==shift
    result['final_modifier_counterpart']={'path':fp,'sha256':fh,'entry':'004f1fcc','matches140_entry004f1f78':True}
    result['original_correspondence']={'path':op,'sha256':oh,'dispatcher_matches131':True}
    result['verified']=['131 dispatcher matches supplied original;140 contains Tab/Escape chat-gate bypass and Shift-sensitive Tab dispatch.',
        '140 modifier helper tests GetAsyncKeyState sign and returns EAX plus final ZF;dispatcher branches on flags.',
        '140 named-arrow tokens/scanner connect to existing previous/next fallbacks.',
        'Complete previous/next selection routines and lobby handler are byte-identical131/140;routing changes do not imply a rewritten order algorithm.']
    result['limits']=['No interactive keyboard/chat test or complete entry-order producer/data/callback qualification.',
        'MP140-015 switching-order claim remains unresolved;do not conflate it with independently verified Tab/chat/arrow routing.',
        'Selected entry callback can consume keys before fallback;new routes are conditional.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/menu-key-routing-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 Tab/chat/named-arrow routing dated;previous/next bodies retained,order claim separate')


if __name__=='__main__':main()
