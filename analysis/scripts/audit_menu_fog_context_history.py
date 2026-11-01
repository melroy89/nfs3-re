"""Static140->150 parsed support/effective menu fog policy and DX6 boundary."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    report={'kind':'static-menu-fog-context-history','versions':{}};shared={};drivers=[]
    dll_pins={'1.4.0':'d32ee0f11361977ecaa01402b33a0a1ea4f4732b118355a5b98696768f8d25cb',
              '1.5.0':'6c4a300fd55ed5e6c3c85983d43903717543d1b69146275856322da61a76b152'}
    for version,(ah,eh)in HISTORY.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'nfs3.exe']);assert sha(raw)==eh;pe=pefile.PE(data=raw)
        get=lambda a,b:pe.get_data(a-0x400000,b-a)
        old=version=='1.4.0';a,b=(0x4b5b0b,0x4b5b2f)if old else(0x4b58c4,0x4b58e7)
        reader=get(a,b);assert reader[:7].hex()=='6830397a006a00'
        for off,label in [(8,b'FogSupport'),(13,b'THRASH')]:
            ptr=struct.unpack('<I',reader[off:off+4])[0];assert pe.get_string_at_rva(ptr-0x400000)==label
        assert reader[17:]==bytes.fromhex('ff157446530085c0740431c0b004a3643a7a00'if old else'ff156c46530085c0740331c040a3543a7a00')
        spans=[('fog_reader',a,b),('gate_region',0x431c20,0x431c40),('menu_context_zero',0x44b271,0x44b27e),
               ('pause_context_one',0x44b958,0x44b96a),('race_context_one',0x44ba38,0x44ba4d),
               ('scene_entry',0x4bc160,0x4bc176),('menu_refresh',0x44b346,0x44b34b),('scene_state_restore',0x431b40,0x431bb4)]
        shared[version]={n:get(s,e)for n,s,e in spans}
        if old:assert get(0x431c20,0x431c25).hex()=='5589e55dc3'
        else:
            assert get(0x431c20,0x431c40).hex()=='a1543a7a002305d4d16f0023053492550085c07405b804000000a3643a7a00c3'
            assert get(0x44b346,0x44b34b).hex()=='e8d568feff'
            assert get(0x4bc16d,0x4bc176).hex()=='e8ae5af7ffeb029090'
        dll=subprocess.check_output(['7z','x','-so',str(archive),'drivers/dx6/dx6a.dll']);assert sha(dll)==dll_pins[version]
        dp=pefile.PE(data=dll);drivers.append(dp);sections={s.Name.rstrip(b'\0').decode():s for s in dp.sections}
        init_end=0x60001c81 if old else 0x60001c87;blob=dp.get_data(0x1c50,init_end-0x60001c50)
        report['versions'][version]={'archive':rel,'archive_sha256':ah,'exe_sha256':eh,
            'captures':[{'name':n,'start':f'{s:08x}','end_exclusive':f'{e:08x}','hex':get(s,e).hex(),'sha256':sha(get(s,e)),
                         'disassembly':disassemble(get(s,e),s)}for n,s,e in spans],
            'dx6':{'member':'drivers/dx6/dx6a.dll','sha256':sha(dll),'bytes':len(dll),
                   'sections':[{'name':n,'rva':s.VirtualAddress,'bytes':len(s.get_data()),'sha256':sha(s.get_data())}for n,s in sections.items()],
                   'changed_initializer':{'start':'60001c50','end_exclusive':f'{init_end:08x}','hex':blob.hex(),'disassembly':disassemble(blob,0x60001c50)}}}
    for n in ('menu_context_zero','pause_context_one','race_context_one','scene_state_restore'):
        assert shared['1.4.0'][n]==shared['1.5.0'][n]
    old_sections={s.Name:s for s in drivers[0].sections};new_sections={s.Name:s for s in drivers[1].sections};counts={}
    for n,s in old_sections.items():
        t=new_sections[n];x,y=s.get_data(),t.get_data();assert len(x)==len(y)
        counts[n.rstrip(b'\0').decode()]=sum(a!=b for a,b in zip(x,y))
        if n.startswith(b'.text'):
            changes=[f'{0x60000000+s.VirtualAddress+i:08x}'for i,(a,b)in enumerate(zip(x,y))if a!=b]
            assert changes==[f'{a:08x}'for a in range(0x60001c7f,0x60001c87)]
    assert counts=={'.text':8,'.rdata':0,'.data':0,'.reloc':44,'.rsrc':24}
    report['dx6_changed_section_bytes']=counts
    report['verified']=['140 config writes effective gate0/4 directly;150 separates normalized support0/1 and adds contextual effective recomputation.',
        'Checked main menu writes context0;checked pause/in-race initializers write1,with retained writer bytes.',
        '150 refreshes gate in menu loop and scene entry;context0 forces effective gate0 on this route.',
        'Retained scene restore requests selector15h using effective gate.',
        'DX6 whole code-section delta is eight bytes:insert INC[6003bd3c],move POP EDI/RET;other section differences are separately counted.']
    report['limits']=['No target,menu,API,instruction probe,compiler or Ghidra writes.',
        'Selected context writers are not all writes/lifetime coverage;do not call context globally immutable.',
        'No direct taillight rendering chain or visible colour result established;MP150-033 remains vendor-only.',
        'DX6 counter purpose/producer-consumer lifecycle unresolved;do not label its increment a fog/light fix.',
        'Relocation/resource differences are counted,not semantically explained here;code-byte coverage is not complete driver equivalence.']
    (ROOT/'analysis/evidence/audits/menu-fog-context-history.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:140->150 menu fog context split and selected writers;DX6 eight-byte code delta isolated,taillight attribution unresolved')


if __name__=='__main__':main()
