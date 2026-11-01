"""Resolve DX6 post-enumeration increment as public mode-count adjustment."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_endpoint_comma_history import HISTORY
from audit_dx5_reference_final import disassemble


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.4.0':'d32ee0f11361977ecaa01402b33a0a1ea4f4732b118355a5b98696768f8d25cb',
          '1.5.0':'6c4a300fd55ed5e6c3c85983d43903717543d1b69146275856322da61a76b152'}
    result={'kind':'static-dx6-mode-count-history','versions':{}};retained={}
    for version,digest in pins.items():
        ah,_=HISTORY[version];rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';archive=ROOT/rel
        assert sha(archive.read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(archive),'drivers/dx6/dx6a.dll']);assert sha(raw)==digest
        pe=pefile.PE(data=raw);get=lambda a,b:pe.get_data(a-0x60000000,b-a)
        spans=[('about',0x60001000,0x600010fb),('callback',0x60001cd0,0x60001d90),('insert_record',0x6000e500,0x6000e59d)]
        retained[version]=[get(a,b)for n,a,b in spans]
        assert get(0x600010d4,0x600010de).hex()=='c70540bd036000f00360'
        assert get(0x600010f5,0x600010fb).hex()=='b800bd0360c3'
        assert get(0x6000e521,0x6000e52a).hex()=='6bf82881c728f00360'
        assert get(0x6000e53e,0x6000e54f).hex()=='8b1d3cbd036083fb647346ff053cbd0360'
        assert get(0x60001d7c,0x60001d81).hex()=='e87fc70000'
        assert get(0x60001c51,0x60001c69).hex()=='b9e803000031c0bf28f00360f3abc7053cbd036000000000'
        end=0x60001c81 if version=='1.4.0'else 0x60001c87
        spans.append(('enumeration_initializer',0x60001c50,end))
        if version=='1.5.0':assert get(0x60001c7f,0x60001c87).hex()=='ff053cbd03605fc3'
        sections=[]
        for address in (0x6003bd00,0x6003bd3c,0x6003f000,0x6003f028):
            s=pe.get_section_by_rva(address-0x60000000);offset=address-0x60000000-s.VirtualAddress
            sections.append({'address':f'{address:08x}','section':s.Name.rstrip(b'\0').decode(),
                'offset_in_section':offset,'raw_size':s.SizeOfRawData,'virtual_size':s.Misc_VirtualSize,
                'file_backed_at_address':offset<s.SizeOfRawData})
        assert all(not s['file_backed_at_address']for s in sections)
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'drivers/dx6/dx6a.dll','sha256':digest,
            'storage':sections,'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}',
             'hex':get(a,b).hex(),'sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert retained['1.4.0']==retained['1.5.0']
    result['layout']={'descriptor':'6003bd00','count_field_offset':'3c','count_cell':'6003bd3c',
        'published_table_pointer_field_offset':'40','published_table_base':'6003f000','insertion_base':'6003f028',
        'record_bytes':40,'leading_slots_before_insertion_base':1,'insert_helper_limit':100,
        'explicit_zeroing':{'start':'6003f028','bytes':4000,'excludes_leading_record':True}}
    result['ordinary_derived_counts']=[{'inserted_distinct_records':n,'140_reported_count':n,'150_reported_count':n+1,
        'condition':'Fresh successful synchronous enumeration with insertion countN;no runtime observation.'}for n in (0,3,100)]
    result['verified']=['Counter6003bd3c is descriptor+3c;about exposes table base6003f000 via descriptor+40.',
        'Callback builds40-byte temporary record and calls retained insertion helper;helper stores at6003f028+40*index.',
        'Insertion searches by first three DWORDs;equal keys overwrite record without increment,new keys insert with unsigned count<100.',
        '150 post-call increment changes reported countN->N+1 after enumeration;one leading public-table slot is outside inserted-record base.',
        'Descriptor/table storage is loader-zero-filled virtual storage;explicit initializer clears4000 bytes beginning after leading slot.']
    result['limits']=['No driver,enumerator,API,game,instruction probe,compiler or Ghidra writes.',
        'Leading-slot contents and full external consumer semantics are not proved by pointer offset alone.',
        'Existing EXE search/admission evidence includes inclusive scans;do not assume every consumer uses exclusive count or claim last mode restoration universally.',
        'At100 inserted records count becomes101;all later array accesses/bounds and device acceptance require separate qualification.',
        'Callback insertion return and enumeration result are not locally used to guard added increment;provider failures remain unresolved.',
        'No taillight/fog attribution or full driver equivalence;prior section/resource/code difference qualifications remain.']
    (ROOT/'analysis/evidence/audits/dx6-mode-count-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:DX6 counter is published descriptor mode count;retained callback/insertion/public base explain150 extra leading slot')


if __name__=='__main__':main()
