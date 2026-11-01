"""Paired named opponent HUD defaults and retained conditional draw gates."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-opponent-hud-defaults','binaries':{}};consumers=[]
    name_addresses=[0x556848,0x5568e8,0x5569b0,0x556a50,0x556af0,0x556b90]
    list_addresses=[a+20 for a in name_addresses]
    suffixes=['','cop','1','cop1','2','cop2']
    for label,(relative,digest,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        descriptors=[]
        for profile,suffix in enumerate(suffixes):
            for field,addresses,offset in [('opponentName',name_addresses,4),('opponentList',list_addresses,8)]:
                address=addresses[profile];words=struct.unpack('<5I',get(address,address+20))
                assert words[1:]==(0x5561be,0,0,0x6fbc50+profile*0x1a4+offset)
                assert pe.get_string_at_rva(words[0]-0x400000).decode()==field+suffix
                descriptors.append({'address':f'{address:08x}','token':field+suffix,'storage':f'{words[4]:08x}'})
        assert get(0x5561be,0x5561c4)==struct.pack('<3H',229,228,0)
        spans=[(0x485880,0x485a51 if label=='original' else 0x4859f7),
               (0x482dcd,0x482e6f),(0x483614,0x4836c4)]
        consumers.append([get(a,b) for a,b in spans[1:]])
        if label=='original':
            assert get(0x4858c5,0x4858d1).hex()=='8915e4c26f0089159cbf6f00'
            assert get(0x4858e0,0x4858e2).hex()=='31d2'
            for site,target in [(0x4858fa,0x6fc2e8),(0x485900,0x6fbfa0)]:
                assert get(site,site+6)==b'\x89\x15'+struct.pack('<I',target)
        else:
            assert get(0x485886,0x48588b).hex()=='31c931d242'
            for site,target in [(0x4858bb,0x6fbf9c),(0x4858c7,0x6fc2e4)]:
                assert get(site,site+6)==b'\x89\x0d'+struct.pack('<I',target)
            for site,target in [(0x4858df,0x6fbfa0),(0x4858eb,0x6fc2e8)]:
                assert get(site,site+6)==b'\x89\x15'+struct.pack('<I',target)
        result['binaries'][label]={'path':relative,'sha256':digest,'descriptors':descriptors,
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    assert consumers[0]==consumers[1]
    result['derived_racer_suffix_defaults']={'original':{'name':1,'list':0},'official_modern':{'name':0,'list':1},'suffixes':['1','2']}
    result['consumer_conditions']=['00482dd3 loads profile+8; zero skips list branch.',
        '00483624 tests profile+8; zero skips list branch.',
        'Both branches use a nonzero role-local route to0048a660; zero role reaches additional signed005efda0>1 gate before0048ae70.']
    result['limits']=['Static defaults and selected conditional consumers, not guaranteed visible lists, actual profiles or saved settings.',
        'Profile suffixes/role names come from descriptor tokens; full session/view index production and runtime cycling are separate.',
        'Original literal1 provenance through preserved EDX uses the already documented HUD initializer/helper evidence.',
        'No1.0.0 introduction evidence, game/draw/instruction execution or Ghidra writes.',
        'Retained branch bytes do not establish transitive equivalence of called renderers or machine state.']
    (ROOT/'analysis/evidence/audits/opponent-hud-defaults.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:12 named paired descriptors, racer suffix defaults, two byte-identical conditional consumer spans')


if __name__=='__main__':main()
