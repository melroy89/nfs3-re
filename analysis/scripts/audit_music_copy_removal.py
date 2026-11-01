"""Static removed music-copy routine and direct-source suffix construction."""
import hashlib,json,struct
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-music-copy-removal','binaries':{}};images={}
    for label,(relative,digest,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw);images[label]=pe
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        spans=[(0x410030,0x410329),(0x4107c0,0x4109cc if label=='original' else 0x41099b),
               (0x4e2de0,0x4e2e1a),(0x4e2e20,0x4e2e5a)]
        strings={f'{a:08x}':pe.get_string_at_rva(a-0x400000).decode() for a in [0x536880,0x536898,0x5368a4,0x5368e8,0x5368f0,0x5368f8,0x536900,0x54a244,0x54a250]}
        assert list(strings.values())==(['%stemp.mus','rock.mus','tech.mus'] if label=='original' else ['','',''])+['.lin','.map','.mus','%stemp','readhandle','writehandle']
        result['binaries'][label]={'path':relative,'sha256':digest,'strings':strings,
            'captures':[{'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),
                         'hex':get(a,b).hex(),'disassembly':disassemble(get(a,b),a)}for a,b in spans]}
    old,new=images.values()
    def data(pe,a,b):return pe.get_data(a-0x400000,b-a)
    assert data(new,0x410030,0x410329)==b'\x90'*761
    assert data(old,0x410046,0x41004b).hex()=='ba00000800'
    for site,target in [(0x410230,0x4e43a0),(0x41025f,0x4e28d0),(0x410270,0x4e2ae0),
                        (0x410297,0x4e2e60),(0x4102a2,0x4e2de0),(0x4102b0,0x4e2e20)]:
        b=data(old,site,site+5);assert b[0]==0xe8 and site+5+int.from_bytes(b[1:],'little',signed=True)==target
    assert data(old,0x410917,0x410925).hex()=='6834277a0068006953008d457e50'
    assert data(new,0x410917,0x410930).hex()=='bef86853008b9d7e0100008d557e5729c949b000f2ae83ef05'
    assert data(new,0x410930,0x410932).hex()=='eb15'
    assert data(old,0x410947,0x410960)==data(new,0x410947,0x410960)
    for a,b in [(0x4e2de0,0x4e2e1a),(0x4e2e20,0x4e2e5a)]:assert data(old,a,b)==data(new,a,b)
    result['verified']=['Original761-byte copy routine replaced entirely with NOPs.',
        'Original source path ends rock.mus/tech.mus; destination formatting uses %stemp.mus.',
        'Original requests512KiB chunk capacity, seeks source, reads into buffer, writes buffer to destination and loops until final-block/abort condition.',
        'Read/write calls have no immediate return tests in the loop; complete successful-copy semantics not established.',
        'Original start formats %stemp then appends .mus; Modern retains source prefix and replaces last four suffix bytes with .mus.',
        'The append loop at00410947 is retained; Modern SUB EDI,5 follows a scan including NUL, positioning at the four-byte suffix.']
    result['limits']=['No game, file-copy, audio, API or extracted instruction execution.',
        'Handle backend dispatch, source-size query, path validity and error/short-I/O outcomes not fully qualified.',
        'No fixed10MiB total, measured time/SSD-write savings or proof about original design motive.',
        'Direct-source filename request does not establish successful stream opening/playback or absence of every other copy path.',
        'Caller admission, all lifecycle cleanup, malformed paths and1.0.0 introduction remain unverified.',
        'Global path buffers, encoded file handles and custom register contracts need preservation in reconstruction.']
    (ROOT/'analysis/evidence/audits/music-copy-removal.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:761-byte copy removal,512KiB chunk request, paired path strings and direct-source suffix replacement')


if __name__=='__main__':main()
