"""Inventory linear-decoded status/environment-reader candidates; not a global CFG proof."""
import collections
import hashlib
import json
import re
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

READERS = {'fnstsw','fstsw','fnstenv','fstenv','fnsave','fsave','fxsave','fxsave64',
           'xsave','xsaveopt','xsavec','xsaves'}
COMPARE = {'fcom','fcomp','fcompp','fucom','fucomp','fucompp','ftst'}


def main():
    out = {'scope': 'Executable-section linear x87 status/environment reader inventory', 'baselines': {}}
    images = {}
    address_sets = {}
    for label,(relative,wanted,_) in SPECS.items():
        path = ROOT/relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == wanted
        pe = pefile.PE(data=raw)
        images[label] = pe
        text = subprocess.check_output(['objdump','-d','--no-show-raw-insn','-Mintel',str(path)],text=True)
        rows = []
        for line in text.splitlines():
            match = re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
            if match:
                va,op,args = match.groups()
                rows.append({'va': va.zfill(8), 'mnemonic': op, 'operands': args.strip()})
        observers = []
        categories = collections.Counter()
        for index,row in enumerate(rows):
            if row['mnemonic'] not in READERS:
                continue
            previous = index-1
            while previous >= 0 and rows[previous]['mnemonic'] in {'wait','fwait'}:
                previous -= 1
            before = rows[previous] if previous >= 0 else None
            category = 'lexically-adjacent-compare' if before and before['mnemonic'] in COMPARE else 'needs-context-review'
            categories[category] += 1
            observers.append({**row, 'lexical_category': category,
                'previous_nonwait': before, 'context': rows[max(0,index-4):index+5]})
        address_sets[label] = {row['va'] for row in observers}
        out['baselines'][label] = {'path': relative, 'sha256': wanted, 'candidates': len(observers),
            'mnemonic_counts': dict(collections.Counter(row['mnemonic'] for row in observers)),
            'lexical_categories': dict(categories), 'observers': observers}
    old,new = address_sets['original'],address_sets['official_modern']
    out['address_set_comparison'] = {'shared': len(old & new), 'original_only': sorted(old-new),
        'modern_only': sorted(new-old), 'limit': 'Same-address candidates are not semantic counterparts.'}
    assert [out['baselines'][label]['candidates'] for label in SPECS] == [1660,1658]
    modern = images['official_modern']
    top = [0x526fd1,0x52701d,0x527069,0x5270b5]
    for va in top:
        assert modern.get_data(va-0x400000,7) == bytes.fromhex('dfe02500380000')
    assert 0x3800 & 0x4500 == 0
    wrapper = images['original'].get_data(0xff624,52)
    assert wrapper == modern.get_data(0xff624,52)
    assert modern.get_data(0xff642,4) == bytes.fromhex('6625ff00')
    assert modern.get_data(0xff646,5) == bytes.fromhex('660b442404')
    assert modern.get_data(0xff650,3) == bytes.fromhex('dd2424')
    out['bounded_special_cases'] = {
        'top_only_readers': [f'{va:08x}' for va in top], 'top_mask': '3800', 'tracked_cbit_mask': '4500',
        'mask_intersection': '0000',
        'retained_saved_image_wrapper': {'start': '004ff624','end_exclusive': '004ff658',
            'bytes': 52,'sha256': hashlib.sha256(wrapper).hexdigest(),
            'scope': 'FNSAVE/FRSTOR preserves saved image; merges helper low status byte, not a proven C-bit branch observer.'}}
    out['limits'] = ['Linear objdump decoding can include data/misaligned instructions and omit alternate boundaries; counts are candidates, not reachable-code coverage.',
        'Lexical comparison adjacency is not CFG dominance; alternate or indirect entries remain unverified.',
        'Environment saves can propagate complete state without making condition bits a semantic branch dependency.',
        'No whole-game unobservability, machine equivalence, new probes, target execution or Ghidra changes.']
    index_path = ROOT/'analysis/evidence/audits/x87-status-observer-sites.jsonl'
    records = []
    for label,row in out['baselines'].items():
        for observer in row['observers']:
            previous = observer['previous_nonwait'] or {}
            records.append([label,observer['va'],observer['mnemonic'],observer['operands'],
                            previous.get('va'),previous.get('mnemonic'),observer['lexical_category']])
        row['review_contexts'] = [observer for observer in row.pop('observers')
                                  if observer['lexical_category'] == 'needs-context-review']
    index_raw = ''.join(json.dumps(record,separators=(',',':'))+'\n' for record in records).encode()
    index_path.write_bytes(index_raw)
    out['reader_index'] = {'path': str(index_path.relative_to(ROOT)),
        'sha256': hashlib.sha256(index_raw).hexdigest(), 'rows': len(records),
        'columns': ['baseline','reader_va','mnemonic','operands','previous_nonwait_va','previous_nonwait_mnemonic','lexical_category']}
    (ROOT/'analysis/evidence/audits/x87-status-observers.json').write_text(json.dumps(out,indent=2)+'\n')
    for label,row in out['baselines'].items():
        print(label,row['candidates'],row['mnemonic_counts'],row['lexical_categories'])


if __name__ == '__main__':
    main()
