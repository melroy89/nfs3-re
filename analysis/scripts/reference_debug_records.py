"""Narrow parser for the four-form debug carriers in pinned renderer references."""
import struct

def uleb(raw,pos,end):
    value=shift=0
    while pos<end:
        byte=raw[pos];pos+=1;value|=(byte&127)<<shift
        if byte<128:return value,pos
        shift+=7;assert shift<35
    raise AssertionError('Truncated ULEB')



def parse_debug_overlay(overlay):
    assert overlay[:7]==b'\x7fELF\x01\x01\x01'
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',overlay)
    assert header[1:4]==(2,3,1) and header[6]==52 and header[11:14]==(40,5,4)
    sections=[struct.unpack_from('<10I',overlay,52+i*40)for i in range(5)]
    sh=sections[4];assert sh[4]+sh[5]<=len(overlay);names=overlay[sh[4]:sh[4]+sh[5]];data={}
    for sh in sections[1:]:
        assert sh[4]+sh[5]<=len(overlay)
        name=names[sh[0]:names.index(0,sh[0])].decode();assert name not in data
        data[name]=overlay[sh[4]:sh[4]+sh[5]]
    info=data['.debug_info'];abbrev=data['.debug_abbrev']
    entries={};pos=0
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
    return units,records,abbrev
