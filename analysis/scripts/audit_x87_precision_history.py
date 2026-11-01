"""Historical x87 control policy witnesses; static bytes only."""
import hashlib
import json
import re
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def calls(pe, target):
    found = []
    for section in pe.sections:
        if not section.Characteristics & 0x20000000:
            continue
        raw = section.get_data()
        base = pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
        for i in range(len(raw)-4):
            if raw[i] == 0xe8 and base+i+5+struct.unpack_from('<i',raw,i+1)[0] == target:
                found.append(base+i)
    return found


def main():
    a = json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']['1.5.3']
    b = json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())['packages']['1.6.0']
    specs = {'1.5.3':(a['archive'],a['archive_sha256'],a['executable_sha256']),
             '1.6.0':(b['archive_path'],b['archive_sha256'],next(x['sha256'] for x in b['members'] if x['member']=='nfs3.exe'))}
    capture = ROOT/'analysis/captures/modern-differences/x87-history'
    capture.mkdir(parents=True,exist_ok=True)
    result = {'kind':'historical-x87-control-policy','versions':{},
        'limits':['Static EXE witnesses, no target execution or runtime control-word observations.',
                   'Direct E8/mask scans are candidates; indirect calls, external DLL controls and all paths not covered.',
                   'Control-word precision is not memory storage width or proof of replay/network incompatibility.']}
    for version,(relative,archive_hash,exe_hash) in specs.items():
        archive=ROOT/relative
        assert sha(archive.read_bytes())==archive_hash
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
        assert sha(raw)==exe_hash
        binary=capture/f'nfs3-{version}.exe'
        binary.write_bytes(raw)
        pe=pefile.PE(data=raw)
        restore=calls(pe,0x4955c8)
        single=calls(pe,0x4955d4)
        mask=[]
        for section in pe.sections:
            if section.Characteristics&0x20000000:
                mask += [pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress+m.start()
                         for m in re.finditer(bytes.fromhex('25fff0ffff'),section.get_data())]
        if version=='1.5.3':
            assert restore==[0x494fc1,0x495272,0x495614,0x4a3e5a,0x4a3e9b,0x4b5d01,0x4bc692]
            assert single==[0x495159,0x495589,0x4a3e67,0x4a3ea8,0x4b5cef,0x4bc7e7]
            assert mask==[0x4955e8]
            assert pe.get_data(0x955c8,10).hex()=='9bdbe3d92df4f37900c3'
            assert pe.get_data(0x955d4,37).hex()=='9bdbe39bd93decf37900a1ecf37900a3f4f3790025fff0ffffa3ecf37900d92decf37900c3'
        else:
            assert not restore and not single and not mask
            assert pe.get_data(0x955c8,49)==b'\x90'*49
            assert pe.get_data(0xbc687,4)==bytes.fromhex('9bdbe39b')
            assert pe.get_data(0xa3b4a,3)==bytes.fromhex('9bdbe3')
        spans=[(0x4955c8,0x4955f9),(0x4bc680,0x4bc6a7),(0x4a3e9b,0x4a3eb9)]
        spans += [(s,s+5) for s in restore+single]
        if version=='1.6.0':spans += [(0x4a3b4a,0x4a3b8d)]
        rows=[]
        for start,end in spans:
            output=capture/f'{version}-{start:08x}.asm'
            output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'bytes_sha256':sha(pe.get_data(start-0x400000,end-start)),
                'assembly':str(output.relative_to(ROOT)),'assembly_sha256':sha(output.read_bytes())})
        result['versions'][version]={'archive':relative,'archive_sha256':archive_hash,
            'executable_reference':str(binary.relative_to(ROOT)),'executable_sha256':exe_hash,
            'restore_helper_call_candidates':[f'{s:08x}' for s in restore],
            'single_helper_call_candidates':[f'{s:08x}' for s in single],
            'mask_candidates':[f'{s:08x}' for s in mask],'spans':rows}
    (ROOT/'analysis/evidence/audits/x87-153-160-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: historical x87 helper/call removal and selected v1.6.0 FINIT boundaries')


if __name__=='__main__':
    main()
