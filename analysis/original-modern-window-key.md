# Original versus Modern: window-key translation

## Evidence boundary

Paired translator entry **`004ccaa0`**, original body ending at exclusive **`004ccc67`**, Modern at **`004ccaf6`**. Modern immediately follows its code with mapping data; do not disassemble the tables as function instructions. Reproduce with `python3 analysis/scripts/audit_window_key_difference.py`; the [manifest](evidence/audits/original-modern-window-key.json) records hash-checked baselines, complete disassemblies, decoded Modern tables and its actual `GetKeyState` import. See the [baseline comparison](original-modern-differences.md). No key events or target instructions were executed.

## Branch tree becomes two tables and a toggle-state gate

Both accept message value EAX=`0x100` or `0x104`, use EDX as the key value, and return a translated code in EAX or0. Original uses an unsigned comparison tree and fixed immediate results. Modern searches a WORD-key/WORD-result table at **`004ccaf8`**, with22 entries and a zero terminator. On a miss it calls **`GetKeyState(0x90)`** through import **`00534744`**, tests low bit0, and returns0 when that bit is set. Otherwise it searches the second table at **`004ccb54`**, with11 entries and a zero terminator.

The `0x90` toggle is Num Lock. This is a toggle-bit test, not a current-key-down test of the high bit. The first table’s matches return before consulting it; the gate applies only to second-table candidates. There is no local translation of ordinary digit characters on the gated return0 path; any other handling is a caller question.

| Key codes | Original local mapping | Modern local mapping |
|---|---|---|
| `25,27,26,28` hex | `4b00,4d00,4800,5000` | Same, first table |
| `2e,21,22,24,23,2d` | `5300,4900,5100,4700,4f00,5200` | Same, first table |
| `70..79` | `3b00..4400` | Same, first table |
| `7a,7b` | `8700,8800` | Same, first table |
| `60..69` | `5200,4f00,5000,5100,4b00,4c00,4d00,4700,4800,4900` without a Num Lock query | Same results only when the queried toggle bit is clear |
| `6c` | Falls through to0 in the inspected tree | `5300` when toggle bit is clear |

These are raw hexadecimal values. Codes`60..69` are numeric-keypad keys, and`6c` is the separator key. The table retains navigation/function-key mappings while separating keypad handling by Num Lock state. This establishes local policy, not how every keyboard layout or device generates these messages.

## ABI and limits

Modern saves/restores ESI, which it uses as the table cursor. Original uses an EBP frame. Both have plain RET and no local stack-argument consumption. Modern still compares the incoming EDX after the `GetKeyState` call; this helper contains no explicit save/restore around that API. A full ABI review must therefore account for register state across that call rather than assume the queried-key value is protected by a generic C signature. No runtime clobber or resulting defect is asserted.

The audit retains both bodies and the tables, but does not implement an executable emulator or exhaustively test every32-bit input. Remaining work: caller fallback for return0, producer/key-layout behavior, the API/register boundary, and runtime checks with Num Lock on/off. No unique historical release attribution or whole input-subsystem equivalence is claimed.
