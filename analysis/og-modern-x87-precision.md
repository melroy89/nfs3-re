# Original versus Modern Patch: x87 precision

**Verdict:** the local binaries confirm a real precision-policy change. The original/backup executable explicitly selects single precision at six identified control blocks; Modern Patch removes those blocks and uses extended-precision initialization at the inspected application/race-render boundaries. The claim is substantially correct about that change, but its “only menu/HUD”, “80-bit everywhere”, and automatic incompatibility wording is too absolute.

This is read-only static investigation of the two supplied files, not new game, network, replay or ARM64 execution. [Byte witnesses and fingerprints](evidence/audits/og-modern-x87-precision.json) retain the actual differences. Existing Modern Patch reconstruction and raw exports were not changed.

## Exact targets

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Supplied original/backup | `nfs3_org.exe` | 1,589,248 | `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` |
| Local Modern Patch-based target | `nfs3.exe` | 1,699,840 | `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb` |

Both use image base `00400000`, entry `004f7fa0`. The Wine-prefix original supplied by the user matches the project-local ignored original copy byte-for-byte. “Original” here identifies that supplied artifact; its exact retail provenance/version has not been independently authenticated. Modern Patch provenance remains as recorded in [TARGET](../docs/TARGET.md).

The saved Ghidra database still targets Modern Patch. Its function names helped identify the current application, frontend and race-render paths. Original-code conclusions below come from original PE bytes, not from assuming every Modern Patch function boundary/address transfers unchanged to the original.

## What the instructions establish

Intel specifies that FINIT/FNINIT initializes CW to `037f`: exceptions masked, nearest rounding, PC=`11` (64-bit significand in the 80-bit format). PC=`00` selects a 24-bit significand. This controls arithmetic precision, not the size of every value in memory. [Intel architecture manual](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366521.pdf)

At original `00495159..0049517f`:

```text
00495159 FINIT                         ; CW = 037f
0049515c FSTCW [0079f3ec]
00495165 MOV EAX,[0079f3ec]
0049516a MOV [0079f3f4],EAX             ; retain reset/extended CW
0049516f AND EAX,fffff0ff              ; low word 037f -> 007f
00495174 MOV [0079f3ec],EAX
00495179 FLDCW [0079f3ec]              ; PC=00, RC=00
```

The mask clears precision bits 8–9 and rounding bits 10–11, so the resulting low word is **`007f` (single precision, nearest)**, not binary64/double precision. The same reset/save/clear/load sequence appears at original AND sites `004955df`, `004a3e83`, `004a3ec9`, `004b622f`, `004bc807`. No corresponding decoded `AND EAX,fffff0ff` site remains in Modern Patch. These are static instruction witnesses, not observations of every runtime path.

| Boundary | Original executable | Modern Patch executable |
|---|---|---|
| Frontend/application dispatch | `004a3e5a..64` restores saved extended CW before frontend setup; `004a3e6d..93` resets/saves/reselects single after it returns. The second frontend branch repeats this at `004a3e9b..004a3ed9`. | Loop at `004a3ea0` performs FINIT. Frontend calls at `004a3ec6`/`004a3ed7` return to that loop without the original single-precision reset blocks. |
| Loading-artwork path | Original control block above reselects single after rendering. | Current `LoadAndRenderRaceLoadingArtwork` ends at `00495165`; the old reset area is removed/NOP-padded. |
| Race-frame rendering | When flag `[007a3a70]==0`, `004bc692..9c` restores saved extended CW on entry; `004bc7f1..817` reselects single before returning. | `RenderRaceFrame` starts with FINIT at `004bc687`; the old restore/return-to-single code is removed. |

The race-frame witness is important: the original uses extended precision around race rendering as well as frontend work. Therefore “80-bit **only** in menu and HUD” is not an exact description of the inspected control flow. A more accurate summary is **single-precision game-side context with extended-precision frontend/render regions, versus Modern Patch's extended baseline at these boundaries**. Fully labeling every physics, online, replay or worker-thread interval still requires its own call/control-word trace.

The patch's bundled `readme_en.txt`, under v1.6.0 (2016-09-22), line 174, independently documents the intended change: “FPU always uses extended precision for all calculations.” That is patch-author documentation corroborated by the byte changes above, not a blanket runtime measurement.

## Why “80-bit everywhere” is shorthand

Local FPU-control helpers still exist. For example, Modern Patch's `004dfd56..004dfd6c` pushes CW `0c3f`, saves the incoming CW separately, loads the temporary word, executes FRNDINT, then restores the saved word. The temporary word has PC=`00`, but FRNDINT is not one of the arithmetic instructions controlled by PC. This is a scoped conversion/rounding helper, not evidence that normal patched race arithmetic reverts to single precision.

Thus it would be wrong to claim the control word is always `037f`, or that every result is stored in 80 bits. In fact the 747 bytes of the first reconstructed helper `00485c30` are **identical in both executables**, SHA-256 `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f`. Both retain its binary32 memory accesses. A change in surrounding arithmetic mode can matter without converting all data structures to double or extended storage.

## Follow-up: text/HUD changes distinguish arithmetic, storage and ABI

