"""Bounded inspection of the original-reference appended debug carrier; never executes it."""
import hashlib,json,struct,subprocess,tempfile
import pefile
from audit_thrash_loader_difference import ROOT,SPECS
from reference_debug_records import parse_debug_overlay


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    rel='analysis/captures/modern-differences/upstream/history/nfs3_orig.7z';archive=ROOT/rel
    assert sha(archive.read_bytes())=='374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'
    raw=subprocess.check_output(['7z','x','-so',str(archive),'softtria.dll']);assert sha(raw)=='8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02'
    pe=pefile.PE(data=raw);overlay=raw[275968:];assert len(overlay)==28514
    units,records,abbrev=parse_debug_overlay(overlay)
    assert len(units)==173 and len(records)==1034
    by_name={r['attributes'].get('3'):r for r in records if r['tag']==10};anchors=[]
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        expected=exp.name.decode().replace('_THRASH_','_SOFTTRI_',1)
        if expected in by_name:
            row=by_name[expected];stored=row['attributes']['17'];assert stored+0x1000==exp.address
            anchors.append({'export':exp.name.decode(),'debug_name':expected,'stored_address':stored,'export_rva':f'{exp.address:08x}','entry_offset':row['entry_offset']})
    assert len(anchors)>=20
    with tempfile.NamedTemporaryFile(suffix='.elf')as f:
        f.write(overlay);f.flush();run=subprocess.run(['readelf','--debug-dump=info',f.name],capture_output=True,text=True)
    carriers=[]
    original_path,original_hash,_=SPECS['original'];original=(ROOT/original_path).read_bytes();assert sha(original)==original_hash
    for label,blob in [('supplied_original_exe',original),('reference_d3da',subprocess.check_output(['7z','x','-so',str(archive),'d3da.dll'])),('reference_voodoo2a',subprocess.check_output(['7z','x','-so',str(archive),'voodoo2a.dll']))]:
        image=pefile.PE(data=blob);end=max(s.PointerToRawData+s.SizeOfRawData for s in image.sections if s.PointerToRawData);extra=blob[end:]
        carriers.append({'label':label,'sha256':sha(blob),'file_bytes':len(blob),'raw_section_end':end,'overlay_bytes':len(extra),'overlay_sha256':sha(extra),'overlay_first16_hex':extra[:16].hex(),'elf_magic':extra.startswith(b'\x7fELF'),'scope':'Only trailing PE overlay inspected;no in-section debug absence or complete payload semantics asserted.'})
    assert [r['overlay_bytes']for r in carriers]==[0,26449,24054]
    assert [r['elf_magic']for r in carriers]==[False,True,True]
    result={'kind':'static-softtri-reference-debug-inspection','archive':rel,'archive_sha256':sha(archive.read_bytes()),'member_sha256':sha(raw),'overlay_sha256':sha(overlay),
        'related_carrier_inventory':carriers,'abbreviation_hex':abbrev.hex(),'abbreviation_terminating_zero_entry_present':False,'parser_policy':'Accept exact declared abbreviation extent after four bounded definitions;no bytes appended or repaired.',
        'units':units,'records':records,'tag_counts':{str(t):sum(r['tag']==t for r in records)for t in [17,10,52]},'export_address_anchors':anchors,
        'stock_reader':{'version':subprocess.check_output(['readelf','--version'],text=True).splitlines()[0],'exit_code':run.returncode,'stdout':run.stdout,'stderr_sha256':sha(run.stderr.encode()),'distinct_stderr_lines':sorted(set(run.stderr.splitlines()))},
        'limits':['Custom bounded record extraction,not a complete DWARF implementation or validation of every debug address.',
            'Stored addresses plus1000h match listed exports;general mapping for all records remains inferred.',
            'Names/source paths do not supply source code,types,full signatures or final-version ABI contracts.',
            'Reference provenance is author-hosted,not authenticated pristine retail;no Ghidra labels or game bytes changed.',
            'No ELF/PE/target instruction execution;readelf is a static host inspection tool.']}
    (ROOT/'analysis/evidence/audits/softtri-reference-debug.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS:173 debug units,1034 bounded records,{len(anchors)} export address anchors;stock reader exit{run.returncode},original bytes preserved')


if __name__=='__main__':main()
