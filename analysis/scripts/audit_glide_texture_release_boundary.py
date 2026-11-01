"""Static author-hosted1.4.0/1.5.0 Glide texture-table boundary, no loading."""
import json
import struct
import subprocess
import pefile
from audit_dx5_reference_final import sha, intervals, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs=[('1.4.0','8181722b8aadd9b7a0a5de6f9d16a6db4034c71ef755aec21d4d64b76e933aa9',
            '67764a56917fd93fffb847968f2cf90cff7c0fd8ab812d99403bfa88ef0208d3',0x100f4,0x10110,0x10134,9),
           ('1.5.0','de6cbbbce4b77765f96472aaf8c12a4e245e2abceaf26dd9b84215442b1f4a0f',
            'bea4abc9ff9b3e54ed304d2fd05d6be7005e1933b209e5a3975da4f897b67fab',0xfe34,0xfe40,0xfe70,12)]
    result={'kind':'static-historical-glide-texture-boundary','releases':{},'function_changes':[]}
    images=[]
    for version,archive_sha,dll_sha,lod,square,side,count in specs:
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/relative;assert sha(archive.read_bytes())==archive_sha
        member='drivers/glide3x/voodoo2a.dll'
        raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==dll_sha
        pe=pefile.PE(data=raw);images.append(pe)
        exports={x.name.decode():x.address for x in pe.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
        assert exports['_THRASH_talloc@20']==0x24e0
        row={'archive':relative,'url':f'https://veg.by/files/nfs3/nfs3_modern_patch_v{version}.7z',
             'archive_sha256':archive_sha,'member':member,'member_sha256':dll_sha,
             'member_bytes':len(raw),'tables':{},'captures':[],'named_exports':exports}
        for label,rva,width,values in [('lod',lod,1,list(range(count))),
                                      ('square',square,4,[4**i for i in range(count)]),
                                      ('side',side,4,[2**i for i in range(count)])]:
            data=pe.get_data(rva,count*width)
            assert (list(data) if width==1 else list(struct.unpack('<'+'I'*count,data)))==values
            row['tables'][label]={'address':f'{0x60000000+rva:08x}','values':values,'bytes_hex':data.hex(),'sha256':sha(data)}
        for start,end,label in [(0x24e0,0x2654,'complete-talloc'),(0x2660,0x26dd,'complete-upload-loop')]:
            body=pe.get_data(start,end-start)
            row['captures'].append({'label':label,'start':f'{0x60000000+start:08x}',
                'end_exclusive':f'{0x60000000+end:08x}','sha256':sha(body),'disassembly':disassemble(body,0x60000000+start)})
        result['releases'][version]=row
    assert result['releases']['1.4.0']['named_exports']==result['releases']['1.5.0']['named_exports']
    for start,end,sites in [(0x24e0,0x2654,[0x60002526,0x60002536]),(0x2660,0x26dd,[0x60002688,0x600026c3])]:
        changes=intervals(images[0].get_data(start,end-start),images[1].get_data(start,end-start),0x60000000+start)
        assert [int(x['start_va'],16) for x in changes]==sites
        assert sum(len(x['reference_hex'])//2 for x in changes)==6
        result['function_changes'].append({'start':f'{0x60000000+start:08x}','changed_bytes':6,'intervals':changes})
    result['conclusion']='Named author-hosted1.4.0->1.5.0 driver member expands9-entry tables through256 to12 entries through2048, with only table-address changes in these two complete functions.'
    assert [x['sha256'] for x in result['releases']['1.5.0']['captures']]==[
        'b9d5f4e0eb0d8780db31f85b56a4bba4f79499a598fb74c37b37ca6fcd040dd6',
        'cc8b7b6a5b9067dd51b0f7faea515adae861aad07c26002b24287dfa5d3371d3']
    result['existing_final_evidence_reuse']='Both1.5.0 function-body hashes match the corresponding pinned final bodies in glide-reference-identity.json; not whole-DLL equality.'
    result['limits']=['Archive release names/source identify the compared packages, not publisher signatures or authenticated development chronology.',
        'No assertion about every earlier beta/branch or other renderer member.',
        'No provider acceptance, larger-texture upload execution, rendered quality or complete driver equivalence.',
        'Archives read without loading/installing/executing contents; original EXEs and saved Ghidra state preserved.']
    (ROOT/'analysis/evidence/audits/glide-texture-release-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.4.0/1.5.0 archives/members; tables expand9->12; two complete functions differ only by table addresses')


if __name__=='__main__':main()
