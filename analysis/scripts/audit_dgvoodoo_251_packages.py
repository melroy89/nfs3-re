"""Inspect packaged140/150 dgVoodoo metadata, not wrapper execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dgvoodoo-251-packages','versions':{}};blobs=[]
    for version,pin,size in [('1.4.0','8cfb00c6de02b8fb8eb255b7f4d8053eefea7aadf1dd2de32674cbc269ebe525',81920),('1.5.0','541b3b367e2fecf6b982ffc1dc300960f3f2fdeeda203186b361fe3608e757c9',83456)]:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==HISTORY[version][0]
        member='drivers/dgvoodoo/glide3x.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert len(raw)==size and sha(raw)==pin
        pe=pefile.PE(data=raw);assert pe.FILE_HEADER.Machine==0x14c;blobs.append(raw)
        tables=[t.entries for group in pe.FileInfo for info in group for t in getattr(info,'StringTable',[])]
        assert tables and all(t[b'ProductVersion']==b'2.5.1.0'and t[b'FileVersion']==b'3.10.0.0'and t[b'ProductName']==b'dgVoodoo'and b'Napalm'in t[b'FileDescription']for t in tables)
        result['versions'][version]={'archive':rel,'archive_sha256':HISTORY[version][0],'member':member,'bytes':size,'sha256':pin,
            'version_tables':[{k.decode():v.decode('utf-8')for k,v in t.items()}for t in tables],
            'wip_ascii_count':raw.lower().count(b'wip'),'wip_utf16le_count':raw.lower().count('WIP'.lower().encode('utf-16le')),
            'sections':[{'name':s.Name.rstrip(b'\0').decode(),'rva':f'{s.VirtualAddress:08x}','raw_bytes':s.SizeOfRawData,'sha256':sha(s.get_data())}for s in pe.sections]}
    assert blobs[0]!=blobs[1]
    result['comparison']={'identical_files':False,'size_delta':len(blobs[1])-len(blobs[0]),'product_version_equal':True,'file_version_equal':True}
    result['limits']=['Version resources identify packaged claims,not authenticated upstream build ancestry or complete semantics.',
        'WIP16 build identity unverified;absence of WIP literals does not disprove vendor attribution.',
        'Different bytes/sizes with equal versions do not identify changed wrapper behavior.',
        'No DLL/API/game execution,installation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/dgvoodoo-251-packages.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:140/150 wrappers identify dgVoodoo2.51 Napalm but have different hashes/sizes;WIP16 unverified')


if __name__=='__main__':main()
