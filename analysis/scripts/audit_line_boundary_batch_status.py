"""Bounded static x87-status propagation through batch helpers; no instruction execution."""
import hashlib
import json
import re
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

RANGES = [(0x49bcd0,0x49bcee,[]),(0x49bd30,0x49bdbe,[0x49bdc0]),
          (0x49bdc0,0x49be3d,[0x4ea4f0])]
COPY_RANGES = [(0x4ea4f0,0x4ea547,[0x503281,0x5033e5,0x50356d]),
               (0x503281,0x5033e3,[]),(0x5033e5,0x503569,[]),(0x50356d,0x503664,[])]
TRACK_RANGES = [(0x48cb50,0x48cc60,[]),(0x48cc60,0x48cce8,[0x487620]),
                (0x477d90,0x477df0,[0x477a10,0x477a10,0x477990]),
                (0x477a10,0x477a42,[]),
                (0x477990,0x4779d6,[0x477850,0x477850,0x4b6a30,0x4b6ca0])]
TRACK_ALLOWED = {'fld','fadd','faddp','fmul','fmulp','fstp','fsub','fsubp','fsubr','fxch',
                 'imul','or','and','sar','sbb','je','jl'}
COPY_ALLOWED = {'ja','jae','jb','je','jns','js','jl','test','emms','fild','fxch','fistp','movq'}
ALLOWED = {'push','pop','mov','add','sub','inc','dec','shl','lea','cmp','jge','jne','jmp','call','ret','xor'}


def main():
    specs = {label: (path,sha) for label,(path,sha,_) in SPECS.items()}
    specs['local_analysis'] = ('nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe',
        '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb')
    out = {'schema_version': 2, 'scope': 'Bounded C0/C2/C3 propagation through batch/copy and track-map helpers',
           'baselines': {}, 'canonical_bodies': {}}
    reference = {}
    for label,(relative,wanted) in specs.items():
        path = ROOT/relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == wanted
        pe = pefile.PE(data=raw)
        rows = []
        for start,end,calls in RANGES+COPY_RANGES+TRACK_RANGES:
            code = pe.get_data(start-0x400000,end-start)
            if start in reference:
                assert code == reference[start]
            else:
                reference[start] = code
            text = subprocess.check_output(['objdump','-d','--no-show-raw-insn','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',str(path)],text=True)
            instructions = []
            targets = []
            for line in text.splitlines():
                match = re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
                if not match:
                    continue
                address,mnemonic,operands = match.groups()
                extras = COPY_ALLOWED if start in {row[0] for row in COPY_RANGES} else (TRACK_ALLOWED if start in {row[0] for row in TRACK_RANGES} else set())
                assert mnemonic in ALLOWED | extras, line
                instructions.append({'va': address.zfill(8), 'mnemonic': mnemonic, 'operands': operands.strip()})
                if mnemonic == 'call':
                    targets.append(int(operands.strip(),16))
            assert instructions and targets == calls
            body = {'start': f'{start:08x}', 'end_exclusive': f'{end:08x}',
                'bytes': len(code), 'sha256': hashlib.sha256(code).hexdigest(), 'hex': code.hex(),
                'instructions': instructions,
                'x87_mmx_instructions': [row for row in instructions if row['mnemonic'].startswith('f') or row['mnemonic'] in {'emms','movq'}],
                'direct_call_targets': [f'{va:08x}' for va in targets]}
            key = f'{start:08x}'
            if key in out['canonical_bodies']:
                assert out['canonical_bodies'][key] == body
            else:
                out['canonical_bodies'][key] = body
            rows.append({'canonical_body': key, 'bytes': len(code), 'sha256': hashlib.sha256(code).hexdigest()})
        out['baselines'][label] = {'path': relative, 'sha256': wanted, 'helpers': rows}
    out['resolved_copy_boundary'] = {'callsite': '0049be25', 'target': '004ea4f0',
        'copy_bytes_identical': 1076,
        'scope': 'Dispatcher and all three direct copy backends checked; no explicit x87 status/environment reader or further calls in backends.',
        'limit': 'x87 integer transfers and MMX/EMMS affect other floating-point state; full machine equivalence not implied.'}
    out['track_map_frontiers'] = {'rectangle_submit_target': '00487620',
        'pose_unpack_target': '00477850', 'pose_interpolation_targets': ['004b6a30','004b6ca0'],
        'limit': 'Reviewed local bodies do not read incoming condition bits; these callees and outer returns remain unresolved.'}
    out['limits'] = ['Integer-only batch paths preserve live condition bits; x87/MMX copy paths need separate full-state contracts.',
        'Copy cascade contains no explicit C0/C2/C3 reader; other outer/transform/renderer boundaries remain unresolved.',
        'Memory faults, asynchronous observers, other render/transform paths and indirect callers excluded.',
        'No game, compiler, probe, C reconstruction, Ghidra mutation or target instruction execution.']
    (ROOT/'analysis/evidence/audits/line-boundary-batch-status.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 1997 identical bytes across three baselines; canonical body evidence and narrowed track-map frontiers')


if __name__ == '__main__':
    main()
