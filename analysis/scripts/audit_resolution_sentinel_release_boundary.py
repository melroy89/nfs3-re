"""Static historical scalar-resolution persistence; no game or instruction execution."""
import json
import subprocess
import pefile
from audit_dx5_reference_final import sha, intervals, disassemble
from audit_thrash_loader_difference import ROOT


def main():
    specs=[('1.3.0','93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad',
            'deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146'),
           ('1.3.1','6f12b2806378c4b2c843f82265b0c7d20ee8427b963d017e940717c468a23934',
            '199aa49dc76e7a2549949760b3d00d9118340a288cc77d4642c4a4d37c9a4664')]
    result={'kind':'static-historical-resolution-sentinel-boundary','releases':{}}
    images=[]
    for version,archive_sha,exe_sha in specs:
        path=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z'
        archive=ROOT/path;assert sha(archive.read_bytes())==archive_sha
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==exe_sha
        pe=pefile.PE(data=raw);images.append(pe)
        row={'archive':path,'archive_sha256':archive_sha,'member':'nfs3.exe','sha256':exe_sha,'captures':[]}
        for start,end,label in [(0x448210,0x4482b9,'complete-menu-collector'),
            (0x4482c0,0x4482e7,'list-initializer-envelope'),
            (0x4483a0,0x4483dc,'complete-driver-id-to-menu-selection'),
            (0x4483dc,0x4483ff if version=='1.3.0' else 0x448419,'complete-request-and-active-mode-update'),
            (0x4484e0,0x448558,'graphics-transition-envelope'),
            (0x4bee80,0x4bef4b,'complete-score-selector'),
            (0x473279,0x473288,'startup-request-to-selection-calls')]:
            body=pe.get_data(start-0x400000,end-start)
            row['captures'].append({'label':label,'start':f'{start:08x}','end_exclusive':f'{end:08x}',
                'sha256':sha(body),'disassembly':disassemble(body,start)})
        result['releases'][version]=row
    old,new=images
    assert old.get_data(0xbee80,0xcb)==new.get_data(0xbee80,0xcb)
    assert old.get_data(0x484e0,0x78)==new.get_data(0x484e0,0x78)
    assert new.get_data(0x482c9,5).hex()=='a3b0277a00'
    assert new.get_data(0x48263,23).hex()=='8b42040faf420803420c3b05b0277a007e05a3b0277a00'
    assert new.get_data(0x483dc,28).hex()=='8b46040faf460803460c3b05b0277a007505b8ffffff7fa318bc6f00'
    assert old.get_data(0x483dc,10).hex()=='ad8b060faf4604034608'
    assert new.get_data(0x73279,5).hex()=='a118bc6f00'
    for site,target in [(0x47327e,0x4bee80),(0x473283,0x4483a0)]:
        call=new.get_data(site-0x400000,5)
        assert call[0]==0xe8 and site+5+int.from_bytes(call[1:],'little',signed=True)==target
    result['contract']={
        'historical_score':'wrap32(width*height + depth), not final packed width/height request',
        'new_maximum':'List initializer resets007a27b0=0; admitted menu rows update it when signed score is greater.',
        'new_request':'Selected row score==tracked maximum writes7fffffff to006fbc18; otherwise writes score.',
        'old_request':'Selected row score stored as concrete scalar; width/height/depth published through old active-mode cells.',
        'retained_selector':'004bee80..004bef4b uses signed absolute score difference and first-wins ties, fallback index1 if no candidate.',
        'retained_transition':'004484e0..00448558 calls004483dc on the selected menu row in both versions.',
        'ordinary_sentinel_effect':'For nonnegative fitting eligible scores below7fffffff, smallest sentinel distance means largest score.',
        'limits':['A menu-max score and full-driver candidate set are distinct; all reset/list lifecycle and filtering domains are not equivalent by assumption.',
            'Integer products/addition wrap32, signed absolute value has INT_MIN edge behavior; ordinary formula excludes those cases.',
            'Score includes depth; it is not universally strict width/height ordering or exact pixel-area-only ordering.',
            'No external-display hotplug, changed list, persistence file, actual selection or rendering executed.',
            '1.3.1 scalar7fffffff mechanism must not be replaced with final1.6.1 packed7fff7fff semantics.']}
    result['local_update_changed_intervals']=intervals(old.get_data(0x483dc,0x54),new.get_data(0x483dc,0x54),0x4483dc)
    (ROOT/'analysis/evidence/audits/resolution-sentinel-release-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned1.3.0/1.3.1 EXEs; new max-score sentinel producer, retained transition/score selector and startup consumer')


if __name__=='__main__':main()
