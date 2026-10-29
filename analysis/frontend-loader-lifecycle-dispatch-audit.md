# Frontend loader lifecycle dispatch audit

## Finding

The two unchecked lifecycle blocks have exact incoming references from pointer-valued data locations, but the available static references do not reveal who owns or reads those entries. I could not identify the event or dispatcher that invokes either block, and therefore cannot say whether dispatch tests loader-active `+0xb1`, request IDs, or completion phases before invoking them. This pass finds no concrete active-load callback path and no proof of serialization.

This audit covers the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) with read-only REA/Ghidra queries and bounded raw-file inspection. The session was closed without a snapshot. No executable, runtime, or persistent Ghidra changes were made.

## Exact observations

- At `00557390`, the 32-byte read includes eight zero bytes followed by `00 77 46 00` and `30 79 46 00`, i.e. little-endian pointers to `00467700` and `00467930` (`read_bytes` Evidence `ev_2b5a38bc006f0a58fd01d00976e7f75d37204698458b5e7bf69ad9f896e93458`; an independent readback is `ev_2a00865902fa1efafb733b6bf80bde4f81655a94c0b4125da53be1fd96aa6652`). The data establishes adjacency of two code pointers; it does not by itself establish a table type, owner, or lifecycle semantics.
- Xrefs to `00467700` return only `00557398` (`ev_07de1f26a3072c5e8e21d5d3d664820a4935053eaecc9c06fad7f95aeb2518fc`); xrefs to `00467930` return only `0055739c` (`ev_99c8e3854f4e8f24d29c24e3002e92749b3bdf087107c194d1a7683d14ad836c`).
- Separate exact-address xref queries for `00557370`, `00557374`, `00557378`, `00557380`, `00557384`, `00557388`, `0055738c`, `00557390`, `00557394`, `00557398`, `0055739c`, and `005573a0` returned no references. The Ghidra xref query projects direct address references; it cannot exclude computed indexing or a base pointer obtained indirectly.
- A bounded raw-byte scan of the exact installed file found the encoded callback addresses `00467700` and `00467930` only at their data slots (file offsets `0x155d98` and `0x155d9c`). It found no raw occurrence of the absolute data-slot/base addresses `00557390`, `00557398`, or `0055739c`. This is consistent with indirect/computed access or an external registration path, but does not identify one.
- The prior exact assembly review establishes that `00467700` clears outer active byte `+0xb1` before checking nested `+0xb8`, then resets/frees that nested context when nonnull; `00467930` passes `0044a660`, clears selected outer flags, then resets/frees nested `+0xb8`. Neither block checks request IDs or phases locally. Those instructions describe callee-side behavior only.

## Bounded search and limits

The search boundary was the exact pointer pair and immediate surrounding data at `00557390`, direct xrefs to each slot and nearby aligned words through `005573a0`, direct xrefs to both lifecycle entry addresses, and exact-byte occurrences of the relevant absolute addresses in the installed executable. No candidate code instruction loading this table base, no direct callsite beyond the pointer slots, and no owning/constructor procedure emerged. No broad all-function decompilation or runtime replay was performed.

Consequently, it is not supported to label `00557390` a confirmed callback table with a known owner. The evidence supports only a pair of adjacent pointer-valued entries targeting the two lifecycle blocks. Nor can this static search determine which event dispatches them, whether invocation is synchronous or re-entrant, or whether any dispatcher checks `+0xb1`, `+0x160/+0x164/+0x170`, or `+0x198/+0x19c`.

## Next discriminator

The exact next static target is the code/data path that supplies or registers base `00557390` (including computed address construction or startup registration), followed to its indirect dispatch and guarded event branch. The current references do not provide that path. If no such path can be recovered from the installed image, resolving whether lifecycle dispatch can overlap a pending read requires a passive runtime trace correlating callback entry with the same nested object's active byte, request IDs, phase fields, and worker helper entry/return. No such runtime observation was made here.
