"""Date selected cooperative input-worker lifecycle to120->130; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.2.0':('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003'),
          '1.3.0':('93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad','deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146')}
    result={'kind':'static-input-worker-history','versions':{}};retained=[]
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a);old=version=='1.2.0'
        spans=[('worker_callback',0x42dc20 if old else 0x41d7c8,0x42dc40 if old else 0x41d7f7),('startup_witness',0x4b61f9,0x4b620a),('shutdown_complete',0x4b6250,0x4b6292 if old else 0x4b628d)]
        if old:assert get(0x4b6200,0x4b620a).hex()=='b820dc4200e896950200'
        else:
            assert get(0x4b6200,0x4b620a).hex()=='b8c8d74100e896950200'
            assert get(0x4b626f,0x4b6274).hex()=='e8ac79f7ff'
            spans.append(('cooperative_shutdown',0x42dc20,0x42dc3c))
        shared=[('collector',0x48f550,0x48f69a),('signal_entry',0x42dc40,0x42dc57),('create_event',0x4dfb00,0x4dfb14),('signal_event',0x4dfb20,0x4dfb3d),('wait_event',0x4dfb70,0x4dfb8f),('close_handle',0x4dfc00,0x4dfc0d),('forced_stop_prefix',0x4df870,0x4df894),('complete_library_thread_creator',0x4df7a0,0x4df866),('thread_entry_shim',0x4df730,0x4df73b)]
        spans+=shared;retained.append([get(a,b)for n,a,b in shared]+[get(0x554e34,0x554e4c)])
        imports={f'{i.address:08x}':i.name.decode()for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name and i.address in [0x534488,0x534494,0x5345e8,0x534608,0x534630]}
        assert imports=={'00534488':'CloseHandle','00534494':'CreateEventA','005345e8':'SetEvent','00534608':'TerminateThread','00534630':'WaitForMultipleObjectsEx'}
        all_imports={i.address:i.name.decode()for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert {a:all_imports[a]for a in [0x5344a4,0x5345bc,0x534604]}=={0x5344a4:'CreateThread',0x5345bc:'ResumeThread',0x534604:'SleepEx'}
        assert get(0x4df7c9,0x4df7de).hex()=='89e0506a04556830f74d00576a002eff15a4445300'
        assert get(0x4df7ed,0x4df7ef).hex()=='8903'
        assert get(0x4df804,0x4df80c).hex()=='512eff15bc455300'
        assert get(0x4df730,0x4df73b).hex()=='8b442404ffd031c0c20400'
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'imports':imports,'callback_table_sha256':sha(get(0x554e34,0x554e4c)),'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert retained[0]==retained[1]
    result['publication_contract']={'thread_creation_flags':4,'entry_shim':'004df730','callback_parameter':'Creator incomingEAX passed asCreateThread lpParameter;shim calls it without explicit arguments and discards result.',
        'order':['CreateThread suspended','nonnull handle stored descriptor+0 at004df7ed','other descriptor fields and priority setup','ResumeThread at004df805','SleepEx(0,1)request at004df810'],
        'imports':{'005344a4':'CreateThread','005345bc':'ResumeThread','00534604':'SleepEx'},
        'scope':'Ordinary successful creation publishes thread descriptor before resume;no explicit event-created readiness wait;full callback event publication and completion remain separate.'}
    result['limits']=['Selected120->130 lifecycle addition,not all multiplayer changes or causal attribution toMP130-003.',
        '130 worker41d7c8 differs from final41d7e4 address;12042dc20 is callback,130 same address is shutdown helper.',
        'CloseHandle is not a join;sentinel clear requires wake;no readiness/publication/refcount/concurrency success guaranteed.',
        'Event creation/wait/close/signal failures,all callers,descriptor reuse and complete collector dependencies remain unverified.',
        'Retained local collector/table does not prove identical device input,sampling,network or replay behavior.',
        'No target/API/instruction execution,compilation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/input-worker-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:120->130 cooperative input-worker lifecycle dated;collector/table/wrappers retained;multiplayer fix attribution unverified')


if __name__=='__main__':main()
