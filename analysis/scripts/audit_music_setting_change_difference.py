"""Static comparison of music-setting change requests; no target execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    out = {'kind': 'static-music-setting-change-comparison', 'baselines': {}}
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        path = ROOT / relative
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        end = 0x43833d if label == 'original' else 0x43833e
        data = pe.get_data(0x38260, end - 0x438260)
        out['baselines'][label] = {'path': relative, 'sha256': expected,
            'start': '00438260', 'end_exclusive': f'{end:08x}', 'bytes': len(data),
            'hex': data.hex(), 'body_sha256': hashlib.sha256(data).hexdigest(),
            'disassembly': subprocess.check_output(['objdump', '-d', '-Mintel',
                '--start-address=0x438260', f'--stop-address={end}', str(path)], text=True)}
    assert images['original'].get_data(0x38260, 140) == images['official_modern'].get_data(0x38260, 140)
    for va in (0x4382f9, 0x43831c):
        assert images['official_modern'].get_data(va-0x400000, 10) == bytes.fromhex('c705344f550001000000')
    assert images['original'].get_data(0x3830e, 6) == bytes.fromhex('8935344f5500')
    modern_request=images['official_modern'].get_data(0x103a0,166)
    assert modern_request[:7]==bytes.fromhex('6089e585d27438')
    assert bytes.fromhex('344f5500') not in modern_request
    out['modern_request_helper']={'start':'004103a0','end_exclusive':'00410446',
        'bytes':166,'hex':modern_request.hex(),
        'sha256':hashlib.sha256(modern_request).hexdigest(),
        'direct_pending_address_operand_occurrences':0,
        'limit':'No direct absolute00554f34 operand in this complete helper; indirect aliases and called helpers not excluded.'}
    out['observed_change'] = {
        'setting0': {'live': '006fbbe4', 'cached': '005f3968', 'request_edx': 0},
        'setting1': {'live': '006fbbec', 'cached': '005f3964', 'request_edx': 1},
        'pending_flag': '00554f34', 'request_target': '004103a0',
        'original': 'First changed branch writes flag1 after request; second changed branch has no local flag write.',
        'modern': 'Each changed branch writes flag1 before cache update/request.',
        'limits': ['No audio or instruction execution.', 'Request-helper side effects, callbacks, concurrency and audible outcome not established.',
                   'Local write ordering is not proof of final flag value after called helpers.',
                   'Equal prefix does not establish unchanged callees or whole-function machine equivalence.']}
    (ROOT / 'analysis/evidence/audits/music-setting-change-difference.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PASS: paired complete setting-change bodies, retained prefix and pending-flag write sites')


if __name__ == '__main__':
    main()
