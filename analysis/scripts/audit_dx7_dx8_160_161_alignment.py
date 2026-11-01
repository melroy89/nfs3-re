"""Pin DX7/DX8 historical alignment helpers without executing renderers."""
import hashlib,json,re,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT


def direct_calls(pe,target):
    section=next(s for s in pe.sections if s.Name.startswith(b'.text'))
    raw=section.get_data();base=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress
    return [base+i for i in range(len(raw)-4) if raw[i]==0xe8 and
            base+i+5+int.from_bytes(raw[i+1:i+5],'little',signed=True)==target]


def main():
    baseline=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())
    capture=ROOT/'analysis/captures/modern-differences/dx7-dx8-alignment';capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-dx7-dx8-160-161-alignment','range_end':'exclusive','drivers':{}}
    core=bytes.fromhex('d907d8e1d91fd94704d8e1d95f04')
    for driver,target,constant in [('dx7',0x6000d580,0x1544c),('dx8',0x60001ff0,0x18220)]:
        versions={};images={}
        for version in ('1.6.0','1.6.1'):
            package=baseline['packages'][version];archive=ROOT/package['archive_path']
            assert hashlib.sha256(archive.read_bytes()).hexdigest()==package['archive_sha256']
            member=f'drivers/{driver}/{driver}a.dll'
            raw=subprocess.check_output(['7z','x','-so',str(archive),member])
            expected=next(x['sha256'] for x in package['members'] if x['member']==member)
            assert hashlib.sha256(raw).hexdigest()==expected
            pe=pefile.PE(data=raw);images[version]=pe
            assert raw.count(core)==(0 if version=='1.6.0' else 1)
            binary=capture/f'{driver}-{version}.dll';binary.write_bytes(raw)
            calls=direct_calls(pe,target)
            spans=([(target,target+44)] if driver=='dx7' else
                   [(target,0x600021f7 if version=='1.6.0' else 0x60002067)])
            spans += [(site,site+5) for site in calls]
            if driver=='dx8' and version=='1.6.1':
                spans += [(0x600037a3,0x600037b8),(0x60006486,0x60006498),
                          (0x60006501,0x60006535),(0x60001b40,0x60001b68),
                          (0x60001f20,0x60001fc2),(0x60003740,0x6000375a),
                          (0x60003d2a,0x60003d51),(0x600061ec,0x6000627e),
                          (0x600076f0,0x600077c0),(0x60011244,0x6001124a)]
            rows=[]
            for start,end in spans:
                body=pe.get_data(start-0x60000000,end-start);output=capture/f'{driver}-{version}-{start:08x}.asm'
                output.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={end}',str(binary.relative_to(ROOT))],cwd=ROOT))
                rows.append({'start':f'{start:08x}','end_exclusive':f'{end:08x}','sha256':hashlib.sha256(body).hexdigest(),
                             'assembly':str(output.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
            versions[version]={'member':member,'sha256':expected,'direct_call_candidates':[f'{s:08x}' for s in calls],'spans':rows}
        assert struct.unpack('<f',images['1.6.1'].get_data(constant,4))[0]==0.5
        if driver=='dx7':
            assert direct_calls(images['1.6.0'],target)==[]
            assert direct_calls(images['1.6.1'],target)==[0x60006f5e,0x600082ca,0x600087ee]
            assert images['1.6.1'].get_data(0xd594,len(core))==core
            contract='New44-byte helper: stack pointer/count inputs; subtract0.5 from X/Y at32-byte stride; zero count skips arithmetic; ECX/EDI restored; plainRET, no DX6-style pushed constant adapter.'
        else:
            calls=direct_calls(images['1.6.0'],target)
            assert len(calls)==15 and calls==direct_calls(images['1.6.1'],target)
            assert images['1.6.1'].get_data(0x1ff0,27).hex()=='578b7c2408d90520820160d907d8e1d91fd94704d8e1d95f04ddd8'
            assert struct.unpack('<f',images['1.6.1'].get_data(0x18140,4))[0]==65535.0
            assert struct.unpack('<f',images['1.6.1'].get_data(0x185c0,4))[0]==255.0
            assert images['1.6.1'].get_data(0x37a3,21).hex()=='33c080c9ff2ac88888a0080260403d000100007ced'
            contract='Matched vertex helper has15 retained direct calls; new prefix subtracts0.5 from one supplied vertex X/Y before existing/reworked colour/fog policy. Other helper changes are not declared equivalent.'
        result['drivers'][driver]={'versions':versions,'constant_rva':f'{constant:08x}','constant':0.5,'contract':contract}
    headers={}
    for name,expected in [('d3d8.h','e93563a03f30a83dae6afe20ad0061558f6a56fe7d101b3d883749b47d1edeef'),
                          ('d3d8types.h','6443383135f69c8199f4c9c1b81717b94ade16ae625f760f198d7c49d864353d')]:
        path=ROOT/'analysis/captures/modern-differences/dx8-api-headers'/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        headers[name]={'snapshot':str(path.relative_to(ROOT)),'sha256':expected,
            'url':'https://raw.githubusercontent.com/mingw-w64/mingw-w64/master/mingw-w64-headers/include/'+name}
    declaration=(ROOT/headers['d3d8.h']['snapshot']).read_text().split('DECLARE_INTERFACE_IID_(IDirect3DDevice8,')[1].split('};')[0]
    names=re.findall(r'STDMETHOD(?:_\(\s*[^,]+,\s*|\(\s*)(\w+)\)',declaration)
    slots={name:names.index(name)*4 for name in ['SetRenderState','DrawPrimitive','SetVertexShader','SetStreamSource']}
    assert slots=={'SetRenderState':0xc8,'DrawPrimitive':0x118,'SetVertexShader':0x130,'SetStreamSource':0x14c}
    types=(ROOT/headers['d3d8types.h']['snapshot']).read_text()
    for name,value in [('FOGENABLE',28),('FOGTABLEMODE',35),('FOGVERTEXMODE',140),('FOGCOLOR',34)]:
        assert re.search(r'D3DRS_'+name+r'\s*=\s*'+str(value)+r'\s*,',types)
    for name,value in [('XYZRHW',4),('DIFFUSE',64),('SPECULAR',128),('TEX1',256)]:
        match=re.search(r'#define\s+D3DFVF_'+name+r'\s+(0x[0-9a-fA-F]+)',types)
        assert match and int(match.group(1),16)==value
    pe=images['1.6.1']
    assert any(entry.dll.lower()==b'd3d8.dll' and any(
        item.name==b'Direct3DCreate8' and item.address==0x600180b8 for item in entry.imports)
        for entry in pe.DIRECTORY_ENTRY_IMPORT)
    result['api_header_evidence']={'headers':headers,'device8_vtable_byte_offsets':slots,
        'limits':'Primary implementation header snapshots qualify ABI labels; no API execution or device acceptance.'}
    result['limits']=['Official historical renderer pairs, not original-retail DLL pairing.',
        'Direct E8 scans are bounded call candidates; indirect calls and complete export reachability not established.',
        'In-place coordinate changes, not direct U/V writes. No rendered sharpness/pixel coverage or callback execution.',
        'Raw same-address older DX7 helper-region bytes are a location witness, not a semantic counterpart.']
    (ROOT/'analysis/evidence/audits/dx7-dx8-160-161-alignment.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: historical DX7/DX8 pairs, new half-unit coordinate adjustments and3/15 direct-call witnesses')


if __name__=='__main__':main()
