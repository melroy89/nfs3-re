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

Every other body byte, including vehicle-record setup and second-pass calls, is identical. Those retained callees can contain independent differences; this does not prove vehicle initialization equivalence. A complete executable-file search for the little-endian absolute address bytes `40 73 53 00` finds exactly one occurrence in each version: operand `0042c756` of this FDIVR instruction (file offset `0002bb56`). The manifest retains this bounded search. No additional direct absolute references were found; computed addresses, aliases and external references remain outside that result. The reason for the exact 3.8 value remains unresolved.

## Duplicate-choice code receives a callable register-preserving boundary

Modern `0045d7ad..0045d834` is a 135-byte helper: PUSHAD, six ordered pair checks, POPAD, RET. It compares globals `006fbba8`, `006fbbac`, `006fbbb0`, `006fbbb4` and clears later matching entries to zero, in this sequence: second against first; third against first; fourth against first; third against the possibly updated second; fourth against that second; fourth against the possibly updated third. Zero is not exempted from comparisons. Clearing to zero does not establish that all resulting values are distinct.

Original `0045d7ad` is a RET. The next 132 bytes, `0045d7ae..0045d832`, are byte-identical to Modern's comparison body, but original continues with `MOV EAX,3` at `0045d832`; Modern substitutes POPAD/RET. Consequently, the original comparison instructions already exist and must not be described as newly invented checks. The [caller follow-up](original-modern-camera-duplicates.md) now verifies the original action-handler path into that block and two Modern calls, including the registered camera transition’s non-Cancel path. The verified change is the new callable boundary preserving general registers; PUSHAD/POPAD do not preserve arithmetic flags. Named camera registrations now support the local camera-choice interpretation; full named-button routing and user-visible behavior remain unverified.

## Modern wrappers and seed setter

| Modern entry and complete extent | Verified local contract | Comparison limit |
|---|---|---|
| `004f915e..004f916a`, 12 bytes | Save ECX/EDX; push incoming EAX as path pointer; call IAT `00534520`, verified as `GetFileAttributesA`; restore ECX/EDX; return API result in EAX. | Original same-address bytes belong to other surrounding code, not a matching wrapper established here. No error translation is present locally; flags and other API effects are not characterized. |
| `00517784..0051778a`, 6 bytes | Store EAX to DWORD `007a32b4`, RET. MOV and RET do not change arithmetic flags. | Original same-address region contains an epilogue and following code. No original seed setter counterpart established here. |
| `00533e86..00533e93`, 13 bytes | Load EAX with string `0053d2f2`, exactly `DDRAW.DLL is not imported.`; call `004b570c`; if it returns, execute `RET 12`. | Original region contains import jumps, not this diagnostic wrapper. Failure trigger, caller ABI and whether the callee returns need separate tracing; the text alone is not proof of a particular runtime failure. |

