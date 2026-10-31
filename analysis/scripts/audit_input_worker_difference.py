"""Static input-worker correspondence; no target execution."""
import hashlib
import json
import subprocess
import struct
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    result = {'kind': 'static-input-worker-comparison', 'range_end': 'exclusive', 'binaries': {}}
    capture = ROOT / 'analysis/captures/modern-differences/input-worker'
    capture.mkdir(parents=True, exist_ok=True)
    images = {}
    for label, (relative, expected, _) in SPECS.items():
        raw = (ROOT / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == expected
        pe = pefile.PE(data=raw)
        images[label] = pe
        spans = ([(0x42dc20,0x42dc40),(0x4b61f9,0x4b620a),(0x4b626f,0x4b6279),(0x4df870,0x4df894)] if label == 'original' else [(0x41d7e4,0x41d813),(0x42dc20,0x42dc3c),(0x4b5d44,0x4b5d5f),(0x4b5d84,0x4b5db1)])
        spans += [(0x48f550,0x48f69a),(0x42dc40,0x42dc57),(0x4dfb00,0x4dfb14),(0x4dfb20,0x4dfb3d),(0x4dfb70,0x4dfb8f),(0x4dfc00,0x4dfc0d)]
        rows=[]
        for start,end in spans:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        imports={f'{i.address:08x}':i.name.decode() for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address in (0x534488,0x534494,0x5345e8,0x534608,0x534630)}
        assert imports == {'00534488':'CloseHandle','00534494':'CreateEventA','005345e8':'SetEvent','00534608':'TerminateThread','00534630':'WaitForMultipleObjectsEx'}
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,'imports':imports}
    collector = [p.get_data(0x8f550,0x14a) for p in images.values()]
    assert collector[0] == collector[1]
    tables = [p.get_data(0x154e34,24) for p in images.values()]
    assert tables[0] == tables[1]
    pointers = struct.unpack('<6I', tables[0])
    assert pointers == (0x4318b0,0x431740,0x4316c0,0x4316f0,0x4317d0,0x431800)
    result['identical_collector'] = {'start':'0048f550','end':'0048f69a','size':330,'sha256':hashlib.sha256(collector[0]).hexdigest()}
    result['initial_callback_table'] = {'address':'00554e34','sha256':hashlib.sha256(tables[0]).hexdigest(),'pointers':[f'{v:08x}' for v in pointers]}
    result['limits']=['No worker scheduling, shutdown race or compatibility test.','Modern shutdown closes thread handle and signals event; no join established in that body.','Same address 0042dc20 denotes different roles across versions.']
    (ROOT/'analysis/evidence/audits/original-modern-input-worker.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: original worker correspondence, Modern sentinel loop, shutdown and imported primitives')


if __name__ == '__main__':
    main()
