"""Static paired DX7 clip-record depth value; no viewport/driver execution."""
import hashlib,json,struct,subprocess
import pefile
from audit_thrash_loader_difference import ROOT
from audit_dx5_reference_final import disassemble


def main():
    baseline=json.loads((ROOT/'analysis/evidence/audits/official-160-161-baseline.json').read_text())
    result={'kind':'historical-dx7-clip-record-depth','versions':{},
        'limits':['No renderer, viewport, API or instruction execution.',
                  'SetViewport identity supported by SDK layout/vtable; complete factory/object lifetime not qualified.',
                  'No demonstrated link to Old Church black-polygon symptom or all rendering paths.'],
        'sdk_references':['https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3dtypes.h',
                          'https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d.h']}
    capture=ROOT/'analysis/captures/modern-differences/dx7-viewport-depth';capture.mkdir(parents=True,exist_ok=True)
    bodies=[]
    for version in ('1.6.0','1.6.1'):
        package=baseline['packages'][version];archive=ROOT/package['archive_path']
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==package['archive_sha256']
        member='drivers/dx7/dx7a.dll';raw=subprocess.check_output(['7z','x','-so',str(archive),member])
        expected=next(r['sha256']for r in package['members']if r['member']==member)
        assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw)
        assert any(e.name==b'_THRASH_clip@16' and e.address==0x13c0 for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
        body=pe.get_data(0x13c0,0x96);bodies.append(body)
        assert pe.get_data(0x141c,4).hex()=='c7442424'
        bits=struct.unpack('<I',pe.get_data(0x1420,4))[0]
        assert bits==(0x3f7fff00 if version=='1.6.0' else 0x3f800000)
        assert pe.get_data(0x1414,8).hex()=='c744242000000000'
        assert pe.get_data(0x1442,9).hex()=='8d5424005250ff5134'
        out=capture/f'{version}-600013c0.asm';out.write_text('\n'.join(disassemble(body,0x600013c0))+'\n')
        result['versions'][version]={'archive_sha256':package['archive_sha256'],'member':member,'sha256':expected,
            'entry':'600013c0','end_exclusive':'60001456','bytes':len(body),'bytes_sha256':hashlib.sha256(body).hexdigest(),
            'depth_bits':f'{bits:08x}','binary32_value':struct.unpack('<f',struct.pack('<I',bits))[0],
            'assembly':str(out.relative_to(ROOT)),'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    changes=[0x600013c0+i for i,(a,b)in enumerate(zip(*bodies))if a!=b]
    assert changes==[0x60001421,0x60001422]
    result['changed_addresses']=[f'{x:08x}'for x in changes]
    result['interpretation']={'record':'SixDWORDs: x,y,wrap32(x2-x),wrap32(y2-y),float0,changedfloat',
        'consumer':'Object60058d9c vtable+34h receivespointertorecord',
        'sdk_correspondence':'D3DVIEWPORT7 hasfourDWORDcoordinates/extents thenfloatdvMinZ/dvMaxZ;IDirect3DDevice7 slot13=SetViewport',
        'limitation':'Matching other clipbody bytes do not prove unchanged flushhelper effects or successful API call;body returns1withouttestingAPIresult'}
    (ROOT/'analysis/evidence/audits/dx7-viewport-depth.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: pinned DX7 pairs, complete150-byte clipbody and onlytwo changeddepth-immediate bytes')


if __name__=='__main__':main()
