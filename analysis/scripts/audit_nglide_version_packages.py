"""Identify110/120/130/131/140/150 nGlide package versions and byte differences; static only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_endpoint_comma_history import HISTORY


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-nglide-version-packages','versions':{}};blobs={}
    specs=[('1.1.0','31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac','21e5b7e7f2554b876e2b9c9fa357111bde7b612e6ba8aefef70e1785795b6ed9',b'nGlide v1.04.1'),
        ('1.2.0','151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','e4a815c565ffd61d18974ea4d139390ee84ba6918b106c1835f861bb61872e5c',b'nGlide 1.04.2'),
        ('1.3.0','93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad','b042e03135ba45553aed5e8c93bf0ca0d2c7056d19e52fe7eee41a98dc849f1d',b'nGlide 1.04.3'),
        ('1.3.1',PINS['1.3.1'][0],'b042e03135ba45553aed5e8c93bf0ca0d2c7056d19e52fe7eee41a98dc849f1d',b'nGlide 1.04.3'),
        ('1.4.0',HISTORY['1.4.0'][0],'16865452af3bc41ae203f9f11808bd94820477070c011790b5fc66ad0e2963ad',b'nGlide v1.05'),
        ('1.5.0',HISTORY['1.5.0'][0],'87842a85d1bfda4217e691a9d4412915c74905eed818c5a727e2f2d6b814edb6',b'nGlide v1.05')]
    for version,ah,pin,label in specs:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel;assert sha(archive.read_bytes())==ah
        member='glide3x.dll'if version=='1.1.0'else'drivers/nglide/glide3x.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==pin;blobs[version]=raw
        pe=pefile.PE(data=raw);assert pe.FILE_HEADER.Machine==0x14c
        tables=[t.entries for group in pe.FileInfo for info in group for t in getattr(info,'StringTable',[])]
        assert tables and all(t[b'LegalCopyright']==label and t[b'FileVersion']==b'3.10.00.0658'and t[b'ProductVersion']==b'3.10.00.0658'for t in tables)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,'bytes':len(raw),'sha256':pin,
            'version_tables':[{k.decode():v.decode('utf-8')for k,v in t.items()}for t in tables],
            'sections':[{'name':s.Name.rstrip(b'\0').decode(),'rva':f'{s.VirtualAddress:08x}','raw_bytes':s.SizeOfRawData,'sha256':sha(s.get_data())}for s in pe.sections]}
    assert blobs['1.3.0']==blobs['1.3.1']
    assert len(blobs['1.2.0'])==len(blobs['1.3.0'])and blobs['1.2.0']!=blobs['1.3.0']
    result['120_130_comparison']={'bytes_each':len(blobs['1.2.0']),'changed_file_bytes':sum(a!=b for a,b in zip(blobs['1.2.0'],blobs['1.3.0'])),'label_before':'nGlide1.04.2','label_after':'nGlide1.04.3','130_131_byte_identical':True,'scope':'Package transition and metadata;minimize/restore implementation or safety not established.'}
    assert len(blobs['1.4.0'])==len(blobs['1.5.0'])and blobs['1.4.0']!=blobs['1.5.0']
    result['140_150_comparison']={'bytes_each':len(blobs['1.4.0']),'changed_file_bytes':sum(a!=b for a,b in zip(blobs['1.4.0'],blobs['1.5.0'])),'same_nglide_label':True}
    import configparser
    archive=ROOT/result['versions']['1.2.0']['archive'];paired={}
    for directory,adapter,adapter_hash,provider_hash in [
        ('nglide','nglide.dll','bf075c8deec77ce8f87ee76b11662f257dd5cc5e9d91bc69cfd4afcc36b4301b','e4a815c565ffd61d18974ea4d139390ee84ba6918b106c1835f861bb61872e5c'),
        ('dgvoodoo','voodoo2.dll','857f8dd4dd997006012ae233722f382068c6c41d20c2f3166ba2b5df79122cc0','3b6a477900cc16993df1262ea638f8a86a68dea16ec8cc6d0dc23072bc5b4bc2')]:
        provider_member=f'drivers/{directory}/glide3x.dll';provider=subprocess.check_output(['7z','x','-so',str(archive),provider_member]);assert sha(provider)==provider_hash
        adapter_member=f'drivers/{directory}/{adapter}';adapter_raw=subprocess.check_output(['7z','x','-so',str(archive),adapter_member]);assert sha(adapter_raw)==adapter_hash
        ini_member=f'drivers/{directory}/thrash.ini';ini=subprocess.check_output(['7z','x','-so',str(archive),ini_member]);cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read_string(ini.decode());assert cfg['THRASH']['File']==adapter and cfg['THRASH']['Type']=='voodoo'
        pe=pefile.PE(data=provider);metadata=[{k.decode():v.decode('utf-8')for k,v in t.entries.items()}for g in pe.FileInfo for info in g for t in getattr(info,'StringTable',[])]
        assert metadata
        if directory=='dgvoodoo':assert all(t['ProductVersion']=='2.4.4.0'and'dgVoodoo 2.44'in t['FileDescription']for t in metadata)
        paired[directory]={'provider_member':provider_member,'provider_sha256':provider_hash,'provider_bytes':len(provider),'version_tables':metadata,'adapter_member':adapter_member,'adapter_sha256':adapter_hash,'adapter_bytes':len(adapter_raw),'ini_member':ini_member,'ini_sha256':sha(ini),'ini_text':ini.decode()}
    result['120_provider_adapter_pairs']=paired
    result['limits']=['Packaged self-identification,not upstream signature/build authentication or implementation semantics.',
        'MP140-046 source says gGlide;association with packaged nGlide1.05 is inferred,not silently corrected.',
        'Different140/150 bytes do not establish the advertised NFS3-specific fixes or effective behavior.',
        '110 retained package label1.04.1 does not establish exact100 introduction or extended API behavior.',
        '120 bundles distinct provider/adapter pairs;configuration is not successful loading or physical hardware support.',
        'No wrapper/game/API execution,installation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/nglide-version-packages.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:110->150 nGlide labels;120 two provider/adapter pairs pinned;fix/API semantics unverified')


if __name__=='__main__':main()
