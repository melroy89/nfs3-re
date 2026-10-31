# Original versus Modern: track-chain detail selection

## Evidence boundary

Static comparison of complete paired track-chain builder bodies: original **`0041cdc0..0041d210`**, Modern **`0041cdc0..0041d1f6`**. The classifier counterpart is original **`0041aa60..0041aaab`**, Modern **`0041aa60..0041aa97`**. Ends are exclusive. Reproduce with `python3 analysis/scripts/audit_track_detail_difference.py`; the [manifest](evidence/audits/original-modern-track-detail.json) binds both executables, disassembly spans and the file-backed selection table. See the [baseline](original-modern-differences.md). No game, instruction probe or Ghidra write.

## Classifier no longer rejects the mirror context

Original `0041aa64` reads incoming EAX as a context pointer and returns0 immediately when DWORD0==1. Modern removes that dependency: its classifier starts by loading selected-record pointer `005dd830`, then compares the squared binary32 fields at record+`0x44` and +`0x40` against the one binary32 stack argument. It returns EAX=0/1/2. EDX and EBP are restored; RET4 consumes the stack value. The caller correspondingly removes its `MOV EAX,ESI` before the remaining classification call.

For ordered comparisons, the first threshold square below the supplied value returns0; otherwise the second threshold square below it returns1; otherwise2. Equality takes the higher branch. Actual x87 precision, unordered comparison handling and exceptions follow `FCOMP/FNSTSW/SAHF` and the active control state; this is not an assertion of equivalent portable C arithmetic. The selected-record fields, their runtime ordering and complete writer lifecycle remain separate work.

## Mirror quality moves into the caller

The builder obtains a signed high WORD from the visible-block entry; sentinel−1 calls the classifier using the current block’s squared X/Z distance, retained in a binary32 local. The original then forces selection0 whenever context DWORD0==1. Modern applies this policy instead at **`0041cea0..0041ceb5`**:

| Context / setting | Modern selection |
|---|---|
| Tag other than1 | Keep incoming/classified selection |
| Tag1, unsigned setting `006fd1d8`=0 | Keep selection |
| Tag1, setting=1 | Decrement selection; retain it if the result has a clear sign bit, otherwise use0 |
| Tag1, unsigned setting>1 | Use0 |

For ordinary classifier outputs0/1/2, Medium therefore maps to0/0/1 and Low to0/0/0. The exact `DEC/JNS` sequence is a sign-bit test after 32-bit wrap, not a universally safe signed-C `max(selection-1,0)` expression for arbitrary bit patterns. No validity guarantee for nonsentinel entry high WORDs is inferred.

The [night-lighting analysis](original-modern-night-lighting.md) binds this global to **Rear View Detail:0 High,1 Medium,2 Low**, and traces tag1 to the optional mirror-setting-gated render pass. Both changes therefore share a verified setting and context route.

The paired file-backed table at **`00552e20`** contains three12-byte rows: **`{1,0,150}`, `{2,2,100}`, `{3,4,50}`**. Selection indexes a row. Its first DWORD selects a track-block count at block+`0x5c+4*value`; its second DWORD becomes the selector passed to geometry submission `0041b300`, followed by that selector+1. The third DWORD controls the batching threshold described below; later writes mean its file-backed value is not a permanent runtime constant. Do not turn these rows into invented structure or LOD names solely from their values.

## Removed next-block classification and diagnostic tail

Original **`0041cec6..0041cf0a`** computes the next block index (`current+1`, wrapping to0 when signed greater than `005dd83c`), forms that block’s X/Z squared distance, rounds it to binary32 and calls `0041aa60` again. The selected table row and submission selector have already been saved. At `0041cf0a` the next common instruction overwrites EAX, so this second call’s EAX result is discarded locally. It can still affect x87 status/exception behavior and register/flag state; removing it is not automatically full machine-state equivalence. Modern jumps directly to `0041cf0a`, with66 NOP bytes at `0041cec8..0041cf0a`.

The common downstream region **`0041cf0a..0041d1ef`** is byte-identical. Earlier **`0041cdc0..0041ce96`** is also identical. Within the intervening region115 byte positions differ; this count excludes the different function tails and classifier bodies.

Original’s extra tail calls `00431c20` twice with EDX1/2 and locals−`0x34`/−`0x30`, before its epilogue. In the inspected original, `00431c20..00431c25` is only `PUSH EBP; MOV EBP,ESP; POP EBP; RET`. Modern omits those calls. No meaningful renderer-state update is attributed to that empty original helper, although incidental return registers/flags are not a declared stable API.

## Remaining scope

Confirmed static changes: removed classifier context input, three-level mirror selection policy, removed discarded next-block classification, and omitted empty-helper tail. Required follow-up: complete selected-record/table initialization and valid selector ranges, full submission-helper behavior, x87 state requirements and visual comparison at each detail setting. Historical release attribution remains unresolved; this final-pair evidence does not by itself verify every version’s rear-view-detail release-note claim.

## Table threshold and conditional initialization writes

The third DWORD is consumed at **`0041d14c..0041d175`**, within the paired identical downstream body. The builder compares its accumulated submission-helper return values (local−4) against selected row+8 using **signed `JLE`**. Only when the accumulator is greater **and `007a3a60 != 0`** does it call `0041c1a0`, then reset the accumulator to0. Existing [render-chain research](detailed-analysis-notes.md) identifies that helper as a six-chain drain; this bounded consumer establishes a batching threshold, not a triangle count or a memory-capacity bound. Signed arithmetic and the helper return units must remain explicit during reconstruction.

Paired complete helper **`0041d900..0041d953`** is byte-identical. If WORD `007a3a58` has either bit in mask`0x0180` set, it writes **`0xffffffff`** to all three threshold cells **`00552e28`, `00552e34`, `00552e40`**, replacing150/100/50. It then clears DWORD block+`0x18` for signed indices0 through `005dd83c-1`, using block base `00571370` and stride`0x5c0`. No mask-bit meaning or block-field identity is inferred from those writes. If neither bit is set, this helper leaves both thresholds and those block fields unchanged; it does not restore the file defaults.

A paired call witness **`0041da24..0041da33`** loads selected circuit `006fd4ac`, calls `00470b90`, then calls this writer at `0041da2e`. This is an observed initialization route, not proof that every startup/reload path reaches it or that no other writer exists.

With threshold−1, an ordinary nonnegative accumulator passes the signed greater-than test on every visited block; the separate `007a3a60` gate still applies. Thus calling this value an unsigned “unlimited threshold” would invert the observed policy. Both versions retain this mechanism. The newly selectable mirror rows can use it, but no new Modern threshold initialization is identified in these paired spans.
