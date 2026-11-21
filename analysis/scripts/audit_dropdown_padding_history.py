"""Compare shared frontend bounds arithmetic at131/140; no target execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble,intervals


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dropdown-padding-history','versions':{}};images={}
    spans=[('label_bounds',0x4628d0,0x4629bf),('dropdown_bounds',0x464560,0x4646db)]
    for version,(ah,eh)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh
        pe=pefile.PE(data=raw);images[version]=pe;get=lambda a,b:pe.get_data(a-0x400000,b-a)
        old=version=='1.3.1'
        for a,value in [(0x462971,5 if old else 15),(0x46297f,5 if old else 2),
                        (0x4645ea,5 if old else 15),(0x4645f8,5 if old else 2)]:
            assert get(a,a+5)==b'\x05'+value.to_bytes(4,'little')
        captures=[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),
                   'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]
        row={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,'captures':captures}
        if not old:
            body=get(0x472924,0x472959)
            assert body[:11].hex()=='5352833db8d36f00037520'
            assert pe.get_string_at_rva(0x137e34)==b'tracks'and pe.get_string_at_rva(0x1382ec)==b'rectrk'
            assert get(0x4628ef,0x4628f4).hex()=='e830000100'
            assert get(0x464570,0x464575).hex()=='e8afe30000'
            row['shared_predicate']={'start':'00472924','end_exclusive':'00472959','hex':body.hex(),'sha256':sha(body),
                                     'disassembly':disassemble(body,0x472924),'names':['tracks','rectrk']}
        result['versions'][version]=row
    changes=[]
    allowed=[(0x4628ea,0x46291a),(0x462971,0x462976),(0x46297f,0x462984),
             (0x46456b,0x464587),(0x4645ea,0x4645ef),(0x4645f8,0x4645fd)]
    for name,a,b in spans:
        old=images['1.3.1'].get_data(a-0x400000,b-a);new=images['1.4.0'].get_data(a-0x400000,b-a)
        delta=intervals(old,new,a)
        for i,(x,y)in enumerate(zip(old,new)):
            if x!=y:assert any(s<=a+i<e for s,e in allowed)
        changes.append({'name':name,'changed_bytes':sum(x!=y for x,y in zip(old,new)),'intervals':delta})
    result['complete_selected_body_changes']=changes
    result['verified']=['Both selected bounds paths change width additive5->15 and row-height additive5->2,storing lowWORD results at+1e/+20.',
        '131 label path picks35 fortracks/rectrk independently ofR;131 dropdown path picks35 wheneverR=3.',
        '140 both use shared predicate472924:35 only forR=3 and matchingtracks/rectrk,otherwise15.',
        'All differing bytes in the two complete declared envelopes belong to these predicate-selection regions or four arithmetic immediates.']
    result['limits']=['Complete selected function-byte accounting is not complete frontend/input/rendering coverage.',
        'No visible alignment or universal all-lists improvement validated;caller/label metric/row-count lifetime remain qualified.',
        'WORD stores and low-bit/wrapping arithmetic must be retained for exceptional values;ordinary size formulas are not arbitrary-input safe C.',
        'No target/API/instruction execution,compilation or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/dropdown-padding-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131->140 two shared bounds paths change margins and unify conditional width allowance;all selected body deltas accounted')


if __name__=='__main__':main()
