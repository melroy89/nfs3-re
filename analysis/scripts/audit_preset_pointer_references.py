"""Bounded linear-disassembly inventory; no target execution or alias proof."""
import hashlib
import json
import re
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-selected-preset-pointer-reference-inventory', 'binaries': {},
              'limits': ['GNU objdump linear decoding is not a reachable-code proof.',
                         'Literal references do not enumerate aliases, copied pointers or computed addresses.',
                         'Following instructions are context, not a complete def-use or call analysis.',
                         'No target execution; no physical meaning assigned to record+2c.']}
    expected = [0x41aa64, 0x41ab0c, 0x41ab2e, 0x41abe7, 0x41af7a,
                0x41b3bf, 0x41b6e2, 0x41ba94, 0x41bb6e, 0x41ce4e,
                0x41d194, 0x41d29d, 0x41d2d7, 0x41d33f, 0x41e0bf]
    for label, (relative, digest, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        pe = pefile.PE(data=raw)
        text = subprocess.check_output(['objdump', '-d', '-Mintel', str(ROOT / relative)], text=True)
        lines = text.splitlines()
        rows = []
        for index, line in enumerate(lines):
            if not re.search(r'\b0x5dd830\b', line):
                continue
            va = int(line.split(':', 1)[0].strip(), 16)
            data = pe.get_data(va - 0x400000, 32)
            kind = 'publication' if va == 0x41d33f else 'load'
            assert data.startswith(bytes.fromhex('890d30d85d00') if kind == 'publication'
                                   else bytes.fromhex('8b1530d85d00') if va in (0x41aa64, 0x41aa70)
                                   else bytes.fromhex('a130d85d00'))
            rows.append({'address': f'{va:08x}', 'kind': kind, 'context_32_bytes_hex': data.hex(),
                         'context_sha256': hashlib.sha256(data).hexdigest(),
                         'linear_instruction_context': lines[index:index+10]})
        sites = expected.copy()
        if label == 'original':
            sites[0] = 0x41aa70
        assert [int(row['address'], 16) for row in rows] == sites
        assert sum(row['kind'] == 'load' for row in rows) == 14
        relocations = []
        for block in pe.DIRECTORY_ENTRY_BASERELOC:
            for entry in block.entries:
                if entry.type != 3:
                    continue
                target = int.from_bytes(pe.get_data(entry.rva, 4), 'little')
                if 0x5dd0e0 <= target < 0x5dd230:
                    relocations.append({'operand_address': f'{entry.rva+0x400000:08x}',
                                        'target': f'{target:08x}'})
        assert len(relocations) == (37 if label == 'original' else 7)
        contact = pe.get_data(0x1d350, 0x1b9)
        assert pe.get_data(0x1d4a1, 32).hex() == '668b530e0fbec88d04950000000029d031db8b802dd25d00ba02000000c1f818'
        result['binaries'][label] = {'path': relative, 'sha256': digest, 'references': rows,
            'highlow_relocations_targeting_four_record_region': relocations,
            'contact_helper': {'start': '0041d350', 'end_exclusive': '0041d509',
                               'sha256': hashlib.sha256(contact).hexdigest(),
                               'bytes_hex': contact.hex()}}
    old = result['binaries']['original']['references']
    new = result['binaries']['official_modern']['references']
    matches = [a['context_32_bytes_hex'] == b['context_32_bytes_hex'] for a, b in zip(old, new)]
    assert matches == [False] + [True] * 14
    assert result['binaries']['original']['contact_helper'] == result['binaries']['official_modern']['contact_helper']
    result['adjacent_table_read'] = {
        'site': '0041d4b3', 'index_source': 'zero-extended WORD at linked record+0e',
        'read_address': '005dd22d + 3*index', 'read_width': 4,
        'result': 'SAR32(load_le32(005dd22d+3*index),24) = sign_extend8(byte[005dd230+3*index])',
        'index_zero_read_range': '[005dd22d,005dd231)',
        'boundary': 'At index0 three bytes read belong to the preceding four-record region, but are discarded by SAR24. This is not a semantic read of preset+2c.',
        'c_portability': 'For result-only reproduction with ordinary accessible RAM, a signed-byte load avoids an unaligned cross-object DWORD access. It does not reproduce the original four-byte access footprint or possible faults.',
        'limits': 'Complete helper bytes retained/equal; no proof of all caller index domains, allocation bounds, runtime effects or memory fault equivalence.'}
    result['comparison'] = {'references_per_binary': 15, 'loads': 14, 'publication_stores': 1,
                            'equal_paired_32_byte_contexts': 14,
                            'differing_context': 'Classifier has the previously documented changed return/control flow; its pointer load and first field read remain the same.',
                            'classifier_load_moves_from': '0041aa70', 'classifier_load_moves_to': '0041aa64',
                            'interpretation': 'Pointer-reference forms correspond; fourteen local contexts are retained, while the classifier context differs. This is not whole-consumer equivalence.'}
    destination = ROOT / 'analysis/evidence/audits/preset-pointer-references.json'
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 15 references per binary; 14 loads/one store; 14 equal contexts and one changed classifier context')


if __name__ == '__main__':
    main()
