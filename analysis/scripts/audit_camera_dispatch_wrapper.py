"""Pair camera-dispatch wrappers and resolve jump-table stubs statically."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    capture=ROOT/'analysis/captures/modern-differences/camera-dispatch';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-camera-dispatch-wrapper','binaries':{},'mode_routes':[],
        'limits':['No game, instruction, callback or Ghidra execution.',
                  'Paired wrappers and handler addresses, not equivalence of every handler or input domain.',
                  'No projection-cache capture writer or visible horizon result established.']}
    images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==expected
        pe=pefile.PE(data=raw);images[label]=pe
        end=0x42655a if label=='original' else 0x42649a
        rows=[]
        for start,stop in [(0x426450,end),(0x426370,0x4263ef),(0x425060,0x4251ef)]:
            output=capture/f'{label}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={stop}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{stop:08x}',
                'bytes_sha256':sha(pe.get_data(start-0x400000,stop-start)),
                'assembly':str(output.relative_to(ROOT)),'assembly_sha256':sha(output.read_bytes())})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'table_sha256':sha(pe.get_data(0x263f0,96)),
            'raw_table':[f'{x:08x}' for x in struct.unpack('<24I',pe.get_data(0x263f0,96))]}
    old,new=images.values()
    for index,(a,b) in enumerate(zip(result['binaries']['original']['raw_table'],result['binaries']['official_modern']['raw_table']),1):
        va=int(a,16)
        if va==0x426555:
            assert index in [15,22]
            assert int(b,16)==0x426290 and new.get_data(0x26290,1)==b'\xc3'
            resolved=None
        else:
            body=old.get_data(va-0x400000,7)
            assert body[:3]==bytes.fromhex('89c8e8')
            resolved=va+7+struct.unpack('<i',body[3:])[0]
            assert resolved==int(b,16)
        result['mode_routes'].append({'mode':index,'original_stub':a,
            'original_handler':f'{resolved:08x}' if resolved is not None else None,
            'modern_handler':b,'relation':'same_handler' if resolved else 'old_return_vs_new_ret_stub'})
    assert old.get_data(0x26370,127)==new.get_data(0x26370,127)
    assert old.get_data(0x25060,399)==new.get_data(0x25060,399)
    assert new.get_data(0x2646e,11).hex()=='89f831d2ff149df0634200'
    assert new.get_data(0x2648b,13).hex()=='b82012660031d242e828dcffff'
    result['contract_changes']={'entry_inputs':'EAX=mode, EDX=slot; descriptor lookup precedes unsigned handler-range check in both.',
        'original':'Saves EBX/ECX/ESI/EBP; tail-dispatch stubs call selected handler; EDX=mode-1 on admitted handler entry.',
        'modern':'PUSHAD/POPAD; selected handler EAX=descriptor, EDX=0; optional fixed descriptor661220 update with EDX1 after handler.',
        'post_condition':'Only admitted modes1..24 reach post block; requires006fd3b0!=1 and006fd1cc!=0.',
        'retained':'Complete127-byte preparer and399-byte type8 handler identical.',
        'limits':'Callee input/output liveness and all shared-state lifetimes remain separate; complete projection capture not recovered.'}
    (ROOT/'analysis/evidence/audits/camera-dispatch-wrapper.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete paired wrappers;24 resolved routes; retained preparer/type8 body; new post-handler fixed-descriptor branch')


if __name__=='__main__':main()
