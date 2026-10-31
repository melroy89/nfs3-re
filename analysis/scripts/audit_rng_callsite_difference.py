"""Decoded direct-call census; no execution or whole-program reachability claim."""
import hashlib
import json
import re
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'decoded-direct-rng-callsite-comparison','binaries':{}}
    bodies=[];sites={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        assembly=subprocess.check_output(['objdump','-d','-Mintel',relative],cwd=ROOT,text=True)
        calls={f'{target:08x}':[] for target in (0x4e0d88,0x517784,0x51778c,0x5177ac,0x5177cc)}
        for match in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\bcall\s+0x([0-9a-f]+)\b',assembly,re.M):
            va,target=(int(x,16) for x in match.groups())
            if f'{target:08x}' not in calls:continue
            data=pe.get_data(va-0x400000,5)
            assert data[0]==0xe8 and (va+5+struct.unpack('<i',data[1:])[0])&0xffffffff==target
            calls[f'{target:08x}'].append(f'{va:08x}')
        sites[label]=set(calls['004e0d88'])
        body=pe.get_data(0x4e0d88-0x400000,0x4e0e2b-0x4e0d88)
        bodies.append(body)
        result['binaries'][label]={'path':relative,'sha256':expected,
            'disassembler_command':['objdump','-d','-Mintel',relative],
            'disassembly_sha256':hashlib.sha256(assembly.encode()).hexdigest(),
            'decoded_direct_calls':calls,
            'shared_generator_and_seed_span':{'start':'004e0d88','end_exclusive':'004e0e2b',
                'sha256':hashlib.sha256(body).hexdigest()}}
    assert bodies[0]==bodies[1]
    old,new=sites['original'],sites['official_modern']
    assert len(old)==194 and len(new)==191
    assert old-new=={'0041001a','0041016f','0041058f'} and not new-old
    assert result['binaries']['official_modern']['decoded_direct_calls']['005177cc']==[
        '0040fed7','0040feed','0040ffa1']
    modern_row=result['binaries']['official_modern']
    assert modern_row['decoded_direct_calls']['00517784']==['004a3e02']
    modern=pefile.PE(str(ROOT/modern_row['path']))
    startup=modern.get_data(0x4a3dfd-0x400000,10)
    assert startup==bytes.fromhex('e88ee90400e87d390700')
    clock=modern.get_data(0x4f2790-0x400000,11)
    assert clock==bytes.fromhex('5152ff15644653005a59c3')
    imports={i.address:(d.dll.decode(),i.name.decode())
             for d in modern.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
    assert imports[0x534664][1]=='timeGetTime'
    setter=modern.get_data(0x517784-0x400000,6)
    assert setter==bytes.fromhex('a3b4327a00c3')
    result['modern_music_lcg_startup_seed']={
        'startup_calls_start':'004a3dfd','calls_hex':startup.hex(),
        'clock_helper':'004f2790','clock_hex':clock.hex(),
        'clock_iat':'00534664','import_dll':imports[0x534664][0],
        'import_name':imports[0x534664][1],
        'setter':'00517784','setter_hex':setter.hex(),'state':'007a32b4',
        'flow':'Unmodified EAX clock return becomes stored 32-bit LCG seed.',
        'limit':'Observed startup path only; no run count, actual seed, entropy quality or indirect reseeding claim.'}
    result['shared_generator_callsite_delta']={'original_only':sorted(old-new),
        'modern_only':sorted(new-old),'same_address_sites_in_both':len(old&new)}
    result['limits']=['Linear disassembly can decode embedded data or miss alternate instruction boundaries.',
        'No indirect calls, runtime-generated calls, external callers or reachability proof.',
        'Equal sites/counts do not establish equal invocation frequency, seeding or shared-state trajectories.',
        'No target instructions executed; executable/Ghidra/raw exports unchanged.']
    (ROOT/'analysis/evidence/audits/rng-callsite-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: identical shared generator/seed; decoded direct sites 194 original, 191 Modern, three music-only removals')


if __name__=='__main__':main()
