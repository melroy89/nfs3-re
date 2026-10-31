"""Static camera duplicate-cleanup caller correspondence; no menu/game execution."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'camera-duplicate-cleanup-caller-comparison','binaries':{}}
    capture=ROOT/'analysis/captures/modern-differences/camera-duplicates'
    capture.mkdir(parents=True,exist_ok=True);images={}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in [(0x45d770,0x45d83d if label=='original' else 0x45d7a4),
                          (0x45d7ad,0x45d837),(0x45d920,0x45d9a0),
                          (0x45d9e0,0x45daa4)]:
            data=pe.get_data(start-0x400000,end-start)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':hashlib.sha256(data).hexdigest(),'assembly':str(path.relative_to(ROOT))})
        registrations={}
        for address,name,token in [(0x555d50,'pscamera',0x537c78),(0x556008,'camera',0x537d84)]:
            words=struct.unpack('<6I',pe.get_data(address-0x400000,24))
            assert words==(token,0,0,0x45d920,0x45d9e0,0x45d9a0)
            assert pe.get_data(token-0x400000,16).split(b'\0')[0].decode()==name
            registrations[name]={'address':f'{address:08x}','words':[f'{x:08x}' for x in words]}
        assert pe.get_data(0x53a7fc-0x400000,32).split(b'\0')[0]==b'CANCEL_CAMERA_OPTIONS'
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'registrations':registrations,'cancel_token':'CANCEL_CAMERA_OPTIONS'}
    old,new=[images[k] for k in ('original','official_modern')]
    assert old.get_data(0x45d7ae-0x400000,132)==new.get_data(0x45d7ae-0x400000,132)
    assert new.get_data(0x45d798-0x400000,5)==bytes.fromhex('e810000000')
    assert new.get_data(0x45da44-0x400000,5)==bytes.fromhex('e864fdffff')
    assert old.get_data(0x45da49-0x400000,91)==new.get_data(0x45da49-0x400000,91)
    assert old.get_data(0x45da0c-0x400000,2)==bytes.fromhex('753b')
    assert new.get_data(0x45da0c-0x400000,2)==bytes.fromhex('7536')
    assert old.get_data(0x45da1d-0x400000,2)==bytes.fromhex('742a')
    assert new.get_data(0x45da1d-0x400000,2)==bytes.fromhex('7425')
    result['verified_modern_calls']=['0045d798','0045da44']
    result['retained_post_cleanup_tail']={'start':'0045da49','end_exclusive':'0045daa4',
        'sha256':hashlib.sha256(old.get_data(0x45da49-0x400000,91)).hexdigest()}
    result['limits']=['Non-Cancel callback branch verified; exact Race/Credits/Exit lifecycle coverage and runtime saving remain unverified.',
        'Clear-to-zero policy does not guarantee all four raw values are distinct; zeros can repeat.',
        'No target execution, Ghidra edits or executable changes.']
    (ROOT/'analysis/evidence/audits/camera-duplicate-callers.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired camera registrations, original inline cleanup and Modern non-Cancel cleanup call')


if __name__=='__main__':main()
