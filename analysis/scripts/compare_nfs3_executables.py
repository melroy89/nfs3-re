"""Read-only PE/function-range inventory for original, official Modern and local NFS3.

A same-VA byte difference is not a proved function match or behavior change.
Never treats zero-offset uninitialized sections as file-backed data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pefile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def section_bytes(pe, start, size):
    rva = start - pe.OPTIONAL_HEADER.ImageBase
    for sec in pe.sections:
        if sec.PointerToRawData and not (sec.Characteristics & 0x80):
            delta = rva - sec.VirtualAddress
            if 0 <= delta and delta + size <= sec.SizeOfRawData:
                return pe.__data__[sec.PointerToRawData + delta:sec.PointerToRawData + delta + size]
    return None


def identity(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}


def imports(pe):
    return [{'dll':d.dll.decode(), 'lookup_rva':hex(d.struct.OriginalFirstThunk),
             'iat_rva':hex(d.struct.FirstThunk),
             'symbols':[i.name.decode() if i.name else '#'+str(i.ordinal) for i in d.imports]}
            for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])]


def resources(pe):
    result = {}
    def visit(tree, path):
        for entry in tree.entries:
            key = str(entry.name) if entry.name else str(entry.id)
            if hasattr(entry,'directory'):
                visit(entry.directory,path+[key])
            else:
                r = entry.data.struct
                raw = pe.get_data(r.OffsetToData,r.Size)
                result['/'.join(path+[key])] = {'rva':hex(r.OffsetToData),'size':r.Size,'sha256':digest(raw)}
    if hasattr(pe,'DIRECTORY_ENTRY_RESOURCE'):
        visit(pe.DIRECTORY_ENTRY_RESOURCE,[])
    return result


def compare_functions(functions, a, b, original_entries):
    records = []
    for fn in functions:
        left,right=[],[]
        for start,end in fn['ranges']:
            start,end=int(start,16),int(end,16)
            x,y=section_bytes(a,start,end-start),section_bytes(b,start,end-start)
            if x is None or y is None:
                left=right=None
                break
            left.append(x);right.append(y)
        record={k:fn[k] for k in ('entry','name','ranges','thunk')}
        record['original_entry_identified_by_autoanalysis']=fn['entry'] in original_entries
        if left is None:
            record['status']='not_fully_file_backed_at_both_same_VAs'
        else:
            x,y=b''.join(left),b''.join(right)
            record.update(status='identical_same_VA_bytes' if x==y else 'different_same_VA_bytes',
                          bytes=len(x),changed_bytes=sum(i!=j for i,j in zip(x,y)),
                          original_sha256=digest(x),modern_sha256=digest(y))
        records.append(record)
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','modern','local','functions','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--original-functions',type=Path)
    args=parser.parse_args()
    org,modern,local=[pefile.PE(str(p)) for p in (args.original,args.modern,args.local)]
    inv=json.loads(args.functions.read_text())
    original_entries=set()
    original_inventory=None
    if args.original_functions:
        original_inv=json.loads(args.original_functions.read_text())
        original_entries={f['entry'] for f in original_inv['functions']}
        original_inventory={'path':str(args.original_functions),'sha256':digest(args.original_functions.read_bytes()),
                            'program_executable_sha256':original_inv['executable_sha256']}
    result={'schema':1,'binaries':{k:identity(p) for k,p in [('original',args.original),('official_modern',args.modern),('local_modern',args.local)]},
            'function_inventory':{'path':str(args.functions),'sha256':digest(args.functions.read_bytes()),'program_executable_sha256':inv['executable_sha256']},
            'original_function_inventory':original_inventory,
            'limits':['Uses saved Modern function names/ranges; does not infer semantic function correspondence from a shared address.',
                      'Changed bytes can be data/control operands, relocated/replaced code or unrelated original bytes, not a one-to-one vendor fix.',
                      'Original autoanalysis entries are boundary candidates, not recovered source identities.',
                      'Uninitialized/zero-offset sections are not read as file-backed bytes.'],
            'sections':[],'imports':{'original':imports(org),'official_modern':imports(modern)},
            'resources':{'original':resources(org),'official_modern':resources(modern),'local_modern':resources(local)}}
    for old in org.sections:
        matches=[s for s in modern.sections if s.VirtualAddress==old.VirtualAddress]
        row={'original_name':old.Name.rstrip(b'\0').decode(),'original_va':hex(0x400000+old.VirtualAddress),'original_raw_size':old.SizeOfRawData,'original_raw_offset':old.PointerToRawData}
        if matches:
            new=matches[0];row.update(modern_name=new.Name.rstrip(b'\0').decode(),modern_raw_size=new.SizeOfRawData,modern_raw_offset=new.PointerToRawData)
            if old.PointerToRawData and new.PointerToRawData and not(old.Characteristics&0x80 or new.Characteristics&0x80):
                a,b=old.get_data(),new.get_data();row['changed_bytes_over_common_span']=sum(x!=y for x,y in zip(a,b));row['size_delta']=len(b)-len(a)
        else:row['same_VA_section_match']=False
        result['sections'].append(row)
    result['functions']=compare_functions(inv['functions'],org,modern,original_entries)
    counts={}
    for f in result['functions']:counts[f['status']]=counts.get(f['status'],0)+1
    result['counts']=counts
    local_deltas=[]
    for sec in modern.sections:
        same=[s for s in local.sections if s.VirtualAddress==sec.VirtualAddress]
        if not sec.PointerToRawData or sec.Characteristics&0x80 or not same:continue
        a,b=sec.get_data(),same[0].get_data()
        local_deltas.append({'section':sec.Name.rstrip(b'\0').decode(),'official_bytes':len(a),'local_bytes':len(b),'changed_common_bytes':sum(x!=y for x,y in zip(a,b)),
                             'changed_VAs':[f'{0x400000+sec.VirtualAddress+i:08x}' for i,(x,y) in enumerate(zip(a,b)) if x!=y] if sec.Name.startswith(b'.code') else []})
    result['official_to_local_sections']=local_deltas
    old_code, new_code = org.sections[0], modern.sections[0]
    if old_code.VirtualAddress == new_code.VirtualAddress and old_code.SizeOfRawData == new_code.SizeOfRawData:
        a, b = old_code.get_data(), new_code.get_data()
        covered = bytearray(len(b))
        code_va = modern.OPTIONAL_HEADER.ImageBase + new_code.VirtualAddress
        for fn in result['functions']:
            for start, end in fn['ranges']:
                lo, hi = int(start,16)-code_va, int(end,16)-code_va
                if 0 <= lo < hi <= len(covered): covered[lo:hi] = b'\1'*(hi-lo)
        changed = [i for i,(x,y) in enumerate(zip(a,b)) if x != y]
        outside = [i for i in changed if not covered[i]]
        from collections import Counter
        result['code_byte_coverage'] = {'code_bytes':len(b),'changed_bytes':len(changed),
            'changed_bytes_inside_modern_function_ranges':sum(bool(covered[i]) for i in changed),
            'changed_bytes_outside_modern_function_ranges':len(outside),
            'outside_modern_values':dict(Counter(f'{b[i]:02x}' for i in outside).most_common(8))}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'counts':counts,'sections':result['sections'],'official_to_local':local_deltas},indent=2))

if __name__=='__main__':main()
