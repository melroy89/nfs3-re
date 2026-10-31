"""Decode the inspected 10fb RefPack stream for static logo asset auditing."""

def decode(s):
    assert s[:2]==b'\x10\xfb';size=int.from_bytes(s[2:5],'big');i=5;o=bytearray()
    while i<len(s):
     c=s[i];i+=1
     if c>=0xfc:
      n=c&3;o+=s[i:i+n];i+=n;break
     if c>=0xe0:
      n=((c&31)<<2)+4;o+=s[i:i+n];i+=n;continue
     if c>=0xc0:
      a,b,d=s[i:i+3];i+=3;n=c&3;length=((c&12)<<6)+d+5;off=((c&16)<<12)+(a<<8)+b+1
     elif c>=0x80:
      a,b=s[i:i+2];i+=2;n=a>>6;length=(c&63)+4;off=((a&63)<<8)+b+1
     else:
      a=s[i];i+=1;n=c&3;length=((c&28)>>2)+3;off=((c&96)<<3)+a+1
     o+=s[i:i+n];i+=n
     assert 0<off<=len(o)
     for _ in range(length):o.append(o[-off])
     assert len(o)<=size
    assert len(o)==size
    return bytes(o)
