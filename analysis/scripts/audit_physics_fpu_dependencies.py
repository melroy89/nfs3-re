"""Conservative static direct-edge inventory, not a runtime reachable call graph."""
import collections
import hashlib
import json
import re

import pefile
from audit_thrash_loader_difference import ROOT, SPECS
from audit_dx5_reference_final import disassemble

ROOT_ENTRY = 0x4ad7a3
CONTROL = re.compile(r'\b(finit|fninit|fsave|fnsave|fldcw|fldenv|frstor|fxrstor|xrstor)\b')


def main():
    inventory_path = ROOT / 'analysis/evidence/audits/original-modern-function-diff.json'
    inventory_raw = inventory_path.read_bytes()
    index = {int(row['entry'], 16): row for row in json.loads(inventory_raw)['functions']}
    out = {'kind': 'conservative-static-physics-fpu-dependencies', 'root': f'{ROOT_ENTRY:08x}',
           'inventory_sha256': hashlib.sha256(inventory_raw).hexdigest(), 'baselines': {}}
    for baseline, (path, expected, _) in SPECS.items():
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        image = pefile.PE(data=raw)
        imports = {i.address: d.dll.decode() + '!' + (i.name.decode() if i.name else '#' + str(i.ordinal))
                   for d in image.DIRECTORY_ENTRY_IMPORT for i in d.imports}
        queue = collections.deque([(ROOT_ENTRY, [])]); visited = {}; unresolved = []
        while queue:
            entry, route = queue.popleft()
            if entry in visited:
                continue
            if entry not in index:
                unresolved.append({'target': f'{entry:08x}', 'route': route})
                continue
            assert len(visited) < 1000, 'inventory unexpectedly expanded; inspect before increasing'
            saved = index[entry]
            ranges = [(int(a, 16), int(b, 16)) for a, b in saved['ranges']]
            chunks = [image.get_data(a - 0x400000, b - a) for a, b in ranges]
            lines = sum([disassemble(chunk, a) for chunk, (a, _) in zip(chunks, ranges)], [])
            row = {'entry': f'{entry:08x}', 'name': saved['name'], 'ranges': saved['ranges'],
                   'sha256': hashlib.sha256(b''.join(chunks)).hexdigest(), 'route': route,
                   'control_instructions': [line for line in lines if CONTROL.search(line)],
                   'decode_warnings': [line for line in lines if '(bad)' in line or '.byte' in line],
                   'outgoing_direct_edges': [], 'indirect_edges': []}
            visited[entry] = row
            for line in lines:
                # Include external direct jumps, including conditional branches, not only calls.
                m = re.search(r'\b(call|j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)', line)
                if m:
                    target = int(m[2], 16)
                    if any(a <= target < b for a, b in ranges):
                        continue
                    edge = {'site': line.split(':')[0], 'operation': m[1], 'target': f'{target:08x}'}
                    row['outgoing_direct_edges'].append(edge)
                    queue.append((target, route + [edge]))
                elif re.search(r'\b(call|jmp)\b', line):
                    slot = re.search(r'PTR\s+(?:ds:|cs:)?0x([0-9a-f]+)\b', line)
                    row['indirect_edges'].append({'instruction': line, 'static_import':
                        imports.get(int(slot[1], 16)) if slot else None})
        out['baselines'][baseline] = {'path': path, 'sha256': expected,
            'nodes': [visited[k] for k in sorted(visited)], 'unresolved_direct_targets': unresolved,
            'node_count': len(visited), 'indirect_edge_count': sum(len(r['indirect_edges']) for r in visited.values()),
            'control_instruction_count': sum(len(r['control_instructions']) for r in visited.values())}
    out['explicit_state_anchors'] = {}
    for baseline, (path, _, _) in SPECS.items():
        image = pefile.PE(str(ROOT / path))
        spans = [(0x4dfd56, 0x4dfd73 if baseline == 'original' else 0x4dfd6d),
                 (0x4ff624, 0x4ff658), (0x51f386, 0x51f3a2)]
        out['explicit_state_anchors'][baseline] = [
            {'start': f'{a:08x}', 'end_exclusive': f'{b:08x}',
             'hex': image.get_data(a - 0x400000, b - a).hex(),
             'disassembly': disassemble(image.get_data(a - 0x400000, b - a), a)} for a, b in spans]
    old, new = [{row['entry']: row for row in out['baselines'][key]['nodes']}
                for key in ('original', 'official_modern')]
    out['comparison'] = {'only_original_nodes': sorted(old.keys() - new.keys()),
        'only_modern_nodes': sorted(new.keys() - old.keys()),
        'different_shared_ranges': [entry for entry in sorted(old.keys() & new.keys())
                                    if old[entry]['sha256'] != new[entry]['sha256']],
        'identical_shared_ranges': sum(old[e]['sha256'] == new[e]['sha256'] for e in old.keys() & new.keys())}
    out['limits'] = [
        'Saved Modern function ranges are reused for both files; this is not independent original boundary recovery.',
        'Linear disassembly can include embedded data; warnings and branch-to-nonentry gaps are retained.',
        'All syntactic direct edges are followed, including error paths; route presence is not runtime reachability.',
        'Indirect imports, callbacks and jump-table destinations are not expanded; no transitive closure claimed.',
        'No target execution, instruction probes, compilation, executable changes or Ghidra writes.',
        'Original004dfd56 extends beyond the saved Modern range; explicit full-body anchors are retained separately.',
    ]
    (ROOT / 'analysis/evidence/audits/physics-fpu-dependencies.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: {x: v[x] for x in ('node_count', 'indirect_edge_count', 'control_instruction_count')}
                      for k, v in out['baselines'].items()}))
    print(json.dumps(out['comparison']))


if __name__ == '__main__':
    main()
