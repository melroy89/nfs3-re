"""Connect retained static producer evidence to the removed mode-budget gate."""
import json
import struct
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    images = {}
    result = {'kind': 'static-renderer-budget-field-linkage', 'binaries': {}, 'producers': []}
    for role, (path, expected, _) in SPECS.items():
        raw = (ROOT/path).read_bytes()
        assert sha(raw) == expected
        images[role] = pefile.PE(data=raw)
        result['binaries'][role] = {'path': path, 'sha256': expected}
    old = images['original']
    specs = [([1,2],0x4b5a94,0x4b5aa4,4<<20,'bb','891dd0fe5500'),
             ([3,4],0x4b5ba7,0x4b5bd5,8<<20,'bb','891dd0fe5500'),
             ([5],0x4b5c55,0x4b5c68,2<<20,'be','8935d0fe5500'),
             ([6],0x4b5d44,0x4b5d57,2<<20,'bf','893dd0fe5500'),
             ([7,8],0x4b5dd9,0x4b5df6,2<<20,'be','8935d0fe5500')]
    for selectors, load, store, value, opcode, encoded in specs:
        assert old.get_data(load-0x400000,5) == bytes.fromhex(opcode)+struct.pack('<I',value)
        assert old.get_data(store-0x400000,6).hex() == encoded
        body = old.get_data(load-0x400000,store+6-load)
        result['producers'].append({'selectors':selectors,'load':f'{load:08x}','store':f'{store:08x}',
            'value':value,'bytes_hex':body.hex(),'sha256':sha(body),'disassembly':disassemble(body,load)})
    body = old.get_data(0xbee15,0x1d)
    result['consumer'] = {'start':'004bee15','end_exclusive':'004bee32',
        'bytes_hex':body.hex(),'sha256':sha(body),'disassembly':disassemble(body,0x4bee15)}
    assert old.get_data(0xbee1f,5).hex() == 'a1d0fe5500'
    result['ordinary_positive_arithmetic'] = {'condition':'budget/2 >= 2*width*height, with fitting products',
        'equivalent':'budget >= 4*width*height',
        'maximum_pixel_products':{str(value):value//4 for value in (2<<20,4<<20,8<<20)},
        'examples_not_instruction_probes':[
            {'width':w,'height':h,'required_budget':4*w*h,
             'passes_by_budget_MiB':{str(m):4*w*h <= (m<<20) for m in (2,4,8)}}
            for w,h in [(640,480),(800,600),(1024,768),(1280,960),(1600,1200)]]}
    result['limits'] = ['Producer selector mapping reuses the complete dispatch evidence in original-modern-renderer-initialization.md.',
        'Constants cross calls in nonvolatile registers; fixed-value interpretation assumes their documented/ordinary callee preservation and no intervening alias writer.',
        'No hardware-memory measurement inferred; selector0/invalid/failure/alternate producers are not normalized into these cases.',
        'Gate examples isolate budget only; original also requires other flags/depth/aspect/driver fields.',
        'Modern repurposes the same address for border thickness; do not merge the two objects across versions.',
        'No target execution, instruction probes, driver calls or saved Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/renderer-budget-field.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: five original budget producer witnesses and consumer; conditional arithmetic examples retained')


if __name__ == '__main__':
    main()
