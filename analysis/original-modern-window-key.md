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

The audit retains both bodies and the tables, but does not implement an executable emulator or exhaustively test every32-bit input. Caller fallback for return0 is resolved below. Producer/key-layout behavior, the API/register boundary and runtime checks with Num Lock on/off remain open. No unique historical release attribution or whole input-subsystem equivalence is claimed.

## Caller handling of zero and nonzero results

The audit now retains paired identical caller spans **`004cd0a7..004cd0dd`** and **`004cd5b0..004cd5de`**, plus each executable’s actual message-API import mapping.

At **`004cd5b0`**, nonzero mode flag `007f7488` bypasses translation entirely. Otherwise the message and key fields are loaded into EAX/EDX and passed to `004ccaa0`. Return0 calls **`TranslateMessage`** through `005347a4`; nonzero skips that call. Both routes then call **`DispatchMessageA`** through `0053472c`. Thus a keypad key rejected locally by Modern’s Num Lock gate can continue through the ordinary message-translation path. This does not establish what character is produced for any particular layout, nor does the nonzero route suppress message dispatch itself.

At the other caller, **`004cd0a9`**, return0 branches straight to the caller epilogue and remains its return value. Nonzero is saved in ESI and passed to **`004cc8e0`** in a repetition loop, with another field derived from bit24 of EDI and a code loaded from `007f748c`; that route ultimately returns1. The helper’s complete queue semantics and preservation of the loop state remain separate work. This is an observed local admission distinction, not proof that zero discards every possible input action.

The caller comparison therefore resolves where the translator’s result is consumed. Remaining uncertainty is layout-specific message production, downstream queue behavior, the API/register contract inside the translator and actual Num Lock on/off runtime behavior.

## Retained message callers connect conversion to queued input

The [supplementary static audit](scripts/audit_window_key_translation_difference.py), with its [manifest](evidence/audits/window-key-translation-difference.json), now verifies complete **`004cd020..004cd0dd`**,189-byte key-down callback, is byte-identical across both EXEs. Existing [window registration research](original-modern-window-handling.md) establishes its message route. On its translated-input branch it supplies message in EAX and raw key in EDX, calls`004ccaa0` at`004cd0a9`, saves a nonzero result in ESI, and enqueues that encoded value through **`004cc8e0`** at`004cd0ca`. A zero conversion skips that repeat-enqueue path. A separate mode selected by`007f7488` bypasses this translator and queues zero-word records with scan/index data instead, as recorded in the [key-down contract](detailed-analysis-notes.md#recovered-key-down-callback-boundary).

The callback computes its repeat count in **ECX** before conversion and decrements ECX afterwards without restoring it around`004ccaa0`. Original’s branch-tree translator does not locally modify ECX; Modern’s primary-table matches also avoid a native API call and leave ECX alone locally. Modern’s primary miss reaches GetKeyState without saving ECX, introducing a provider-preservation dependency for the repeat loop in addition to the translator’s EDX key dependency. This is a machine-contract limitation, not an observed Wine/input failure or a guarantee about actual OS register values.

Identical message-loop span **`004cd5b9..004cd5d3`**,26 bytes, supplies saved key/message values to the same translator at`004cd5bf`; it branches on zero result before its subsequent OS message processing. The two direct callsites are independently checked in both binaries. This establishes a static message/queue effect route, while real physical events, all queue consumers, exact repeat count on the API path and provider behaviour remain untested.

## Outside-body table partition

The supplementary audit checks complete outside-function interval **`004ccaf6..004ccb84`**:142 bytes with116 differing positions. Modern contains two NOPs, then the92-byte primary table (22 mappings plus terminator) and48-byte keypad table (11 mappings plus terminator). These are WORD/WORD data records replacing original branch-tree instructions. The original function continues through`004ccc67`; this inventory boundary does not define a paired function.

This chapter is the canonical keyboard comparison. The earlier audit retains baseline translator/table/import and TranslateMessage/DispatchMessage evidence; the supplementary audit adds the complete189-byte key-down callback, repeat-register lifetime and interval partition. Their static scopes overlap deliberately as retained evidence, while this prose provides one consolidated conclusion. No new input/OS test or whole-subsystem equivalence claim follows.
