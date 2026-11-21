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
