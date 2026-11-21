"""Bounded inspection of the original-reference appended debug carrier; never executes it."""
import hashlib,json,struct,subprocess,tempfile
import pefile
from audit_thrash_loader_difference import ROOT


def sha(raw):return hashlib.sha256(raw).hexdigest()


def uleb(raw,pos,end):
    value=shift=0
    while pos<end:
        byte=raw[pos];pos+=1;value|=(byte&127)<<shift
        if byte<128:return value,pos
        shift+=7;assert shift<35
    raise AssertionError('Truncated ULEB')


def main():
    rel='analysis/captures/modern-differences/upstream/history/nfs3_orig.7z';archive=ROOT/rel
    assert sha(archive.read_bytes())=='374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'
    raw=subprocess.check_output(['7z','x','-so',str(archive),'softtria.dll']);assert sha(raw)=='8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02'
    pe=pefile.PE(data=raw);overlay=raw[275968:];assert len(overlay)==28514
    info=overlay[252:22732];abbrev=overlay[22732:22770];entries={};pos=0
    while pos<len(abbrev):
        code,pos=uleb(abbrev,pos,len(abbrev));assert code and code not in entries
        tag,pos=uleb(abbrev,pos,len(abbrev));children=abbrev[pos];pos+=1;attrs=[]
        while True:
            attr,pos=uleb(abbrev,pos,len(abbrev));form,pos=uleb(abbrev,pos,len(abbrev))
            if (attr,form)==(0,0):break
            assert attr and form in (1,8,12,16);attrs.append((attr,form))
        entries[code]=(tag,children,attrs)
    assert entries=={1:(17,1,[(16,16),(3,8)]),2:(17,1,[(3,8)]),3:(10,0,[(17,1),(63,12),(3,8)]),4:(52,0,[(17,1),(63,12),(3,8)])}
    records=[];units=[];pos=0
    while pos<len(info):
        start=pos;length=struct.unpack_from('<I',info,pos)[0];end=pos+4+length;assert end<=len(info);pos+=4
        version,offset,address_size=struct.unpack_from('<HIB',info,pos);pos+=7;assert(version,offset,address_size)==(2,0,4)
        first=len(records);nulls=0
        while pos<end:
            entry_offset=pos;code,pos=uleb(info,pos,end)
            if code==0:nulls+=1;continue
            tag,children,attrs=entries[code];values={}
            for attr,form in attrs:
                if form in (1,16):assert pos+4<=end;value=struct.unpack_from('<I',info,pos)[0];pos+=4
                elif form==12:assert pos<end;value=info[pos];pos+=1
                else:
                    stop=info.index(0,pos,end);value=info[pos:stop].decode('latin1');pos=stop+1
                values[str(attr)]=value
            assert pos<=end;records.append({'unit_offset':start,'entry_offset':entry_offset,'tag':tag,'abbreviation':code,'attributes':values})
        assert pos==end and records[first]['tag']==17
        units.append({'offset':start,'length':length,'records':len(records)-first,'null_entries':nulls})
    assert len(units)==173 and len(records)==1034
    by_name={r['attributes'].get('3'):r for r in records if r['tag']==10};anchors=[]
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        expected=exp.name.decode().replace('_THRASH_','_SOFTTRI_',1)
        if expected in by_name:
            row=by_name[expected];stored=row['attributes']['17'];assert stored+0x1000==exp.address
            anchors.append({'export':exp.name.decode(),'debug_name':expected,'stored_address':stored,'export_rva':f'{exp.address:08x}','entry_offset':row['entry_offset']})
    assert len(anchors)>=20
    with tempfile.NamedTemporaryFile(suffix='.elf')as f:
        f.write(overlay);f.flush();run=subprocess.run(['readelf','--debug-dump=info',f.name],capture_output=True,text=True)
    result={'kind':'static-softtri-reference-debug-inspection','archive':rel,'archive_sha256':sha(archive.read_bytes()),'member_sha256':sha(raw),'overlay_sha256':sha(overlay),
        'abbreviation_hex':abbrev.hex(),'abbreviation_terminating_zero_entry_present':False,'parser_policy':'Accept exact declared abbreviation extent after four bounded definitions;no bytes appended or repaired.',
        'units':units,'records':records,'tag_counts':{str(t):sum(r['tag']==t for r in records)for t in [17,10,52]},'export_address_anchors':anchors,
        'stock_reader':{'version':subprocess.check_output(['readelf','--version'],text=True).splitlines()[0],'exit_code':run.returncode,'stdout':run.stdout,'stderr_sha256':sha(run.stderr.encode()),'distinct_stderr_lines':sorted(set(run.stderr.splitlines()))},
        'limits':['Custom bounded record extraction,not a complete DWARF implementation or validation of every debug address.',
            'Stored addresses plus1000h match listed exports;general mapping for all records remains inferred.',
            'Names/source paths do not supply source code,types,full signatures or final-version ABI contracts.',
            'Reference provenance is author-hosted,not authenticated pristine retail;no Ghidra labels or game bytes changed.',
            'No ELF/PE/target instruction execution;readelf is a static host inspection tool.']}
    (ROOT/'analysis/evidence/audits/softtri-reference-debug.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:173 debug units,1034 bounded records,{len(anchors)} export address anchors;stock reader exit{run.returncode},original bytes preserved')


if __name__=='__main__':main()
