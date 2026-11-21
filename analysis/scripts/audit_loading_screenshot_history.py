"""Pin loading-progress screenshot service addition131->140; static only."""
import hashlib,json,re,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-loading-screenshot-history','versions':{}}
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);old=version=='1.3.1';get=lambda a,b:p.get_data(a-0x400000,b-a)
        spans=[('progress_complete',0x495230,0x4955fb if old else 0x4955c6),
               ('processor',0x4c4480,0x4c4485 if old else 0x4c44b8)]
        if not old:spans.append(('early_exit_stub',0x495229,0x495230))
        captures=[]
        for name,start,end in spans:
            body=get(start,end);asm=disassemble(body,start)
            captures.append({'name':name,'start':f'{start:08x}','end_exclusive':f'{end:08x}','hex':body.hex(),'sha256':sha(body),'disassembly':asm})
        assert bytes.fromhex(captures[0]['hex']).endswith(bytes.fromhex('c20400'))
        direct_calls=[]
        for line in captures[0]['disassembly']:
            m=re.search(r'^([0-9a-f]+):.*\bcall\s+0x([0-9a-f]+)$',line)
            if m:direct_calls.append({'instruction':f'{int(m[1],16):08x}','target':f'{int(m[2],16):08x}'})
        if old:
            assert get(0x4c4480,0x4c4485).hex()=='5589e55dc3'
            assert not any(c['target']in ['004c4480','004c4490']for c in direct_calls)
        else:
            assert {'instruction':'0049526d','target':'004c4480'}in direct_calls
            assert get(0x495242,0x49524b).hex()=='833d88f279000074de'
            assert get(0x495250,0x495259).hex()=='833d8ce855000075d0'
            assert get(0x495264,0x495268).hex()=='85c078c1'
            assert get(0x4c4480,0x4c448a).hex()=='833d78277a00007501c3'
            assert get(0x4c44ac,0x4c44b8).hex()=='c70578277a000000000061c3'
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'captures':captures,'progress_direct_calls':direct_calls}
    result['findings']=[
        '131 progress body contains no decoded direct call to screenshot capture004c4490 or placeholder004c4480;indirect/transitive absence not asserted.',
        '140 progress continuation calls screenshot request processor004c4480 at0049526d,after00434b20 and before current progress drawing.',
        '140 active-state,abort-latch and signed estimator-result gates can bypass this service call.',
        'Processor returns immediately when request007a2778 is0;otherwise normalizes/prepares/launches,and clears request on ordinary completion including failed preparation/launch.']
    result['limits']=[
        'No actual loading image,screenshot,keyboard delivery,worker completion or file success observed.',
        'Service precedes current progress drawing;fresh/current-frame identity is not established.',
        'No whole-program original absence or complete callback/input cadence established.',
        'No target/API/instruction execution or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/loading-screenshot-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 loading-progress screenshot service addition pinned;frame/output behavior unverified')


if __name__=='__main__':main()
