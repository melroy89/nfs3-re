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
        for start,stop in [(0x426450,end),(0x426370,0x4263ef),(0x425060,0x4251ef),
                           (0x4240c0,0x424252),(0x4dffb0,0x4dfff3),(0x421570,0x4215b7)]:
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
    a,b=[p.get_data(0x240c0,402) for p in [old,new]]
    assert a[:0x41]==b[:0x41] and a[0xab:]==b[0xab:]
    for rva,size in [(0xdffb0,67),(0x21570,71)]:
        assert old.get_data(rva,size)==new.get_data(rva,size)
    assert old.get_data(0x24101,6).hex()=='8b15fc227900'
    assert new.get_data(0x24104,4).hex()=='85d2752a'
    assert new.get_data(0x2413c,4).hex()=='85d27524'
    result['fixed_descriptor_handler']={
        'complete_span':'004240c0..00424252','bytes':402,'changed_envelope':'00424101..0042416b',
        'unchanged_callees':['004dffb0..004dfff3','00421570..004215b7'],
        'contract_change':'Original overwrites EDX with007922fc before testing it; Modern tests incomingEDX first and uses EAX for that global.',
        'fixed_call_effect':'EDX1 selects descriptor+50=0 and first local offset component0; stores position+14..1c and matrix+2c..4c.',
        'fixed_destinations':['00661270','00661234..00661240','0066124c..00661270'],
        'destination_range_end':'exclusive',
        'projection_exclusion':'For descriptor661220 and forward copies, direct stores and both callees target this descriptor/stack, not5e1020/2c/30/38.',
        'limits':'Generic descriptor aliases, source-pointer validity, ambient x87/DF and visible camera behavior not verified.'}
    result['contract_changes']={'entry_inputs':'EAX=mode, EDX=slot; descriptor lookup precedes unsigned handler-range check in both.',
        'original':'Saves EBX/ECX/ESI/EBP; tail-dispatch stubs call selected handler; EDX=mode-1 on admitted handler entry.',
        'modern':'PUSHAD/POPAD; selected handler EAX=descriptor, EDX=0; optional fixed descriptor661220 update with EDX1 after handler.',
        'post_condition':'Only admitted modes1..24 reach post block; requires006fd3b0!=1 and006fd1cc!=0.',
        'retained':'Complete127-byte preparer and399-byte type8 handler identical.',
        'limits':'Callee input/output liveness and all shared-state lifetimes remain separate; complete projection capture not recovered.'}
    (ROOT/'analysis/evidence/audits/camera-dispatch-wrapper.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete paired wrappers;24 resolved routes; retained preparer/type8 body; new post-handler fixed-descriptor branch')


if __name__=='__main__':main()
