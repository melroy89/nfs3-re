"""Classify original renderer snapshot routines replaced by Modern NOPs."""
import hashlib,json,re,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/renderer-snapshots';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'removed-renderer-context-snapshot-bodies','binaries':{}}
    binding=json.loads((ROOT/'analysis/evidence/audits/original-modern-thrash-loader.json').read_text())
    slots=[int(row['slot_va'],16) for row in binding['original_explicit_bindings']]
    assert len(slots)==34 and len(set(slots))==34
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        for start,end in [(0x517170,0x517362),(0x517370,0x51755e),(0x4f87a0,0x4f87d9)]:
            data=pe.get_data(start-0x400000,end-start)
            path=capture/f'{label}-{start:08x}.asm';asm=subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT,text=True);path.write_text(asm)
            if label=='official_modern':assert set(data)=={0x90}
            elif start in (0x517170,0x517370):
                addresses={int(v,16) for v in re.findall(r'\[eax\*4\+0x([0-9a-f]+)\]',asm)}
                assert addresses==set(range(0x564a70,0x564afc,4))
                assert all(struct.pack('<I',slot) in data for slot in slots)
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','length':len(data),'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    result['contract']={'slot_count':8,'record_stride':140,'record_base':'00564a70','module_handle':'00564a6c','active_index':'00564a68','callback_slots':[f'{v:08x}' for v in slots],'index_input':'EAX signed; outside0..7 becomes0','restore':'00517170','save':'00517370','caller':'Original004f87a0 cleanup calls restore0 then savepreviousindex'}
    result['limits']=['Static complete bodies; no renderer or target execution.','Removed same-address bodies do not establish removal of rendering support.','All snapshot data writers, initialization and runtime multi-driver switching remain unresolved.']
    (ROOT/'analysis/evidence/audits/renderer-context-snapshots.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original35-DWORD snapshots,34known slots, and Modern NOP replacements')


if __name__=='__main__':main()
