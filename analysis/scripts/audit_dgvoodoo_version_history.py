"""Static packaged dgVoodoo identity1.5.3->1.6.0; no component execution."""
import hashlib
import json
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT

MEMBERS=['drivers/dgvoodoo/glide3x.dll','drivers/dgvoodoo/dgvoodooconf.exe',
         'drivers/dgvoodoo/voodoo2a.dll','drivers/dgvoodoo/thrash.ini','drivers/dgvoodoo/dgvoodoo.conf']


def main():
    a=json.loads((ROOT/'analysis/evidence/audits/language-fallback-history.json').read_text())['packages']['1.5.3']
    b=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())['packages']['1.6.0']
    specs={'1.5.3':(a['archive'],a['archive_sha256']),'1.6.0':(b['archive_path'],b['archive_sha256'])}
    result={'kind':'historical-dgvoodoo-version-identity','versions':{},
        'limits':['Packaged metadata identification, not upstream signature/build authentication.',
                  'No wrapper, setup utility, driver, config parser or game execution.',
                  'No claim about performance, compatibility or all provider code changes.']}
    blobs={}
    for version,(relative,expected) in specs.items():
        archive=ROOT/relative;assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
        rows=[]
        for member in MEMBERS:
            raw=subprocess.check_output(['7z','x','-so',str(archive),member]);blobs[version,member]=raw
            row={'member':member,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            if member in MEMBERS[:2]:
                pe=pefile.PE(data=raw)
                tables=[t.entries for group in pe.FileInfo for info in group for t in getattr(info,'StringTable',[])]
                product=b'2.5.1.0' if version=='1.5.3' else b'2.5.3.0'
                assert tables and all(t[b'ProductVersion']==product for t in tables)
                row['version_strings']=[{k.decode():v.decode('utf-8')for k,v in t.items()
                    if k in (b'ProductName',b'ProductVersion',b'FileVersion',b'FileDescription')}for t in tables]
            rows.append(row)
        result['versions'][version]={'archive':relative,'archive_sha256':expected,'members':rows}
    result['component_comparison']=[{'member':m,'identical':blobs['1.5.3',m]==blobs['1.6.0',m]}for m in MEMBERS]
    assert blobs['1.5.3',MEMBERS[2]]==blobs['1.6.0',MEMBERS[2]]
    assert blobs['1.5.3',MEMBERS[3]]==blobs['1.6.0',MEMBERS[3]]
    old,new=[blobs[v,MEMBERS[4]]for v in specs]
    assert len(old)==127 and len(new)==128 and old[:4]==new[:4]==b'DEGE'
    result['binary_config']={'old_hex':old.hex(),'new_hex':new.hex(),
        'changed_shared_offsets':[{'offset':i,'old':a,'new':b}for i,(a,b)in enumerate(zip(old,new))if a!=b],
        'appended_hex':new[len(old):].hex(),'field_meanings':'Unresolved; byte evidence only'}
    (ROOT/'analysis/evidence/audits/dgvoodoo-version-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned archives, wrapper/setup product2.51->2.53, adapter/INI equality and binary config delta')


if __name__=='__main__':main()
