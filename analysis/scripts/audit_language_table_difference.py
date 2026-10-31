"""Static language marker/fallback comparison; no target or asset loading."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/language-table'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-language-table-comparison','range_end':'exclusive','string_decoding':'latin-1 byte-preserving','binaries':{},
        'limits':['No language asset/game/instruction execution.','Marker check is not full offset/payload validation.']}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        def string(va):return pe.get_data(va-0x400000,512).split(b'\0')[0].decode('latin-1')
        rows=[]
        for start,end in [(0x4d1750,0x4d18a2)]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows,
              'language_names':[string(v) for v in struct.unpack('<6I',pe.get_data(0x563a68-0x400000,24))]}
        if label=='official_modern':
            item['required_marker']=string(0x53d37d)
            item['fallback_entries']=[{'id':0x788+i,'offset':off,'text':string(0x53d310+off)}
                for i,off in enumerate(struct.unpack('<27I',pe.get_data(0x53d310-0x400000,108)))]
            assert item['required_marker']=='v1.6.0'
        result['binaries'][label]=item
    (ROOT/'analysis/evidence/audits/original-modern-language-table.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: language baselines, lookup/load spans, marker and 27 fallback entries')


if __name__=='__main__':main()
