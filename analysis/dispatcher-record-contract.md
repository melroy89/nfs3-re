# Record comparison dispatcher at `004b48d0`

## Evidence and scope

This is a read-only static analysis of the shipped `nfs3.exe` in the local Ghidra 12.1.4 REA session. Its SHA-256 is `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Ghidra imported it in an ephemeral, source-immutable session. No runtime execution or binary modification was performed.

## Observed record and result contract

- `004b48d0` has a machine-code function prologue, but Ghidra does not recognize it as a procedure. The dispatch instruction at `004b4919` likewise has no procedure, so there is no decompiler/caller report for this code. Its bytes are retained in REA evidence `ev_6ca01a9f28ceec6fcba203361ef85db302040ccb625a6ef9e0d0294d92b60258`.
- Entry copies `EAX` to `ECX` and `EDX` to `ESI`. These are two input record pointers. If either pointer is null, the routine immediately returns `AL=1` (`004b48da..004b48eb`). The exact higher-level identities of those records and the caller that supplies them remain unresolved.
- The result scratch is 80 bytes at `[EBP-0x54 .. EBP-0x05]`, indexed by slot `EDX` (`0..79`). The routine initializes it by setting `EBX=0x50`, `EDX=0`, and `EAX=&scratch`, then calling `004e0640` (`004b48ed..004b48f7`). Helper assembly evidence `ev_edba6031245f08defe2455037e5f985bc5cdd37d3a164dc6cc2ec0077638f2f9` shows `004e0640` sets `ECX=EBX`, replicates `DL` across `EDX`, and calls `004ff4c0`; the latter is a fill loop. Since `DL=0`, this zero-fills all 80 bytes. Thus the initial value is **zero**, not one.
- The dispatcher jumps through the 80-entry table at `004b478c`. Each case compares data in the two records and writes its Boolean equality result (1 equal, 0 unequal) into `[EBP+EDX-0x54]`. The observed cases in the detailed notes map slots 16–30 to parser descriptor fields and record offsets; they support a typed record-comparison interpretation. Full per-slot mapping is incomplete.
- Cases store their result and rejoin the increment path; the common match path at `004b4905` stores 1. The increment path advances `EDX` and terminates when `EDX >= 0x50` (`004b4905..004b4917`). The loop therefore covers exactly 80 slots, with valid table indices 0 through 79. `004b4919` performs the indirect jump through the same table. Ghidra's recorded exact xref inventory lists this jump; raw disassembly additionally shows the initial table jump at `004b48fe` (`ev_caaad7385c4d1632b609f2e5c6070e3a421aec299c612b61258234b5a0956c34`).
- Final scan evidence `ev_12fb2ea479046d5b7ce2c516cbbe91d9ff4ac70b6273d4e5c28cb450fb440b0f` decodes `004b54c5..004b54e9`: scan scratch from index 0 through 79; if any byte is zero, return `AL=1`; if all 80 bytes are nonzero, return `AL=0`. Therefore, for non-null inputs, this is a **difference predicate**: returns 1 if any compared slot differs, 0 if all compared slots match. Null inputs also return 1, a special case that must not be conflated with ordinary comparison.

## Candidate `004b474f`

`004b474f` is not the dispatcher entry and Ghidra resolves it as `not_in_procedure` (`ev_669fe456becfc9e3b4eddfc3b5e82b598b668b678a8c884a7f41ee866d8c060a`). Its bytes are in the same REA read (`ev_6ca01a9f28ceec6fcba203361ef85db302040ccb625a6ef9e0d0294d92b60258`). They continue a preceding cleanup path: the code iterates `EDX=0..79`, loads pointer entries from `[EBP+EDX*4-0x196]`, calls `004e1890` for non-null entries, and clears each entry. It then returns at `004b4788`; `004b4789..004b478b` is padding before the table at `004b478c`. Exact ownership of that preceding cleanup path and any relation to the comparison inputs are not established. Exact direct xrefs to `004b474f` are empty (`ev_e4c985d7a51937f2a4e606d895251649d801b39189209c0edfe83e282b7131c2`).

## Unresolved

- The upstream caller and the semantic names/roles of the two compared records.
- Whether every table case is reachable in an intended calling context. Case offsets/extents and descriptor crosswalks are now covered by dispatcher-case-audit.md, dispatcher-loops-40-41.md and dispatcher-descriptor-crosswalk.md.
- Whether `004b474f`'s cleanup loop prepares or owns any data used by the comparator; adjacency and a shared loop bound alone do not prove a relationship.
- Runtime reachability and behavior. No dynamic execution was used.
