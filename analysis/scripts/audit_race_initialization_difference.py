"""Static race initialization call-sequence and removed-stub comparison."""
import hashlib,json,re,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    out={'kind':'race-initialization-sequence-comparison','binaries':{}};images=[]
    capture=ROOT/'analysis/captures/modern-differences/race-initialization';capture.mkdir(parents=True,exist_ok=True)
    leaves=[0x401220,0x40c150,0x408ad0,0x404c40,0x401230,0x40c140,0x408ae0,0x404650,0x405fb0]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images.append(pe);rows=[]
        spans=[(0x4c45f0,0x4c4733 if label=='original' else 0x4c471a),(0x4c4740,0x4c481d)]
        spans += [(0x4bc530,0x4bc559)]
        if label=='original':spans += [(0x4bc8b0,0x4bc8dd),(0x47b390,0x47b39a),(0x4dcd10,0x4dcd1a),(0x434ae0,0x434ae5),(0x421480,0x421485)]
        spans += [(0x4c7130,0x4c7149),(0x4dbbc0,0x4dbbd6),(0x4cb6f0,0x4cb723),(0x47b350,0x47b37a),(0x4dcdf0,0x4dd1ed),(0x4e070c,0x4e0716)]
        if label=='original':spans += [(a,a+5) for a in leaves]+[(0x404660,0x40466a)]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start);path=capture/f'{label}-{start:08x}.asm'
            asm=subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True);path.write_text(asm)
            calls=[{'site':f'{int(a,16):08x}','target':f'{int(b,16):08x}'} for a,b in re.findall(r'^\s*([0-9a-f]+):.*\bcall\s+0x([0-9a-f]+)',asm,re.M)]
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT)),'direct_calls':calls})
        out['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=images
    assert all(old.get_data(a-0x400000,5)==bytes.fromhex('5589e55dc3') for a in leaves)
    wrapper=old.get_data(0x4663,5);assert wrapper[0]==0xe8
    assert 0x404668+int.from_bytes(wrapper[1:],'little',signed=True)==0x404650
    assert old.get_data(0xc45f0,0x5b)==new.get_data(0xc45f0,0x5b)
    def targets(label,index):return [int(row['target'],16) for row in out['binaries'][label]['spans'][index]['direct_calls']]
    removed_init={0x404660,0x401220,0x40c150,0x408ad0,0x404c40}
    assert [v for v in targets('original',0) if v not in removed_init]==targets('official_modern',0)
    removed_reset={0x401230,0x40c140,0x408ae0,0x404650,0x405fb0}
    added_reset={0x4c7130,0x4dbbc0,0x4cb6f0,0x47b350,0x4dcdf0}
    assert [0x4bc530 if v==0x4bc8b0 else v for v in targets('original',1) if v not in removed_reset]==[v for v in targets('official_modern',1) if v not in added_reset]
    out['sequence_delta']={'removed_initialization_calls':[f'{v:08x}' for v in sorted(removed_init)],'removed_reset_calls':[f'{v:08x}' for v in sorted(removed_reset)],'added_reset_calls':[f'{v:08x}' for v in sorted(added_reset)],'changed_reset_target':['004bc8b0','004bc530'],'retained_call_order_verified':True}
    retained=[]
    for start,end in [(0x4c7130,0x4c7149),(0x4dbbc0,0x4dbbd6),(0x4cb6f0,0x4cb723),(0x47b350,0x47b37a),(0x4dcdf0,0x4dd1ed)]:
        a,b=[pe.get_data(start-0x400000,end-start) for pe in images];assert a==b
        retained.append({'entry':f'{start:08x}','end_exclusive':f'{end:08x}','length':end-start,'sha256':hashlib.sha256(a).hexdigest()})
    out['added_reset_calls_target_retained_original_bodies']=retained
    common_a,common_b=[pe.get_data(0xbc530,0x29) for pe in images];assert common_a==common_b
    out['bypassed_original_wrapper']={'entry':'004bc8b0','end_exclusive':'004bc8dd','direct_targets':['00434ae0','00421480','004c7130','004dbbc0','004cb6f0','0047b390','004dcd10','004bc530'],'modern_direct_final_target':'004bc530','shared_final_body_bytes':41,'shared_final_body_sha256':hashlib.sha256(common_a).hexdigest(),'interpretation':'Three calls are hoisted unchanged; environment/weather targets differ; two original wrapper-prefix calls are bypassed on this route.'}
    observed=next(row for row in out['binaries']['original']['spans'] if row['start']=='004bc8b0')['direct_calls']
    assert [row['target'] for row in observed]==out['bypassed_original_wrapper']['direct_targets']
    for entry,target in [(0x47b390,0x47b350),(0x4dcd10,0x4dcdf0)]:
        data=old.get_data(entry-0x400000,10)
        assert data[:3]==bytes.fromhex('5589e5') and data[-2:]==bytes.fromhex('5dc3') and data[3]==0xe8
        assert entry+8+int.from_bytes(data[4:8],'little',signed=True)==target
    assert all(old.get_data(v-0x400000,5)==bytes.fromhex('5589e55dc3') for v in (0x434ae0,0x421480))
    flattened=[]
    mapping={0x47b390:0x47b350,0x4dcd10:0x4dcdf0}
    for target in targets('original',1):
        if target in removed_reset:continue
        if target==0x4bc8b0:
            flattened.extend(mapping.get(int(v,16),int(v,16)) for v in out['bypassed_original_wrapper']['direct_targets'] if v not in ('00434ae0','00421480'))
        else:flattened.append(target)
    assert flattened==targets('official_modern',1)
    masked=[]
    for label,pe in zip(('original','official_modern'),images):
        data=bytearray(pe.get_data(0xc4740,0xdd))
        for call in out['binaries'][label]['spans'][1]['direct_calls']:
            offset=int(call['site'],16)-0x4c4740;data[offset+1:offset+5]=b'\0'*4
        masked.append(data)
    assert masked[0]==masked[1]
    out['flattened_reset_comparison']={'substantive_direct_target_sequence':[f'{v:08x}' for v in flattened],'same_after_original_stub_removal_and_wrapper_expansion':True,'non_call_displacement_bytes_identical':True,'wrapper_bypasses':{'0047b390':'0047b350','004dcd10':'004dcdf0'},'additional_original_noop_leaves':['00434ae0','00421480'],'limits':'Local logical call-tree comparison; not transitive game-state, stack-memory, timing or runtime equivalence.'}
    out['removed_stub_entries']=[f'{v:08x}' for v in leaves]
    out['wrapper_to_stub']={'wrapper':'00404660','target':'00404650'}
    out['limits']=['No race, initializer or target execution.','Direct-call sequences do not establish full effects or correspondence of changed callees.','Removed stub bodies are original evidence, not inferred from Modern reuse of their addresses.']
    (ROOT/'analysis/evidence/audits/race-initialization-difference.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: complete paired race setup bodies, exact call lists and nine original no-op leaves')


if __name__=='__main__':main()
