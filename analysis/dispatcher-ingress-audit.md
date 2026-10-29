# Static ingress audit: record comparator `004b48d0`

## Target and constraints

Audited the installation executable at:

`/home/melroy/.local/share/winegui/prefixes/NFS3/dosdevices/c:/Program Files/Electronic Arts/Need For Speed III/nfs3.exe`

REA/Ghidra canonicalized the DOS-device path to `/home/melroy/.local/share/winegui/prefixes/NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III/nfs3.exe`. SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, matching the executable named by the preceding dispatcher reports. PE x86; Ghidra 12.1.4; ephemeral, source-immutable analysis. No target execution, binary edits, saved Ghidra project edits, or persistent annotations were made.

This is a bounded static ingress search. It does not claim runtime reachability.

## Findings

- REA's indexed xrefs to `004b48d0` are empty (`ev_86228838061ee2ca4f80ba70f1668818e9561961580ced93a6c127ac2f8cf13a`). Address context classifies it as `not_in_procedure` (`ev_bea126657cb6095e5148155211353ddf7505b07c4efa16f138546b9cc5e60efc`). Thus Ghidra has no caller report for this code.
- Indexed xrefs to the interior dispatch instruction `004b4919` are also empty (`ev_17c41537dd1f158025a705b5b9da9f055500d9cb1f72b3b8458087b62e1e5f69`). The jump table at `004b478c` has the expected single indexed reference from `004b4919` (`ev_caaad7385c4d1632b609f2e5c6070e3a421aec299c612b61258234b5a0956c34`). These results corroborate that the indexed graph sees the internal table dispatch but provides no external ingress.
- Inspected analyzed bytes across `004b47c0..004b4950` (`ev_bea126657cb6095e5148155211353ddf7505b07c4efa16f138546b9cc5e60efc`). The region begins with the 80-DWORD case table and then the comparator's setup at `004b48d0`. Existing reports establish that nearby cleanup code returns at `004b4788`, followed by table padding; that return does not provide a fall-through caller into the comparator.
- Independent raw search of the exact file found **zero** file occurrences of the little-endian absolute pointer/value `d0 48 4b 00`, and **zero** `E8 rel32` call or `E9 rel32` jump encodings whose destination, when mapped through the PE code-section raw/virtual mapping, equals `004b48d0`. A full `objdump -d -Mintel` pass over the same executable also produced no direct `call`/`jmp`/conditional-branch target in `004b47xx..004b48d0`. The latter is supplementary disassembler output, not proof against indirect control flow.

## Conclusion and identity assessment

No caller, containing routine, or semantic caller identity is established. No direct relative call/jump or absolute pointer reference to the comparator entry was recovered. The code may be reached through an indirect register/memory transfer, a derived address, an unrecognized code region, or may be unreachable in this artifact; this search does not distinguish those possibilities. The two record pointer roles remain the only supported input description from `dispatcher-record-contract.md`; no higher-level record or caller identity is assigned.

## Reproduction boundary

1. Verify the exact executable SHA-256 above.
2. In a read-only byte search, check the entire file for the little-endian 32-bit value `0x004b48d0` (`d0 48 4b 00`).
3. For every file offset in the mapped PE code section, decode candidate five-byte `E8`/`E9` rel32 forms, compute `VA(next_instruction) + signed_disp32` using the section's `PointerToRawData` and `VirtualAddress`, and retain exact destinations `0x004b48d0`. No candidate was found.
4. Run `objdump -d -Mintel` on this same file and search direct call/jump/conditional-branch operands in the local `004b47xx..004b48d0` neighborhood. No such operand was found.
5. Query indexed xrefs for `0x004b48d0`, `0x004b4919`, and `0x004b478c`; preserve the distinction between the empty ingress results and table's dispatch reference.

These checks cover direct references and common embedded address forms only. They do not exhaust instruction sequences that synthesize addresses, indirect control transfers, opaque data/code overlap, or runtime-generated control flow.
