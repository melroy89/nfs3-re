"""Check131/140 package text-table inclusion; no target execution."""
import hashlib,json,struct,subprocess
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-language-asset-introduction','versions':{}}
    for version,(ah,_)in PINS.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        listing=subprocess.check_output(['7z','l','-slt',str(archive)],text=True)
        paths=[line[7:].replace('\\','/')for line in listing.splitlines()if line.startswith('Path = ')]
        selected=sorted(p for p in paths if p.lower().startswith('fedata/text/'))
        expected=['fedata/text/text.'+ext for ext in ['eng','fre','ger','ita','spa','swe']]
        assert selected==([]if version=='1.3.1'else expected)
        rows=[]
        for member in selected:
            raw=subprocess.check_output(['7z','x','-so',str(archive),member]);first=struct.unpack_from('<I',raw)[0]
            assert first>0 and first%4==0 and first<len(raw)
            count=first//4;offsets=struct.unpack_from('<'+'I'*count,raw)
            assert offsets[0]==first and all(a<b for a,b in zip(offsets,offsets[1:]))
            for i,offset in enumerate(offsets):
                bound=offsets[i+1]if i+1<count else len(raw)
                assert raw.index(0,offset)+1==bound
            rows.append({'member':member,'bytes':len(raw),'sha256':sha(raw),'table_bytes':first,'entry_count':count,
                'complete_partition':True})
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'matching_paths':selected,'assets':rows}
    result['verified']=['131 archive has no fedata/text/ members;140 includes exactly six named text assets.',
        'Every140 asset partitions fully into ascending little-endian offsets and individually NUL-terminated payloads.']
    result['limits']=['Package inclusion,not first availability in all distributions or proof131 cannot load externally installed language assets.',
        'No authenticated retail text comparison,translation-quality judgement,game codepage/font acceptance or actual loader execution.',
        'No game/API/target instructions executed;no executable or Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/language-asset-introduction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131 has no packaged text members;140 adds six fully partitioned text tables')


if __name__=='__main__':main()