The later [text measurement investigation](original-modern-car-alias.md#width-dependency-removes-an-intermediate-integer-conversion) compares the supplied original with the **official Modern v1.6.1 executable**, SHA-256`240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. This is a separate pinned Modern artifact from the local target in the initial table above; see the [three-way baseline](original-modern-differences.md#1-three-way-provenance). Its [static audit](evidence/audits/original-modern-car-alias.json) and the [numeric-scale audit](evidence/audits/original-modern-numeric-scale.json) supply the following bounded results:

| Layer | Original → official Modern | Reconstruction consequence |
|---|---|---|
| Measurement wrapper`004d1430` | Truncate x87 result through signed DWORD and FILD → return callee x87 result directly | Preserve or remove this conversion deliberately; changing only global precision does not reproduce it |
| Per-glyph accumulation`004d1000` | Identical216-byte body; binary32 FSTP after each advance in both | Extended arithmetic baseline does not mean extended storage or uninterrupted extended accumulation |
| Glyph`004d06f0`, adjustment`004d1480` | Identical complete799/110-byte bodies | Their unchanged code still depends on initialized metric data and the changed wrapper |
| Scale setter`004d1390` | Identical99-byte body and file-backed factor | No scale-setter change is established by the wrapper difference |
| Right anchor`004d10e0` | Callee discards x87 draw return → caller owns that return | Caller/callee stack effects must be matched, not inferred from the numeric type |
| Right-anchor callers | Shared wrapper changes one branch byte to execute cleanup; Modern numeric scale explicitly pops | The two identified direct callers locally compensate for the new return contract; indirect references remain unverified |

The [font-loader follow-up](original-modern-car-alias.md#complete-font-loader-and-retained-asset-candidates) further verifies equal681-byte loader bodies, equal filename formats and three byte-identical installed/backup FFN pairs. The official patch archive contains no FFN members. This narrows one possible source of differences without authenticating retail assets or observing runtime path selection. Font metrics/scale live in uninitialized storage and acquire values later; local file identity cannot substitute for loading/initialization evidence.

These findings show why a port needs **conversion boundaries, storage widths, control-word scope and x87 return ownership** in addition to a choice of `float` or `double`. They do not establish changes to every HUD component or simulation routine. The numeric-scale caller evidence places one affected use in race HUD rendering; it must not all be described as menu-only. No ARM64, replay, multiplayer or rendered-width comparison was executed in these follow-ups.

## Historical release boundary: v1.5.3 to v1.6.0

The [historical audit](scripts/audit_x87_precision_history.py) now pins this adjacent release pair using author-hosted archive/member identities already retained in the [language-history manifest](evidence/audits/language-fallback-history.json) and [1.6.0 baseline](evidence/audits/official-160-161-baseline.json). Run `python3 analysis/scripts/audit_x87_precision_history.py`; [its evidence](evidence/audits/x87-153-160-history.json) retains control helpers, caller candidates, mask scans and selected application/render boundaries. Nothing was executed from either game binary.

V1.5.3 had already centralized the original repeated control sequences:

| Historical v1.5.3 helper | Complete body and contract | Direct E8 candidates |
|---|---|---:|
| `004955c8..004955d2` | FINIT, then FLDCW from saved cell `0079f3f4`, then RET |7 |
| `004955d4..004955f9` | FINIT, save CW at `0079f3ec`, copy to `0079f3f4`, AND with `fffff0ff`, store/reload `0079f3ec`, RET |6 |

The second helper therefore saves the initialized037f control word and selects007f (24-bit significand, nearest rounding), under the documented FINIT semantics. The first restores whatever is in its saved cell; complete writer ownership is not established by its body alone. The sole executable-section occurrence of the exact `AND EAX,fffff0ff` encoding in this release is `004955e8`. Thus counting the original six inline masks as if they all persisted at the same addresses in every Modern version would be wrong.

In1.6.0, both helper envelopes are NOP-filled, no direct E8 candidates to either target remain, and that exact AND encoding is absent from executable sections. The new application loop begins with FINIT at **`004a3b4a`**, with frontend calls at `004a3b74`/`004a3b85`; do not substitute final1.6.1's loop address `004a3ea0`. At the race-render entry,1.5.3 conditionally calls the saved-CW helper from `004bc692`;1.6.0 instead begins the inspected entry sequence with FINIT at `004bc687` and bypasses the old conditional restore area. The existing original/final analysis supplies the wider context, not an assumption of equal same-address bodies.

This verifies a concrete x87 policy transition in the release pair named by MP160-012. It does not prove that every path, thread, external DLL or later control-word write uses extended precision. Binary32 memory stores and conversion rounding remain separate. Direct-call and exact-mask scans are bounded corroboration, not exhaustive semantic recovery. No additional replay, multiplayer or ARM64 compatibility conclusion follows from the historical attribution.

## Assessment of the other user's claims

| Claim | Assessment |
|---|---|
| Modern Patch changes OG's single-precision arithmetic policy toward extended precision. | **Confirmed statically for the inspected controls**, with corroborating patch documentation. |
| OG uses 32-bit precision in all race/online/replay execution and extended only in menus/HUD. | **Overgeneralized.** Single-precision switches are real; race-frame rendering has a conditional extended region too. Every online/replay/worker path has not been traced. |
| Modern Patch uses binary64 `double` everywhere. | **Incorrect description:** the verified baseline is x87 extended (64-bit significand), not binary64 (53-bit significand), and binary32 memory storage remains. |
| A float-everywhere ARM64 port runs without issues. | **Not verified here:** that port's source/binary, test cases and results were not supplied. Running without a crash is also a narrower observation than deterministic equivalence. |
| That port connects but desynchronizes positions/replay trajectories. | **Not verified here.** Numerically plausible, but needs the specific port and a controlled comparison; the inspected binaries alone cannot establish those reported outcomes or their cause. |
| Using native float necessarily makes a port incompatible with both versions. | **Not established.** Native float alone does not reproduce every x87 rule, but compatibility depends on observable arithmetic, timing, serialization and protocol behavior. Neither guaranteed compatibility nor inevitable incompatibility follows solely from the type choice. |

For replay trajectories and simulation-based multiplayer, a useful decisive test is identical recorded inputs against the chosen original binary, comparing state at matched simulation ticks, then testing actual replay/network exchange. For authoritative state exchange, protocol/state reconciliation details also matter. We have not established a universal NFS3 synchronization model or cross-version compatibility from this precision inspection.

## Scope and continuation

No executable, saved Ghidra database, maintained C or raw reference export was changed. The initial precision pass did not rerun tests; later follow-ups reran static evidence scripts only, as linked above. The conclusion is the verified **precision-policy difference between these exact two files**, not complete knowledge of Modern Patch or a guarantee about any ARM64 port.

A broader Modern-versus-original audit should remain version-bound and address-mapped: precision/control-word policy first; then separately documented simulation changes, replay/network formats and other patch behavior. Import/analyze the original in a distinct Ghidra program/project if deeper original cross-references are needed; do not replace or reinterpret the current Modern Patch database as original analysis. GUI launch is not required for these headless saved-project inspections.

## Frontend background rendering removes a local x87 reset

A later complete comparison against the **official Modern v1.6.1** artifact (distinct from the local target in the initial table) verifies same-address background renderer `00495600..004956e1` (225 bytes, exclusive end). [The expanded texture/background audit](scripts/audit_texture_loading_followup.py) checks both pinned executable identities and exact removed bytes; [its manifest](evidence/audits/texture-loading-followup.json) retains full-span hashes and disassembly.

Original executes the following at `00495614..0049561f`:

```text
FINIT
FLDCW WORD [0079f3f4]
FWAIT
```

Modern replaces the eleven-byte block with `JMP 0049561f` and nine NOPs. Every other byte in the complete function is identical. The saved Modern body union excludes those nine NOPs and reports 216 bytes; that union's two changed-byte count is not complete coverage of the removed instructions.

This is **removal of a per-call reset**, not evidence that the background renderer explicitly selects extended precision in Modern. Original FINIT initializes x87 state, including control/status, tags and stack state, then loads the saved control word. The earlier startup evidence identifies the ordinary original saved extended control word, but later writes and arbitrary entry state must not be assumed impossible. Modern instead enters the retained remainder with its incoming x87 state unless another surrounding path established it.

Consequently the difference includes local stack/status/exception-state treatment as well as removal of the control-word load. If the incoming state differs from original's reset state, unchanged arithmetic need not be machine-state equivalent. Conversely a local reset's absence does not by itself prove a visible background defect, changed asset, or a particular arithmetic precision at every call.

**Bounded status: done; confidence: verified dual-binary instructions, with machine consequences derived.** Full callers, incoming control/stack state, pending exceptions and actual rendered output remain untested. For reconstruction, neither silently retain original's FINIT in a Modern-compatible function nor silently drop it from an original-compatible function without a documented state contract. No target instructions, Ghidra writes or maintained-C edits were performed.

## Packaged components are a separate control-state boundary

The [official DLL control-word follow-up](original-modern-packaged-x87.md) inventories all11 packaged DLLs and verifies a DX8 save/rounding/restore pair. That pair changes RC while preserving PC; it is not evidence that the patched game switches normal arithmetic back to24-bit precision. Other linear candidates, especially the MPRESS-named dgVoodoo payload, remain unvalidated. Full runtime control-state guarantees require actual component/caller contracts; neither this scan nor unchanged x87 instructions proves replay or multiplayer compatibility.

## Retained batch helpers do not close condition-bit liveness

The [line-boundary caller follow-up](line-boundary-x87-callers.md#batch-helper-follow-up-across-original-and-modern-baselines) verifies297 identical bytes across three batch helper bodies in original, official Modern and local analysis EXEs. Their local instructions are integer-only; one is call-free, while a conditional removal path reaches byte mover `004ea4f0`. They neither establish a new precision-policy delta nor prove the reconstructed helper's differing C0/C2/C3 bits are globally unobservable. A subsequent follow-up checks the byte-mover dispatcher and all three backends (1076 additional identical bytes), finding no explicit condition-bit reader there. Outer returns and other transform/render callees remain unresolved; x87/MMX side effects prevent a full-state transparency claim. This is additional static evidence, with no new probe or game run.

## Status-reader inventory

The [original/Modern observer inventory](original-modern-x87-observers.md) records all linear-decoded x87 status/environment-reader candidates, nonshared addresses and nine special contexts per baseline. It distinguishes four TOP-only masks from C0/C2/C3 consumers and verifies the shared saved-image atan wrapper. Lexical comparison adjacency is explicitly weaker than control-flow dominance, and the inventory does not establish whole-game condition-bit unobservability.

## Paired DLL control sites qualify whole-game precision claims

The [four-pair DLL comparison](original-modern-paired-dll-x87.md) now verifies matching control-site candidates/encodings/short contexts in author-reference versus final DX5, software, sound and Glide components. It adds older-side correspondence beyond the earlier package-only scan. Identical component instructions do not negate this chapter’s changed EXE scopes: incoming CW, runtime operands, providers and environment restoration can still differ. No universal fixed policy or replay/network equivalence is established by the102 primary and six environment-state candidates.

## Complete race-frame partition against the official final executable

The [frame audit](scripts/audit_race_frame_partition.py) compares the supplied
original with the **official final Modern** baseline, not the locally edited
Modern target from this report's initial table. Its
[manifest](evidence/audits/race-frame-partition.json) retains complete original
`004bc680..004bc81e` (414 bytes), Modern through its earlier return at
`004bc7e4` (356 bytes), the following tail and original no-op/helper bodies.
Within the complete original frame envelope, exactly three changed regions exist:

| Region | Verified change |
|---|---|
| `004bc687..004bc6a7` | Entry's conditional FINIT/saved-CW restore and EAX3/no-op call become unconditional FINIT/FWAIT, preserved ESI assignment and jump to retained frame work |
| `004bc794..004bc797` | Call operand bypasses original wrapper `004bc660`; both routes reach `0044ba30` |
| `004bc7de..004bc81e` | Exit's EAX3/no-op call and conditional FINIT/CW-save/single selection are replaced by an earlier saved-register epilogue/return and NOPs |

Original state-call targets `00431c30` and `00431c40` are each exactly five-byte
frame/return stubs. Their removal does not remove a renderer request hidden
behind those particular calls. Original wrapper `004bc660..004bc66a` merely
calls `0044ba30` within a frame; Modern reaches that same target directly at
`004bc793`. These findings qualify incidental call removals separately from
the substantive x87 policy change already described above.

Outside-body interval `004bc7e4..004bc830` is76 NOP-replaced bytes, beginning
inside the operand of original CALL `004bc7e3`. It contains the old conditional
control-word tail, original epilogue, alignment and separate five-byte no-op
at `004bc820`. It is not a standalone removed76-byte function. No original
call into that no-op is inferred from proximity.

**Done, verified static:** complete frame partition, same-target wrapper
bypass, no-op target bodies and outside-tail classification. The earlier x87
limits remain: intervening callbacks can change state, equal retained bytes
can consume different data, no full-frame machine-state/render equivalence is
established, and precision policy alone does not prove replay/network results.
No frame, callback, API or instruction probe was executed; executables and
saved Ghidra state were preserved.


## Removed optional startup exception unmasking

**Verified static difference, separate from precision control.** The [startup audit](scripts/audit_startup_fpuerrors_difference.py) and [manifest](evidence/audits/startup-fpuerrors-difference.json) bind the original/official final hashes, exact five call setups, removed span and retained helper bytes. Original ordinary switch slot25 is **`-fpuerrors`**; final Modern keeps that slot but its string is empty. The [parser comparison](original-modern-command-line.md) establishes slot-to-flag mapping.

Original `004a3d05` tests byte `0055eb2f` mask`02`, corresponding to bit25 of `0055eb2c`. If clear, it skips to `004a3d4a`. If set, five calls to **`004f7c90`** each supply EAX=0 and EDX masks **`0004`, `0002`, `0001`, `0008`, `0010`**, in that order. Their setup addresses are `004a3d0e`, `004a3d1a`, `004a3d26`, `004a3d32`, `004a3d3e`.

Complete helper `004f7c90..004f7cdc` is **76 bytes, identical in both executables**. When byte `005644c0` is nonzero, it saves CW and, for a nonzero mask, computes `CW = (oldCW & ~mask) | (EAX_input & mask)`, loads it, then rereads it. It returns the resulting WORD zero-extended in EAX. With the guard clear it does not access CW and returns0. The five startup return values are unused.

For the active-guard path, these calls clear mask bits`001f`: invalid operation, denormal operand, divide-by-zero, overflow and underflow become unmasked. They **leave precision/inexact maskbit`0020`, precision-control bits and rounding-control bits unchanged**. This does not select32-,64- or80-bit arithmetic. Existing later FINIT/FLDCW paths can replace this control word; the inspected startup block does not prove a persistent race/menu exception policy.

Final Modern replaces **`004a3d05..004a3d4a` with69 NOP bytes**, removing this conditional startup sequence in addition to emptying the named switch. The helper itself remains. Thus neither removal of all floating-point error support nor a claim that every exception is always masked follows. Other callers, guard initialization, exception delivery and user-visible failures remain unqualified. No floating-point exception or target instruction was executed.

## Bounded race scheduling and four-wheel arithmetic comparison

Fresh static comparison of the hash-pinned original and official final Modern EXEs
reproduces five identical ranges. The [audit output](evidence/audits/race-arithmetic-path.json)
retains aligned disassembly, hashes, direct/indirect calls and the selected arithmetic window.
Reproduce with `python3 analysis/scripts/audit_race_arithmetic_path.py`.
Names reuse the saved analysis; byte equality is independently checked from the two files.
All ends below are exclusive.

| Range | Role | Verified comparison |
|---|---|---|
| `004c48d0..004c4abc` | Simulation tick | Identical 492 bytes; even pre-increment ticks dispatch list `007d3690`, every tick dispatches `007d368c` |
| `0042c830..0042c94e` | Vehicle callback registration | Identical 286 bytes; loads function pointers from vehicle fields and inserts them by priority |
| `004be3a0..004be3cc` | Callback dispatch | Identical 44 bytes; context enters EAX, indirect call at `004be3c1` |
| `004ae4c1..004ae5c2` | Vehicle physics dispatch | Identical 257 bytes; category bit02 selects AI; selected non-AI branch calls `004ad7a3` at `004ae592` |
| `004ad7a3..004ae4c1` | Four-wheel integration | Identical 3,358 bytes, including the binary32 velocity update below |

The non-AI integration branch requires byte vehicle+8a==0 and a **signed raw DWORD**
comparison of vehicle+10c against `3f666666` to pass. This is not generally interchangeable
with a C floating comparison for negative values, NaNs or arbitrary bit patterns. Other
paths call `004aa8e7`; this comparison does not qualify those paths or AI dynamics.
[Existing callback lifecycle evidence](callback-list-lifecycle.md) supplies registration
and scheduling context. The five compared ranges alone do not prove every constructor's
callback-field assignments, successful initialization, actual runtime roster or all callback targets.

### A concrete storage boundary inside physics

At `004ae185..004ae1df`, three straight-line sequences load binary32 values from
vehicle+2e8/+2ec/+2f0, multiply by binary32 constant `0053dea0` (bits `3d000000`, exactly
1/32), add the binary32 velocity components at +a4/+a8/+ac and store back with `FSTP DWORD`.
The three stores are at `004ae19d`, `004ae1bb` and `004ae1d9`. Both baselines retain the
same instructions and constant. There is no call or control-word write in this window.
Thus these persistent outputs remain binary32 in Modern; the patch does not turn this
physics state into double or 80-bit storage.

Arithmetic still uses the **inherited** x87 precision/rounding mode before the stores.
This window does not independently establish that mode. The wider original/Modern CW
policy difference documented above can affect retained arithmetic elsewhere, especially
multi-operation intermediates; binary32 stores alone do not prove identical results.
Conversely, this exact 1/32 scaling window is not evidence of observed divergence: ordinary
finite scaling by a power of two is exact when representable, and exceptional/range cases
and upstream inputs require separate treatment. Do not infer desynchronization from its
presence or promise equivalence from byte equality.

### Control-word ownership remains a precise open boundary

None of these five ranges contains a direct `FINIT`/`FNINIT`, `FLDCW`, environment restore,
control-word store or integer x87 conversion. This is a **local instruction inventory**,
not a transitive guarantee: the integration routine delegates helpers, and the scheduler
executes dynamically populated callback lists. Any such callee may change the inherited
state. Existing original render-return single-precision selection and Modern render-entry
`FINIT` are established policy anchors, not a proof that every intervening path preserves CW.

Next static action: establish the selected vehicle's callback-field producer, then audit
its intervening callbacks/helpers for CW changes and floating stores/conversions. Only
after that can a particular original/Modern simulation arithmetic path have fully owned
CW state. Behavioral replay/network compatibility would additionally require matched
inputs, ticks and states; no new target instructions or probes were executed here.

For reconstruction, preserve the EAX vehicle/context contracts, explicit binary32 stores,
operation order and raw integer branch tests. A native C float expression, reassociation
or fused multiply-add is not automatically the original x87 contract. This finding adds
a concrete physics boundary; it does not qualify a game-facing replacement or whole-game
precision policy on every thread.

### Callback producer and immediate-helper follow-up

The same reproducible audit now also checks initializer `0042c400..0042c51f`
(287 identical bytes) and all **18 distinct direct callees** of `004ad7a3`.
Their saved ranges are re-read from both pinned files; all are byte-identical.
The evidence retains each helper's range/hash, call sites and integer conversions.
This extends the five-range finding above rather than replacing its limits.

Initializer `0042c423` writes `004ae4c1` into vehicle+608. Registration
`0042c8a2..0042c8b4` loads that field and inserts it into even-tick list
`007d3690` at priority30 with the vehicle as context. The preceding +60c callback
has the same priority and is inserted first for each vehicle. The [existing lifecycle
analysis](callback-list-lifecycle.md) establishes stable equal-priority insertion.
The dispatcher loads context into EAX before its indirect call. These instructions
establish the selected static assignment-to-dispatch chain in both baselines, subject
to successful setup and no subsequent overwrite/list mutation.

There are explicit alternatives: category bit02 replaces +608 with AI dynamics
`004088f0` at `0042c4ba`; the network-associated branch also writes that target at
`0042c4f8`. The latter requires `006fd50c!=0`, signed session value `006fd3b0>1`,
vehicle index+1f0 different from local index `006fd4f4` and signed index below
`006fd514`. Do not describe every multiplayer participant as executing the same
full four-wheel callback. This routing is retained in both EXEs; its existence does
not prove the network synchronization algorithm or a particular observed roster.

No direct CW-changing instruction occurs in the 18 immediate helpers, but:

| Helper | Retained integer conversions | Further dependency |
|---|---|---|
| `004a9bc4` smoothed controls/mode state | Seven `FISTP DWORD`: `004a9d7d`, `004a9e8f`, `004a9ee2`, `004a9f35`, `004a9f8f`, `004aa2cb`, `004aa35d` | Eight call sites; their transitive state effects remain outside this follow-up |
| `004aaed1` engine RPM/drive response | Three `FISTP DWORD`: `004ab111`, `004ab447`, `004ab7bd` | Seven call sites, including temporary rounding helper `004dfd56` discussed above |
| Other16 immediate helpers | No direct `FIST*` instruction | Some delegate additional math/response helpers; see evidence call lists |

`FISTP` conversion obeys the then-current rounding mode; x87 precision control and
rounding control are separate fields. Ten retained conversion sites do not imply ten
behavior changes, and no difference in their actual results has been measured. A C
cast truncates rather than automatically reproducing x87 conversion under an arbitrary
CW, and exceptional/out-of-range conversions need explicit treatment. The existing
`004dfd56` temporary-CW evidence must be followed through its actual callers rather
than assumed to set the entire integration routine's policy.

Remaining action for CW ownership: trace those further calls and earlier callbacks
on the selected list, including the +60c contact callback that precedes +608. The
producer question is now answered for this initializer; exhaustive later field writers,
active list contents and complete transitive state preservation remain open. No new
runtime test, instruction probe or executable/Ghidra mutation was performed.

### Deeper dependency inventory: retained local extended-state math

The [direct-edge inventory](evidence/audits/physics-fpu-dependencies.json), reproduced by
`python3 analysis/scripts/audit_physics_fpu_dependencies.py`, follows syntactic direct calls
and external direct branches from `004ad7a3`, separately in the pinned original and official
Modern bytes. Both visit176 saved-function entries;174 paired saved ranges are identical.
The two differing ranges are abort handler `00401010` and truncation helper `004dfd56`.
This is **not** a runtime reachability or complete call-graph claim: each inventory leaves
111 indirect call/jump sites unexpanded and one nonentry direct target, `004fe81e`, on an
abort/runtime path. Zero linear decode warnings do not prove that embedded data or all
function boundaries were recovered. The manifest records shortest syntactic routes,
call edges, imports, hashes and these omissions. It reuses Modern's saved range inventory;
explicit anchors below recover the original truncation helper's longer tail separately.

**Shared epilogue resolved by inspection.** The surviving nonentry
edge is a conditional jump at `004fe8b2` from the routine entered at
`004fe828`. The source prologue saves ECX, ESI, EDI and EBP and
allocates four local bytes. Target `004fe81e..004fe826` frees those
four bytes, restores those four registers in reverse order and
returns. Both the source through the jump and the complete epilogue
match byte for byte between the pinned executables. The target is a
shared unwind sequence with no x87 instruction or further call.
The generated inventory still records the branch as a nonentry edge.
The 111 indirect sites remain unexpanded.

A concrete retained physics-to-angle route is:

`004ad7a3` → (`004adff3`) `004aca4f` → (`004ace3b`) `004ea9c0` →
(`004ea9c9`) `004e06d9` → (`004e06e8`) `004ff624` → (`004ff637`) `0051f320`.

These named ranges match in both files. At `004ff628`, the wrapper stores an operand as
80-bit TBYTE; `004ff62c FNSAVE [ESP]` saves the environment/registers and **initializes the
FPU**, including CW037f. FNSAVE is therefore a state-changing instruction, not merely a
memory copy. The wrapper reloads two TBYTE operands and calls the angle routine; the normal
tail writes its result into the saved register image, merges low status bits and executes
`004ff650 FRSTOR [ESP]`. This preserves the caller's saved CW while returning the computed
register result; it does not promise an untouched complete FPU state. Intel documents the
save-and-initialize behavior in [Software Developer's Manual Volume1, x87 state saving](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf).

Inside the retained angle routine, `0051f386 FNSTCW` records CW. The sequence through
`0051f39e FLDCW` computes `(savedCW | 033f) & f3ff`: masked exceptions, PC11 (64-bit
significand), nearest rounding. Special input branches can bypass this sequence, and
its indirect jump tables remain unexpanded here. The inspected normal route nevertheless
contains local extended-mode setup **inside a physics dependency in the original too**.
Do not equate the original's ordinary race single-precision baseline with every nested
math operation. Runtime branch frequency, complete exceptional paths and trajectory
impact were not measured. These retained helpers are not new Modern-only changes.

### The retained angle dispatch restores the saved word on all eight table routes

The indirect branch at `0051f479` uses the eight file-backed DWORDs
at `0056cb38..0056cb58`. Both executables have the same table and
the same code through the eight returns at `0051f480..0051f510`.
The index starts at zero at `0051f3a2`, can increment once, and
then takes two successive doubling-plus-carry operations, so the
normal path selects an index from zero through seven.

| Table index | Target | Saved control-word reload |
|---:|---|---|
| 0 | `0051f480` | `0051f480` |
| 1 | `0051f48b` | `0051f48d` |
| 2 | `0051f498` | `0051f4a0` |
| 3 | `0051f4ab` | `0051f4b5` |
| 4 | `0051f4c0` | `0051f4c8` |
| 5 | `0051f4d3` | `0051f4dd` |
| 6 | `0051f4e8` | `0051f4f0` |
| 7 | `0051f4fb` | `0051f505` |

Each route reloads the WORD from `[ESP+18h]` before unwinding.
This resolves one of the inventory's five indirect jump sites
per build. The inventory also records 27 import-bound sites and
79 other indirect call sites per build. These counts describe
syntactic sites. They do not establish runtime frequency, effects
of imports on the x87 environment or equivalence for exceptional
angle inputs.

### Changed drivetrain truncation helper

The direct drivetrain route `004ad7a3` → (`004adc0a`) `004aaed1` → (`004ab10c`)
`004dfd56` reaches different implementations:

| Original `004dfd56..004dfd73` | Official Modern `004dfd56..004dfd6d` |
|---|---|
| Saves CW, copies it, replaces high byte with1f, loads temporary CW, FRNDINT, restores CW; waiting save/wait instructions | Pushes0c3f, saves CW into upper WORD of stack allocation, loads0c3f, FRNDINT, restores CW |
| Temporary PC11, RC11; low CW byte retained | Temporary PC00, RC11; all six exception masks set |
| 29-byte body | 23-byte body |

Ends are exclusive. Both select truncation toward zero and restore incoming CW on their
inspected normal return. FRNDINT is not controlled by PC, so the PC difference alone is
not evidence of different ordinary finite truncation results. Exception masking/waiting
behavior and exceptional operands are distinct unresolved behavioral questions; do not
silently discard them in a native replacement. Modern's saved function boundary would
truncate the original tail if reused without inspection; explicit complete anchors in
the new evidence avoid that mistake.

This closes the question of whether the selected physics dependency tree contains local
FPU setup: it does, in both versions. It does **not** close the inherited CW at every
callback entry, indirect target effects, full math semantics, or replay/network equivalence.
The next precision work should address a specific indirect/callback boundary or a matched
behavioral experiment when authorized, rather than continue assuming all retained physics
instructions execute under a single unchanging precision setting.

### Race-loop tick call sites

The supplied original and official Modern retain the same 164 bytes at
`004c5342..004c53e6` (exclusive end, SHA-256
`470183c72bbf46053a1f1b3f27eacbb3928618a850df9b96ac335e7d119cbaec`).
This covers all four identified direct calls from the race loop to
`004c48d0`. The branch at `004c5346` selects the single-call path when
the signed division remainder is zero. With a nonzero remainder, mode
`[007cd94c]` equal to 2 also takes that path, while mode 3 calls twice
and then increments `[007d36b0]`. On the separate path at `004c53d2`,
the loop calls `004c81c0` immediately before reloading the sequence in
EAX and calling the simulation tick.

The 49-byte `004c81c0..004c81f1` body is also identical (SHA-256
`ad7007bc1ed7a0051701583b59c3d51b59053195945332c03e0b6d5192121d47`).
It reaches `004c8250` only when signed `[006fd3a0] <= 1`, session
`[006fd3b0]` is neither 0 nor 1, `[006fd50c]` is nonzero and the
sequence in AL is odd. The wrapper contains no x87 instructions. This
identifies a conditional pre-tick dependency for the input/state comparison.
Its callee, the values feeding the scheduling branches, and actual tick
cadence remain separate evidence gaps.

The hashes cover file-backed PE bytes at the listed virtual addresses
using image base `00400000`. Both full executable hashes were checked
against the original and official-final pins before disassembly.

### Replay input blocks in both executables

Direct PE reads of the hash-pinned original and official Modern confirm
identical bytes and matching [inventory hashes](evidence/audits/original-modern-function-diff.json)
for these saved ranges:

| Range (exclusive end) | Bytes | Role |
|---|---:|---|
| `004bd380..004bd3dc` | 92 | Select record or playback tick path |
| `004bd000..004bd087` | 135 | Gather and buffer participant input |
| `004bd090..004bd1df` | 335 | Decode and apply participant input |
| `004bda00..004bdb5b` | 347 | Record vehicle event priorities |
| `00477c20..00477d90` | 368 | Update recorded vehicle pose sample |
| `00477b00..00477b47` | 71 | Read optional pose extension |

The retained recording code gathers four bytes per tick and buffers them
in four 32-byte channels. Playback calls decoder `004bcee0` and copies
128 decoded bytes to `007cd548 + participantIndex*0x80`. The participant
cursor indexes the four channel starts at offsets 0, 32, 64 and 96.
See the [original layout investigation](detailed-analysis-notes.md#replay-decode-destination-and-channel-layout-004bd090).

This establishes a shared decoded control layout at the tick boundary.
Complete file format, pose-extension handling across versions, and matched
trajectory results remain open. Matching recorded input
does not establish matching initial state or arithmetic.

The compressed control blocks also use the same run-length codec. Direct
PE reads from the same pinned executables matched each of these ranges
and their hashes in the paired function inventory:

| Range (exclusive end) | Bytes | Role |
|---|---:|---|
| `004bcda0..004bced1` | 305 | Append four encoded channels |
| `004bcee0..004bcffd` | 285 | Decode four channels and advance the compressed cursor |
| `004bc9b0..004bca7f` | 207 | Encode one 32-byte channel |
| `004bca80..004bcaf1` | 113 | Decode one channel |

Disassembly of both wrappers confirms four calls to their respective
per-channel helper. The [encoder analysis](detailed-analysis-notes.md#replay-encoder-paired-stream-partition-and-expansion)
establishes the 32-byte partition for correctly aligned, intact encoder
output. This comparison covers the codec used for the selected control
stream. Loading a complete replay still requires compatible container
fields, initialization and playback state.

### Default replay resource entry points

Both pinned executables retain identical bodies for default replay save
(`004bd1e0..004bd2d3`, 243 bytes), default replay load
(`004bd2e0..004bd37d`, 157 bytes), and optional pose extension write
(`00477ac0..00477afc`, 60 bytes). The paired function inventory records
the exact hashes, confirmed by fresh reads from both PE files.

The save and load paths both reference the resource name at `00540168`.
The load path reads into `007a3e50` and calls the pose extension reader
`00477b00` when the flag at `007a5f40` is nonzero. Afterwards it calls
the preparation car-reference and model-index resolvers at `00478090`
and `00478100`. Asset resolution is thus a separate compatibility
dependency even when the compressed controls and resource entry points
match. The complete resource writer/reader chain, loaded asset identities
and cross-version playback results still require verification.

Both files store the same NUL-terminated literals: `replay.rp3` at
`00540168` and `rb+` at `00540174`. Nine immediate dependencies also
match the full SHA-256 values in the paired function inventory:

| Role | Identical function entries |
|---|---|
| Preparation car identifier encoding and population | `00478010`, `004781b0` |
| Preparation car reference and model lookup | `00478090`, `00478100` |
| Resource open, read and save | `004e28d0`, `004e2de0`, `004eeae0` |
| Buffered seek and write used by the pose extension writer | `004e9088`, `004eebd0` |

Together with the tick and codec comparisons, this confirms retained code
from the default replay entry points into resource I/O and car resolution.
The actual asset tables, file contents and downstream initialization still
matter when comparing playback across versions.

Both preparation resolvers call `00439990`. Its 84-byte body
(`00439990..004399e4`) matches in fresh reads from the pinned EXEs.
It compares exactly 16 bytes against each registry entry at entry+0x31c,
returns the index of the first match, and returns -1 at the end of the
registry. The saved comparison inventory also records identical iterator
bodies at `00438a80` (26 bytes) and `00438aa0` (33 bytes). For a fixed
identifier and ordered registry, the lookup rule is retained. Replay car
identity across installations still depends on registry population, order
and the assets behind the selected entry. See the
[car alias comparison](original-modern-car-alias.md) for separate changes
elsewhere in car naming and selection.

Registry discovery itself differs. The [paired car registry audit](original-modern-car-registry-flags.md)
locates the change at `0043a20e..0043a25c`. The original conditionally
sets record+0x380 bit 0x20 for Ferrari and Mercedes. Modern skips that
block. The flag write is separate from the identifier bytes at +0x31c
that replay lookup compares. The known consumer affects Hot Pursuit
eligibility. Evidence of a different replay lookup result would require
a change in the ordered identifier list or in the assets that a matching
entry resolves to. The registry audit reproduced from both pinned EXEs.

### Ghost loading changes the surrounding configuration

The default replay resource path above and the current-race ghost wrapper
are separate entry points. The changed ghost wrapper at `004466a0` retains
the call to reader `00477b50`, but changes the snapshot timing and the
configuration it restores after a successful load. Modern restores the
refreshed 12-byte race configuration header and three additional 11-byte
identity fields. This is a verified loading-state difference beside the
retained replay codec. It gives a concrete reason to compare initial
configuration as well as recorded controls in a cross-version test.
[Paired ghost loading audit](original-modern-ghost-loading.md).

### Retail renderer setup controls the race-frame x87 boundary

In the supplied original, the renderer dispatcher clears
`007a3a70` at `004b59d7`. How it leaves that cell depends on the
selected branch. The `nulla.dll` branch writes 1 at `004b5a16`.
The Voodoo and PowerVR candidate branches load 1 into ESI and EDI
respectively before their renderer state calls and store those
registers at `004b5bdb` and `004b5dfc`. With the ordinary callback
register-preservation contract those stores also write 1. The D3D
candidate branch has no direct store to that cell after the common
clear, through its local continuation. This is a branch analysis,
with indirect writes and alternative loaded DLLs still possible.

A nonzero value at the two race-frame tests bypasses both the
entry control-word reload and the exit reset to single precision.
The bypass preserves the incoming control word at those boundaries
unless intervening code changes it. It does not prove the precision
in effect throughout the frame. Final Modern Patch removes those
tests and reuses the same address for the adapter index, as traced
in the [renderer comparison](original-modern-renderer-lifecycle.md#retail-uses-a-different-adapter-field-and-a-fixed-follow-up-mode).

The software candidate paths (selectors 1 and 2) explicitly leave
the gate at zero. They clear ECX at `004b5a92`, call `00431c50`,
then store ECX at `004b5aaa`. The complete helper
`00431c50..00431d50` saves ECX at entry and restores it at
`00431d4d`. Its internal integer colour-table calculations do
not carry an ECX result back to the caller. The Rage candidate
branch at `004b5bef..004b5c76` has no direct write to the gate
after the common clear.

Thus the ordinary software path requests the retail race-frame
control-word transitions described above. This concerns the
candidate branches and the named state writes. The actual driver
selected by an override and any indirect changes during a frame
remain outside the result. See the
[retail selector table](original-modern-renderer-initialization.md#original-numeric-selection-before-loading).

### The flag becomes the adapter index in 1.6.0

Packaged 1.5.2 and 1.5.3 both clear `007a3a70` at
`004b59fd` and set it to 1 on the renderer branch at
`004b5b2f`. Version 1.5.2 tests it around inline control-word
sequences. Version 1.5.3 still tests it at `004bc689` and
`004bc7de`, but calls the factored helpers at `004bc692`
and `004bc7e7` respectively.

In 1.5.3 the renderer-name suffix parser stores the adapter
index to `0055fdbc` at `004b5822`. The startup display
call reads it at `0051768b`. Both operand addresses change
to `007a3a70` in 1.6.0, at the same instruction sites,
while the race-frame tests disappear. The change to the
x87 path and the reuse of its old flag address therefore
occur at the same packaged boundary. Address-based data types
and names should follow the selected executable version.
See the [later adapter input trace](original-modern-renderer-lifecycle.md#the-adapter-index-input-is-retained-across-the-reorder).

In both 1.5.2 and 1.5.3, the dispatcher at `004b5a4a`
uses BSF on the renderer mask at `007a3a58`. For a nonzero
mask, jump-table entries 3 and 4 at `004b59e0` and `004b59e4`
both lead to `004b5b1b`, the branch that sets the x87 bypass
flag. Thus the branch is selected when the **lowest set bit**
is bit 3 or bit 4. A mask with a lower bit set reaches a
different entry even if bit 3 or 4 is also set. This describes
the dispatcher and its direct store. A zero mask, earlier driver
initialization failure, and indirect state changes are outside
the verified branch contract.

The ordinary INI path maps the bypass to a named renderer type.
In both releases, the bytes at `004b58ce..004b58f5` match.
After reading `[THRASH] Type` and lowercasing it, the loader
maps first bytes `d`, `v`, and `s` to masks `40h`, `10h`,
and `02h`, with a default of `01h`. It writes the mask at
`004b58f0`. Thus the normal INI route can reach the bypass
through bit 4 (`v`). None of those four outputs sets bit 3.
The retained 1.5.3 package supplies `Type=voodoo` in
`drivers/nglide/thrash.ini` and `Type=d3d` in
`drivers/dx7/thrash.ini`. This ties those two authored choices
to different frame-boundary policies when loading and renderer
initialization succeed. Other producers of bit 3 and runtime
control words remain unverified.

The angle routine's file-backed constant span
`0056cb28..0056ccd0` is also byte-identical in the two executables.
It includes the 16.0 and 0.0625 binary32 scaling constants, the
extended-precision polynomial coefficients and result offsets,
and the indexed table region beginning at `0056cbb0`.

Both normal-path calls to `00526aeb` load selector `0fh`.
The corresponding DWORD at `0056cd18` is `00526b9f` in both
files. That branch spills both x87 operands as TBYTEs and
calls the retained divide helper at `005269d4`. The helper body
through `00526aeb` matches, including the branch into a scoped
control-word adjustment. This resolves the dispatch target for
these two known callers. Other selectors, exceptional operands
and live state remain outside this comparison.

### The shared divide helper restores precision before the final divide

On the checked scaling paths in `005269d4`, the local control word
sets extended precision and nearest rounding and masks exceptions.
The helper multiplies both operands by the same binary32 constant.
It uses 0.9375 at `00526a40` or 1.0625 at `00526a57` depending on
the exponent check. The constants at `0056ccd0..0056ccd8` match
in the two executables. Each path restores the word saved at
`[ESP+1ch]` **before** its final FDIVP.

The separate branch at `00526a86` can scale one operand by
`2^63` (matching binary32 bytes at `0056ccd8`), spill it as
TBYTE, restore the caller's word, and retry classification at
`005269dc`. Its other exit restores the word before dividing
at `00526ae8`. Direct divide paths bypass these local changes.
Thus the extended scope covers operand preparation. The divide
itself executes with the restored word or the incoming word.
This is static control-flow evidence for the matching bodies.
Exception outcomes and complete numerical equivalence were
not tested.

### The angle fallback uses FPATAN before any local control-word change

Both pinned executables have the same complete 512-byte body at
`0051f320..0051f520`, with SHA-256
`bed104cc803cbc0cc31697509db6f3d020cd476757d7110fa3093bd7da8b9d5f`.
After spilling its operands as TBYTEs, the entry branches to
`0051f510` if either operand's explicit significand integer bit
is clear or its masked exponent is zero or `7fffh`. The six
tests all precede the saved control-word sequence at `0051f386`.

The fallback reloads both TBYTE operands, executes FPATAN at
`0051f517`, unwinds and returns. It makes no local control-word
change. This distinguishes the fallback from the polynomial
path and its eight restore routes. On the documented physics path,
the wrapper has already initialized the FPU with FNSAVE before
calling this routine. Other callers can supply a different incoming
environment. The exact result and exception flags for special
operands remain untested.

### The physics wrapper merges only the angle call's low status byte

The complete 52-byte wrapper `004ff624..004ff658` is identical
in both executables (SHA-256
`582c24d8849b7d0ff5083f5ec3bbd46a82dbbc3d6abd4fa4c0f559ec48db755b`).
It snapshots the angle call's status with FNSTSW at `004ff63c`,
before spilling the result at `004ff63e`. The merge at
`004ff642..004ff650` ORs bits 0–7 of that snapshot into the
saved status word at `[ESP+4]`, then reloads the saved image.

This carries the six exception flags, stack-fault flag and
exception-summary bit into the restored image. The inner call's
condition codes and TOP are outside the low byte. Those bits come
from the image captured after the wrapper's initial operand pop.
The final result spill occurs after the inner status snapshot, so
flags raised by that spill are outside the merge. This records
the normal instruction sequence and leaves pending exceptions
and exceptional unwinds untested.

### The selected physics caller stores the scaled angle as binary32

The original and Modern executables match across the caller span
`004ace32..004ace43`, scaler `004ea9c0..004ea9d8` and dispatcher
`004e06d9..004e06ee`. The scaler loads two binary32 arguments
and calls the dispatcher. That routine exchanges the operands
and checks bit 0 of `00567858`. A clear bit executes FPATAN
directly. A set bit enters the previously mapped FNSAVE wrapper.
The flag's runtime value is not established by this branch trace.

On either return, `004ea9ce` multiplies the angle by the same
binary64 value at `0054b6c0` in both executables (approximately
0.159154958). That multiply is outside the wrapper's isolated
x87 environment. Then `004ace40` stores the result as binary32
at `[EBP-0ch]`, before the following vehicle-state branch.
A comparison must therefore account for the environment of
the outer multiply and store, even when the isolated angle
calculation matches. The inspected caller makes no integer
conversion at this boundary. Stored values and trajectory
effects remain untested.

### The angle dispatch bit comes from a retained startup arithmetic check

In both executables the file-backed byte at `00567858` is zero.
The matching routine at `0051f2a0..0051f31e` is referenced by
a relocated function pointer at `0056b810` in both images.
It loads fixed operands and skips the check when the unsigned
byte at `005644c1` is below 3. Otherwise it runs the arithmetic
sequence at `0051f2ce..0051f30e`. The signed-greater branch outcome
after `0052699c` sets bit 0 through OR at `0051f310`. The other
returns leave the byte unchanged.

This is the direct producer for the bit tested by the angle
dispatcher at `004e06db`. It also feeds other math dispatchers.
The original and Modern retain the same producer instructions,
initial value and relocation. The pointer alone does not establish
initialization order, the arithmetic check's result on a given
CPU or Wine configuration, or the branch taken in an observed race.

With the dispatch bit initially clear, the startup check uses
the direct FDIV at `00526476`. The fixed binary64 inputs are
4,195,835 and 3,145,727. It computes the quotient, multiplies it
by the second input, and subtracts the product from the first.
The helpers store each arithmetic result as binary64 before
passing it on in registers. For these ordinary finite operands,
the comparator at `0052699c` causes the flag to be set when
the residual exceeds the encoded binary64 threshold of
approximately `1e-8`. This is a one-sided check.

The inspected divide, multiply, subtract and compare paths
match in the two executables. The test detects a discrepancy
in divide-and-multiply arithmetic rather than reading a CPU
model identifier at the flag write. Its result also depends
on the x87 environment in effect when the initializer runs.
No hardware or Wine result was measured.

The startup dispatch is also retained. In both executables,
`004ff370` calls `004ff41c` with priority limit `21h`.
The runner scans ten six-byte records at `0056b7de..0056b81a`,
ignores records marked 2, selects the lowest eligible priority,
calls its pointer through `004ff410`, marks it 2 and repeats.
The file-backed table and the runner bytes match.

The FPU initializer `004ff5dc` has priority 2. Its admitted
path executes FNINIT and can publish the FPU classification
byte at `005644c1`. The arithmetic check `0051f2a0` has
priority 3 and reads that byte. From the file-backed initial
record state, the runner therefore dispatches the FPU initializer
before the arithmetic check. The initializer has its own skip
conditions, so that ordering alone does not establish the
control word or classification on every startup.

The classifier called by that initializer is also retained.
`004ff59c` loads the same file-backed word `127fh` from
`0056acf8` in both images and calls `0051f272`. The latter
executes FINIT, computes 1 divide by zero with the initialized
exception masks, then compares the result with its negation.
It returns classification 2 if the comparison sets ZF through
FNSTSW/SAHF, or 3 if ZF is clear. Before returning it executes
FINIT again and loads the word passed in AX at entry. That load
uses the supplied word and does not recover whatever control
word was active before the classifier call.

The initializer at `004ff5dc` can publish this classification
to `005644c1` at `004ff618`. The arithmetic check at priority 3
admits classifications of at least 3. The compared bytes cover
the classifier, its immediate caller and the initializer.
Actual publication still depends on the initializer's gates.
The classification is an arithmetic observation encoded by the
program, with no live result measured in this comparison.

For these fixed inputs, ordinary correctly rounded arithmetic
under the classifier's `127fh` control word (24-bit significand,
round to nearest) produces a zero residual. This follows by
rounding each operation at the selected precision and then
rounding each spill to binary64. At 24 bits the quotient is
exactly `11188897 / 8388608` after rounding, and multiplying
back rounds to 4,195,835. Exact rational calculation with
53-bit and 64-bit operation precision, retaining the binary64
spills, also gives a zero residual.

Directed rounding can change the outcome. With 24-bit precision
and rounding toward negative infinity, the product rounds to
4,195,834.5 and the residual is 0.5, above the threshold even
with a correctly rounded divide. With rounding toward positive
infinity, the residual is −0.5 and the one-sided check stays
clear. These are derived cases for the direct divide path with
the bit initially clear. They neither reproduce faulty hardware
nor measure the effective startup control word.

The four direct reads of bit 0 of `00567858` found in each
executable take the same alternatives in the matched spans:

| Test | Bit clear | Bit set |
|---|---|---|
| `004e06c6` | One-argument angle path loads 1 and executes FPATAN | Calls the saved-state angle wrapper with the same prepared operands |
| `004e06db` | Two-operand angle path exchanges the operands and executes FPATAN | Calls the same saved-state wrapper |
| `005233fa` | Executes FDIVRP after loading 1 | Calls the previously mapped divide dispatch with selector `0fh` |
| `00526466` | Divides by the binary64 stack operand directly | Calls `0052700c`, which checks exponent bits and x87 TOP before dispatching |

The last read is inside the helper used by the startup arithmetic
check itself. The residual calculation documented above assumes
the initially clear bit, so it uses direct FDIV. These checks
establish the matching direct consumers and branch targets.
The complete divide workaround and any indirect users remain
outside this trace.

### The drivetrain conversion writes an integer RPM limit after restoring CW

The original and Modern caller instructions at
`004ab0e6..004ab13c` match. Two upstream arms materialize
binary32 at `[EBP-48h]`. One multiplies the integer at
profile offset `1c4h` by the vehicle float at `5f0h`.
The other converts the integer at profile offset `1c0h`.
The caller reloads that binary32 value and enters the differing
FRNDINT helper at `004ab10c`.

After the helper restores its incoming control word, the caller
performs FISTP to a signed DWORD local at `004ab111`.
For an in-range finite integer returned by FRNDINT this second
conversion preserves the value. The caller then takes the signed
minimum with profile offset `1c4h` and keeps it in `[EBP-28h]`
for later drivetrain branches. Because the multiply and binary32
spill precede FRNDINT, matching finite truncation behavior alone
does not establish an identical limit. The conversion also has
no local invalid-result check before the signed cap. The
[drivetrain trace](police-torque-runtime.md#full-drivetrain-entry-versus-actual-torque-interpolation)
covers the later branch conditions. No live RPM or exceptions were
measured here.

The free-rev route supplies a concrete consumer of that limit.
In the matching span `004ab13c..004ab203`, a nonzero vehicle
WORD at `164h` adds profile DWORD `1ch` to the limit before
comparison. When current RPM at vehicle offset `590h` is below
that limit and shift state `510h` is zero, the routine adds
250 to RPM, takes the signed minimum with the adjusted limit,
then takes the signed maximum with the profile value at `1c0h`.
It writes the result back to vehicle offset `590h` at
`004ab1f8`. The additions are 32-bit wrapping operations.

Thus a changed converted limit can affect whether this branch
runs or the value it writes when its upper cap applies. The
lower cap and state gates can also make a difference in the
limit immaterial to this write. This is a static dependency
shared by both executables. No divergent RPM or trajectory
was observed.

After the free-rev RPM write, the matching block at
`004ab3e0..004ab3ff` clears vehicle DWORDs `598h` and `594h`
and jumps to the shared response tail. That tail at
`004abd2b..004abd9c` selects the returned response using
vehicle state `164h`, the comparison against zero of float
`4f4h`, and the response locals. It does not reload the RPM
field `590h` on this path. The two file-backed response
coefficients at `0053dd44..0053dd4c` also match.

The caller at `004adc0a` stores the returned x87 value as
binary32 and splits it into a fraction scaled by profile float
`1d0h` and the remaining difference. This sequence matches in
both files. The trace therefore establishes an RPM state write
and a separate response return. It supplies no direct edge
from the newly written RPM to that return within this tail.
Later RPM consumers and any effect across simulation ticks
remain open.
