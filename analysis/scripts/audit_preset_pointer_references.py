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
        result['binaries'][label] = {'path': relative, 'sha256': digest, 'references': rows}
    old = result['binaries']['original']['references']
    new = result['binaries']['official_modern']['references']
    matches = [a['context_32_bytes_hex'] == b['context_32_bytes_hex'] for a, b in zip(old, new)]
    assert matches == [False] + [True] * 14
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
