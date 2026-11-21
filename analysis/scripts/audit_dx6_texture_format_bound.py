"""Bind120 DX6 format callback to its100-entry guard; no target execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    rel='analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.2.0.7z';ah='151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b'
    assert sha((ROOT/rel).read_bytes())==ah
    member='drivers/dx6/dx6.dll';raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member]);pin='81cc2b24972d37efca68ad277b714f5053672994df1ed266c529e1e24cd3420f';assert sha(raw)==pin
    p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x60000000,b-a)
    assert get(0x60007092,0x600070a3).hex()=='8b2d80b8016031c083fd640f8382010000'
    assert get(0x600070ab,0x600070bb).hex()=='69d59c0000008dba88d10360b127f3ab'
    assert get(0x600070bb,0x600070c7).hex()=='89de8dbad0d10360b108f3a5'
    assert get(0x6000721c,0x6000722a).hex()=='455f892d80b801605e5d5bc20800'
    assert get(0x60006e65,0x60006e78).hex()=='689070006050c70580b8016000000000ff5120'
    spans=[('registration_and_reset',0x60006e5a,0x60006e78),('complete_callback',0x60007090,0x6000722a)]
    table=0x6003d188;stride=156;end=table+100*stride;s=p.get_section_by_rva(table-0x60000000)
    result={'kind':'static-dx6-texture-format-bound','archive':rel,'archive_sha256':ah,'member':member,'sha256':pin,
        'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans],
        'layout':{'count':'6001b880','table':f'{table:08x}','stride_bytes':stride,'guard_unsigned_count_limit':100,'ordinary_record_indices':[0,99],'end_exclusive_at100':f'{end:08x}','record_zeroing_bytes':156,'input_copy_bytes':32,'input_copy_record_offset':72,'section':s.Name.rstrip(b'\0').decode(),'section_rva':f'{s.VirtualAddress:08x}','raw_size':s.SizeOfRawData,'virtual_size':s.Misc_VirtualSize},
        'limits':['Source claim belongs to DX6 subsection,not DX5;no prepatch NFS4 DX6 binary is available in the inspected reference/110 archives.',
            'Local100 guard and reset/callback registration verified;historical guard addition,old allocation or reproduced crash not established.',
            'Ordinary synchronous count progression assumed;all writers,concurrency/reentrancy and pointer validity are not proved.',
            'No guarantee malformed zero channel masks terminate interior loops;not a complete format-validation audit.',
            'No provider/API/game/instruction execution,compilation or binary/Ghidra mutation.']}
    (ROOT/'analysis/evidence/audits/dx6-texture-format-bound.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:120 DX6 callback registration,count reset,unsigned100 guard and156-byte record layout verified;prepatch/crash unverified')


if __name__=='__main__':main()
