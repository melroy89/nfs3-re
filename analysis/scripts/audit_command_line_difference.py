"""Static command-line tables/parser witnesses; no target execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS


def main():
    capture=ROOT/'analysis/captures/modern-differences/command-line'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-command-line-comparison','range_end':'exclusive','binaries':{},
        'limits':['No command-line/game execution.','Table recognition is not full downstream option semantics.',
                  'No universal claim that legacy options have no other parser path.']}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        def string(va):return pe.get_data(va-0x400000,512).split(b'\0')[0].decode('ascii')
        spans=[(0x4a5080,0x4a54e4)]
        if label=='official_modern':spans += [(0x4b57f4,0x4b5841),(0x4b5844,0x4b5877),(0x4f9400,0x4f9448),(0x4f0ae0,0x4f0aee),(0x4eede0,0x4eedee)]
        rows=[]
        for start,end in spans:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        switches=[]
        for i in range(33):
            ptr=struct.unpack('<I',pe.get_data(0x55eb34-0x400000+4*i,4))[0]
            switches.append({'index':i,'pointer':f'{ptr:08x}','text':string(ptr)})
        prefixes=[{'index':i,'pointer':f'{v:08x}','text':string(v)} for i,v in enumerate(struct.unpack('<12I',pe.get_data(0x15ec50,48)))]
        assert prefixes[1]['text']=='-PORT='
        aliases=[string(v) for v in struct.unpack('<5I',pe.get_data(0x55ec3c-0x400000,20))]
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'switches':switches,'help_aliases':aliases,'network_prefixes':prefixes,
            'port_scan_format':string(0x53d68c),'network_argument_error':string(0x53d764)}
    assert result['binaries']['original']['network_prefixes']==result['binaries']['official_modern']['network_prefixes']
    modern=result['binaries']['official_modern']['switches']
    assert [(r['index'],r['text']) for r in modern if r['text']]==[(0,'-driver='),(11,'-nomovies')]
    assert result['binaries']['original']['help_aliases']==result['binaries']['official_modern']['help_aliases']
    (ROOT/'analysis/evidence/audits/original-modern-command-line.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: baselines, 33 paired switch slots, help aliases and parser spans')


if __name__=='__main__':main()
