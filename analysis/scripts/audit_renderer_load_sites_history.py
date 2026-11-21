"""Compare110/120 decoded direct renderer load/switch call sites; static only."""
import hashlib,json,re,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.1.0':('31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72'),
          '1.2.0':('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003')}
    targets=[0x4f8390,0x4f87e0,0x4f87a0,0x517170,0x517370];result={'kind':'static-renderer-load-sites-history','versions':{}};snapshots=[]
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a);calls={f'{a:08x}':[]for a in targets};scanned=[]
        for s in p.sections:
            if not s.Characteristics&0x20000000 or not s.PointerToRawData:continue
            scanned.append({'rva':f'{s.VirtualAddress:08x}','bytes':s.SizeOfRawData,'sha256':sha(s.get_data())})
            for line in disassemble(s.get_data(),0x400000+s.VirtualAddress):
                m=re.search(r'^([0-9a-f]+):.*\bcall\s+0x([0-9a-f]+)$',line)
                if m and int(m[2],16)in targets:calls[f'{int(m[2],16):08x}'].append(f'{int(m[1],16):08x}')
        expected={'004f8390':['004f8807','004f8827'],'004f87e0':['004b59f9','004b5a32','004b5ad6','004b5c00','004b5cc7','004b5d6f'],'004f87a0':['004f8820'],'00517170':['004f87bd'],'00517370':['004f87c4']}if version=='1.1.0'else{'004f8390':['004b58aa'],'004f87e0':[],'004f87a0':[],'00517170':[],'00517370':[]}
        assert calls==expected
        assert get(0x4f8390,0x4f83a5).hex()=='535152565581ec0002000089c6502eff158c455300'
        assert any(i.address==0x53458c and i.name==b'LoadLibraryA'for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports)
        spans=[('loader_entry',0x4f8390,0x4f83b4),('old_switch_envelope',0x4f87e0,0x4f882e),('old_cleanup',0x4f87a0,0x4f87d9)]
        if version=='1.2.0':
            assert get(0x4f87a0,0x4f87d9)==b'\x90'*57 and get(0x4f87e0,0x4f882e)==b'\x90'*78
            spans.append(('new_load_site',0x4b58a5,0x4b58af))
        snaps=[get(a,b)for a,b in [(0x517170,0x517362),(0x517370,0x51755e)]];snapshots.append(snaps)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'linear_sweep_sections':scanned,'decoded_direct_calls':calls,'retained_snapshot_hashes':[sha(x)for x in snaps],'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert snapshots[0]==snapshots[1]
    result['limits']=['Linear sweep of executable file-backed sections is not a complete control-flow graph or indirect/tail-call/pointer-use inventory.',
        'One decoded direct load site does not imply one runtime invocation;low-level entry still callsLoadLibraryA without local handle guard.',
        'Old snapshot bodies remain byte-identical120 despite disappearing selected direct callers;not proof globally dead or already removed.',
        'Handle reference ownership,all cleanup/recovery and provider initialization frequency remain unverified.',
        'No target/API/instruction execution,compilation or executable/Ghidra changes.']
    (ROOT/'analysis/evidence/audits/renderer-load-sites-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:110 six switch sites ->120 one direct loader site;old cleanup/switch NOPs,snapshot bodies retained;runtime count unverified')


if __name__=='__main__':main()
