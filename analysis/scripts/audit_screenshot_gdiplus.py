"""Static screenshot GDI+ lifecycle evidence; never loads the DLL."""
import hashlib,json,struct,subprocess,uuid
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    out={'kind':'screenshot-gdiplus-lifecycle','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/screenshot-gdiplus';capture.mkdir(parents=True,exist_ok=True)
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);spans=[]
        for start,end in [(0x4e2eb0,0x4e2fac),(0x4e2fac,0x4e2fec)]:
            data=pe.get_data(start-0x400000,end-start);path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            spans.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        row={'path':relative,'sha256':expected,'spans':spans,'pairing':'Modern implementation locations; original same-address bytes are not claimed counterparts.'}
        if label=='official_modern':
            entries=[]
            for address in range(0x54d750,0x54d788,8):
                name_ptr,initial=struct.unpack('<II',pe.get_data(address-0x400000,8))
                name=pe.get_data(name_ptr-0x400000,48).split(b'\0')[0].decode('ascii');assert initial==0
                entries.append({'name':name,'name_pointer':f'{name_ptr:08x}','function_slot':f'{address+4:08x}','initial_value':initial})
            assert len(entries)==7 and pe.get_data(0x14d788,4)==b'\0'*4
            row['exports']=entries
            row['library']=pe.get_data(0x14d67c,12).split(b'\0')[0].decode('ascii')
            row['startup_input_dwords']=list(struct.unpack('<4I',pe.get_data(0x14d790,16)))
            row['mime_names']={f'{a:08x}':pe.get_data(a-0x400000,n).decode('utf-16le').rstrip('\0') for a,n in [(0x54d720,20),(0x54d734,22)]}
            row['initial_encoder_guids']={f'{a:08x}':str(uuid.UUID(bytes_le=pe.get_data(a-0x400000,16))) for a in (0x54d7a0,0x54d7b0)}
            assert list(row['mime_names'].values())==['image/png','image/jpeg']
            assert row['startup_input_dwords']==[1,0,0,1]
            assert pe.get_data(0xe2eb0,7)==bytes.fromhex('833d84277a0000')
            assert pe.get_data(0xe2f84,3)==bytes.fromhex('83c44c')
            assert pe.get_data(0xe2f87,3)==bytes.fromhex('ff4df8')
            row['imports']={f'{i.address:08x}':i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address in (0x53458c,0x534558,0x5344dc)}
        out['binaries'][label]=row
    out['limits']=['No DLL loading, GDI+ calls, screenshots or target instruction execution.','Complete Modern initializer/shutdown bodies; original screenshot counterpart is documented separately.','Encoder data validity, concurrency and actual save outcomes untested.']
    (ROOT/'analysis/evidence/audits/screenshot-gdiplus.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: complete lifecycle bodies, seven exports, MIME names and initialized GUIDs')


if __name__=='__main__':main()
