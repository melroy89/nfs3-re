"""Bounded absolute float-centre reference inventory; static bytes/disassembly only."""
import hashlib
import json
import re
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def main():
    result={'kind':'absolute-float-projection-centre-references','binaries':{},
            'limits':['Complete executable literal search with disassembly corroboration, not a computed-alias analysis.',
                      'No external modules, runtime-generated code, invocation order or rendering observed.']}
    kinds={'d905':'FLD read','d805':'FADD read','d825':'FSUB read','d91d':'FSTP write'}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        asm=subprocess.check_output(['objdump','-d','-Mintel',relative],cwd=ROOT,text=True)
        lines={int(m[1],16):line for line in asm.splitlines()
               if (m:=re.match(r'\s*([0-9a-f]+):',line))}
        targets=[]
        for address in (0x5600a4,0x5600a8):
            off=0;rows=[]
            while True:
                off=raw.find(struct.pack('<I',address),off)
                if off<0:break
                opcode=raw[off-2:off].hex();assert opcode in kinds
                va=pe.get_rva_from_offset(off-2)+0x400000
                line=lines[va];assert f'0x{address:x}' in line
                assert kinds[opcode].split()[0].lower() in line
                rows.append({'instruction_va':f'{va:08x}','operand_file_offset':off,
                             'kind':kinds[opcode],'encoding':raw[off-2:off+4].hex(),
                             'disassembly':line.strip()})
                off+=1
            counts={kind:sum(r['kind']==kind for r in rows) for kind in kinds.values()}
            assert len(rows)==40 and counts['FSTP write']==2
            expected_sites=([0x421415,0x4bf2a0] if address==0x5600a4 else [0x421425,0x4bf2a6]) if label=='original' else ([0x4213e6,0x4bf2a0] if address==0x5600a4 else [0x4213f2,0x4bf2a6])
            assert [int(r['instruction_va'],16) for r in rows if r['kind']=='FSTP write']==expected_sites
            targets.append({'address':f'{address:08x}','counts':counts,'references':rows})
        result['binaries'][label]={'path':relative,'sha256':expected,'targets':targets}
    (ROOT/'analysis/evidence/audits/projection-centre-references.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:80 corroborated absolute centre references per binary, four stores per binary in two known functions')


if __name__=='__main__':main()
