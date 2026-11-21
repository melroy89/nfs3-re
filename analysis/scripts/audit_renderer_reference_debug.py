"""Extract bounded DX5/Voodoo reference debug names with independent export anchors."""
import hashlib,json,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from reference_debug_records import parse_debug_overlay


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    rel='analysis/captures/modern-differences/upstream/history/nfs3_orig.7z';archive=ROOT/rel
    assert sha(archive.read_bytes())=='374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127'
    result={'kind':'static-renderer-reference-debug-records','archive':rel,'archive_sha256':sha(archive.read_bytes()),'parser':{'path':'analysis/scripts/reference_debug_records.py','sha256':sha((ROOT/'analysis/scripts/reference_debug_records.py').read_bytes())},'members':{}}
    for member,prefix,expected_units,expected_records in [('d3da.dll','_D3D_',193,961),('voodoo2a.dll','_VOODOO2_',176,877)]:
        raw=subprocess.check_output(['7z','x','-so',str(archive),member]);pe=pefile.PE(data=raw)
        start=max(s.PointerToRawData+s.SizeOfRawData for s in pe.sections if s.PointerToRawData);overlay=raw[start:]
        units,records,abbrev=parse_debug_overlay(overlay);assert(len(units),len(records))==(expected_units,expected_records)
        names={r['attributes'].get('3'):r for r in records if r['tag']==10};anchors=[]
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            name=exp.name.decode().replace('_THRASH_',prefix,1);assert name in names
            row=names[name];address=row['attributes']['17'];assert address+0x1000==exp.address
            anchors.append({'export':exp.name.decode(),'debug_name':name,'stored_address':address,'export_rva':f'{exp.address:08x}','entry_offset':row['entry_offset']})
        assert len(anchors)==34
        result['members'][member]={'sha256':sha(raw),'overlay_file_offset':start,'overlay_bytes':len(overlay),'overlay_sha256':sha(overlay),
            'abbreviation_hex':abbrev.hex(),'unit_count':len(units),'record_count':len(records),'tag_counts':{str(t):sum(r['tag']==t for r in records)for t in [17,10,52]},'export_address_anchors':anchors,'units':units,'records':records}
    result['limits']=['Same narrow four-abbreviation/form parser as SoftTri;accepts declared abbreviation extent without terminal zero entry,does not repair source bytes.',
        '34 export anchors per DLL validate listed correspondences;general address mapping and nonexport names remain inferred until instruction/data checks.',
        'Names and unit paths are not full source/types/signatures,pristine retail authentication or final-patch ABI evidence.',
        'No debug names applied to Ghidra,no target/API/payload execution or executable/database mutations.']
    (ROOT/'analysis/evidence/audits/renderer-reference-debug.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:DX5 193units/961records,Voodoo176units/877records;34 independent export anchors each;original bytes preserved')


if __name__=='__main__':main()
