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
        spans=[(0x4d1750,0x4d18a2)]
        if label=='original':spans += [(0x4a6e10,0x4a6f61)]
        else:spans += [(0x4a6e68,0x4a6ec1),(0x4f93c8,0x4f93ea),
            (0x44b271,0x44b28f),(0x44b950,0x44b97b),(0x472aff,0x472b09)]
        for start,end in spans:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        item={'path':relative,'sha256':expected,'spans':rows,
              'selector_names':[string(v) for v in struct.unpack('<6I',pe.get_data(0x55fd24-0x400000,24))],
              'language_names':[string(v) for v in struct.unpack('<6I',pe.get_data(0x563a68-0x400000,24))]}
        if label=='official_modern':
            item['setting_strings']={f'{va:08x}':string(va) for va in [0x53f5e0,0x53f5e8,0x53eaf0]}
            item['required_marker']=string(0x53d37d)
            item['fallback_entries']=[{'id':0x788+i,'offset':off,'text':string(0x53d310+off)}
                for i,off in enumerate(struct.unpack('<27I',pe.get_data(0x53d310-0x400000,108)))]
            assert item['required_marker']=='v1.6.0'
        else:
            assert string(0x53dc3c)=='rt' and string(0x53dc40)=='install.win'
            assert pe.get_data(0xa6e24,17).hex()=='bb00140000b834267a0031d2e80b980300'
            assert pe.get_data(0xa6ece,19).hex()=='8b457ebf34267a008d75fac1e0078b4d7e01c7'
            assert pe.get_data(0xa6efc,8).hex()=='894d7ee953ffffff'
            item['installation_record_writer']={'function':'004a6e10..004a6f61',
                'file':'install.win','mode':'rt','clear_base':'007a2634','clear_bytes':5120,
                'read_count':127,'line_buffer':'EBP-6 after adjusted frame',
                'processing':'Remove LF and CR if found,skip empty processed buffer,copy NUL-terminated bytes,increment record index',
                'destination':'007a2634 + (index<<7)','stride':128,
                'slot0':'007a2634,language selector source','slot1':'007a26b4,remote-prefix classifier source',
                'limits':['No local record-count bound before indexed copy;40 slots describes cleared extent, not enforced admission.',
                          'Read return ignored before scans; helper failure/truncation and unusually long input remain unqualified.',
                          'No source-file provenance, successful read or later immutability claim.']}
            item['source_strings']={f'{va:08x}':string(va) for va in [0x53dc3c,0x53dc40]}
        result['binaries'][label]=item
    (ROOT/'analysis/evidence/audits/original-modern-language-table.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: language baselines, lookup/load spans, marker and 27 fallback entries')


if __name__=='__main__':main()
