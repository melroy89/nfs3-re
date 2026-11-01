"""Static intensity-to-packed-colour contract; models are derived, not probes."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from audit_dx5_reference_final import disassemble


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    result={'kind':'static-intensity-packed-color-contract','binaries':{}};bodies=[]
    for label,(relative,digest,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert sha(raw)==digest
        pe=pefile.PE(data=raw)
        def get(a,b):return pe.get_data(a-0x400000,b-a)
        body=get(0x49d800,0x49d8eb);bodies.append(body)
        assert get(0x53c698,0x53c6a0)==struct.pack('<d',65536.0)
        assert get(0x49d8d7,0x49d8e3).hex()=='8935e0e65500893ddce65500'
        assert body[0xe:0x15]==bytes.fromhex('f605583a7a00'+('40'if label=='original'else'50'))
        assert get(0x49d826,0x49d832).hex()=='dc5df8dfe09e0f86a5000000'
        result['binaries'][label]={'path':relative,'sha256':digest,
            'constant_0053c698_hex':get(0x53c698,0x53c6a0).hex(),
            'capture':{'start':'0049d800','end_exclusive':'0049d8eb','sha256':sha(body),'hex':body.hex(),'disassembly':disassemble(body,0x49d800)}}
    assert [i for i,(a,b)in enumerate(zip(*bodies))if a!=b]==[0x14]
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert sha(archive.read_bytes())=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    asset=subprocess.check_output(['7z','x','-so',str(archive),'fedata/menus/advgrph.mnu'])
    blocks=asset.decode('ascii').replace('\r\n','\n').split('\n\n')
    blocks=[b for b in blocks if 'codelink=SFX_INTENSITY' in b]
    assert len(blocks)==1 and 'text=kMenuADVGRPHAlphaInt001' in blocks[0]
    result['official_control']={'member':'fedata/menus/advgrph.mnu','sha256':sha(asset),'block':blocks[0]}
    result['derived_examples']=[{'intensity':0,'mask_byte':'10','original_color':'ffffffff','modern_color':'00000000'},
        {'intensity':0.5,'mask_byte':'10','original_color':'ffffffff','modern_color':'7f7f7f7f'},
        {'intensity':1,'mask_byte':'10','original_color':'ffffffff','modern_color':'ffffffff'}]
    result['contract']={'input_colors':'EAX and EDX copied to EDI and ESI',
        'output_stores':'EDI ->0055e6dc; ESI ->0055e6e0; no ordinary scalar-return claim',
        'ordered_admission':'Renderer mask admitted and intensity<1; unordered compare takes bypass if execution continues nontrapping',
        'normal_factor':'FISTP32(intensity*65536); signed result>=65536 replaced by65535; logical shift8 and AND255 gives q',
        'normal_channel':'For valid0<=q<=255, each of four input bytes becomes floor(byte*q/256)',
        'repeated':'Intensity conversion and colour arithmetic repeated independently for the second input',
        'default1':'Equality bypasses both conversions and retains both input colours'}
    result['reused_evidence']=['analysis/evidence/audits/effect-renderer-masks.json','analysis/original-modern-graphics-menu-transition.md','analysis/original-modern-renderer-loading.md']
    result['limits']=['No game, colour helper, API or extracted instruction execution; examples are static arithmetic derivations.',
        'Ordinary finite0..1 example scope; no universal behavior claim for negative, NaN, overflow or unmasked exceptions.',
        'Ambient FISTP rounding controls quantization; converting with a portable C cast generally changes the contract.',
        'Four-byte scaling does not independently establish colour-channel semantic labels, blending, visible shine or provider output.',
        'Menu writeback and renderer-type mapping use linked existing audits; full lifetime, callers and1.0.0 introduction remain unverified.']
    (ROOT/'analysis/evidence/audits/intensity-color-contract.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: complete235-byte colour helper, one-byte mask delta, 65536 constant and official Alpha Intensity codelink')


if __name__=='__main__':main()
