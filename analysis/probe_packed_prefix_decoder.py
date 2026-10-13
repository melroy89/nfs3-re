"""Bounded synthetic tests of unchanged NFS3 prefix-decoder machine code.

Runs a freestanding Linux i386 ELF, not Wine or gameplay. Requires GNU as/ld,
Linux i386 execution support and pefile. Inputs are complete hand-built canonical
codebooks with explicit end commands and readable lookahead padding. No malformed
inputs, allocation, upstream dispatch or asset-file compatibility are tested.
"""
import argparse
import hashlib
import json
import pathlib
import struct
import subprocess
import tempfile

import pefile

EXPECTED_SHA = '2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb'
OUTPUT_SIZE = 4096


def integer_code(value):
    """k zeroes, one, k+2 payload bits: value = 2**(k+2)-4+payload."""
    width = (value + 4).bit_length() - 1
    return '0' * (width - 2) + '1' + format(value + 4 - (1 << width), f'0{width}b')


def codebook(counts, symbols, escape):
    assert len(symbols) == sum(counts) <= 256
    assert len(set(symbols)) == len(symbols) and escape in symbols
    assert sum(n * (1 << (len(counts) - i - 1)) for i, n in enumerate(counts)) == 1 << len(counts)
    table = format(escape, '08b') + ''.join(integer_code(n) for n in counts)
    used, previous = set(), 255
    for symbol in symbols:
        cursor, rank = previous, 0
        while True:
            cursor = (cursor + 1) & 255
            if cursor not in used:
                if cursor == symbol:
                    break
                rank += 1
        table += integer_code(rank)
        previous = symbol
        used.add(symbol)
    codes, next_code, index = {}, 0, 0
    for length, count in enumerate(counts, 1):
        next_code <<= 1
        for _ in range(count):
            codes[symbols[index]] = format(next_code, f'0{length}b')
            next_code += 1
            index += 1
    return table, codes


