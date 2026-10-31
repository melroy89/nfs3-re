"""Static config load/header comparison; no target/file API execution."""
import hashlib
import json
import struct
import subprocess
import pefile
from audit_thrash_loader_difference import ROOT, SPECS

SPANS={'original':[(0x472980,0x472b60),(0x4728e0,0x47297d),
                   (0x4723f0,0x47242c),(0x4e0640,0x4e0658),(0x4ff4c0,0x4ff563),
                   (0x472820,0x4728d3),(0x40faf0,0x40fb0f)],
       'official_modern':[(0x472980,0x472b48),(0x472230,0x472248),
                          (0x4723f0,0x472402),(0x472820,0x4728d3),(0x40faf0,0x40fb0f)]}


def main():
    capture=ROOT/'analysis/captures/modern-differences/config-loading'
    capture.mkdir(parents=True,exist_ok=True)
    result={'kind':'static-config-loading-comparison','range_end':'exclusive','binaries':{},
        'limits':['No config, game or instruction execution.','Header acceptance is not complete serialized-field validation.']}
    for label,(relative,expected,_) in SPECS.items():
        raw=(ROOT/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        pe=pefile.PE(data=raw);rows=[]
        sound_descriptor=struct.unpack('<5I',pe.get_data(0x156c08,20))
        assert sound_descriptor[0]==0x5382c0 and sound_descriptor[4]==0x6fbc00
        assert pe.get_string_at_rva(0x1382c0)==b'audiomode'
        assert struct.unpack('<5H',pe.get_data(0x156364,10))==(155,156,157,158,0)
        switch_pointer=struct.unpack('<I',pe.get_data(0x15eb34+21*4,4))[0]
        switch_name=pe.get_string_at_rva(switch_pointer-0x400000).decode('ascii')
        assert switch_name==('-msdemo' if label=='original' else '')
        if label=='original':
            assert pe.get_data(0x15e8b8,8)==bytes(8)
            assert pe.get_data(0x7241f,13).hex()=='891540bb6f00ba01000000a5a5'
            result['original_default_header_prefix']={
                'producer':'004723f0..0047242c prefix; remaining defaults not qualified here',
                'size_store':'0047241f stores20f0 at006fbb40',
                'template':'0055e8b8: eight file-backed zero bytes copied to006fbb44/+48 by MOVSD pair0047242a/2b',
                'modern_consequence':'Ordinary zero version takes grouped reset, not accepted-header bypass.',
                'limits':['Template must remain unchanged and DF must be clear; captures retain fill adapters for ESI/EDI preservation inspection.',
                          'Later original header writes, complete defaults, saving and real-file provenance remain unqualified.']}
        if label=='official_modern':
            assert pe.get_data(0x72aac,33).hex() == '813d40bb6f00f0200000751566a144bb6f0084e475103c06720ce865f7ffffeb1e'
            assert pe.get_data(0x72ad7,5).hex()=='e834020000'
            result['view_angle_header_route']={
                'storage':'006fbc40','offset_from_loaded_block_006fbb40':'00000100',
                'accepted_header':'size20f0, version high byte0, low byte6..255 ->00472230 then00472aeb; skips00472d10.',
                'reset_header':'Size mismatch or rejected version reaches00472d10 at00472ad7; its direct selector reset chooses0/Automatic.',
                'limits':['No per-field View Angle remapping in the header decision sequence or narrow sound normalizer00472230.',
                          'Successful block copy, full save layout and later writes are not established by the header branches alone.']}
        for start,end in SPANS[label]:
            out=capture/f'{label}-{start:08x}.asm'
            out.write_bytes(subprocess.check_output(['objdump','-d','-Mintel',
                f'--start-address={start}',f'--stop-address={end}',relative],cwd=ROOT))
            rows.append({'start':f'{start:08x}','end':f'{end:08x}',
                'bytes_sha256':hashlib.sha256(pe.get_data(start-0x400000,end-start)).hexdigest(),
                'assembly':str(out.relative_to(ROOT)),
                'assembly_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
        result['binaries'][label]={'path':relative,'sha256':expected,'spans':rows,
            'flag_bit21_switch':{'slot_address':'0055eb88','pointer':f'{switch_pointer:08x}',
                'text':switch_name,'consumer_byte':'0055eb2e','mask':'20',
                'binding':'Parser index21 corresponds to DWORD0055eb2c bit21; parser proof retained in command-line audit.'},
            'file_backed_header_hex':pe.get_data(0x55e8a0-0x400000,12).hex(),
            'format_string':pe.get_data(0x53b00c-0x400000,30).split(b'\0')[0].decode('ascii'),
            'relevant_imports':{f'{i.address:08x}':i.name.decode()
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports
                if i.name and i.name in [b'CompareFileTime',b'GetFileTime',b'_lopen',b'_lclose',b'GetModuleFileNameA']}}
    images=[pefile.PE(str(ROOT/SPECS[label][0])) for label in ('original','official_modern')]
    assert images[0].get_data(0xeaf0,31)==images[1].get_data(0xeaf0,31)
    archive=ROOT/'analysis/captures/modern-differences/upstream/nfs3_modern_patch.7z'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3'
    english=subprocess.check_output(['7z','x','-so',str(archive),'fedata/text/text.eng'])
    labels=[]
    for ident in (155,156,157,158):
        offset=struct.unpack_from('<I',english,4*ident)[0]
        labels.append(english[offset:english.index(b'\0',offset)].decode('latin1'))
    assert labels==['Stereo','Mono','Dolby Surround','D3D/EAX']
    result['sound_mode_normalization']={'descriptor':'00556c08','key':'audiomode','storage':'006fbc00',
        'ordinal_labels':labels,'english_sha256':hashlib.sha256(english).hexdigest(),
        'capability_helper':'0040faf0..0040fb0f identical:004e21b0(EAX=ffffffff), return Boolean mask20000h.',
        'normalizer':'Modern00472230 changes ordinal3 to0 when capability helper returns0.',
        'limits':'Final official English labels; backend capability source/lifetime and actual availability transition untested. Original retail labels and historical introduction unverified.'}
    old,new=[image.get_data(0x72820,0xb3) for image in images]
    assert old[:14]==new[:14] and old[27:]==new[27:]
    assert old[14:27].hex()=='f6052eeb5500200f858f000000'
    assert new[14:27].hex()=='e8bdfbffff'+'90'*8
    result['save_entry_policy']={
        'paired_complete_span':'00472820..004728d3','bytes':179,
        'changed_region':'0047282e..0047283b; all other envelope bytes identical',
        'original':'TEST byte0055eb2e,20h; nonzero skips to epilogue004728ca.',
        'modern':'CALL004723f0 refreshes header before remaining save admission gates; eight NOP bytes.',
        'retained':'006fd3a0 gate, literal20f0-byte disk request,0055e88c gate, block-copy/format/write/free sequence.',
        'limits':['Removed local flag gate is not proof of unconditional save or absence of other callers/gates.',
                  'Modern refresh occurs even if a later gate prevents writing; actual file/API effects untested.']}
    (ROOT/'analysis/evidence/audits/original-modern-config-loading.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: config baselines, header bytes, import identities and load spans')


if __name__=='__main__':main()