The [music-selection comparison](original-modern-music-selection.md#modern-playlist-seeding-and-race-load-update-placement) traces the Modern generator using `007a32b4`. The [idle-movie comparison](original-modern-idle-movie.md) documents reuse of that address from an original path buffer. The seed store does not imply a cross-version shared union or identical random sequence initialization.

## Original import thunks beneath the DirectDraw fallback

The original thunk at `00533e86` jumps through IAT slot `00534668` to `DDRAW.dll!DirectDrawCreate`. The next three original jumps target `VERSION.dll`: `00533e8c` uses `0053467c` for `VerQueryValueA`, `00533e92` uses `00534674` for `GetFileVersionInfoA`, and `00533e98` uses `00534678` for `GetFileVersionInfoSizeA`. Modern's diagnostic wrapper overlays parts of these jumps. The final 11 bytes from `00533e93` to `00533e9e` become NOPs.

The decoded calls at `004eb445` and `005051ec` still target `00533e86` in final Modern, where that entry is now the diagnostic. Equal call bytes therefore hide a callee change. The original VERSION callers in the configuration timestamp path are covered in the [configuration comparison](original-modern-config-loading.md). Reproduce by disassembling `00533e80..00533e9e`, then resolving the six-byte jumps against the original PE import table. This establishes the static callees. Runtime reachability of the DirectDraw diagnostic remains unresolved.

## Application wrapper retargets one call

The complete same-address wrapper `00524290..005242ed` is 93 bytes in both versions. Only two CALL-displacement bytes change at `005242de`: original invokes `004a39f0`, Modern invokes `004a3db0`. The argument loads remain EAX=`[00a18210]`, EDX=`[00a18214]`. Stack-workspace setup, global `00567824` publication, helper `0052b640`, and following runtime call `004dfd04` are byte-identical. The [startup policy report](original-modern-startup-policy.md) covers the Modern application path; this wrapper comparison does not establish equivalence of the two application bodies or give the retained runtime call a newly verified contract.

## Status and follow-up

**Bounded work status: done. Confidence: verified static bytes, local control flow and identified data/import/string references.** No executable, database, raw reference export or reconstruction source was changed; no target instructions were executed.

| Remaining question | Status / confidence | Required evidence |
|---|---|---|
| Duplicate-choice named-button save coverage | Local original/Modern paths done / verified; full lifecycle pending / unresolved | Follow the [camera transition evidence](original-modern-camera-duplicates.md) through Race/Credits/Exit dispatch and persistence before claiming the complete fix. |
| Original functional counterparts of three Modern wrappers | Pending / unresolved | Trace corresponding callers/imports and original RNG ownership, rather than pairing same-address bytes. |
| Diagnostic trigger and error handling | Pending / unresolved | Trace callers and complete `004b570c` contract. |
| Progress constant reachability and actual presentation | Direct absolute reference search done / verified; computed aliases and visual behavior unresolved | Trace computed aliases if evidence warrants it; runtime comparison only if subsequently authorized. |
| Whole-game behavior and external component effects | Pending / unresolved | Broader existing audit backlog; these seven entries cannot establish it. |

### Incoming DirectDraw call chains

The paired executable listings retain three decoded calls into `004eb430` at `004ebb5f`, `004ebb82` and `004ebd0a`. That routine passes a device selector from EDX, a local output pointer and a null outer object to the thunk at `004eb445`. The separate call at `0050557e` enters `005051c0`, which reaches the thunk at `005051ec` only when `00567e2c` and `00567ddc` are zero and `00567df4` is nonzero. It supplies `00567e2c` as the output slot and null for the other two arguments. These direct caller edges and local argument setups survive in final Modern.

Reproduce the edge census with `objdump -d` on both executables and filter decoded CALLs to `004eb430` and `005051c0`. Neither entry address occurs as a raw little-endian DWORD in the final PE sections, which narrows the search for direct stored pointers. Computed pointers and reachability from game startup or a supported renderer remain unresolved.

The three calls into `004eb430` belong to the routine starting at `004ebaf0`. Both executables retain its decoded caller at `00507b53`. The other chain also survives at `005050e2 → 005052a0 → 00505570 → 005051c0`. In that chain, `005052a0` reaches its call to `00505570` only when bit 1 of `00567dd8` is set. Both binaries also contain the little-endian address of `005052a0` at `00564b0c`. This is a candidate stored reference, whose consumer has yet to be confirmed. Neither chain establishes that the required state is reached in normal gameplay.

The file-backed vector at `00564b00..00564b88` is identical in the two executables. Its first four DWORDs are `00504e00`, `00504f90`, `005050f0` and `005052a0`. The first target initializes the built-in Glide descriptor with signature `0x33444658` and the name `3Dfx Voodoo`. Its presence makes this a candidate built-in renderer callback table. A static byte search of the final Modern PE sections found no literal DWORD for the vector base or slot `00564b0c`. This leaves the registration or indexing mechanism unresolved. The separate external renderer loading path is described in the [renderer loading comparison](original-modern-renderer-loading.md).

The `00507b53` caller belongs to window callback `00507b10`. Both executables register this callback for message `0x0464` at `005083bb..005083cc`, passing the message and callback address to `004cc6d0`. That registration is on the `00508390` DirectDraw window-session initialization route where the first DWORD of `009f38d0` is zero. The callback itself skips `00507b53` when `004f9120` returns zero. This establishes a static registration and gate for the first chain. The producer that sends this message in a supported Modern renderer session remains unverified.
