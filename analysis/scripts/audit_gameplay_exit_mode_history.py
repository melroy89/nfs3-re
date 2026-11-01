"""Static shutdown mode-request suppression on the checked terminal route."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    inputs={k:((ROOT/p).read_bytes(),h,{'path':p})for k,(p,h,_)in SPECS.items()}
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        inputs[version]=(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']),eh,{'archive':rel,'archive_sha256':ah})
    result={'kind':'static-gameplay-exit-mode-request-history','binaries':{}};parts={}
    for label,(raw,digest,identity)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        old=label in ('original','1.4.0');end=0x4a3684 if old else(0x4a3680 if label=='1.5.0'else 0x4a3681)
        target=None
        if old:assert get(0x4a35d0,0x4a35d9).hex()=='535152565589e589c6'
        else:
            branch=get(0x4a35d0,0x4a35d9);assert branch[:5].hex()=='6085c00f84'
            target=0x4a35d9+struct.unpack('<i',branch[5:])[0]
            assert target==(0x4a365b if label=='1.5.0'else 0x4a3657)
        assert get(0x4a361d,0x4a362c).hex()=='b9e0010000bb80020000e8a41cf9ff'
        assert get(0x4a3829,0x4a383b).hex()=='833db4367d00017407b801000000eb0231c0'
        assert get(0x4a383b,0x4a3840).hex()=='e890fdffff'
        assert get(0x4c4d35,0x4c4d3a).hex()=='83f8057535'
        assert get(0x4c4d69,0x4c4d6f).hex()=='890db4367d00'
        assert get(0x4ce750,0x4ce757).hex()=='535152565589e5'
        assert get(0x4ce7f9,0x4ce7ff).hex()=='5d5e5a595bc3'
        spans=[('shutdown',0x4a35d0,end),('postrace_shutdown_input',0x4a3829,0x4a3840),
               ('accepted_action5',0x4c4d35,0x4c4d6f),('pause_action_mapping',0x44bcf6,0x44bd3b),
               ('exit_confirmation_callback',0x44b0f0,0x44b164),
               ('state_finalizer_preserves_ecx',0x4ce750,0x4ce7ff)]
        parts[label]={'setup':get(0x4a35d9,0x4a3652),'route':[get(a,b)for name,a,b in spans[1:]]}
        result['binaries'][label]={**identity,'sha256':digest,'zero_input_skip_target':f'{target:08x}'if target else None,
            'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    assert parts['1.4.0']['setup']==parts['1.5.0']['setup']
    assert all(p['route']==parts['original']['route']for p in parts.values())
    result['verified']=['140->150 adds input-zero branch skipping frontend mode/viewport setup; final retains conditional admission with changed cleanup target.',
        'Historical setup block itself is identical140/150;it contains frontend mode apply and640x480 viewport arguments.',
        'Retained shutdown caller passes0 when terminal state007d36b4 equals1,otherwise1.',
        'Retained accepted action5 arm publishes terminal state1 after its checked cleanup calls.',
        'Retained in-race action mapping returns5 for action10;retained confirmation callback can return action10.',
        'Skip targets still run cleanup;nonzero shutdown input retains setup path.']
    result['limits']=['Static selected path/branch evidence;no game,mode API,provider,instruction probe,compiler or Ghidra writes.',
        '640x480 literals feed viewport helper004352d0;actual mode request uses configured index0055fec8 and can differ.',
        'Existing mode-application report qualifies renderer acceptance/failure and descriptor selection;no OS resolution observed.',
        'Network result mediation004c5720 can alter the action before accepted-action5 route;full mediator not qualified here.',
        'Other exits,callee failures/context changes,callback admission and full cleanup lifetime remain unverified.',
        'MP150-035 has partial static support,not universal proof that no resolution change can occur on exit.']
    (ROOT/'analysis/evidence/audits/gameplay-exit-mode-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:four builds,140->150 zero-input shutdown gate;retained action/state/input chain and viewport request')


if __name__=='__main__':main()
