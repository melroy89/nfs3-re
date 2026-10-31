"""Static render arena initialization/free counterparts; no allocations executed."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'render-scratch-arena-backing-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/render-arena';capture.mkdir(parents=True,exist_ok=True);consumers=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        spans=[(0x4bbd70,0x4bbd7f),(0x4bbde0,0x4bbe3a)]
        spans += [(0x4bbd80,0x4bbdbc),(0x4bbdc0,0x4bbdd9),(0x4b56e0,0x4b5700),(0x4b5700,0x4b570e)] if label=='original' else [(0x4bbd80,0x4bbda4),(0x4bbda4,0x4bbdb6),(0x4f1efc,0x4f1f10),(0x4f1f30,0x4f1f44)]
        rows=[]
        for start,end in spans:
            data=pe.get_data(start-0x400000,end-start);path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        if label=='original':assert pe.get_data(0xb56e5,11)==bytes.fromhex('ba00340c00c70000340c00')
        else:
            assert pe.get_data(0xbbd80,5)==bytes.fromhex('b800008000')
            assert pe.get_data(0xbbd99,10)==bytes.fromhex('c705043d7a009cff7f00')
            imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
            assert imports[0x534644]=='HeapAlloc' and imports[0x534648]=='HeapFree'
        consumer=pe.get_data(0x4bbde0-0x400000,90);consumers.append(consumer)
        assert pe.get_data(0x4bbe1a-0x400000,14)==bytes.fromhex('39f87e116848015400e8e851f4ff')
        message=pe.get_data(0x540148-0x400000,80).split(b'\0')[0]
        assert message==b'Render_GetTm() raM out of raN\n'
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'arena_failure_message':{'address':'00540148','value':message.decode('ascii')},
            'failure_branch':'004bbe1c signed JLE to success; otherwise PUSH message and CALL 00401010'}
    assert consumers[0]==consumers[1]
    result['identical_bump_consumer']={'start':'004bbde0','end_exclusive':'004bbe3a',
        'sha256':hashlib.sha256(consumers[0]).hexdigest(),
        'base':'0055fe34','cursor':'0055fe38','capacity':'007a3d04',
        'diagnostic_call':'004bbe23','target':'00401010',
        'limits':'Signed low-32-bit pointer-distance test; output pointer/cursor already changed before failure. Handler return/termination and all car requests unverified.'}
    result['contract']={'original_request_bytes':0xc3400,'modern_request_bytes':0x800000,'headroom_subtracted':100,'base_cell':'0055fe34','cursor_cell':'0055fe38','capacity_cell':'007a3d04','modern_heap_handle_cell':'009f3d40','limits':'No allocation success, full heap lifecycle, renderer concurrency or runtime capacity test.'}
    (ROOT/'analysis/evidence/audits/render-arena-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: arena backing sizes, moved free counterpart and HeapAlloc/HeapFree bindings')


if __name__=='__main__':main()
