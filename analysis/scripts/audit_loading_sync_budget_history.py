"""Static loading timestamp placement and elapsed-budget subtraction history."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    inputs={}
    for v,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{v}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        inputs[v]=(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']),eh,{'archive':rel,'archive_sha256':ah})
    path,digest,_=SPECS['official_modern'];inputs['final']=((ROOT/path).read_bytes(),digest,{'path':path})
    specs={'1.4.0':{'caller':(0x4a3400,0x4a3498),'refresh':(0x4a3568,0x4a35a3),'clock':(0x4b56d0,0x4b56e0),'clock_operand':0x4b56d8,'network_call':0x4a347c,'refresh_call':0x4a3493},
        '1.5.0':{'caller':(0x4a3400,0x4a349d),'refresh':(0x4a3578,0x4a35c5),'clock':(0x4f1ea0,0x4f1eab),'clock_operand':0x4f1ea4,'network_call':0x4a3481,'refresh_call':0x4a3498,'baseline':(0x4a356c,0x4a3577),'baseline_call':0x4a345e},
        'final':{'caller':(0x4a33f0,0x4a3482),'refresh':(0x4a3558,0x4a35a5),'clock':(0x4f2790,0x4f279b),'clock_operand':0x4f2794,'network_call':0x4a346b,'refresh_call':0x4a347d,'baseline':(0x4a354c,0x4a3557),'baseline_call':0x4a3417}}
    result={'kind':'static-loading-sync-budget-history','binaries':{}};parts={}
    for label,(raw,digest,identity)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a);s=specs[label]
        def target(site):
            data=get(site,site+5);assert data[0]==0xe8
            return site+5+struct.unpack('<i',data[1:])[0]
        assert target(s['network_call'])==0x477f60
        assert target(s['refresh_call'])==s['refresh'][0]
        if 'baseline'in s:
            assert target(s['baseline_call'])==s['baseline'][0]
            assert s['baseline_call']<s['network_call']<s['refresh_call']
        iat=struct.unpack('<I',get(s['clock_operand'],s['clock_operand']+4))[0]
        imported=next((d.dll.decode(),i.name.decode())for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address==iat)
        assert imported[1]==('timeGetTime'if label=='final'else'GetTickCount')
        spans=[(name,*s[name])for name in ('caller','refresh','clock')]
        if 'baseline'in s:spans.append(('baseline',*s['baseline']))
        spans.append(('network_setup_wrapper',0x477f60,0x477fc2))
        parts[label]={name:get(a,b)for name,a,b in spans}
        result['binaries'][label]={**identity,'sha256':digest,'network_call':f'{s["network_call"]:08x}',
            'refresh_call':f'{s["refresh_call"]:08x}','baseline_call':f'{s["baseline_call"]:08x}'if'baseline_call'in s else None,
            'clock_import':{'dll':imported[0],'name':imported[1],'iat':f'{iat:08x}'},
            'captures':[{'name':name,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                         'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for name,a,b in spans]}
    assert parts['1.5.0']['refresh'][7:]==parts['final']['refresh'][7:]
    assert parts['1.4.0']['network_setup_wrapper']==parts['1.5.0']['network_setup_wrapper']==parts['final']['network_setup_wrapper']
    result['ordinary_derived_cases']=[{'seconds':s,'elapsed_ms':e,'140_budget_ms':max(0,min(10,s))*1000,
        '150_budget_ms':max(0,min(10000,s*1000-e)),
        'limit':'Ordinary non-wrapping scalar example;not an executed instruction or measured network interval.'}for s,e in [(5,2000),(5,6000),(20,15000)]]
    result['verified']=['140 starts full clamped splash budget after setup;150 inserts an earlier baseline and subtracts elapsed before progress refresh.',
        '150 baseline precedes artwork/network preparation;final baseline is even earlier in its repacked caller.',
        'Historical wrappers call GetTickCount;final calls timeGetTime;all are millisecond source interfaces,not identical clock state.',
        '150 refresh suffix matches final after its clock call;140 clamps seconds before multiplication,150/final clamp signed wrapped milliseconds after subtraction.',
        'Selected98-byte network setup wrapper is retained across these three builds;its transitive network duration is not measured.']
    result['limits']=['No game,clock/API,network,instruction probe,compilation or Ghidra writes.',
        'Elapsed interval includes artwork/other preparation,not exclusively preliminary network synchronization.',
        'Existing setup audit qualifies wrapper session/playback/abort admission;called network routines are not fully compared here.',
        'Original supplied EXE fixed-argument route is documented in the paired loading-timing report;these new helper addresses are not assigned original counterparts.',
        'Clock wrap,low32 IMUL/SUB and signed clamp must be retained;ordinary examples do not cover arbitrary INI values.',
        'MP150-031 has partial static support;visible progress,synchronization completion and exact wall-clock timing remain unverified.']
    (ROOT/'analysis/evidence/audits/loading-sync-budget-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140->150 elapsed budget subtraction surrounds retained setup;final formula and clock-source distinction verified')


if __name__=='__main__':main()
