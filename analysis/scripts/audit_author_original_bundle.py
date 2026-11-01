"""Inventory an author-hosted original-reference bundle without execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    archive=ROOT/'analysis/captures/modern-differences/upstream/history/nfs3_orig.7z'
    expected='374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'
    assert sha(archive.read_bytes())==expected
    listing=subprocess.check_output(['7z','l','-slt',str(archive)],text=True)
    names=[]
    for block in listing.split('\n\n'):
        fields=dict(line.split(' = ',1) for line in block.splitlines() if ' = ' in line)
        if 'Size' in fields and 'Path' in fields and not fields.get('Attributes','').startswith('D'):
            names.append(fields['Path'])
    assert len(names)==98 and len(set(n.lower() for n in names))==98
    result={'kind':'author-hosted-original-reference-bundle','url':'https://veg.by/files/nfs3/nfs3_orig.7z',
        'archive':str(archive.relative_to(ROOT)),'archive_bytes':archive.stat().st_size,
        'archive_sha256':expected,'members':[],
        'limits':['Author-hosted bundle identity, not pristine retail provenance or publisher-signature verification.',
                  'Includes later nGlide patch files and a wrapper; timestamps are not authenticated build dates.',
                  'Member/PE metadata only; no DLL equivalence, installation, loading, execution or database mutation.']}
    for name in names:
        raw=subprocess.check_output(['7z','x','-so',str(archive),name])
        row={'member':name,'bytes':len(raw),'sha256':sha(raw)}
        if name.lower().endswith(('.exe','.dll')):
            pe=pefile.PE(data=raw)
            exports=getattr(pe,'DIRECTORY_ENTRY_EXPORT',None)
            row['pe']={'machine':f'{pe.FILE_HEADER.Machine:04x}',
                'image_base':f'{pe.OPTIONAL_HEADER.ImageBase:08x}',
                'entry_rva':f'{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08x}',
                'sections':[s.Name.rstrip(b'\0').decode('latin1') for s in pe.sections],
                'named_exports':[e.name.decode('ascii') for e in exports.symbols if e.name] if exports else []}
        result['members'].append(row)
    exe=next(r for r in result['members'] if r['member']=='nfs3.exe')
    assert exe['sha256']=='8ace9af9d197a938f0ddd6b013f552104d23b34580b900a52f052ed800938fe2'
    supplied=(ROOT/SPECS['original'][0]).read_bytes()
    hosted=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe'])
    assert sha(supplied)==SPECS['original'][1] and len(supplied)==len(hosted)==1589248
    differences=[i for i,(a,b) in enumerate(zip(supplied,hosted)) if a!=b]
    assert differences==[0xb579b] and supplied[0xb579b]==0x75 and hosted[0xb579b]==0xeb
    assert pefile.PE(data=hosted).get_rva_from_offset(0xb579b)+0x400000==0x4b639b
    result['supplied_original_comparison']={'supplied_sha256':sha(supplied),
        'hosted_sha256':sha(hosted),'same_length':True,'differing_bytes':1,
        'offset':'000b579b','va':'004b639b','supplied_byte':'75','hosted_byte':'eb',
        'instruction_change':'JNE rel8 becomes JMP rel8 with unchanged displacement5a; intent/runtime consequence not established here.'}
    dlls=[r['member'] for r in result['members'] if r['member'].lower().endswith('.dll')]
    assert sorted(dlls)==['d3da.dll','eacsnd.dll','glide3x.dll','softtria.dll','voodoo2a.dll']
    result['supplied_original_exe_matches_by_sha256']=False
    result['menu_count']=sum(r['member'].lower().endswith('.mnu') for r in result['members'])
    assert result['menu_count']==80
    result['next_comparison_candidates']={'d3da.dll':'final drivers/dx5 member, subject to explicit pairing',
        'softtria.dll':'final drivers/softtri member, subject to explicit pairing',
        'voodoo2a.dll':'final Glide driver, subject to explicit pairing',
        'menus':'case-normalized paired member inventory, without assuming backups are pristine'}
    (ROOT/'analysis/evidence/audits/author-original-bundle.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:98 file identities, one-byte EXE variant, five DLLs and{result["menu_count"]} menu members; no execution')


if __name__=='__main__':main()
