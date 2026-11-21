"""Compare131/140 DX6 enumeration admission and sorting; no target execution."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dx6-mode-admission-history','versions':{}}
    specs=[('1.3.1','dx6.dll','81cc2b24972d37efca68ad277b714f5053672994df1ed266c529e1e24cd3420f'),
           ('1.4.0','dx6a.dll','d32ee0f11361977ecaa01402b33a0a1ea4f4732b118355a5b98696768f8d25cb')]
    for version,name,pin in specs:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/rel;ah=PINS[version][0];assert sha(archive.read_bytes())==ah
        member='drivers/dx6/'+name;raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==pin
        pe=pefile.PE(data=raw);assert pe.OPTIONAL_HEADER.ImageBase==0x60000000
        old=version=='1.3.1';get=lambda start,end:pe.get_data(start-0x60000000,end-start)
        spans=[('initializer',0x60001c50,0x60001cb7 if old else 0x60001c81),
               ('callback',0x60001cd0,0x60001db8 if old else 0x60001d90)]
        if old:
            assert get(0x60001d51,0x60001d56).hex()=='394f087756'
            assert get(0x60001c95,0x60001ca0).hex()=='b93cbd0360c70102000000'
            assert get(0x60001c72,0x60001c79).hex()=='c7420810000000'
            assert get(0x60001d3f,0x60001d44).hex()=='833a657368'
        else:
            assert get(0x60001d7a,0x60001d81).hex()=='89e0e87fc70000'
            assert get(0x60001c5f,0x60001c69).hex()=='c7053cbd036000000000'
            assert get(0x6000e52a,0x6000e539).hex()=='b903000000f3a77448770489c2ebda'
            spans.append(('insertion',0x6000e500,0x6000e59d))
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':member,'sha256':pin,
            'captures':[{'name':n,'start':f'{start:08x}','end_exclusive':f'{end:08x}','hex':get(start,end).hex(),
             'sha256':sha(get(start,end)),'disassembly':disassemble(get(start,end),start)}for n,start,end in spans]}
    result['findings']=[
        '131 initializer seeds640x480 with depth16 and sets count2;it already supports a16-bit seed.',
        '131 callback treats matching width/height as one key and rejects when stored depth is unsigned greater than incoming;otherwise overwrites.',
        '131 special640x480 branch has separate occupied-slot/depth16 admission;do not generalize the ordinary branch to every mode.',
        '140 callback builds a temporary40-byte record and calls insertion6000e500;new helper compares width,height,stored depth lexicographically as unsigned DWORDs.',
        '140 equal triple overwrites;different depth is a distinct key;new-key capacity100 and sorted insertion replace131 append/overwrite scan.',
        'Both callbacks convert classifier3 depth to15;140 conversion occurs before insertion key comparison.',
        '140 initializer removes fixed seed/count2,clears4000 bytes at6003f028 and resets insertion count0;131 clearing request is1200 bytes.']
    result['limits']=[
        'Static requested-record policy,not observed enumeration,available modes,device acceptance or menu order.',
        'No claim131 lacked all16-bit support;seed and callback already allow16-bit cases.',
        'Count/public leading-slot conventions and150 increment are separately audited;capacity is not visible-mode count.',
        'Classifier full semantics,all malformed descriptors,integer overflow/division failures,DF state,callback ordering and external lifetimes are not established here.',
        'No DLL/API/game/instruction execution,compilation or executable/Ghidra mutation.']
    (ROOT/'analysis/evidence/audits/dx6-mode-admission-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131/140 DX6 seed,depth-key and sorted insertion differences pinned;runtime unverified')


if __name__=='__main__':main()
