"""Static dialog render arguments and initial edit-replacement state."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'choice-dialog-render-and-edit-state','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/choice-dialog-followup'
    capture.mkdir(parents=True,exist_ok=True);blobs={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[];blobs[label]=[]
        for start,end in [(0x444000,0x444350),(0x444c20,0x444f48),(0x444f50,0x4450bd)]:
            data=pe.get_data(start-0x400000,end-start);blobs[label].append(data)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows}
    old,new=blobs['original'],blobs['official_modern']
    allowed=set();values=[]
    for address,ob,nb in [(0x4440d8,0x3f0d0000,0x3f0d4ccd),(0x44410d,0x3f0d0000,0x3f0d4ccd),
                          (0x444220,0x3ef80000,0x3ef8999a),(0x444255,0x3ef80000,0x3ef8999a)]:
        o=address-0x444000;assert old[0][o:o+5]==b'\x68'+struct.pack('<I',ob)
        assert new[0][o:o+5]==b'\x68'+struct.pack('<I',nb)
        allowed.update((o+1,o+2));values.append({'push':f'{address:08x}','original':struct.unpack('<f',struct.pack('<I',ob))[0],'modern':struct.unpack('<f',struct.pack('<I',nb))[0]})
    assert [i for i,(a,b) in enumerate(zip(old[0],new[0])) if a!=b]==sorted(allowed)
    assert old[1][:0x70]==new[1][:0x70] and old[1][0x86:]==new[1][0x86:]
    assert old[1][0x70:0x86]==bytes.fromhex('b401ba010000008825108b55008b451089152c8b5500')
    assert new[1][0x70:0x86]==bytes.fromhex('ba010000008815108b550031c0a32c8b55008b451090')
    assert old[2][0xff:]==new[2][0xff:]
    assert [i for i,(a,b) in enumerate(zip(old[2],new[2])) if a!=b]==[0x86,0x87,0xac,0xad]
    result['render_values']=values
    result['limits']=['Static initial state and handler consequences only; no text-entry or rendering execution.',
        'Dialog type admission, initial buffer contents and textured-draw parameter semantics remain separate.']
    (ROOT/'analysis/evidence/audits/choice-dialog-followup.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 848/808-byte changed bodies and 365-byte edit handler with identical 110-byte insertion tail; four float arguments and initial flag')


if __name__=='__main__':main()
