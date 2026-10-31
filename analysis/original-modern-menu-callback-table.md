# Static menu callback registration changes

## Scope and verified inventory

The unchanged binder `00442b10..00442b5c` scans **57 named rows**, each `18h` bytes, beginning at `00555c48`. Both executables reach the first null-name sentinel at **`005561a0`**. Names and row positions match. Exactly **nine rows / 12 fields** differ: eight nonzero fields become null, and four receive another nonzero pointer.

The [audit script](scripts/audit_menu_callback_table_difference.py) pins both executable hashes, reads the table selected by the actual binder and retains every row, full table-span hashes and exact deltas in [the manifest](evidence/audits/original-modern-menu-callback-table.json). It also verifies complete binder byte identity. No callback was executed. Addresses are virtual addresses; instruction range ends are exclusive.

## Static rows and runtime descriptors are different layouts

The binder compares static row+0 name with runtime descriptor+14h. On a match, it copies **five DWORDs** from static row+4..14h to runtime descriptor+0..10h. Thus a callback offset quoted for the static table must be reduced by four to locate its runtime descriptor field:

| Static row offset | Runtime descriptor offset |
|---|---|
| `04h` | `00h` |
| `08h` | `04h` |
| `0ch` | `08h` |
| `10h` | `0ch` |
| `14h` | `10h` |

These are descriptor callbacks, separate from menu-item callback `+64h`. The [field-parser/helper report](original-modern-menu-text-fields.md) documents the one-time invocation of descriptor+0 and its WORD+20h guard. [Existing lifecycle research](deadzone-disk-save-path.md) maps entry/init and transition roles in selected menus. Exact offsets are used below instead of assigning every slot a universal lifecycle name from those selected contexts.

## All changed fields

| Menu | Static row | Static → descriptor offset | Original pointer | Modern pointer |
|---|---|---|---|---|
| `main` | `00555c60` | `10h → 0ch` | `0045d2f0` | null |
| `mainmult` | `00555ed0` | `10h → 0ch` | `004405b0` | null |
| `mainsplt` | `00555ee8` | `10h → 0ch` | `0045d620` | null |
| `slides` | `00555f90` | `10h → 0ch` | `00453f50` | null |
| `interior` | `00555fa8` | `10h → 0ch` | `00454d50` | null |
| `interior` | `00555fa8` | `14h → 10h` | `00454d40` | null |
| `graphics` | `00556068` | `10h → 0ch` | `004484e0` | `004484bc` |
| `graphics` | `00556068` | `14h → 10h` | `00448430` | null |
| `funkeys` | `005560f8` | `10h → 0ch` | `004377c0` | null |
| `hardkeys` | `00556110` | `0ch → 08h` | `004377d0` | `00437600` |
| `credits1` | `00556188` | `0ch → 08h` | `00454ea0` | `00454dc8` |
| `credits1` | `00556188` | `10h → 0ch` | `00454e80` | `00454da8` |

This table exhausts changed DWORD fields in the inspected 57 rows. It does not exhaust changed callback implementations: an unchanged pointer can target changed code, and a redirected pointer may identify moved equivalent code or a new implementation. Nulling registration does not prove target code was deleted or universally unreachable through other callers.

`hardkeys` now shares `00437600` with `funkeys`. The [Race Now policy comparison](original-modern-race-now.md) already records how Modern `00437600` delegates to helper `00437614`; this table establishes a concrete menu registration that reaches that wrapper. It does not by itself prove which input/lifecycle states invoke the callback at runtime.

`options`, `connect`, `ipx` and `credits` keep the same row words. This is compatible with the [asset-defined new controls](original-modern-common-menu-buttons.md) and changed helper bodies elsewhere: unchanged registration is not unchanged frontend behaviour.

## All eight nulled targets are original return-zero stubs

The expanded audit now reads and disassembles all eight complete original bodies. Each is exactly seven bytes, `55 89 e5 31 c0 5d c3`:

```asm
push ebp
mov  ebp, esp
xor  eax, eax
pop  ebp
ret
```

This covers the original targets `0045d2f0`, `004405b0`, `0045d620`, `00453f50`, `00454d50`, `00454d40`, `00448430`, and `004377c0`, corresponding exactly to the eight null fields above. They return EAX=0, modify arithmetic flags through XOR, balance the stack frame, and have no helper calls or explicit application-memory writes. Their stack writes, return value and flags are machine effects, so skipping the invocation is not full machine-state equivalence.

For this set, the delta is therefore removal of **placeholder return-zero registrations**, not evidence that eight substantive menu behaviours were removed. Whether each caller treats a null callback exactly like a zero return requires its invocation-site contract; that is not established simply by these stubs. Some original target addresses are repurposed by Modern code, so reconstructing a callback from the Modern bytes at the old address would be incorrect even though its original implementation was trivial.

## Reconstruction use and follow-up

Preserve original and Modern callback maps separately while deciding which behaviour to reconstruct. A shared C binder needs the selected map as data; silently reusing the Modern map for an original-mode reconstruction would omit eight return-zero placeholder callbacks and redirect four others before any body translation is considered. The omitted placeholders have no observed application-state logic; their caller-level null-versus-zero semantics still need qualification.

The [graphics transition counterpart](original-modern-graphics-menu-transition.md) now explains one of the four redirected fields. Next, compare the remaining three redirected fields' original/Modern callback counterparts and the invocation sites of all affected descriptor slots. The eight nulled original bodies are now fully inspected as stubs; do not repeatedly investigate them as missing substantive implementations. Prioritize graphics and Interior for the new standard-control policy, and `credits1` for the reported common Credits navigation. Reuse existing function and menu research rather than pairing moved functions solely by address. Qualify actual lifecycle ordering and state mutation before translating callbacks or claiming the null registrations fix a named release-note bug.

This investigation assigns no historical release date or tested visual effect to the pointer deltas. It does not alter executable bytes, saved Ghidra state, exports or maintained C, and uses no target instruction probes.
