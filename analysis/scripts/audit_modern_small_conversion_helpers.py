"""Pin Modern helper bodies and paired original regions without inventing counterparts."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS

BODIES={0x4f93c8:'5031c0ace80f77ffffaa84c075f54e4f58c3',
0x4f9400:'5031c0e310ace8d576ffffaa84c0740349ebf04e4f58c3',
0x4f9424:'5031c0e310ace8b159ffffaa84c0740349ebf04e4f58c3',
0x4e3000:'51525157515631c05050ff15984553005a59c3',
0x4f939c:'50d90424db1c2458c3',
0x4f0ae0:'83f8417c0883f85a7f0383c020c3',
0x4eede0:'83f8617c0883f87a7f0383e820c3'}


def main():
    result={'kind':'modern-small-conversion-helper-contracts','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/small-conversion-helpers'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]={}
        for start,hexbytes in BODIES.items():
            expected_body=bytes.fromhex(hexbytes);end=start+len(expected_body)
            data=pe.get_data(start-0x400000,end-start);blobs[label][start]=data
            if label=='official_modern':assert data==expected_body
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        imports={i.address:i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
        assert imports[0x534598]=='MultiByteToWideChar'
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'import_00534598':imports[0x534598]}
    for a in (0x4f0ae0,0x4eede0):assert blobs['original'][a]==blobs['official_modern'][a]
    result['limits']=['Original same-address utility regions are not established functional counterparts.',
        'No target/API execution, malformed-string probes or x87 equivalence test.']
    (ROOT/'analysis/evidence/audits/modern-small-conversion-helpers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: five Modern helper bodies, two retained ASCII converters and wide-character API binding')


if __name__=='__main__':main()
