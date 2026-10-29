# Control binding persistence audit

## Finding

The installed `FEDATA/CONFIG/config.dat` is 8,432 bytes (`0x20f0`) and contains both control-record layouts at the offsets used by the executable's controls UI and binding initializer:

- Single-player record: file offset `0x16cc`, 13 little-endian DWORDs through `0x16ff`.
- Two-player records: file offset `0x1700`, 26 little-endian DWORDs through `0x1767`; player 1 occupies indices 0–12 and player 2 indices 13–25.

The loader requires an exact `0x20f0` file length before copying the whole file to `006fbb40`. `GetControlMappingBaseForMode` returns `006fd20c` unless the mode value supplied from `006fd3b0` is 1, in which case it returns `006fd240`. These addresses are respectively `006fbb40+0x16cc` and `006fbb40+0x1700`, matching the installed file offsets. The setup routine then selects that same mode-specific base and maps row DWORDs into evaluator slots. This is direct file-to-memory layout evidence; it does not prove the installation's current process loaded this file or which mode/player record is active.

## Installed binding values

Each raw DWORD is shown in hexadecimal as stored on disk. All values have low byte `04`, which the keyboard-binding renderer treats as keyboard input. The displayed key labels come from the packed scancode/character field and the executable's `WriteFrontendKeyboardBindingLabel` mapping. “P1” and “P2” denote positions in the stored two-player table, not a claim that either is currently selected.

| UI row / installed English label | Single record (`0x16cc`) | Two-player P1 (`0x1700`) | Two-player P2 (`0x1734`) |
|---:|---:|---:|---:|
| 0 Steer right | `00004d04` Right | `00004d04` Right | `47002204` G |
| 1 Steer left | `00004b04` Left | `00004b04` Left | `44002004` D |
| 2 Accelerate | `00004804` Up | `00004804` Up | `52001304` R |
| 3 Brake | `00005004` Down | `00005004` Down | `46002104` F |
| 4 Handbrake | `20003904` Space | `00005204` Insert | `20003904` Space |
| 5 Shift up | `41001e04` A | `00004904` Page Up | `41001e04` A |
| 6 Shift down | `5a002c04` Z | `00005104` Page Down | `5a002c04` Z |
| 7 Camera view | `43002e04` C | `4b002504` K | `51001004` Q |
| 8 Horn (Siren) | `48002304` H | `4d003204` M | `57001104` W |
| 9 Look behind | `42003004` B | `00004704` Home | `45001204` E |
| 10 Reset | `52001304` R | `00004f04` End | `58002d04` X |
| 11 Spike strip | `53001f04` S | `50001904` P | `53001f04` S |
| 12 Lights | `4c002604` L | `4c002604` L | `59001504` Y |

For example, row 4 Handbrake is stored as Space for the single-player record and player 2, and Insert for player 1. Its link to evaluator slot 6 and collector action bit `0x04` is documented in [controller-action-label-crosswalk.md](controller-action-label-crosswalk.md). These are stored keyboard bindings, not evidence about physical controller axes.

## Persistence and selection contract

`00472980` constructs a `%sconfig.dat` path using base pointer `007a3034`, opens it through the file layer, and accepts the read only when the returned size equals `0x20f0`. It copies exactly that many bytes to `006fbb40` and checks the first DWORD against `0x20f0`; the following header/version branch may invoke another validator. The save path at `00472820` copies `0x20f0` bytes from `006fbb40` into a newly reserved buffer, clears DWORD index `0x618`, formats the same `config.dat` suffix, and passes the buffer to the file writer. Thus both record ranges persist as part of the full configuration blob.

The mode selector is a runtime global, not an assumption derived from the presence of the two-player record. `004904d0` chooses the 13-DWORD or 26-DWORD base from its mode argument; `ApplyConfiguredBindingsToActionSlots` (`0048f1f0`) uses `006fd3b0` to choose a table and then maps row fields into the evaluator table. No live process, selected UI mode, or active participant was sampled here. The asset's stored bindings happen to match the executable's embedded fallback arrays, but that equality alone does not prove that this specific file was loaded, saved, or currently controls input.

## Provenance and scope

- Installed file: `nfs3_decomp.rep/Electronic Arts/Need For Speed III/FEDATA/CONFIG/config.dat`; size `0x20f0`; SHA-256 `e9e67b195cd90214ae33986ed6d1593e200f067e1b859cd2706e1af9ee0a449d`.
- Executable: installed `nfs3.exe`; SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
- Loader evidence: `00472980`, REA shipped-artifact evidence `ev_af8be2b2697b26ab1daa45dc0b5b05013ceb6e98ddd6fe12b461c0dc66adcc12`. The analysis shows exact-size gate, destination and header check. Mismatched size takes close/delete/fallback; this report does not claim the candidate installed file passed that branch at runtime.
- Save evidence: `00472820`, `ev_a7800462df990baf58a68dc10dac10f1e6159d60a5ba2fbb85193bacdfcd2978`.
- Mode base helper: `004904d0`, `ev_0cae9954e40c484d47f107bb0754119f408c73cfb5aa27400ba8726f6f6f143e`.
- Row-to-slot setup: `0048f1f0`, `ev_23fe7285322b6c7b38ff562d3aa8dd2a148ee9d34d6627300275466c8159dc89`; slot writer `0048f940`, `ev_6f5fb3e3595c01dcbd7ee89382248caacd6f76a7cefab8621640924202853eb8`.
- Packed key label conversion: `0043d7f0`, `ev_a796eb141f02736074b6836063fe211fa45dffc138177d4c9825c382acecb8c8`; controls-row label dispatch and installed English text provenance are listed in [controller-action-label-crosswalk.md](controller-action-label-crosswalk.md). Its `text.eng` SHA-256 is `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`.
- Decoding was limited to bytes `0x16cc..0x1767`, exactly the mapped 13- and 26-DWORD binding arrays. No other config.dat fields were decoded or emitted; whole-file bytes were read only to fingerprint the candidate.

Remaining gap: static evidence identifies the installed candidate's stored bindings and the executable's load/save schema, but cannot establish which on-disk path was resolved, whether startup accepted this file, whether any save occurred afterward, or which mode/player record feeds a particular live input sample.

Parent review corroborated loader00472980 and EAX-mode helper004904d0 and independently decoded the39 bindingDWORDs in both candidates: repository external-install copy (SHAe9e67b...a449d above) and the Wine prefix `NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III/FEDATA/CONFIG/config.dat` (8432 bytes, SHA2562294092f8a3f4d6c5268e962b71eba76e010d5a4f3f453b4ef0d85e1c9e2c781). The two complete files differ, but all39 mapped binding words are identical. Only binding ranges were emitted. This comparison does not establish the runtime-resolved path or active mode.
