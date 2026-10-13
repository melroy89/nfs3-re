"""Run extracted NFS3 arithmetic helpers in an isolated, freestanding i386 ELF.

Requires Linux i386 execution support, GNU as/ld and pefile. Does not launch Wine
or modify the input executable. Error-reporting tail is replaced by a flag and
signed-infinity stub; runtime error side effects are not exercised.
"""
import argparse, hashlib, pathlib, random, tempfile, subprocess, struct, json, pefile
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary',type=pathlib.Path)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
binary=args.binary.resolve()
expected='2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
digest=hashlib.sha256(binary.read_bytes()).hexdigest()
if digest != expected: raise SystemExit('Unexpected executable fingerprint; addresses must be revalidated')
p=pefile.PE(str(binary)); base=p.OPTIONAL_HEADER.ImageBase
t=pathlib.Path(tempfile.mkdtemp(prefix='nfs3-numeric-'))
(t/'helpers.bin').write_bytes(p.get_data(0x526642-base,0x52699c-0x526642))
def bits(x): return struct.unpack('<Q',struct.pack('<d',x))[0]
cases=[('ordinary',bits(3.0),bits(2.0)),('cancel',bits(3.0),bits(3.0)),('negative_zero',bits(-0.0),bits(2.0)),('rhs_zero',bits(-0.0),bits(0.0)),('zero_inf',bits(0.0),bits(float('inf'))),('zero_nan',bits(0.0),0x7ff8000000000001),('tiny_negative',0x8000000000000001,bits(1.0)),('min_normal_half',0x0010000000000000,bits(0.5)),('min_normal_quarter',0x0010000000000000,bits(0.25)),('min_normal_eighth',0x0010000000000000,bits(0.125)),('subnormal',1,bits(2.0)),('overflow',0x7fefffffffffffff,bits(2.0))]
for exponent in [3,10,30,53,54,55]:
 for numerator in [1.0,1.25,1.5,1.75]:
  cases.append((f'subtract_rounding_{exponent}_{numerator}',bits(1.0),bits(numerator*2.0**-exponent)))
rng=random.Random(526642)
for i in range(256):
 a=(rng.getrandbits(1)<<63)|(rng.randrange(900,1100)<<52)|rng.getrandbits(52)
 b=(rng.getrandbits(1)<<63)|(rng.randrange(900,1100)<<52)|rng.getrandbits(52)
 cases.append((f'normal_random_{i}',a,b))
vectors=[(name,a,b,flag,op) for name,a,b in cases for flag in [0,1] for op in [0,1]]
(t/'vectors.bin').write_bytes(b''.join(struct.pack('<QQII',a,b,f,o) for _,a,b,f,o in vectors))
assembly=''' .intel_syntax noprefix
.section .text
.global _start
_start:
 finit
 mov edi,offset vectors
 mov esi,offset results
 mov ebp,COUNT
loop_case:
 mov eax,[edi+16]
 mov byte ptr [0x5644c1],al
 mov dword ptr [error_flag],0
 mov eax,[edi]
 mov edx,[edi+4]
 mov ebx,[edi+8]
 mov ecx,[edi+12]
 cmp dword ptr [edi+20],0
 jne multiplication
 call subtract_helper
 jmp result
multiplication:
 call multiply_helper
result:
 mov [esi],eax
 mov [esi+4],edx
 mov eax,[error_flag]
 mov [esi+8],eax
 add edi,24
 add esi,12
 dec ebp
 jnz loop_case
 mov eax,4
 mov ebx,1
 mov ecx,offset results
 mov edx,RESULT_SIZE
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80
.section .helpers,"ax"
subtract_helper:
.incbin "HELPERS"
.set multiply_helper,subtract_helper+0x1bd
.section .zero,"ax"
 xor edx,edx
 xor eax,eax
 ret
.section .overflow,"ax"
 mov dword ptr [error_flag],1
 and eax,0x80000000
 or eax,0x7ff00000
 mov edx,eax
 xor eax,eax
 ret
.section .probe,"aw"
.byte 0
.section .data
error_flag: .long 0
vectors: .incbin "VECTORS"
results: .space RESULT_SIZE
'''.replace('COUNT',str(len(vectors))).replace('RESULT_SIZE',str(12*len(vectors))).replace('HELPERS',str(t/'helpers.bin')).replace('VECTORS',str(t/'vectors.bin'))
(t/'probe.s').write_text(assembly)
subprocess.run(['as','--32','-o',str(t/'probe.o'),str(t/'probe.s')],check=True)
subprocess.run(['ld','-m','elf_i386','-Ttext=0x100000','-Tdata=0x200000','--section-start=.helpers=0x526642','--section-start=.zero=0x52c88a','--section-start=.overflow=0x52c8a7','--section-start=.probe=0x5644c1','-o',str(t/'probe'),str(t/'probe.o')],check=True)
r=subprocess.run([str(t/'probe')],capture_output=True,timeout=5,check=True)
assert len(r.stdout)==12*len(vectors)
rows=[]
for i,(name,a,b,f,o) in enumerate(vectors):
 value,err=struct.unpack_from('<QI',r.stdout,12*i)
 rows.append(dict(case=name,a=f'{a:016x}',b=f'{b:016x}',path='x87' if f else 'integer',op='multiply' if o else 'subtract',result=f'{value:016x}',overflow_stub=bool(err)))
mismatches=[]
for row in rows:
 if not row['case'].startswith('normal_random_'): continue
 a=struct.unpack('<d',bytes.fromhex(row['a'])[::-1])[0]
 b=struct.unpack('<d',bytes.fromhex(row['b'])[::-1])[0]
 reference=bits(a*b if row['op']=='multiply' else a-b)
 if row['result'] != f'{reference:016x}': mismatches.append(row)
report={'sha256':digest,'method':'Native Linux i386 execution of unchanged extracted helper bytes; FINIT default control word; synthetic operands and dispatch flag',
'code_range':'00526642..0052699b','zero_tail':'local equivalent at0052c88a','overflow_tail':'stub at0052c8a7 records branch and returns signed infinity; original error reporting omitted',
'case_count':len(rows),'normal_random_mismatches':mismatches,'directed_cases':[r for r in rows if not r['case'].startswith('normal_random_')],
'limits':'Not Wine gameplay evidence; no caller admission, all IEEE inputs, alternate rounding modes, x87 status flags or error callback lifecycle guarantee.'}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'temporary_harness':str(t),'output':str(args.output),'case_count':len(rows),'normal_random_mismatches':len(mismatches)}))
