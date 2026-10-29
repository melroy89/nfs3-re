# Dispatcher descriptor crosswalk: cases 0–15 and 31–79

## Scope and method

Read-only static analysis of the shipped `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. The REA Ghidra 12.1.4 session was ephemeral. No persistent Ghidra project, executable, or runtime state was changed.

The descriptor block begins at `004af3b0` and contains 80 eight-byte rows. The raw layout is a DWORD pointer to an eight-character token followed by a DWORD selector/field ID. The full 640 bytes are retained as REA evidence `ev_331f01e71c12015028022782f9140e49432c2732246b2ffe22c09868443b0748`; token bytes are covered by `ev_820388e96b2ac17f9e596372e4c190546a41cc1f850b65301346e1ef4585a20a`. The parser at `004b1380` switches on its field ordinal and writes the parsed value to the profile offsets shown below (pseudocode evidence `ev_9984d645a315ca601be92b2bfc55514c286d8e7a9e4afe1ce403fec36bf95aef`). The dispatcher destinations and complete 320-byte table at `004b478c` are recorded in the [case audit](dispatcher-case-audit.md), including table-byte evidence `ev_3f44636cda7e7fe522f88fb40ef15a6e58366656abaa9f8f382d918d59dc0c88`.

The mapping is supported by the descriptor token at its row, parser-side writes at explicit profile offsets, and the dispatcher case’s observed record offset/type. The join is therefore checked against data layout and parser writes; it is not inferred from a run of switch indices alone. Existing crosswalk for cases 16–30 remains in [detailed analysis notes](detailed-analysis-notes.md#unfunctioned-accesses-to-the-abs-profile-offset).

## Cases 0–15

| Case | Descriptor row | Token (stored ID) | Parser write / comparison access | Crosswalk status |
|---:|---:|---|---|---|
| 0 | 0 | `serialnu` (0) | Parser handles this entry through a separate local value path; dispatcher case 0 stores result `1` unconditionally. | Token row supported; no field comparison established. |
| 1 | 1 | `carclass` (1) | DWORD at `+0x00` | Supported by matching parser and comparator offset. |
| 2 | 2 | `mass[kg]` (2) | Float at `+0x04` | Supported. |
| 3 | 3 | `numberof` (3) | DWORD at `+0x08` | Supported. |
| 4 | 4 | `numberof` (75) | DWORD at `+0x0c` | Supported; repeated token has a distinct stored ID and offset. |
| 5 | 5 | `gearshif` (4) | DWORD at `+0x10` | Supported. |
| 6 | 6 | `shiftbli` (5) | Eight DWORDs at `+0x14 + 4*i`, `i=0..7` | Supported. |
| 7 | 7 | `brakebli` (6) | Eight DWORDs at `+0x34 + 4*i`, `i=0..7` | Supported. |
| 8 | 8 | `citytorp` (7) | Eight floats at `+0x94 + 4*i`, `i=0..7` | Supported. |
| 9 | 9 | `citytorp` (76) | Eight floats at `+0xb4 + 4*i`, `i=0..7` | Supported; repeated token, distinct stored ID and offset. |
| 10 | 10 | `gearrati` (8) | Eight floats at `+0x54 + 4*i`, `i=0..7` | Supported. |
| 11 | 11 | `gearrati` (77) | Eight floats at `+0x74 + 4*i`, `i=0..7` | Supported; repeated token, distinct stored ID and offset. |
| 12 | 12 | `geareffi` (9) | Eight floats at `+0xd4 + 4*i`, `i=0..7` | Supported. |
| 13 | 13 | `geareffi` (78) | Eight floats at `+0xf4 + 4*i`, `i=0..7` | Supported; repeated token, distinct stored ID and offset. |
| 14 | 14 | `torquecu` (10) | 41 floats at `+0x114 + 4*i`, `i=0..40` | Supported. |
| 15 | 15 | `finalgea` (11) | Float at `+0x1b8` | Supported. |

## Cases 31–79

| Case | Descriptor row | Token (stored ID) | Parser write / comparison access | Crosswalk status |
|---:|---:|---|---|---|
| 31 | 31 | `powerste` (26) | DWORD at `+0x238` | Supported. |
| 32 | 32 | `ringacce` (27) | Float at `+0x23c` | Supported. |
| 33 | 33 | `turninra` (28) | Float at `+0x240` | Supported. |
| 34 | 34 | `turnoutr` (29) | Float at `+0x244` | Supported. |
| 35 | 35 | `laterala` (30) | Float at `+0x248` | Supported. |
| 36 | 36 | `aerodyna` (31) | Float at `+0x24c` | Supported. |
| 37 | 37 | `gasofffa` (32) | Float at `+0x250` | Supported. |
| 38 | 38 | `gtransfe` (33) | Float at `+0x254` | Supported. |
| 39 | 39 | `urningci` (34) | Float at `+0x258` | Supported; token retained literally. |
| 40 | 40 | `ecsfront` (35) | Three DWORDs at `+0x25c..+0x264` | Token/offset supported by parser’s three-element write and dispatcher case. |
| 41 | 41 | `pecsrear` (36) | Three DWORDs at `+0x268..+0x270` | Token/offset supported by parser’s three-element write and dispatcher case. |
| 42 | 42 | `tirewear` (37) | Float at `+0x274` | Supported. |
| 43 | 43 | `slidemul` (38) | Float at `+0x278` | Supported. |
| 44 | 44 | `spinvelo` (39) | Float at `+0x27c` | Supported. |
| 45 | 45 | `slidevel` (40) | Float at `+0x280` | Supported. |
| 46 | 46 | `slideass` (41) | DWORD at `+0x284` | Supported. |
| 47 | 47 | `pushfact` (42) | DWORD at `+0x288` | Supported. |
| 48 | 48 | `lowturnf` (43) | Float at `+0x28c` | Supported. |
| 49 | 49 | `highturn` (44) | Float at `+0x290` | Supported. |
| 50 | 50 | `rollfact` (45) | Float at `+0x294` | Supported. |
| 51 | 51 | `roadbump` (46) | Float at `+0x298` | Supported. |
| 52 | 52 | `spoilerf` (47) | DWORD at `+0x29c` | Supported. |
| 53 | 53 | `leractiv` (48) | Float at `+0x2a0` | Supported. |
| 54 | 54 | `gradualt` (49) | DWORD at `+0x2a4` | Supported. |
| 55 | 55 | `mturncut` (50) | DWORD at `+0x2a8` | Supported. |
| 56 | 56 | `pturncut` (51) | DWORD at `+0x2ac` | Supported. |
| 57 | 57 | `mturnspe` (52) | Float at `+0x2b0` | Supported. |
| 58 | 58 | `pturnspe` (53) | Float at `+0x2b4` | Supported. |
| 59 | 59 | `eturnspe` (54) | Float at `+0x2b8` | Supported. |
| 60 | 60 | `subdivid` (55) | DWORD at `+0x2bc` | Supported. |
| 61 | 61 | `cameraar` (56) | DWORD at `+0x2c0` | Supported. |
| 62 | 62 | `odydamag` (57) | Float at `+0x2c4` | Supported. |
| 63 | 63 | `inedamag` (58) | Float at `+0x2c8` | Supported. |
| 64 | 64 | `iondamag` (59) | Float at `+0x2cc` | Supported. |
| 65 | 65 | `enginetu` (60) | Float at `+0x2d0` | Supported. |
| 66 | 66 | `brakebal` (61) | Float at `+0x2d4` | Supported. |
| 67 | 67 | `eeringsp` (62) | Float at `+0x2d8` | Supported. |
| 68 | 68 | `ratfacto` (63) | Float at `+0x2dc` | Supported. |
| 69 | 69 | `tiffness` (64) | Float at `+0x2e0` | Supported. |
| 70 | 70 | `aerofact` (65) | Float at `+0x2e4` | Supported. |
| 71 | 71 | `irefacto` (66) | Float at `+0x2e8` | Supported. |
| 72 | 72 | `aiacc0ac` (67) | 14 floats at `+0x2ec + 4*i`, `i=0..13` | Supported. |
| 73 | 73 | `aiacc1ac` (68) | 14 floats at `+0x324 + 4*i`, `i=0..13` | Supported. |
| 74 | 74 | `aiacc2ac` (69) | 14 floats at `+0x35c + 4*i`, `i=0..13` | Supported. |
| 75 | 75 | `aiacc3ac` (70) | 14 floats at `+0x394 + 4*i`, `i=0..13` | Supported. |
| 76 | 76 | `aiacc4ac` (71) | 14 floats at `+0x3cc + 4*i`, `i=0..13` | Supported. |
| 77 | 77 | `aiacc5ac` (72) | 14 floats at `+0x404 + 4*i`, `i=0..13` | Supported. |
| 78 | 78 | `aiacc6ac` (73) | 14 floats at `+0x43c + 4*i`, `i=0..13` | Supported. |
| 79 | 79 | `aiacc7ac` (74) | 14 floats at `+0x474 + 4*i`, `i=0..13` | Supported. |

The parser evidence explicitly gives the two three-DWORD arrays for cases 40–41 and the eight `0x0e`-element ranges for cases 72–79. The latter cover 112 consecutive floats from `+0x2ec` through `+0x4ab`, with no implied semantic names beyond the literal descriptor tokens.

## Limits

- Case 0 has a descriptor token row, but the comparator unconditionally writes a matching result; no read/compare of the `serialnu` profile field was observed in that case.
- This crosswalk establishes a static relationship among descriptor rows, parser writes, and compared record offsets. It does not establish a caller, record identities, runtime reachability, or broader semantic meanings for literal tokens.
- Case-local equality details and aggregate difference polarity remain as documented in the [case audit](dispatcher-case-audit.md). No new claim of live ABS behavior is made.
