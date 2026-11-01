"""Static screenshot worker partial-local write fixed at140->150."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    inputs={}
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        inputs[version]=(subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']),eh,{'archive':rel,'archive_sha256':ah})
    path,digest,_=SPECS['official_modern'];inputs['final']=((ROOT/path).read_bytes(),digest,{'path':path})
    result={'kind':'static-screenshot-depth-local-history','binaries':{}};cores={}
    for label,(raw,digest,identity)in inputs.items():
        assert sha(raw)==digest;pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x400000,b-a)
        old=label=='1.4.0';end=0x4e3250 if old else 0x4e3248;body=get(0x4e3078,end)
        assert body[:9].hex()=='6089e581ec1c010000'
        write=0x4e3109 if old else 0x4e3107;read=0x4e3164 if old else 0x4e315e
        assert get(write,write+(4 if old else 3)).hex()==('668945f8'if old else'8945f8')
        assert get(read,read+3).hex()=='8b45f8'
        # Complete decoded entry-to-first-read evidence retains other local stores/branches.
        lines=disassemble(body,0x4e3078)
        local_lines=[line for line in lines if 'ebp-0x8]'in line]
        assert len([line for line in local_lines if 'mov    WORD PTR [ebp-0x8],ax'in line])==(1 if old else 0)
        assert len([line for line in local_lines if 'mov    DWORD PTR [ebp-0x8],eax'in line])==(0 if old else 1)
        cores[label]=get(0x4e3104,0x4e31b8)if not old else None
        result['binaries'][label]={**identity,'sha256':digest,'depth_local_write':f'{write:08x}',
            'depth_local_write_bytes':2 if old else 4,'first_dword_depth_read':f'{read:08x}',
            'local_access_disassembly':local_lines,'complete_worker':{'start':'004e3078','end_exclusive':f'{end:08x}',
            'bytes':len(body),'sha256':sha(body),'hex':body.hex(),'disassembly':lines}}
    assert cores['1.5.0']==cores['final']
    samples=[]
    for depth,upper in [(16,0),(16,1),(24,1),(32,1)]:
        old_value=(upper<<16)|depth;stride_old=(((old_value+7)&0xffffffff)>>3)*640&0xffffffff
        stride_new=(((depth+7)&0xffffffff)>>3)*640&0xffffffff
        samples.append({'depth':depth,'prior_upper_word':upper,'width':640,'old_local_dword':old_value,
            '140_source_stride':stride_old,'150_source_stride':stride_new,
            'evidence':'Derived scalar arithmetic;not original instruction execution or an observed stack value.'})
    result['derived_cases']=samples
    result['verified']=['140 writes WORD localEBP-8 then reads DWORD for source stride;no full-width local initialization in captured worker before that read.',
        '150 loads/stores DWORD depth and compares full DWORDs;selected depth/row-loop core is retained final.',
        '140 source address uses stride*(height-1-row)+capture_record+12;low-WORD copy-branch tests do not sanitize stride upper bits.',
        'This is a concrete140->150 partial-write/full-read correction consistent with reported screenshot crash fix.']
    result['limits']=['Static code/derived arithmetic only;no screenshot,thread,game,API,instruction probe,compiler or Ghidra writes.',
        'Actual prior upper local bits,valid buffer extents,source layout and crashes on any OS were not observed.',
        'No XP-specific stack allocation behaviour or exclusive operating-system cause established.',
        'Complete workers include unrelated relocation/literal/call differences;only selected width/stride mechanism is explained here.',
        'Other capture lifetime,dimension,allocation,encoding and concurrency issues retain existing report limits.',
        'MP150-034 receives partial static support,not proof of universal screenshot stability.']
    (ROOT/'analysis/evidence/audits/screenshot-depth-local-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140 WORD-write/DWORD-read depth local becomes full DWORD150;final core retained and stride effect derived')


if __name__=='__main__':main()
