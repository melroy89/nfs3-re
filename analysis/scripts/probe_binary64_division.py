"""Run extracted NFS3 arithmetic helpers in an isolated, freestanding i386 ELF.

Requires Linux i386 execution support, GNU as/ld and pefile. Does not launch Wine
or modify the input executable. Error-reporting tails are replaced by flags and infinity stubs.
Tests integer, ordinary x87, and adjusted x87 division using unchanged bytes.
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
(t/'helpers.bin').write_bytes(p.get_data(0x52643c-base,0x526642-0x52643c))
(t/'adjusted.bin').write_bytes(p.get_data(0x5269d4-base,0x527058-0x5269d4))
(t/'constants.bin').write_bytes(p.get_data(0x56ccc0-base,0x1c))
def bits(x): return struct.unpack('<Q',struct.pack('<d',x))[0]
cases=[('ordinary',bits(3.0),bits(2.0)),('third',bits(1.0),bits(3.0)),('negative_zero',bits(-0.0),bits(2.0)),('rhs_zero',bits(1.0),bits(-0.0)),('both_zero',bits(0.0),bits(0.0)),('tiny_negative',0x8000000000000001,bits(1.0)),('min_normal_twice',0x0010000000000000,bits(2.0)),('min_normal_four',0x0010000000000000,bits(4.0)),('min_normal_eight',0x0010000000000000,bits(8.0)),('subnormal',1,bits(2.0)),('overflow_positive',0x7fefffffffffffff,bits(0.5)),('overflow_negative',0xffefffffffffffff,bits(0.5)),('overflow_negative_divisor',0x7fefffffffffffff,bits(-0.5))]
for exponent in [30,31,32,33,52,53,54,55]:
 cases.append((f'underflow_shift_{exponent}',0x0010000000000000,bits(2.0**exponent)))
for highbyte in [0x8e,0x8f,0xa7,0xbf,0xd7,0xef,0xf0]:
 cases.append((f'adjusted_pattern_{highbyte:02x}',bits(4195835.0),(0x3ff<<52)|((highbyte&0x7f)<<45)))
rng=random.Random(52648)
for i in range(1024):
 a=(rng.getrandbits(1)<<63)|(rng.randrange(900,1100)<<52)|rng.getrandbits(52)
 b=(rng.getrandbits(1)<<63)|(rng.randrange(900,1100)<<52)|rng.getrandbits(52)
 cases.append((f'normal_random_{i}',a,b))
# Direct software entry lacks zero guards: do not feed it signed-zero operands.
vectors=[(name,a,b,flag,op) for name,a,b in cases for flag,op in [(0,0),(1,0),(2,0),(0,1)] if not (op and ((a&0x7fffffffffffffff)==0 or (b&0x7fffffffffffffff)==0))]
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
 shr eax,1
 mov byte ptr [0x567858],al
 mov dword ptr [error_flag],0
 mov eax,[edi]
 mov edx,[edi+4]
 mov ebx,[edi+8]
 mov ecx,[edi+12]
 cmp dword ptr [edi+20],0
 jne software
 call division_helper
 jmp result
software:
 call software_helper
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
division_helper:
.incbin "HELPERS"
.set software_helper,division_helper+0x53
.section .adjusted,"ax"
.incbin "ADJUSTED"
.section .constants,"a"
.incbin "CONSTANTS"
.section .zero,"ax"
 xor edx,edx
 xor eax,eax
 ret
.section .dividezero,"ax"
 jmp dividezero_stub
.section .overflow,"ax"
 mov dword ptr [error_flag],1
 and eax,0x80000000
 or eax,0x7ff00000
 mov edx,eax
 xor eax,eax
 ret
.section .text
dividezero_stub:
 mov dword ptr [error_flag],2
 mov edx,0x7ff00000
 xor eax,eax
 ret
.section .fdflags,"aw"
.byte 0
.section .probe,"aw"
.byte 0
.section .data
error_flag: .long 0
vectors: .incbin "VECTORS"
results: .space RESULT_SIZE
'''.replace('COUNT',str(len(vectors))).replace('RESULT_SIZE',str(12*len(vectors))).replace('HELPERS',str(t/'helpers.bin')).replace('VECTORS',str(t/'vectors.bin')).replace('ADJUSTED',str(t/'adjusted.bin')).replace('CONSTANTS',str(t/'constants.bin'))
(t/'probe.s').write_text(assembly)
subprocess.run(['as','--32','-o',str(t/'probe.o'),str(t/'probe.s')],check=True)
subprocess.run(['ld','-m','elf_i386','-Ttext=0x100000','-Tdata=0x200000','--section-start=.helpers=0x52643c','--section-start=.adjusted=0x5269d4','--section-start=.constants=0x56ccc0','--section-start=.zero=0x52c88a','--section-start=.dividezero=0x52c89b','--section-start=.fdflags=0x567858','--section-start=.overflow=0x52c8a7','--section-start=.probe=0x5644c1','-o',str(t/'probe'),str(t/'probe.o')],check=True)
r=subprocess.run([str(t/'probe')],capture_output=True,timeout=5,check=True)
assert len(r.stdout)==12*len(vectors)
rows=[]
for i,(name,a,b,f,o) in enumerate(vectors):
 value,err=struct.unpack_from('<QI',r.stdout,12*i)
 rows.append(dict(case=name,a=f'{a:016x}',b=f'{b:016x}',path='direct_integer' if o else ('adjusted_x87' if f==2 else ('x87' if f else 'guarded_integer')),op='divide',result=f'{value:016x}',error_stub=err))
mismatches=[]
for row in rows:
 if not row['case'].startswith('normal_random_'): continue
 a=struct.unpack('<d',bytes.fromhex(row['a'])[::-1])[0]
 b=struct.unpack('<d',bytes.fromhex(row['b'])[::-1])[0]
 reference=bits(a/b)
 if row['result'] != f'{reference:016x}': mismatches.append(row)
report={'sha256':digest,'method':'Native Linux i386 execution of unchanged extracted helper bytes; FINIT default control word; synthetic operands and dispatch flag',
'code_range':'0052643c..00526641 and005269d4..00527057; constants0056ccc0..0056ccdb','zero_tail':'local equivalent at0052c88a','divide_zero_tail':'stub at0052c89b records flag2 and returns positive infinity; original callback83 return/sign not modeled',
'overflow_tail':'stub at0052c8a7 records branch and returns signed infinity; original error reporting omitted',
'case_count':len(rows),'normal_random_mismatches':mismatches,'directed_cases':[r for r in rows if not r['case'].startswith('normal_random_')],
'limits':'Not Wine gameplay evidence; adjusted x87 tested only via binary64 wrapper (not extended subnormal/numerator-exponent1 branches or TOP0 branch); direct integer zero precondition inferred from assembly loops; no caller admission, all IEEE inputs, alternate rounding modes, x87 status flags or error callback lifecycle guarantee.'}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'temporary_harness':str(t),'output':str(args.output),'case_count':len(rows),'normal_random_mismatches':len(mismatches)}))
