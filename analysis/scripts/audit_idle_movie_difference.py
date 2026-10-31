"""Static idle-movie admission, availability mask and selection comparison."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/idle-movie';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-idle-movie-comparison','range_end':'exclusive','binaries':{}}
    images={}
    conversion=[(0x4957a0,0x495852),(0x4df1f0,0x4df2af),(0x4df2b0,0x4df306),(0x4fdc90,0x4fe1c9),(0x4dee80,0x4df1e5)]
    common=conversion+[(0x4960e0,0x4961db),(0x4961e0,0x4961ef),(0x4438b0,0x4438ba)]
    spans={'original':[(0x496200,0x4962fd),(0x4730d0,0x473169)],'official_modern':[(0x496200,0x4962c2),(0x4a2f90,0x4a2ffc),(0x4a3e3f,0x4a3e6b),(0x4730d0,0x47314d),(0x4f915e,0x4f9184),(0x4f91ec,0x4f9204)]}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);images[label]=pe;rows=[]
        for start,end in spans[label]+common:
            path=capture/f'{label}-{start:08x}.asm'
            path.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}','bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),'assembly':str(path.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows}
        instruction=pe.get_data(0x96104,5);assert instruction[0]==0xbe
        pointer=int.from_bytes(instruction[1:],'little')
        assert pointer==(0x7a32b4 if label=='original' else 0x7a2cb4)
        item['movie_directory_buffer']=f'{pointer:08x}'
        if label=='official_modern':
            pointers=struct.unpack('<4I',pe.get_data(0x961f0,16))
            item['movie_name_table_004961f0']=[{'index':i,'pointer':f'{a:08x}','name':pe.get_data(a-0x400000,48).split(b'\0')[0].decode()} for i,a in enumerate(pointers)]
            item['file_attribute_import']=[{'dll':entry.dll.decode(),'name':imp.name.decode(),'iat':f'{imp.address:08x}'} for entry in pe.DIRECTORY_ENTRY_IMPORT for imp in entry.imports if imp.address==0x534520]
            assert item['file_attribute_import'][0]['name']=='GetFileAttributesA'
        result['binaries'][label]=item
    result['identical_ranges']=[]
    for start,end in conversion+[(0x4960e0,0x496104),(0x496109,0x49616c),(0x4961ab,0x4961db),(0x4961e0,0x4961ef),(0x4438b0,0x4438ba)]:
        raw=images['original'].get_data(start-0x400000,end-start);assert raw==images['official_modern'].get_data(start-0x400000,end-start)
        result['identical_ranges'].append({'start':f'{start:08x}','end':f'{end:08x}','sha256':hashlib.sha256(raw).hexdigest()})
    result['limits']=['No movies, window interaction or target execution.','No historical intermediate release inspected.','Window activation producer reused from the linked window-handling investigation.','No universal timer-unit or invalid selector-state contract inferred.']
    (ROOT/'analysis/evidence/audits/original-modern-idle-movie.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: paired idle controller, NoMovies mask producer, attribute API and retained timer/input helpers')


if __name__=='__main__':main()
