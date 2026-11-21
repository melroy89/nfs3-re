"""Compare complete sound-bank function envelopes, including removed switch code."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_dx5_reference_final import disassemble
from audit_thrash_loader_difference import ROOT, SPECS

SPANS = [(0x40a010, 0x40a32c), (0x413750, 0x4138d9), (0x413bc0, 0x4147f8)]
READS = [0x40a1a6, 0x413794, 0x414294, 0x414320, 0x414684]


def main():
    result = {'kind': 'sound-bank-language-selection', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/sound-bank-language'
    capture.mkdir(parents=True, exist_ok=True)
    blobs = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        rows = []
        blobs[label] = []
        for a, b in SPANS + [(0x4a6ec4, 0x4a6f2e)]:
            data = pe.get_data(a - 0x400000, b - a)
            blobs[label].append(data)
            path = capture / f'{label}-{a:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={a}', f'--stop-address={b}', relative], cwd=ROOT))
            rows.append({'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
                'sha256': hashlib.sha256(data).hexdigest(), 'assembly': str(path.relative_to(ROOT))})
        selector = 0x6fbb4c if label == 'original' else 0x7a2764
        for a in READS:
            assert pe.get_data(a - 0x400000, 5) == b'\xa1' + struct.pack('<I', selector)
        if label == 'original':
            assert struct.unpack('<6I', pe.get_data(0x13ba8, 24)) == (0x413bf4, 0x413bfb, 0x413c02, 0x413c09, 0x413c10, 0x413bf4)
        else:
            assert pe.get_data(0x13be3, 7) == bytes.fromhex('be342b7a00eb2b')
            assert pe.get_data(0x13bea, 43) == b'\x90' * 43
            assert pe.get_data(0xa6f26, 6) == bytes.fromhex('890d64277a00')
        result['binaries'][label] = {'path': relative, 'sha256': expected, 'spans': rows}
    result['functions'] = []
    for index, (a, b) in enumerate(SPANS):
        old, new = blobs['original'][index], blobs['official_modern'][index]
        changed = [a + i for i, (x, y) in enumerate(zip(old, new)) if x != y]
        allowed = {r + j for r in READS for j in (1, 2, 3)}
        if index == 2:
            allowed.update(range(0x413be1, 0x413c15))
        assert set(changed) <= allowed
        assert len(changed) == [3, 3, 61][index]
        result['functions'].append({'entry': f'{a:08x}', 'envelope_bytes': b-a,
            'changed_bytes': len(changed), 'changed_addresses': [f'{v:08x}' for v in changed]})
    modern_raw=(ROOT/SPECS['official_modern'][0]).read_bytes();mp=pefile.PE(data=modern_raw)
    producer_spans=[('complete_path_initializer',0x4a6ec4,0x4a6f2e),('attribute_wrapper',0x4f915e,0x4f916a),('directory_predicate',0x4f916c,0x4f9184),('copy_string',0x4f93b8,0x4f93c5),('find_terminator',0x4f9448,0x4f9451)]
    assert mp.get_data(0xf915e,12).hex()=='515250ff15204553005a59c3'
    slots={i.address:i.name for d in mp.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name};assert slots[0x534520]==b'GetFileAttributesA'
    names=[];rva=0x13f42c
    for index in range(22):
        text=mp.get_string_at_rva(rva);assert len(text)+1<=128
        names.append({'slot':index,'destination':f'{0x7a27b4+128*index:08x}','text':text.decode('ascii')});rva+=len(text)+1
    assert names[7]['destination']=='007a2b34'and names[7]['text']=='.\\gamedata\\audio\\speech\\'
    assert mp.get_string_at_rva(0x13eaf0)==b'english'
    letters={}
    for role,(relative,expected,_)in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;p=pefile.PE(data=raw)
        tables=[]
        for address in [0x409ff0,0x412950]:
            ptrs=struct.unpack('<7I',p.get_data(address-0x400000,28));values=[p.get_string_at_rva(v-0x400000).decode('ascii')for v in ptrs]
            assert values==(['E','G','F','S','I','E','E']if role=='original'else['E','G','F','S','I','W','E'])
            tables.append({'address':f'{address:08x}','pointers':[f'{v:08x}'for v in ptrs],'letters':values})
        letters[role]=tables
    result['producer_followup']={'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':mp.get_data(a-0x400000,b-a).hex(),'disassembly':disassemble(mp.get_data(a-0x400000,b-a),a)}for n,a,b in producer_spans],'initialized_path_slots':names,'filename_letter_tables':letters,
        'verified':['Copy/find helpers retainECX;GetFileAttributes wrapper explicitly saves/restoresECX/EDX.',
            'Directory predicate returns1 for attributes!=ffffffff and directory bit10h set;other outcomes0.',
            'Selected language string appends to speech base;false predicate replaces suffix withenglish and sets cached selector0.',
            'FallbackEnglish directory and individual banks are not checked again in this initializer.'],
        'limits':['No historical120 boundary established by this original/final producer follow-up.',
            'No playback/crash proof,all selector writers,pointer validity or concurrency/lifetime model.',
            'String helpers require valid terminated buffers and ordinary DF;local code has no length bound.']}
    result['limits'] = ['No game or audio execution; no asset availability validation.',
        'Selected initializer/helper contracts now captured;all selector writers,lifetimes and runtime outcomes remain unverified.']
    (ROOT / 'analysis/evidence/audits/sound-bank-language-difference.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: five selector retargets and removed switch; complete envelopes 796/393/3128 bytes')


if __name__ == '__main__':
    main()
