"""Date removed race-entry termination guard120->130; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble,intervals


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.2.0':('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003'),
          '1.3.0':('93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad','deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146')}
    result={'kind':'static-race-entry-termination-history','versions':{}};prefixes=[];retained=[]
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a)
        prefix=get(0x4c4e40,0x4c4e75);prefixes.append(prefix)
        if version=='1.2.0':assert get(0x4c4e63,0x4c4e75).hex()=='8b0df8fd5e008955f885c97f05e808dc0200'
        else:assert get(0x4c4e63,0x4c4e75)==bytes.fromhex('8955f8eb0d')+b'\x90'*13
        spans=[('race_entry_prefix',0x4c4e40,0x4c4e75),('registered_counter_callback',0x42dc60,0x42dcaf),('counter_registration_initializer',0x42dcb0,0x42dcf7),('termination_entry',0x4f2a7d,0x4f2a84),('complete_callback_registrar',0x48ee30,0x48ee83)]
        assert get(0x48ee30,0x48ee36).hex()=='5351525589e5'
        assert get(0x48ee7e,0x48ee83).hex()=='5d5a595bc3'
        retained.append([get(a,b)for n,a,b in spans[1:]])
        other_spans=[(0x495230,0x4955fb),(0x4a33d0,0x4a35cb)]
        retained[-1]+=[get(a,b)for a,b in other_spans]
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans],'paired_loading_spans':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b))}for a,b in other_spans]}
    assert retained[0]==retained[1]
    changes=intervals(*prefixes,0x4c4e40);assert sum(len(d['reference_hex'])//2 for d in changes)==17
    result['changed_intervals']=changes
    result['verified']=['120 race entry calls004f2a7d unless signed005efdf8>0;130 removes test/read/call and jumps to same continuation004c4e75.',
        'StoreEDX to local-8 retained but moved earlier;earlier read005efdf8 plus10000 retained.',
        'Callback0042dc60 increments005efdf8 when selected bit0 gate005efdf4 clear;initializer0042dcb0 registers callback via0048ee30.',
        'Selected counter/termination bodies and loading spans byte-identical across pair.']
    result['registrar_contract']={'entry':'0048ee30','end_exclusive':'0048ee83','bytes':83,'input':'EAX callback pointer','preserved':['EBX','ECX','EDX','EBP','ESI untouched','EDI untouched'],
        'local_calls':0,'registry':'0079c130,8 DWORD pointers','policy':'Search duplicate callback or first zero slot;only writes callback when absent and a zero slot exists;no capacity error is tested by initializer.',
        'initializer_consequence':'On its first-registration branch,EDX initialized0 survives registrar,so subsequent005efdf8 store is a real zero reset;already-initialized branch skips that reset.',
        'limits':'No callback execution before race entry guaranteed;full registry or deferred callback scenarios are hypothetical,not observed failure causes.'}
    result['limits']=['Candidate mechanism forMP130-002,not independently reproduced failure/root cause or exhaustive release attribution.',
        'Counter meaning,callback timing,all aliases/writers,wrap and actual nonpositive race-entry state remain unverified.',
        'Registrar preservation now verified;actual callback admission/timing,all aliases/writers and zero state at race entry remain unobserved.',
        'Existing terminal-chain report establishesExitProcess route separately;runtime callback/cleanup completion unobserved.',
        'Equal selected loading spans do not prove entire loading flow unchanged.',
        'No target/API/instruction execution,compilation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/race-entry-termination-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:120->130 removes signed nonpositive-counter race-entry termination guard;17 changed bytes;runtime cause unverified')


if __name__=='__main__':main()
