"""Static original/Modern audio snapshot and Cancel restoration; no target execution."""
import hashlib
import json
import struct
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble
import pefile


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    capture=ROOT/'analysis/captures/modern-differences/audio-cancel'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-audio-cancel-snapshot-restoration','binaries':{},
        'limits':['No UI, sound, game or instruction execution.',
                  'Saved block/cache values, flag lifecycle, caller admission and later audio application remain conditional.',
                  'Does not establish all original failures choose maximum127 or precise1.0.0 introduction.']}
    snapshots=[]
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==expected
        pe=pefile.PE(data=raw)
        def get(start,end):return pe.get_data(start-0x400000,end-start)
        spans=[(0x437e00,0x43806b),(0x438070,0x43825c)]
        rows=[]
        for start,end in spans:
            data=get(start,end)
            path=capture/f'{label}-{start:08x}.asm'
            path.write_text('\n'.join(disassemble(data,start))+'\n')
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'bytes':len(data),'sha256':sha(data),'assembly':str(path.relative_to(ROOT)),
                'assembly_sha256':sha(path.read_bytes())})
        snapshot=get(0x43803c,0x438061);snapshots.append(snapshot)
        assert snapshot.hex()=='b910000000a124295500bf20395f00bed0bb6f00a36c395f00a120295500f3a5a360395f00'
        assert pe.get_string_at_rva(0x1375d8)==b'ASLD_ENGINEVOLUME'
        assert pe.get_string_at_rva(0x1375c8)==b'ASLD_SOUNDFX'
        assert pe.get_string_at_rva(0x137608)==b'CANCEL_AUDIO_OPTIONS'
        callbacks={}
        for address,name in ((0x555d20,b'psaudio'),(0x556128,b'audio')):
            words=struct.unpack('<5I',get(address,address+20))
            assert words[3:]==(0x437e00,0x438070)
            assert pe.get_string_at_rva(words[0]-0x400000)==name
            callbacks[name.decode()]=[f'{x:08x}'for x in words]
        if label=='original':
            assert get(0x43818c,0x438192).hex()=='8a1d09295500'
            assert get(0x43819c,0x43819e).hex()=='f3a5'
            assert get(0x4381a3,0x4381bb).hex()=='84db7414a120295500a3f4bb6f00a124295500a3f8bb6f00'
            cancel={'copy':'0043819c','post_copy_override':'004381a3..004381bb',
                'override_hex':get(0x4381a3,0x4381bb).hex(),
                'condition':'00552909 BYTE nonzero',
                'writes':'00552920 ->006fbbf4;00552924 ->006fbbf8'}
        else:
            assert get(0x438198,0x4381a9).hex()=='be20395f00bfd0bb6f00b910000000f3a5'
            assert get(0x4381a9,0x4381c5).hex()=='833d34925500007531a180466600a3d0d16f00eb0790909090909090'
            cancel={'copy':'004381a7','post_copy_policy':'004381a9..004381c5',
                'policy_hex':get(0x4381a9,0x4381c5).hex(),
                'writes':'No corresponding extra006fbbf4/006fbbf8 write; menu-sound006fd1d0 restored from00664680 only if00559234==0'}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'snapshot_hex':snapshot.hex(),'callback_rows':callbacks,'cancel':cancel}
    assert snapshots[0]==snapshots[1]
    fields=[]
    for name,live,cache,saved_cache in [('sound_effects',0x6fbbf4,0x552920,0x5f3960),
                                        ('engine',0x6fbbf8,0x552924,0x5f396c)]:
        saved_block=0x5f3920+(live-0x6fbbd0)
        assert 0x5f3920<=saved_block<0x5f3960
        fields.append({'name':name,'configured_setting':f'{live:08x}',
            'field_in_64_byte_snapshot':f'{saved_block:08x}',
            'separate_cache':f'{cache:08x}','saved_separate_cache':f'{saved_cache:08x}',
            'original_cancel_if_flag_nonzero':'Saved separate-cache value overwrites restored configured block value.',
            'modern_cancel':'Restored configured block value retained locally.'})
    result['snapshot_contract']={'live_block':['006fbbd0','006fbc10'],
        'saved_block':['005f3920','005f3960'],'bytes':64,'fields':fields,
        'preconditions':'Clear DF, valid nonoverlapping memory, saved block/cache survives until Cancel; no concurrent alias mutation.'}
    result['example']={'kind':'derived symbolic consequence, not executed test',
        'saved_configured_engine':95,'saved_separate_engine_cache':127,'flag00552909':1,
        'original_engine_after_local_restore':127,'modern_engine_after_local_restore':95,
        'qualification':'127 is an illustrative saved input, not proven initial cache or universal failure result.'}
    (ROOT/'analysis/evidence/audits/audio-cancel-difference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned audio callbacks, identical snapshot, paired Cancel copy and removed cache-to-setting overrides')


if __name__=='__main__':main()
