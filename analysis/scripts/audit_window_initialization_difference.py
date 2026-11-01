"""Static hash-pinned comparison of NFS3 window-message registrations.

Requires pefile/GNU objdump; never executes target instructions or edits Ghidra.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import pefile
from audit_thrash_loader_difference import SPECS, ROOT

COMMON_SPANS = [(0x4cd6c0, 0x4cdaa0), (0x4cd2d0, 0x4cd348),
                (0x4cdb10, 0x4cdbcd), (0x4cdbd0, 0x4cdc14),
                (0x4cdc20, 0x4cdc4c)]
IDENTICAL_SPANS = [(0x4cd350, 0x4cd475), (0x4cdb10, 0x4cdbcd),
                   (0x4cdbd0, 0x4cdc14), (0x4cdc20, 0x4cdc4c)]


def main():
    capture = ROOT/'analysis/captures/modern-differences/window'
    capture.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'static-window-registration-comparison', 'range_end': 'exclusive',
              'binaries': {}, 'limits': ['No window/game execution.',
                  'Callback address equality is not proof of identical callback behavior.',
                  'Registration extraction covers only direct immediate PUSH arguments to CALL sequences in the pinned initializer span.']}
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        data = (ROOT/relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        pe = pefile.PE(data=data)
        images[label] = pe
        rows = []
        registrations = []
        hook_start = 0x4ccc70 if label == 'original' else 0x4ccb84
        extra = [(0x4fb6f0,0x4fb78f)] if label == 'original' else []
        for start, end in COMMON_SPANS + [(hook_start, 0x4cce90),
                (0x4cd350, 0x4cd4d1 if label == 'original' else 0x4cd488)] + extra:
            text = subprocess.check_output(['objdump', '-d', '-Mintel',
                f'--start-address={start}', f'--stop-address={end}', relative], cwd=ROOT, text=True)
            out = capture/f'{label}-{start:08x}.asm'
            out.write_text(text)
            rows.append({'start': f'{start:08x}', 'end': f'{end:08x}',
                'bytes_sha256': hashlib.sha256(pe.get_data(start-0x400000, end-start)).hexdigest(),
                'assembly': str(out.relative_to(ROOT)),
                'assembly_sha256': hashlib.sha256(out.read_bytes()).hexdigest()})
            if start == 0x4cd6c0:
                instructions = []
                for line in text.splitlines():
                    match = re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z].*)$', line)
                    if match:
                        instructions.append((int(match[1], 16), match[2]))
                pushes = []
                for i, (address, insn) in enumerate(instructions):
                    if insn.startswith('push '):
                        pushes.append((address, insn))
                    if re.fullmatch(r'call\s+0x4cc6d0', insn):
                        a, b = pushes[-2:]
                        handler = re.fullmatch(r'push\s+0x([0-9a-f]+)', a[1])
                        message = re.fullmatch(r'push\s+0x([0-9a-f]+)', b[1])
                        assert handler and message, hex(address)
                        registrations.append({'call': f'{address:08x}',
                            'message': f'{int(message[1],16):04x}',
                            'handler': f'{int(handler[1],16):08x}'})
                    if insn.startswith('call '):
                        pushes = []
        assert len({r['message'] for r in registrations}) == len(registrations)
        result['binaries'][label] = {'path': relative, 'sha256': expected,
            'spans': rows, 'registrations': registrations}
    old, new = [{r['message']: r['handler'] for r in result['binaries'][k]['registrations']}
                for k in ('original', 'official_modern')]
    result['removed_messages'] = sorted(old.keys()-new.keys())
    result['added_messages'] = sorted(new.keys()-old.keys())
    result['same_message_changed_handler_address'] = [
        {'message': k, 'original': old[k], 'modern': new[k]}
        for k in sorted(old.keys() & new.keys()) if old[k] != new[k]]
    assert result['removed_messages'] == ['0007', '0008']
    assert result['added_messages'] == ['0001', '001c', '0218']
    result['identical_geometry_ranges'] = []
    original,modern = images['original'],images['official_modern']
    assert original.get_data(0xcd4a7,31).hex() == '31d2e862e20200b80100000031d2e856e20200b80200000031d2e84ae20200'
    assert modern.get_data(0xcd475,19).hex() == 'c705144856000000000089ec5d5f5e5a595bc3'
    imports={}
    for label,pe in images.items():
        row={i.name.decode():f'{i.address:08x}' for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
             if i.name in [b'GetKeyState',b'keybd_event']}
        assert row=={'GetKeyState':'00534744','keybd_event':'005347ac'}
        imports[label]=row
    result['removed_toggle_reset']={
        'original_helper':'004fb710..004fb78f','original_creation_calls':['004cd4a9','004cd4b5','004cd4c1'],
        'index_keys':{'0':'Caps Lock, VK14h, scan3ah, flags0/2','1':'Num Lock, VK90h, scan45h, flags1/3',
                      '2':'Scroll Lock, VK91h, scan46h, flags0/2'},
        'contract':'EAX=index, EDX=desired toggle; GetKeyState low bit differs -> keybd_event down/up pair. Original creation supplies desired0.',
        'retained_imports':imports,
        'modern':'Matched creation routine returns at004cd487; original three-call setup absent. Old helper addresses reused by INI readers.',
        'limits':['Original route requires successful window creation and00561298==0.',
                  'Import retention is not evidence of current startup calls; all indirect/external routes and runtime LED/toggle state untested.',
                  'No simulated keyboard events executed; exact release introduction unverified.']}
    for start, end in IDENTICAL_SPANS:
        old_bytes = images['original'].get_data(start-0x400000, end-start)
        assert old_bytes == images['official_modern'].get_data(start-0x400000, end-start)
        result['identical_geometry_ranges'].append({'start': f'{start:08x}',
            'end': f'{end:08x}', 'sha256': hashlib.sha256(old_bytes).hexdigest()})
    output = ROOT/'analysis/evidence/audits/original-modern-window-initialization.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'counts': {k: len(v['registrations']) for k,v in result['binaries'].items()},
        'removed': result['removed_messages'], 'added': result['added_messages'],
        'changed_handler_address': result['same_message_changed_handler_address']}, indent=2))


if __name__ == '__main__':
    main()