def pack_bits(bits):
    bits += '0' * (-len(bits) % 8)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def make_case(name, counts, symbols, escape, operations, tag=0x30fb, extra_header=False):
    table, codes = codebook(counts, symbols, escape)
    body, expected = '', bytearray()
    for operation, value in operations:
        if operation == 'literal':
            assert value != escape
            body += codes[value]
            expected.append(value)
        elif operation == 'raw':
            body += codes[escape] + integer_code(0) + '0' + format(value, '08b')
            expected.append(value)
        elif operation == 'repeat':
            assert value > 0 and expected
            body += codes[escape] + integer_code(value)
            expected.extend([expected[-1]] * value)
        else:
            raise AssertionError(operation)
    body += codes[escape] + integer_code(0) + '1'
    header = (tag | (0x100 if extra_header else 0)).to_bytes(2, 'big')
    if extra_header:
        header += bytes.fromhex('123456')
    data = header + len(expected).to_bytes(3, 'big') + pack_bits(table + body) + bytes(16)
    raw = bytes(expected)
    if tag == 0x32fb:
        accumulator = 0
        for i, value in enumerate(expected):
            accumulator += value
            expected[i] = accumulator & 255
    elif tag == 0x34fb:
        first = second = 0
        for i, value in enumerate(expected):
            first += value
            second += first
            expected[i] = second & 255
    return dict(name=name, counts=counts, symbols=symbols, escape=escape,
                operations=operations, tag=f'{tag:04x}', extra_header=extra_header,
                compressed=data, expected=bytes(expected), before_integration=raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA:
        raise SystemExit('Unexpected executable fingerprint; addresses must be revalidated')
    pe = pefile.PE(str(args.binary))
    cases = []
    for tag in [0x30fb, 0x32fb, 0x34fb]:
        for extra in [False, True]:
            cases.append(make_case(f'mixed_{tag:04x}_header{int(extra)}', [2], [0, 65], 0,
                [('literal', 65)] * 17 + [('raw', 0), ('raw', 255), ('repeat', 9)] +
                [('raw', 3), ('repeat', 1), ('literal', 65)], tag, extra))
    cases.append(make_case('empty_end', [2], [0, 65], 0, []))
    cases.append(make_case('single_literal', [2], [0, 65], 0, [('literal', 65)]))
    cases.append(make_case('long_repeat_300', [2], [0, 65], 0, [('literal', 65), ('repeat', 300)]))
    for extra in [False, True]:
        cases.append(make_case(f'nine_bit_escape_header{int(extra)}', [1]*8+[2], list(range(10)), 9,
            [('literal', n) for n in list(range(9))*3] + [('raw', 9), ('repeat', 4)], extra_header=extra))
        cases.append(make_case(f'nine_bit_literal_header{int(extra)}', [1]*8+[2], list(range(10)), 0,
            [('literal', n) for n in list(range(1,10))*3] + [('raw', 0), ('repeat', 4)], extra_header=extra))
    cases.append(make_case('full_byte_alphabet', [0]*7+[256], list(range(256)), 0,
        [('literal', n) for n in range(1,256)] + [('raw', 0), ('repeat', 12)]))
    cases.append(make_case('cyclic_symbol_order', [0,4], [250, 3, 65, 0], 0,
        [('literal', n) for n in [250,3,65]*9] + [('raw', 0)]))
    with tempfile.TemporaryDirectory(prefix='nfs3-prefix-probe-') as temporary:
        temp = pathlib.Path(temporary)
        (temp/'decoder.bin').write_bytes(pe.get_data(0x50ed50-pe.OPTIONAL_HEADER.ImageBase, 0x5100f3-0x50ed50))
        assembly = f''' .intel_syntax noprefix
.section .text
.global _start
_start:
 mov eax,3
 xor ebx,ebx
 mov ecx,offset input_buffer
 mov edx,4096
 int 0x80
 test eax,eax
 jle failed
 mov [saved_stack],esp
 mov eax,offset input_buffer
 mov edx,offset output_buffer
 mov ebx,1
 mov ecx,0x12345678
 mov esi,0x23456789
 mov edi,0x3456789a
 mov ebp,0x456789ab
 call decoder
 mov [result],eax
 mov [result+4],ecx
 mov [result+8],esi
 mov [result+12],edi
 mov [result+16],ebp
 mov eax,esp
 sub eax,[saved_stack]
 mov [result+20],eax
 mov eax,4
 mov ebx,1
 mov ecx,offset result
 mov edx,{OUTPUT_SIZE+24}
 int 0x80
 mov eax,1
 xor ebx,ebx
 int 0x80
failed:
 mov eax,1
 mov ebx,99
 int 0x80
.section .decoder,"ax"
decoder:
.incbin "{temp/'decoder.bin'}"
.section .data
saved_stack: .long 0
input_buffer: .space 4096
result: .space 24
output_buffer: .fill {OUTPUT_SIZE},1,0xa5
'''
        (temp/'probe.s').write_text(assembly)
        subprocess.run(['as','--32','-o',str(temp/'probe.o'),str(temp/'probe.s')], check=True)
        subprocess.run(['ld','-m','elf_i386','-Ttext=0x100000','-Tdata=0x200000',
                        '--section-start=.decoder=0x50ed50','-o',str(temp/'probe'),str(temp/'probe.o')], check=True)
        rows = []
        for case in cases:
            assert len(case['compressed']) < 4096 and len(case['expected']) < OUTPUT_SIZE
            result = subprocess.run([str(temp/'probe')], input=case['compressed'], capture_output=True, timeout=5, check=True)
            assert len(result.stdout) == OUTPUT_SIZE+24, case['name']
            size, ecx, esi, edi, ebp, stack_delta = struct.unpack_from('<6I', result.stdout)
            data = result.stdout[24:]
            assert size == len(case['expected']), (case['name'], 'returned length', size)
            assert data[:size] == case['expected'], (case['name'], 'decoded content')
            assert data[size:] == bytes([0xa5])*(OUTPUT_SIZE-size), (case['name'], 'output canary')
            assert (ecx,esi,edi,ebp,stack_delta) == (0x12345678,0x23456789,0x3456789a,0x456789ab,0), (case['name'], 'ABI')
            rows.append({k:v for k,v in case.items() if k not in ('compressed','expected','before_integration')} |
                        dict(input_hex=case['compressed'].hex(), expected_hex=case['expected'].hex(),
                             raw_before_integration_hex=case['before_integration'].hex(), returned_length=size,
                             decoded_bytes_match=True, untouched_output_tail=True, preserved_ecx_esi_edi_ebp=True,
                             stack_delta=0))
    assert hashlib.sha256(args.binary.read_bytes()).hexdigest() == digest
    report = dict(sha256=digest, code_range='0050ed50..005100f2', case_count=len(rows), all_assertions_passed=True,
                  method='Linux freestanding i386 ELF executing unchanged original decoder bytes at original address; no stubs or Wine',
                  limits='Synthetic valid complete canonical tables only; readable input lookahead padding; no actual asset corpus, malformed inputs, input/output bounds guarantee, alternate EBX branch or upstream dispatch validation. Five-second timeout per process. Canaries check only the allocated output tail.',
                  cases=rows)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(case_count=len(rows), all_assertions_passed=True, output=str(args.output))))


if __name__ == '__main__':
    main()
