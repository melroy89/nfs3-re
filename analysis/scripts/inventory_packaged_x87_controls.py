"""Static packaged-DLL x87-control candidates; no loading/unpacking/execution."""
import hashlib,json,re,subprocess
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
    out['limits']=['Linear executable-section decode only; embedded data, packing and alternate instruction boundaries can produce false or missing candidates.',
        'MPRESS-named sections are not unpacked; their candidate counts are not validated code.',
        'Not an original-versus-Modern DLL comparison or proof any candidate is reached by the game.',
        'Only verified DX8 helper contract interpreted; no global all-80-bit or precision-regression conclusion.',
        'No DLL/game execution, instruction probes, executable patching or Ghidra changes.']
    (ROOT/'analysis/evidence/audits/packaged-x87-control-candidates.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS: 11 pinned DLL members scanned; DX8 51-byte rounding pair verified; candidates remain qualified')


if __name__=='__main__':main()
