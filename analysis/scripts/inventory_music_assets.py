"""Inventory supplied local audio assets; no decoding, playback or provenance claim."""
import hashlib
import json
from audit_thrash_loader_difference import ROOT


def main():
    relative='nfs3_decomp.rep/Electronic Arts/Need For Speed III/GAMEDATA/AUDIO/PC'
    directory=ROOT/relative
    files=[]
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.upper() in ('.MUS','.MAP','.LIN'):
            raw=path.read_bytes()
            files.append({'name':path.name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'first_16_bytes':raw[:16].hex()})
    names={row['name'].upper() for row in files}
    pairs=[]
    for stem in ('HOME','LOST','ATLA','ALPI','EMPR'):
        row={'stem':stem.lower(),'styles':{}}
        for style in ('ROCK','TECH'):
            expected=[f'{stem}{style}{suffix}' for suffix in ('.MUS','.MAP','.LIN')]
            assert all(name in names for name in expected)
            row['styles'][style.lower()]=expected
        pairs.append(row)
    result={'kind':'local-audio-asset-inventory','directory':relative,'files':files,'race_pairs':pairs,
            'limits':['Local supplied installation, not authenticated original or official Modern package provenance.',
                      'Existence and hashes only; no audio decoding, track-title metadata interpretation or playback.',
                      'No claim that these assets changed between executable versions.']}
    (ROOT/'analysis/evidence/inventories/local-music-assets.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(files)} local assets inventoried; five race stem/style triples present')


if __name__=='__main__':main()
