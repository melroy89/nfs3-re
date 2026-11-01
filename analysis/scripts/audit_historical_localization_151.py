"""Parse all six retained1.5.0/1.5.1 text assets; no game/text-loader execution."""
import hashlib
import json
import struct
import subprocess
from audit_thrash_loader_difference import ROOT
from audit_historical_lockwindow_failure import ARCHIVES


def parse(raw):
    first=struct.unpack_from('<I',raw)[0]
    assert first%4==0
    count=first//4
    assert count in (1936,1941)
    offsets=struct.unpack_from('<'+'I'*count,raw)
    assert offsets[0]==first and all(a<b for a,b in zip(offsets,offsets[1:]))
    records=[]
    for i,offset in enumerate(offsets):
        end=raw.index(0,offset)
        bound=offsets[i+1] if i+1<count else len(raw)
        assert end+1==bound
        records.append(raw[offset:end])
    return offsets,records


def display(raw):
    return {'hex':raw.hex(),'latin1_display':raw.decode('latin1')}


def main():
    result={'kind':'historical-localization-151','archives':{},'languages':{},
            'indexing':'zero-based positional entries, not independently named game string IDs',
            'limits':['Static packaged assets only; no game loader/rendering or translation-quality review.',
                      'Latin1 is a reversible display convention, not proof of game font/encoding.',
                      'Five added records and changed existing indices do not independently verify every advertised correction.']}
    assets={}
    for version,expected in ARCHIVES.items():
        relative=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        path=ROOT/relative
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        result['archives'][version]={'path':relative,'sha256':expected}
        for lang in ('eng','ger','fre','spa','ita','swe'):
            member=f'fedata/text/text.{lang}'
            raw=subprocess.check_output(['7z','x','-so',str(path),member])
            offsets,records=parse(raw)
            assets[version,lang]=(offsets,records)
            result['languages'].setdefault(lang,{})[version]={'member':member,
                'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                'entries':len(records),'offset_table_bytes':offsets[0],
                'complete_payload_partition':True}
    for lang,row in result['languages'].items():
        old_offsets,old=assets['1.5.0',lang];new_offsets,new=assets['1.5.1',lang]
        changed=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
        assert changed==([1283,1932] if lang=='fre' else [1932])
        assert old[1932]==new[1936]==b'km'
        row['changed_existing']=[{'index':i,'old_offset':old_offsets[i],'new_offset':new_offsets[i],
            'old':display(old[i]),'new':display(new[i])}for i in changed]
        row['added']=[{'index':i,'offset':new_offsets[i],'value':display(new[i])}for i in range(len(old),len(new))]
    (ROOT/'analysis/evidence/audits/historical-localization-151.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('PASS: two archives, twelve complete text-table partitions, exact changed/additional entries')


if __name__=='__main__':
    main()
