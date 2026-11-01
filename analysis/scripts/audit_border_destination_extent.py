"""Static affine address accounting for straight-line border builders, no execution."""
import json
import re
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind':'static-border-destination-write-accounting','binaries':{}}
    expected_offsets = {vertex*32+field for vertex in range(32) for field in (0,4,24,28)}
    for role, (path, digest, _) in SPECS.items():
        raw = (ROOT/path).read_bytes(); assert sha(raw) == digest
        pe = pefile.PE(data=raw)
        end, pointer = (0x47fbdc,'esi') if role == 'original' else (0x47f98c,'edi')
        body = pe.get_data(0x7f650,end-0x47f650)
        lines = disassemble(body,0x47f650)
        delta = None; writes = []; advances = []
        for line in lines:
            asm = line.split('\t')[-1].strip()
            assert not re.match(r'(?:call|j\w+)\s',asm), asm
            if asm == f'mov    {pointer},eax':
                assert delta is None; delta = 0
            advance = re.fullmatch(r'add\s+'+pointer+r',0x([0-9a-f]+)',asm)
            if advance:
                assert delta is not None
                amount = int(advance[1],16); assert amount == 128
                delta += amount; advances.append(line)
            write = re.match(r'(?:mov|fst|fstp)\s+DWORD PTR \['+pointer+r'(?:(\+|-)0x([0-9a-f]+))?\]',asm)
            if write:
                assert delta is not None
                offset = int(write[2],16) if write[2] else 0
                if write[1] == '-':offset = -offset
                writes.append({'instruction':line,'destination_offset':delta+offset,'bytes':4})
        offsets = {row['destination_offset'] for row in writes}
        assert offsets == expected_offsets
        result['binaries'][role] = {'path':path,'sha256':digest,'start':'0047f650',
            'end_exclusive':f'{end:08x}','body_sha256':sha(body),'disassembly':lines,
            'pointer_register':pointer,'pointer_advances':advances,'writes':writes,
            'unique_DWORD_offsets':sorted(offsets),'quad_blocks':8,'required_span_bytes':1024,
            'maximum_written_byte_offset':1023,'fields_per_vertex':[0,4,24,28]}
    local = ROOT/'nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe'
    local_raw = local.read_bytes()
    assert sha(local_raw) == '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
    local_body = pefile.PE(data=local_raw).get_data(0x7f650,0x33c)
    assert sha(local_body) == result['binaries']['official_modern']['body_sha256']
    result['local_analysis_body_matches_official'] = True
    result['correction'] = 'Both pinned builders write8 quads/32 vertices within0x400 bytes. Earlier9-quad/0x480 and derived slice-overlap claims are incorrect.'
    result['limits'] = ['Static address accounting of these straight-line bodies, not target execution or a floating-point equivalence test.',
        'Writes only XY/UV DWORDs; other vertex fields require existing initialization.',
        'Does not prove caller allocations, all aliases, visual output or complete old/new coordinate equivalence.',
        'Saved Ghidra BuildNineTexturedRectangleBorderQuads name/comments were not changed and remain stale.']
    (ROOT/'analysis/evidence/audits/border-destination-extent.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: both builders write exactly128 unique XY/UV DWORDs in8 quads, maximum byte3ff; local Modern body matches official')


if __name__ == '__main__':main()
