"""Static packaged-DLL x87-control candidates; no loading/unpacking/execution."""
import hashlib,json,re,subprocess,struct
from collections import defaultdict
import pefile
from audit_thrash_loader_difference import ROOT


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    expected='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
    names=re.findall(r'^Path = (.+\.dll)$',subprocess.check_output(['7z','l','-slt',str(archive)],text=True),re.M)
    assert len(names)==11
    root=ROOT/'analysis/captures/modern-differences/driver-fpu-members'
    out={'kind':'official-package-x87-control-candidate-inventory','archive_sha256':expected,'members':[]}
    duplicates=defaultdict(list)
    for name in names:
        raw=subprocess.check_output(['7z','x','-so',str(archive),name])
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert path.read_bytes()==raw
        else:path.write_bytes(raw)
        pe=pefile.PE(data=raw);digest=hashlib.sha256(raw).hexdigest();duplicates[digest].append(name)
        text=subprocess.check_output(['objdump','-d','-Mintel',str(path)],text=True)
        candidates=[]
        for line in text.splitlines():
            if re.search(r'\b(fldcw|fnstcw|fstcw|fninit|finit)\b',line):
                address=re.match(r'^\s*([0-9a-f]+):',line)
                if address:candidates.append({'va':address[1].zfill(8),'disassembly':line.strip()})
        sections=[s.Name.rstrip(b'\0').decode('latin1') for s in pe.sections]
        out['members'].append({'member':name,'sha256':digest,'bytes':len(raw),
            'reference_path':str(path.relative_to(ROOT)),'image_base':f'{pe.OPTIONAL_HEADER.ImageBase:08x}',
            'sections':sections,'mpress_named_sections':any(s.startswith('.MPRESS') for s in sections),
            'candidate_count':len(candidates),'candidates':candidates})
    out['identical_member_groups']=[{'sha256':digest,'members':members} for digest,members in duplicates.items() if len(members)>1]
    dx8=root/'drivers/dx8/dx8a.dll';pe=pefile.PE(str(dx8));base=pe.OPTIONAL_HEADER.ImageBase
    start,end=0x6000b631,0x6000b664
    body=pe.get_data(start-base,end-start)
    assert body==bytes.fromhex('5151d97c24008b4424000d000c000089442404d96c24048b442400a378ef01605959c351a178ef016089442400d96c240059c3')
    capture=root/'dx8-rounding-save-restore.asm'
    capture.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',str(dx8)]))
    out['verified_dx8_rounding_pair']={'member':'drivers/dx8/dx8a.dll','start':f'{start:08x}',
        'end_exclusive':f'{end:08x}','sha256':hashlib.sha256(body).hexdigest(),
        'assembly':str(capture.relative_to(ROOT)),'mask':'00000c00','save_cell':'6001ef78',
        'contract':'First helper saves incoming CW, loads CW OR0c00h; second reloads saved CW. Precision bits0300h unaffected by OR mask.',
        'register_effects':'O=(incoming ECX & ffff0000h)|CW. Save helper returns EAX=O, ECX=O|0c00h; restore helper returns EAX=ECX=saved DWORD. Neither promises incoming ECX preservation.',
        'limits':'Callers, balanced pairing, concurrent ownership and runtime control state not validated.'}
    caller_start,caller_end=0x6000c281,0x6000c352
    caller=pe.get_data(caller_start-base,caller_end-caller_start)
    assert pe.get_data(0x6000c2bd-base,5)==bytes.fromhex('e86ff3ffff')
    assert pe.get_data(0x6000c347-base,5)==bytes.fromhex('e808f3ffff')
    assert pe.get_data(0x6000c29e-base,5)==bytes.fromhex('e9ac000000')
    caller_capture=root/'dx8-rounding-caller.asm'
    caller_capture.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
        f'--start-address={caller_start}',f'--stop-address={caller_end}',str(dx8)]))
    all_asm=subprocess.check_output(['objdump','-d','-Mintel',str(dx8)],text=True)
    sites={}
    for target in (0x6000b631,0x6000b654,0x6000c281):
        found=[]
        for match in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\bcall\s+0x'+f'{target:x}'+r'\b',all_asm,re.M):
            address=int(match[1],16);instruction=pe.get_data(address-base,5)
            assert instruction[0]==0xe8 and address+5+struct.unpack('<i',instruction[1:])[0]==target
            found.append(f'{address:08x}')
        sites[f'{target:08x}']=found
    assert sites['6000b631']==['6000c2bd'] and sites['6000b654']==['6000c347']
    assert sites['6000c281']==['6000c3b2','6000c3ce','6000c701','6000c71d','6000c739']
    imports={i.address:(d.dll.decode(),i.name.decode()) for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
    thunk=pe.get_data(0x6001124a-base,6);assert thunk[:2]==b'\xff\x25'
    iat=struct.unpack('<I',thunk[2:])[0];assert imports[iat]==('MSVCRT.dll','floor')
    allocation=pe.get_data(0x60011256-base,6);assert allocation[:2]==b'\xff\x25'
    allocation_iat=struct.unpack('<I',allocation[2:])[0]
    assert imports[allocation_iat]==('MSVCRT.dll','??2@YAPAXI@Z')
    out['verified_dx8_rounding_caller']={
        'start':f'{caller_start:08x}','end_exclusive':f'{caller_end:08x}',
        'bytes':len(caller),'sha256':hashlib.sha256(caller).hexdigest(),
        'assembly':str(caller_capture.relative_to(ROOT)),'decoded_direct_calls':sites,
        'allocation_failure_branch':'6000c29e jumps to return unwind6000c34f before CW entry6000c2bd',
        'normal_loop_join':'6000c347 invokes restore; local zero-iteration path joins it too',
        'allocation_thunk':'60011256','allocation_import':{'iat':f'{allocation_iat:08x}','dll':'MSVCRT.dll','name':'??2@YAPAXI@Z'},
        'floor_thunk':'6001124a','floor_import':{'iat':f'{iat:08x}','dll':'MSVCRT.dll','name':'floor'},
        'limits':'Normal local control flow only; imported callee FPU contracts, indirect entries, exceptional exits, higher rendering role and concurrency unverified.'}
    out['limits']=['Linear executable-section decode only; embedded data, packing and alternate instruction boundaries can produce false or missing candidates.',
        'MPRESS-named sections are not unpacked; their candidate counts are not validated code.',
        'Not an original-versus-Modern DLL comparison or proof any candidate is reached by the game.',
        'Only verified DX8 helper contract interpreted; no global all-80-bit or precision-regression conclusion.',
        'No DLL/game execution, instruction probes, executable patching or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/packaged-x87-control-candidates.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 11 pinned DLL members scanned; DX8 51-byte rounding pair verified; candidates remain qualified')


if __name__=='__main__':main()
