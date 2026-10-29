# Dispatcher case audit: `004b4919` / `004b478c`

## Current status

**DONE:** case-head inventory, cases40–41 loop extents and the previously missing descriptor crosswalk. See [descriptor crosswalk](dispatcher-descriptor-crosswalk.md). Token-unresolved cells below retain this pass's original evidence boundary; the linked crosswalk supersedes those cells. Caller, semantic record roles and runtime reachability remain OPEN.

## Scope and evidence

This is a read-only static pass over the shipped `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`). REA opened an ephemeral Ghidra 12.1.4 analysis target; no persistent Ghidra project, executable, or runtime writes were made. The table is 80 DWORD destinations, indexed 0..79; `004b4919` is `JMP dword ptr [EDX*4+004b478c]` (current evidence `ev_df685a78a38079eef108f02145f0f97bbc556b88cfa7877e03b2f8334187d658`), and the 320 table bytes were read completely (`ev_3f44636cda7e7fe522f88fb40ef15a6e58366656abaa9f8f382d918d59dc0c88`). The table and dispatch remain outside a recognized procedure. Earlier detailed notes establish descriptor-token links for cases 16–30; see [detailed-analysis-notes.md](detailed-analysis-notes.md#unfunctioned-accesses-to-the-abs-profile-offset).

The new case-head observations are Ghidra-decoded code, not execution. Their key limits are that the switch/cases have no recognized procedure boundary, xrefs do not identify a caller for the candidate entry, and a descriptor-to-case crosswalk outside the previously reviewed 16–30 rows was not recovered in this bounded pass. Consequently, record offsets/types below are direct observations, while any token association beyond the cited existing crosswalk is intentionally left open.

## Cases 0–15

| Case | Destination | Direct observed operation on compared record(s) | Descriptor crosswalk |
|---:|---:|---|---|
| 0 | `004b4905` | Stores byte `1` to the per-case result slot unconditionally. | No descriptor row established. |
| 1 | `004b4920` | DWORD compare at record offset `+0x00`. | Token unresolved. |
| 2 | `004b4932` | x87 float compare at `+0x04`. | Token unresolved. |
| 3 | `004b4949` | DWORD compare at `+0x08`. | Token unresolved. |
| 4 | `004b495d` | DWORD compare at `+0x0c`. | Token unresolved. |
| 5 | `004b4971` | DWORD compare at `+0x10`. | Token unresolved. |
| 6 | `004b4985` | Eight DWORD comparisons, elements at `+0x14 + 4*i`, `i=0..7`. | Token unresolved. |
| 7 | `004b49bc` | Eight DWORD comparisons, elements at `+0x34 + 4*i`, `i=0..7`. | Token unresolved. |
| 8 | `004b49f2` | Eight x87 float comparisons at `+0x94 + 4*i`, `i=0..7`. | Token unresolved. |
| 9 | `004b4a29` | Eight x87 float comparisons at `+0xb4 + 4*i`, `i=0..7`. | Token unresolved. |
| 10 | `004b4a61` | Eight x87 float comparisons at `+0x54 + 4*i`, `i=0..7`. | Token unresolved. |
| 11 | `004b4a93` | Eight x87 float comparisons at `+0x74 + 4*i`, `i=0..7`. | Token unresolved. |
| 12 | `004b4ac5` | Eight x87 float comparisons at `+0xd4 + 4*i`, `i=0..7`. | Token unresolved. |
| 13 | `004b4afd` | Eight x87 float comparisons at `+0xf4 + 4*i`, `i=0..7`. | Token unresolved. |
| 14 | `004b4b35` | 41 x87 float comparisons at `+0x114 + 4*i`, `i=0..40`. | Token unresolved. |
| 15 | `004b4b6d` | x87 float compare at `+0x1b8`. | Token unresolved. |

Switch indices cannot safely be equated with descriptor field numbers; the cases include scalar and array comparisons with different extents. Do not infer a one-to-one field map from index order alone.

## Cases 31–79

Prior detailed notes directly map case 30 to `gripbias` / field 25 at float offset `+0x234`. The new table destinations then show a mixture of sequential scalar accesses and grouped array comparisons. The code evidence supports the offsets and types listed below, but does not by itself prove a descriptor token name for each case.

| Case(s) | Observed record access | Token link |
|---|---|---|
| 31 | DWORD `+0x238` | Unresolved. |
| 32–39 | Float/DWORD accesses at `+0x23c`, `+0x240`, `+0x244`, `+0x248`, `+0x24c`, `+0x250`, `+0x254`, `+0x258` respectively. | Unresolved. |
| 40–41 | Case 40 compares three DWORDs at `+0x25c`, `+0x260`, `+0x264`; case 41 compares three DWORDs at `+0x268`, `+0x26c`, `+0x270`. Each slot starts at 1 and clears on any mismatch. | Token unresolved; see [instruction-level loop contract](dispatcher-loops-40-41.md). |
| 42–45 | Float accesses at `+0x274`, `+0x278`, `+0x27c`, `+0x280` respectively. | Unresolved. |
| 46–47 | DWORD accesses at `+0x284`, `+0x288`. | Unresolved. |
| 48–51 | Float accesses at `+0x28c`, `+0x290`, `+0x294`, `+0x298`. | Unresolved. |
| 52 | DWORD access at `+0x29c`. | Unresolved. |
| 53 | Float access at `+0x2a0`. | Unresolved. |
| 54–56 | DWORD accesses at `+0x2a4`, `+0x2a8`, `+0x2ac`. | Unresolved. |
| 57–59 | Float accesses at `+0x2b0`, `+0x2b4`, `+0x2b8`. | Unresolved. |
| 60–61 | DWORD accesses at `+0x2bc`, `+0x2c0`. | Unresolved. |
| 62–71 | Float accesses at `+0x2c4`, `+0x2c8`, `+0x2cc`, `+0x2d0`, `+0x2d4`, `+0x2d8`, `+0x2dc`, `+0x2e0`, `+0x2e4`, `+0x2e8` respectively. | Unresolved. |
| 72 | 14 float comparisons at `+0x2ec + 4*i`, `i=0..13`. | Unresolved. |
| 73–79 | Seven further float-comparison chunks in the same base array, with starting element indices `14, 28, 42, 56, 70, 84, 98`; each chunk spans 14 elements. | Unresolved. |

For cases 31–71, the full loop bodies were not enumerated instruction-by-instruction here; the row reports case-head offsets/types from the decoded entries. Cases 72–79 are visibly a chunked comparison of a float region beginning at `+0x2ec`; each chunk iterates 14 elements, for 112 values over all eight cases. This is a structural observation, not a semantic or descriptor-name claim.

## Result semantics and remaining gaps

The caller-side/epilogue check reported by the parent analysis establishes the aggregate result polarity: any zero per-case byte produces `AL=1`; all 80 nonzero bytes produce `AL=0`; a null input returns `1`. Thus the aggregate is a difference-like predicate, not an equality-success return. Individual scalar floating comparisons use `FCOMP`/`FNSTSW`/`SAHF` and equality branches; previously audited cases16–30 test only ZF, so unordered comparisons match there. Other cases require per-branch verification; no universal unordered policy is asserted. Array cases initialize their result to `1` and clear it when an element differs. These local case results must be interpreted under the aggregate polarity.

Unresolved: descriptor row/token correspondence for cases 0–15 and 31–79; recognized function entry, enclosing routine, initial call path, input record identities, and runtime reachability. Existing strings in the executable include literal tokens such as `powerste`, `ringacce`, `turninra`, `turnoutr`, `laterala`, `aerodyna`, and others, but this pass does not have a direct row-to-case reference proving their association, so it does not assign those spellings to the cases above. No live ABS behavior or defect is claimed.
