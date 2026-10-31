"""Static raster session registration removal and inactive shutdown branch."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

SPANS=[(0x524650,0x524693),(0x5246a0,0x5247ab),(0x524620,0x524635),
       (0x524640,0x524650),(0x5247ab,0x5247b1),(0x5247c0,0x524814),(0x509940,0x5099fd)]


def main():
    result={'kind':'raster-session-cleanup-registration','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/raster-session'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in SPANS:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    assert old[0][:11]==new[0][:11] and old[0][17:]==new[0][17:]
    assert old[0][11:17]==bytes.fromhex('0f844a010000')
    assert new[0][11:17]==bytes.fromhex('743290909090')
    assert old[4]==bytes.fromhex('0f84defeffff') and new[4]==b'\x90'*6
    assert old[1][:0xad]==new[1][:0xad] and old[1][0xe7:]==new[1][0xe7:]
    assert new[1][0xad:0xbb]==bytes.fromhex('31c0b001a2f0af56005e5a595bc3')
    assert new[1][0xbb:0xe7]==b'\x90'*44
    for i in (2,3):assert new[i]==b'\x90'*len(new[i])
    assert new[5]==b'\x90'*84
    result['removed_dimension_publisher']={'original_entry':'005247c0','end_exclusive':'00524814',
        'bytes':84,'hex':old[5].hex(),'sha256':hashlib.sha256(old[5]).hexdigest(),
        'inputs':{'EAX':'width','EDX':'height','EBX':'depth'},
        'zero_defaults':{'width':640,'height':480,'depth':16},
        'outputs':['00564384 width','00564388 height','0056438c depth',
                   '005643a4 width minus0056439c, wrap32','005643a8 height minus005643a0, wrap32'],
        'conditional_tail_target':'00509940 when00564364 is0',
        'limit':'Local original machine contract; tail target, all callers and Modern replacement ownership not fully qualified.'}
    assert old[6]==new[6]
    result['retained_row_table_tail_target']={'start':'00509940','end_exclusive':'005099fd',
        'bytes':189,'hex':old[6].hex(),'sha256':hashlib.sha256(old[6]).hexdigest(),
        'count_cell':'0056837c','buffer_cell':'00568380','end_pointer_cell':'00a0a810',
        'ordinary_header_writes':['[buffer]=count-2','[buffer+4]=0','00a0a810=buffer+4*count'],
        'allocation_target':'004e1620','minimum_count_diagnostic':204,
        'limit':'Identical local row-table setup; count/storage/allocator prerequisites, diagnostic nonreturn and concurrency not established.'}
    row_strings={}
    for label,(relative,expected,_) in SPECS.items():
        image=pefile.PE(str(ROOT/relative))
        row_strings[label]={f'{va:08x}':image.get_string_at_rva(va-0x400000).decode('latin1')
            for va in (0x54f718,0x54f724,0x54f72c,0x54f770)}
    assert row_strings['original']==row_strings['official_modern']
    result['retained_row_table_tail_target']['strings']=row_strings
    result['limits']=['Static branch/registration witnesses only; no renderer or process-exit execution.',
        'Cleanup registration helper semantics, replacement ownership and callback lifetime remain unverified.']
    (ROOT/'analysis/evidence/audits/raster-session-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 67/267-byte session envelopes, removed callbacks and original shared shutdown tail')


if __name__=='__main__':main()
