"""Pin both1.3.0/1.3.1 Glide wrapper lifecycle mechanisms without execution."""
import json
import struct
import subprocess
import pefile
from audit_dx5_reference_final import sha, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    archives={'1.3.0':'93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
              '1.3.1':'6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934'}
    members={'drivers/dgvoodoo/voodoo2.dll':[
        '857f8dd4dd997006012ae233722f382068c6c41d20c2f3166ba2b5df79122cc0',
        'de501a929c31cd0d878e162c2b06b34088637bfd1871f7992d2af93f7983311a'],
        'drivers/nglide/nglide.dll':[
        'bf075c8deec77ce8f87ee76b11662f257dd5cc5e9d91bc69cfd4afcc36b4301b',
        'a93f1669752edeb2c658640f6dd580dac046cf3c25a1671db2ccbdb48b40457b']}
    result={'kind':'static-historical-glide-init-boundary','files':[]}
    old_init=[0x60001d07,0x60001db2,0x60001f22,0x60002169]
    old_shutdown=[0x60001d27,0x60001e17,0x60001e47,0x60001f82,0x60002069,0x600020d6]
    for index,(version,archive_sha) in enumerate(archives.items()):
        path=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/path;assert sha(archive.read_bytes())==archive_sha
        for member,expected_hashes in members.items():
            raw=subprocess.check_output(['7z','x','-so',str(archive),member]);assert sha(raw)==expected_hashes[index]
            pe=pefile.PE(data=raw);nglide='nglide' in member
            assert pe.get_data(0x1028,9).hex()=='a10cfd006085c00f85'
            loader_end=(0x10f9 if nglide else 0x10f4) if index==0 else (0x110f if nglide else 0x110a)
            cleanup=0x1110 if nglide else 0x110c
            row={'version':version,'archive':path,'archive_sha256':archive_sha,
                 'url':f'https://veg.by/files/nfs3/nfs3_modern_patch_v{version}.7z',
                 'member':member,'sha256':sha(raw),'calls':{},'captures':[]}
            for name,encoded,expected in [
                ('GlideInit','ff1510100160',old_init if index==0 else [0x600010ee if nglide else 0x600010e9]),
                ('GlideShutdown','ff1514100160',old_shutdown if index==0 else [0x60001119 if nglide else 0x60001115])]:
                needle=bytes.fromhex(encoded);sites=[];cursor=0
                while True:
                    offset=raw.find(needle,cursor)
                    if offset<0:break
                    sites.append(0x60000000+pe.get_rva_from_offset(offset));cursor=offset+1
                assert sites==expected
                row['calls'][name]=[f'{address:08x}' for address in sites]
            table=0x1100 if index==0 else 0x1130;bindings={}
            for entry in range(128):
                pointer,slot=struct.unpack('<2I',pe.get_data(table+entry*8,8))
                if pointer==0:break
                bindings[f'{slot:08x}']=pe.get_string_at_rva(pointer-0x60000000).decode('ascii')
            else:raise AssertionError('Missing table terminator')
            assert bindings['60011010']=='_grGlideInit@0' and bindings['60011014']=='_grGlideShutdown@0'
            row['bindings']={slot:bindings[slot] for slot in ('60011010','60011014','600110d8')}
            spans=[(0x1020,loader_end,'complete-loader'),(0x1bb0,0x1d4d,'about-envelope'),
                (0x1d50,0x1e60,'is-envelope-including-padding'),(0x1eb0,0x1fa0,'init-envelope-including-padding'),
                (0x2050,0x2110,'close-and-restore-envelopes'),(0x2110,0x2390,'mode-worker-envelope')]
            if index==0:
                assert pe.get_data(0x1560,1)==b'\xc3'
                spans.append((0x1560,0x1561,'old-cleanup-is-RET'))
            else:
                spans.append((cleanup,cleanup+22,'complete-shutdown-latch'))
                assert pe.get_data(cleanup,22).hex()=='a1d428016085c0740cff1514100160ff0dd4280160c3'
                latch_start=0x10e5 if nglide else 0x10e0
                assert pe.get_data(latch_start,9).hex()=='a1d428016085c07517'
                for site in (0x1e1e,0x20d6):
                    call=pe.get_data(site,5)
                    assert call[0]==0xe8 and site+5+int.from_bytes(call[1:],'little',signed=True)==cleanup
                row['latch']={'cell':'600128d4','shutdown_helper':f'{0x60000000+cleanup:08x}',
                              'nonzero_acquire':'skip initialization without increment','nonzero_release':'shutdown then decrement'}
            for start,end,label in spans:
                body=pe.get_data(start,end-start)
                row['captures'].append({'label':label,'start':f'{0x60000000+start:08x}',
                    'end_exclusive':f'{0x60000000+end:08x}','sha256':sha(body),'disassembly':disassemble(body,0x60000000+start)})
            result['files'].append(row)
    result['conclusion']='Both named1.3.0->1.3.1 wrappers centralize four direct init/six shutdown sites into one of each behind a latch; old loader already caches the module handle.'
    result['limits']=['Static direct-call encodings/sites, not executed counts or exhaustive indirect-call identity.',
        '0/1 latch interpretation assumes ordinary zero initial/serialized use; not a general refcount or synchronization proof.',
        'No measured speedup, provider side-effect equivalence, runtime lifecycle or all historical variants/betas.',
        'Archive labels/source are not publisher-signature authentication; no content loaded/installed/executed.']
    (ROOT/'analysis/evidence/audits/glide-init-release-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: both pinned wrapper pairs; direct calls4/6->1/1; complete loaders and new latch retained')


if __name__=='__main__':main()
