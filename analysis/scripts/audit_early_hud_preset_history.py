"""Compare complete120/130 HUD WORD tables and retained conversion/scaler bodies."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble,intervals


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    pins={'1.2.0':('151e8832f5b39d007d20aeacc8de5b2e91b53408a63ea023eb12ffc31b0e603b','4802ee2948d18f0c24fa50c1300ce1df1de285f135d6441c374b267ffcab4003'),
          '1.3.0':('93b0ecffebb5e6a13ee4d7d3054c3b9dde53ca329d7e87516eaad8dd399a22ad','deac6f7f812d6a1981a3520666adbc9d4f78b9459b4d1eef76408f01729b0146')}
    result={'kind':'static-early-hud-preset-history','versions':{}};tables=[];bodies=[];aspect=[];tails=[];mode_publishers=[];dimension_defaults=[]
    for version,(ah,eh)in pins.items():
        rel=f'analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v{version}.7z';assert sha((ROOT/rel).read_bytes())==ah
        raw=subprocess.check_output(['7z','x','-so',str(ROOT/rel),'nfs3.exe']);assert sha(raw)==eh
        p=pefile.PE(data=raw);get=lambda a,b:p.get_data(a-0x400000,b-a);table=get(0x540500,0x540980);tables.append(table)
        spans=[('preset_copy_prefix',0x485680,0x4856c5),('word_divide1000_to_float',0x4f9404,0x4f9421),('slot_scaler',0x480910,0x4809f7)]
        bodies.append([get(a,b)for n,a,b in spans]);assert bodies[-1][1].hex()=='83ec04890424db0424c70424e8030000da3424d91c248b042483c404c3'
        aspect.append(get(0x4856c5,0x48582c));tails.append(get(0x48582c,0x485875))
        mode_publishers.append(get(0x4483a0,0x4483ff));dimension_defaults.append(get(0x472566,0x47257a))
        expected_cell=0x6fd1e4 if version=='1.2.0'else 0x7a3920
        assert get(0x4483e6,0x4483eb)==b'\xbf'+struct.pack('<I',expected_cell)
        assert get(0x472566,0x472570)==b'\xc7\x05'+struct.pack('<II',expected_cell,640)
        assert get(0x472570,0x47257a)==b'\xc7\x05'+struct.pack('<II',expected_cell+4,480)
        aspect_meta={'width_cell':'006fd1e4','height_cell':'006fd1e8','pixel_coefficient':'exact1/2 through FIDIV2','live_x87_values_popped':5}if version=='1.2.0'else{'width_cell':'007a3920','height_cell':'007a3924','pixel_coefficient_bits':'3efff2e5','pixel_coefficient_binary32':struct.unpack('<f',bytes.fromhex('e5f2ff3e'))[0],'live_x87_values_popped':6}
        result['versions'][version]={'archive':rel,'archive_sha256':ah,'member':'nfs3.exe','sha256':eh,'mode_publisher_capture':{'start':'004483a0','end_exclusive':'004483ff','hex':mode_publishers[-1].hex(),'disassembly':disassemble(mode_publishers[-1],0x4483a0)},'dimension_defaults_capture':{'start':'00472566','end_exclusive':'0047257a','hex':dimension_defaults[-1].hex(),'disassembly':disassemble(dimension_defaults[-1],0x472566)},'aspect_metadata':aspect_meta,'aspect_capture':{'start':'004856c5','end_exclusive':'0048582c','hex':aspect[-1].hex(),'sha256':sha(aspect[-1]),'disassembly':disassemble(aspect[-1],0x4856c5)},'shared_refresh_tail_sha256':sha(tails[-1]),'table':{'start':'00540500','end_exclusive':'00540980','bytes':len(table),'hex':table.hex(),'sha256':sha(table)},'captures':[{'name':n,'start':f'{a:08x}','end_exclusive':f'{b:08x}','sha256':sha(get(a,b)),'disassembly':disassemble(get(a,b),a)}for n,a,b in spans]}
    assert bodies[0]==bodies[1]and tails[0]==tails[1]
    assert sum(x!=y for x,y in zip(*aspect))==329
    result['aspect_changed_intervals']=intervals(*aspect,0x4856c5)
    normalized=bytearray(mode_publishers[0]);normalized[0x47:0x4b]=struct.pack('<I',0x7a3920)
    assert bytes(normalized)==mode_publishers[1]
    result['mode_publisher_contract']={'source_records':'00a18320,stride114h;discardID then copy+4/+8/+c','120_destination':'006fd1e4','130_destination':'007a3920','all_other_publisher_bytes_equal':True,
        'rebuild_gate':'Always copy three fields,then comparewrap32(field4*field8+fieldc)with006fbc18;changedkey storeskey and calls00485680.',
        'default_dimensions':[640,480],'limits':['Selected producer/default path only;not all writers/lifetimes or actual active mode.','Key collisions possible;not unconditional rebuild on every dimension change.']}
    changes=[];counts=[0]*6
    for profile in range(6):
        for slot in range(24):
            offset=profile*192+slot*8;a,b=[struct.unpack('<4H',t[offset:offset+8])for t in tables]
            if a!=b:
                counts[profile]+=1;changes.append({'profile':profile,'slot':slot,'address':f'{0x540500+offset:08x}','120_words':list(a),'130_words':list(b),'deltas':[y-x for x,y in zip(a,b)]})
    changed_words=sum(x!=y for x,y in zip(struct.unpack('<576H',tables[0]),struct.unpack('<576H',tables[1])));changed_bytes=sum(x!=y for x,y in zip(*tables))
    assert counts==[8,7,11,9,11,9]and len(changes)==55 and changed_words==changed_bytes==118
    result.update({'changed_records':changes,'changed_record_count':55,'unchanged_record_count':89,'changed_word_count':changed_words,'changed_byte_count':changed_bytes,'changed_records_by_profile':counts,'limits':[
        'Exhaustive for paired1152-byte preset tables,not all HUD code/data or vague release scope.',
        'WORD sources divide by1000 and adjacent pairs swap;deltas are not pixel movements.',
        'Aspect block changes329 bytes,new dimension cells/half-pixel-style terms and six x87 live values;selected publisher now established;all writers/lifetimes and rendered effects remain unverified.',
        'Retained converter/scaler bytes do not establish selected live profiles,later writes,all callers,x87 input state or rendered output.',
        'No target/API/instruction execution,compilation or binary/Ghidra mutation.']})
    (ROOT/'analysis/evidence/audits/early-hud-preset-history.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:120->130 HUD55/144 records and329 aspect-code bytes change;copy/converter/scaler/tail retained')


if __name__=='__main__':main()
