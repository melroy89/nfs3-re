# Small changed entries: boundaries, wrappers and progress values

This closes the first static inspection of seven entries that lacked chapter references in the changed-function index. It does not establish exhaustive semantic coverage of that index. The [audit script](scripts/audit_remaining_small_entries.py) checks the hash-pinned supplied original and official Modern executables; the [manifest](evidence/audits/remaining-small-entries.json) retains complete span bytes/hashes and disassembly paths. Saved names describe Modern analysis metadata.

## A shortened no-op, not a removed scene operation

At `00426290`, original is the complete five-byte `PUSH EBP; MOV EBP,ESP; POP EBP; RET` stub. Modern is `RET` followed by four NOPs. Both return without a scene update. The saved Modern function range includes only its single RET, explaining the index's one-byte comparison; the five-byte envelope accounts for the old function too. Original performs a temporary stack write, so this is not a claim of identical memory-access traces or timing. Caller reachability and the label `ReturnFromInactiveSceneMode` do not prove a removed gameplay feature.

## Vehicle initialization changes progress inputs and shared data

The complete `0042c700..0042c7e6` body is 230 bytes. Only the MOV immediate at `0042c71a` changes: original binary32 bits `42960000` (75.0), Modern `42c00000` (96.0). However, comparing code bytes alone misses a second relevant difference: the referenced QWORD at `00537340` is original 15.0, Modern 3.8.

For each admitted first-loop iteration, the unchanged sequence at `0042c74e..0042c763` loads the signed DWORD at `006fd510` with FILD, computes the version-specific QWORD divided by that count with FDIVR, adds the local progress value, stores back to binary32, then pushes the stored bits into `00495230`. Thus the nominal recurrences are:

- Original: start 75, repeatedly store `binary32(previous + 15/count)`.
- Modern: start 96, repeatedly store `binary32(previous + 3.8/count)`.

Actual x87 intermediate precision/rounding depends on incoming control state; the binary32 stores remain in both versions. The zero/nonpositive count path skips the loop and its division. The code compares the count as signed and reloads it inside the loop; the usual N-iteration interpretation assumes callees do not change that count or disrupt loop state. Under that assumption and ignoring repeated rounding, endpoints are 90 and 99.8. These are nominal progress inputs, not measured displayed percentages or durations. See [loading timing](original-modern-loading-timing.md) for the changed downstream implementation.

Every other body byte, including vehicle-record setup and second-pass calls, is identical. Those retained callees can contain independent differences; this does not prove vehicle initialization equivalence. Other consumers of shared `00537340` and the reason for the exact 3.8 value require separate tracing.

## Duplicate-choice code receives a callable register-preserving boundary

Modern `0045d7ad..0045d834` is a 135-byte helper: PUSHAD, six ordered pair checks, POPAD, RET. It compares globals `006fbba8`, `006fbbac`, `006fbbb0`, `006fbbb4` and clears later matching entries to zero, in this sequence: second against first; third against first; fourth against first; third against the possibly updated second; fourth against that second; fourth against the possibly updated third. Zero is not exempted from comparisons. Clearing to zero does not establish that all resulting values are distinct.

Original `0045d7ad` is a RET. The next 132 bytes, `0045d7ae..0045d832`, are byte-identical to Modern's comparison body, but original continues with `MOV EAX,3` at `0045d832`; Modern substitutes POPAD/RET. Consequently, the original comparison instructions already exist and must not be described as newly invented checks. Original entry paths into that block and Modern callers remain unresolved. The verified change is the new callable boundary preserving general registers; PUSHAD/POPAD do not preserve arithmetic flags. The saved camera-choice label still requires caller/context evidence before inferring a user-visible policy change.

## Modern wrappers and seed setter

| Modern entry and complete extent | Verified local contract | Comparison limit |
|---|---|---|
| `004f915e..004f916a`, 12 bytes | Save ECX/EDX; push incoming EAX as path pointer; call IAT `00534520`, verified as `GetFileAttributesA`; restore ECX/EDX; return API result in EAX. | Original same-address bytes belong to other surrounding code, not a matching wrapper established here. No error translation is present locally; flags and other API effects are not characterized. |
| `00517784..0051778a`, 6 bytes | Store EAX to DWORD `007a32b4`, RET. MOV and RET do not change arithmetic flags. | Original same-address region contains an epilogue and following code. No original seed setter counterpart established here. |
| `00533e86..00533e93`, 13 bytes | Load EAX with string `0053d2f2`, exactly `DDRAW.DLL is not imported.`; call `004b570c`; if it returns, execute `RET 12`. | Original region contains import jumps, not this diagnostic wrapper. Failure trigger, caller ABI and whether the callee returns need separate tracing; the text alone is not proof of a particular runtime failure. |

The [music-selection comparison](original-modern-music-selection.md#modern-playlist-seeding-and-race-load-update-placement) traces the Modern generator using `007a32b4`. The [idle-movie comparison](original-modern-idle-movie.md) documents reuse of that address from an original path buffer. The seed store does not imply a cross-version shared union or identical random sequence initialization.

## Application wrapper retargets one call

The complete same-address wrapper `00524290..005242ed` is 93 bytes in both versions. Only two CALL-displacement bytes change at `005242de`: original invokes `004a39f0`, Modern invokes `004a3db0`. The argument loads remain EAX=`[00a18210]`, EDX=`[00a18214]`. Stack-workspace setup, global `00567824` publication, helper `0052b640`, and following runtime call `004dfd04` are byte-identical. The [startup policy report](original-modern-startup-policy.md) covers the Modern application path; this wrapper comparison does not establish equivalence of the two application bodies or give the retained runtime call a newly verified contract.

## Status and follow-up

**Bounded work status: done. Confidence: verified static bytes, local control flow and identified data/import/string references.** No executable, database, raw reference export or reconstruction source was changed; no target instructions were executed.

| Remaining question | Status / confidence | Required evidence |
|---|---|---|
| Original paths into duplicate-choice block and Modern caller policy | Pending / unresolved | Boundary-correct direct and indirect caller tracing in both versions. |
| Original functional counterparts of three Modern wrappers | Pending / unresolved | Trace corresponding callers/imports and original RNG ownership, rather than pairing same-address bytes. |
| Diagnostic trigger and error handling | Pending / unresolved | Trace callers and complete `004b570c` contract. |
| Shared progress constant consumers and actual presentation | Pending / unresolved | Inspect remaining `00537340` references; runtime comparison only if subsequently authorized. |
| Whole-game behavior and external component effects | Pending / unresolved | Broader existing audit backlog; these seven entries cannot establish it. |
