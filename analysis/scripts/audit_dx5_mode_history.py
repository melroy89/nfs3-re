"""Pin131/140 DX5 mode callback history; static inspection only."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_screenshot_counter_history import PINS
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    result={'kind':'static-dx5-mode-history','versions':{}};images=[]
    specs=[('1.3.1','dx5.dll','f7f1d79336125c3bac457735939abd78b16930c9341db52280f54d3bf2937c04'),
           ('1.4.0','dx5a.dll','ad46a5b43871be8cc187da11f55b6f4a13b2ba4750baf3649324f12a0127ebb6')]
    for version,name,pin in specs:
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        assert sha((ROOT/rel).read_bytes())==PINS[version][0]
        member='drivers/dx5/'+name;raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),member]);assert sha(raw)==pin
        pe=pefile.PE(data=raw);images.append(pe);old=version=='1.3.1';get=lambda a,n:pe.get_data(a-0x60000000,n)
        assert get(0x60001808 if old else 0x60001804,3).hex()==('833a1e'if old else'833a64')
        assert get(0x6000181a if old else 0x60001816,5).hex()==('394f08776a'if old else'394f0875dd')
        if old:assert get(0x60001824,20).hex()=='3d80020000750d81fbe00100007505b910000000'
        for addr in [0x60001b80,0x600021da]:assert get(addr,5).hex()==('bbb0040000'if old else'bba00f0000')
        spans=[('callback',0x600017bc,0x60001895 if old else 0x6000187d),
               ('first_setup',0x60001b80,0x60001c52),('second_setup',0x600021da,0x60002288),
               ('classifier',0x600025f0,0x600026b1)]
        result['versions'][version]={'archive':rel,'archive_sha256':PINS[version][0],'member':member,'sha256':pin,
            'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','hex':get(a,b-a).hex(),
             'sha256':sha(get(a,b-a)),'disassembly':disassemble(get(a,b-a),a)}for n,a,b in spans]}
    assert images[0].get_data(0x25f0,0xc1)==images[1].get_data(0x25f0,0xc1)
    finalrel='analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha((ROOT/finalrel).read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    final=subprocess.check_output(['7z','x','-so',str(ROOT/finalrel),'drivers/dx5/dx5a.dll'])
    assert sha(final)=='6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42'
    assert images[1].get_data(0x17bc,0xc1)==pefile.PE(data=final).get_data(0x17bc,0xc1)
    result['final_callback_match']={'archive':finalrel,'member_sha256':sha(final),'start':'600017bc','bytes':193}
    result['findings']=['New-key count guard changes unsigned30 to100;both setup clear requests1200 to4000.',
        '131 equal-width/height path rejects when stored depth is unsigned greater than incoming;otherwise overwrites that row.',
        '140 unequal raw depth continues scanning,allowing separate depth keys;classifier3 conversion to15 occurs after comparison.',
        '131 forces640x480 stored depth16 before possible classifier3 override;140 removes that forced-depth block.',
        'Complete classifier retained;140 callback retained in official final.']
    result['limits']=['Not a proof that131 lacks all16-bit modes;classifier and seed paths already allow them.',
        'Threshold not visible row count;initial count,reserved slots,matching and capacity ownership remain separate.',
        'No actual enumeration,device acceptance,all-consumer safety or rendered output tested;no target execution or binary edits.']
    (ROOT/'analysis/evidence/audits/dx5-mode-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:131/140 DX5 threshold,depth-key and clear-request changes;140 callback retained final')


if __name__=='__main__':main()
