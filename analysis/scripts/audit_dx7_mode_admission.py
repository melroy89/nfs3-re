"""Bounded official-package DX7 driver mode admission; no DLL loading."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    member='drivers/dx7/dx7a.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member])
    pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;assert base==0x60000000
    capture=ROOT/'analysis/captures/modern-differences/dx7-mode-admission';capture.mkdir(parents=True,exist_ok=True)
    binary=capture/'dx7a.dll';binary.write_bytes(raw)
    rows=[]
    for start,end in [(0x60001000,0x60001191),(0x60002578,0x600025ec),(0x600025ec,0x600026d2),(0x600026d4,0x6000276d)]:
        path=capture/f'{start:08x}.asm'
        path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
        rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-base,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert pe.get_data(0x2613,11)==bytes.fromhex('3d800200000f82a8000000')
    assert pe.get_data(0x261e,12)==bytes.fromhex('81fbe00100000f829c000000')
    exports=[{'name':x.name.decode(),'address':f'{base+x.address:08x}'} for x in pe.DIRECTORY_ENTRY_EXPORT.symbols if x.name and x.name==b'_THRASH_about@0']
    assert exports==[{'name':'_THRASH_about@0','address':'60001000'}]
    assert pe.get_data(0x1188,9).hex()=='b8c0c70f605f5e5bc3'
    descriptor_rva=0xfc7c0;section=pe.get_section_by_rva(descriptor_rva)
    assert section.Name.rstrip(b'\0')==b'.data' and section.Characteristics&0x80000000
    assert section.VirtualAddress+section.SizeOfRawData<=descriptor_rva<section.VirtualAddress+section.Misc_VirtualSize
    result={'kind':'static-official-dx7-mode-admission','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'member':member,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'image_base':f'{base:08x}','exports':exports,'range_end':'exclusive','spans':rows,'limits':['Official final-package DX7 DLL only; no original or intermediate driver comparison.','No DLL load, graphics API interaction, display enumeration or instruction execution.','Callback registration via vtable offset retained; complete interface identity not independently qualified here.','No universal all-driver or exact 640x480 depth-forcing conclusion.']}
    result['about_descriptor_ownership']={'preferred_address':'600fc7c0','rva':'000fc7c0',
        'storage':'Writable module.data virtual tail beyond raw-backed bytes; not a locally allocated return buffer.',
        'return':'60001188 returns immediate descriptor address after calls60002060/600092c0.',
        'section':{'rva':f'{section.VirtualAddress:08x}','virtual_size':section.Misc_VirtualSize,'raw_size':section.SizeOfRawData,'characteristics':f'{section.Characteristics:08x}'},
        'limits':'Preferred addresses subject to PE relocation; module-owned pointer lifetime depends on mapping, not solely on function return. Callee side effects/concurrent queries and actual unload admission untested.'}
    (ROOT/'analysis/evidence/audits/official-dx7-mode-admission.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: official DX7 member, minimum size branches and about export')


if __name__=='__main__':main()
