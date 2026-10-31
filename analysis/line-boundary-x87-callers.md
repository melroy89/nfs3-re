# Line-boundary helper: caller dependence on x87 condition bits

**Bounded static finding:** none of the six known direct callsites reads the differing C0/C2/C3 bits before overwriting them or returning. This does **not** establish that the differences are unobservable throughout the game: several paths return with the bits still live, and the bounded outer trace reaches unreviewed callees.

This pass inspected saved instructions and recorded comparison results. **No C compilation, new probe, differential test rerun, executable patch or Ghidra mutation was performed.** Prior [functional test results](line-boundary-reconstruction-results.md) remain historical execution evidence, not new results from this review.

## Evidence and method

[Curated instructions/flow metadata and frontiers](evidence/audits/line-boundary-x87-callers.json) pin the executable and saved `db.3146.gbf` hashes. [Read-only Ghidra inventory script](scripts/ghidra/X87CallerInventory.java) collected ten functions from the existing project with `-readOnly -noanalysis`. Full raw instructions are local under `analysis/captures/reconstruction/x87-callers/`; no C sources or annotations changed.

The tracked bits are C0=`0100`, C2=`0400`, C3=`4000`, consistent with the observed SW XORs `0100`, `4000`, `4500`. Integer EFLAGS are a separate state: `TEST EAX` and the following integer branch inspect the returned pointer, not the x87 status word.

For each call return, follow both control-flow successors until an x87 status read/environment save, a fresh x87 comparison/condition producer, another call with a verified entry overwrite, an unresolved call, or a return. A return propagates state; it is not a kill. FLD/FSTP and ordinary arithmetic are not assumed to clear all tracked bits. `FCOMP` defines fresh C0/C2/C3 before the subsequent `FNSTSW`/`SAHF`. The exploration overapproximates branch feasibility and stops conservatively at unreviewed calls.

## All six direct sites

| Helper callsite | Caller | Complete local frontier while the bits remain live |
|---|---|---|
| `00485ff0` | `ClipFloatSegmentToRectangle` (`00485f20`) | `TEST EAX`/integer copies and branches. A continuing path reaches fresh `FCOMP` at `0048601c` before `FNSTSW` at `0048601f`; a failure path returns at `004860a0` without reading the bits. |
| `00486071` | `00485f20` | Integer pointer test/copies, then returns at `00486090` or `004860a0`. There is no path from this second call back to the earlier `0048601c` comparison. |
| `004861cf` | `BuildRectangleCrossingSegmentOutsideFragments` (`004860b0`) | Integer result copies, then `RET` at `004861e9`; no x87 status read or overwrite. |
| `00486247` | `004860b0` | Integer result copies, then `RET` at `00486262`; no x87 status read or overwrite. |
| `0048627e` | `004860b0` | `TEST EAX` and integer branch. Null path returns at `00486292`; nonnull path reaches a new helper invocation at `004862cd`. That invocation executes its own `FCOMP` at `00485c9d` before reading status. |
| `004862cd` | `004860b0` | Integer result copies, then `RET` at `004862f4`; no x87 status read or overwrite. |

The two direct callers have no hidden post-call FNSTSW/environment-save path in their inspected contiguous bodies. This establishes absence of a direct C-bit dependency at those sites, not preservation of the original final machine state. Some early rejection paths can return before the next comparison, so checking only the first successful continuation would be insufficient.

## Outer propagation and unresolved boundaries

- **HUD line append `004873e0`:** the clipper result returns at `00487429`; fragment-builder result at `004874ad`. Their reachable local paths use integer control/copies plus FLD/FSTP, but no x87 condition/status reader. Some loop paths call the clipper/fragment builder again, whose entry comparisons replace incoming bits. Other paths return at `004875fc`. Batch-cursor calls at `0048754e`/`004875b9` target `AdvanceRenderBatchVertexCursor` (`0049bf40`): its entire 15-instruction body is integer-only with no calls, so it does not consume the bits or close their lifetime.
- **Tinted-triangle clipping `00487a30`:** after clipper call `00487c2d`, the next call `00487c40` immediately enters a fresh compare; after that, `00487c52` does likewise. After the third clipper returns, there is no further local status read. Paths may return at `00487fd6`/`00488025`, or invoke `QueueTintedQuad` (`00486f70`) / `AppendTintedTriangleToBatch` (`004870c0`). Those two emitters do not locally read status. The follow-up below checks `0049bcd0` and `0049bd30` plus removal helper `0049bdc0`, first narrowing the boundary to byte mover `004ea4f0`, whose copy cascade is now checked below; outer returns remain propagation boundaries.
- **Track-map ancestor `0048d4c0`:** post-line-append paths from `0048dd78`, `0048def2`, `0048e0ea` reach calls including `0048cb50`, `00477d90`, `0048cc60`, or another line-append call before a guaranteed local status overwrite. Their local bodies and two small pose callees are now reviewed in the follow-up below; the remaining conditional targets are explicitly listed there. Later own comparisons at `0048e568` and beyond do not prove that no earlier callee observed the live bits.
- **RPM-needle ancestor `00489e00`:** after tinted-triangle call `0048a206`, it reaches `RET` at `0048a214` without a new local status read or comparison. The caller of this outer function remains a propagation boundary.

These are real limits of the reviewed scope, not evidence that a caller actually depends on the bits. No raw status read of helper-produced C0/C2/C3 was found in the locally traced paths; a positive dependency or whole-game absence claim would require following the unresolved boundaries.

## Decision and next gate

| Question | Finding / confidence | Status and affected stage |
|---|---|---|
| Do six known direct sites use the differing condition bits? | No, verified from saved local control flow. | **Done:** direct-caller audit. |
| Can the mismatched bits leave those two callers? | Yes, verified return paths preserve live state. | **Done:** propagation identified. |
| Are all downstream observers excluded? | No; render/transform callees, outer returns, indirect callers and asynchronous state observers were not proved safe. | **Pending — runtime/integration qualification:** follow these specific boundaries, recording the next consumer or definite producer before return. |
| Is a game-facing replacement justified now? | No. This review does not prove full machine-state equivalence, and the original-register replacement adapter and broader ABI/input/FPU requirements remain separate. | **Not qualified — linking/runtime integration.** |

The follow-ups below cover the batch/copy cascade and named track-map callees; the remaining gate is outer-return/RPM ancestry and other unreviewed observers, rather than reopening those local helpers. If incoming status is saved, inspect the exact masks/uses to establish whether C0/C2/C3 matter; do not treat every status-word read as a semantic dependency. If an actual dependency exists, reproduce the required outgoing bits or explicitly redesign only an authorized interface. Do not silently discard the mismatch, and do not broaden this into unrelated scratchpad work or a game patch.

## Batch-helper follow-up across original and Modern baselines

Run [the bounded static audit](scripts/audit_line_boundary_batch_status.py). Its [manifest](evidence/audits/line-boundary-batch-status.json) independently pins supplied original, official Modern and local analysis EXEs and retains every decoded instruction plus raw bytes/hashes. All **297 bytes** in the following complete local bodies are identical across all three baselines:

| Helper range, end exclusive | Condition-bit boundary |
|---|---|
| `0049bcd0..0049bcee` (30 bytes) | Integer-only, no CALL. Normal return neither reads nor replaces incoming C0/C2/C3. |
| `0049bd30..0049bdbe` (142 bytes) | Integer-only locally; conditional call at `0049bd50` to `0049bdc0`. The direct no-removal path returns with the bits live. |
| `0049bdc0..0049be3d` (125 bytes) | Integer-only locally; scans index records and can return without another call. Matching-removal path calls `004ea4f0` at `0049be25`. |

The script checks every decoded mnemonic against the reviewed integer/control-flow set and asserts the exact direct-call target lists. These are local instruction/flow checks; the bodies with calls are not declared globally transparent. At this checkpoint the byte mover at **`004ea4f0`** was the conditional unresolved frontier. The subsequent follow-up below reviews its dispatcher and all three selected copy backends; this paragraph is not an additional outstanding byte-mover task.

This closes the first batch helper and narrows the second boundary instead of treating both as wholly unreviewed. It does **not** find an actual C-bit observer, establish that the bits are dead, or justify a game replacement. The no-removal/unsuccessful-search returns propagate incoming state to their callers; track-map transform calls, RPM ancestry, outer returns, indirect calls and asynchronous observers remain on their earlier terms. Integer EFLAGS and memory-output differences remain separate from x87 condition-bit liveness.

The original/Modern byte identity means these local helpers introduce no instruction-level difference in the compared pair. It does not erase the different ambient precision policy or prove identical scheduling/data. No instruction probe, compilation, C export/change, Ghidra write or game execution occurred.

## Copy cascade closes the local status-reader frontier

The same audit now extends through the complete dispatcher and every directly selected backend, reusing [existing x87 copy-core research](detailed-analysis-notes.md#shared-x87-copy-core-and-swapped-pointer-entry), the adjacent MMX/scalar contracts and current binary inspection. All **1076 additional bytes** below are identical in supplied original, official Modern and local analysis EXEs (1373 bytes including the three batch helpers):

| Range, end exclusive | Observed instructions and outgoing calls |
|---|---|
| `004ea4f0..004ea547` (87 bytes) | Overlap/direction and CPU-flag dispatch. Backward branch copies bytes locally; forward branches call exactly the three cores below. MMX return path executes EMMS at `004ea538`. |
| `00503281..005033e3` (354 bytes) | FILD/FISTP QWORD transfers, FXCH and integer prefix/tail/control code; no further CALL. |
| `005033e5..00503569` (388 bytes) | MMX MOVQ transfers and scalar prefix/tails; no internal EMMS and no further CALL. |
| `0050356d..00503664` (247 bytes) | Integer scalar copy instructions only; no further CALL. |

The dispatcher tests mutable flags `005643b4` then `005643ac` to select MMX or x87; the remaining forward branch is scalar. The audit checks the exact call target list and every decoded mnemonic in all seven retained bodies. **No explicit x87 status-word/environment reader, floating-point conditional move, comparison branch on incoming C0/C2/C3, or further unreviewed call appears inside this copy cascade.** This closes `004ea4f0` as a raw condition-bit-reader frontier for the inspected batch-removal path; it does not close the other outer/transform paths listed earlier.

Do not generalize the result to full floating-point transparency. The x87 backend performs integer loads/stores using temporary x87 registers and has stack-capacity/exception/rounding requirements; MMX aliases floating-point register state and the dispatcher performs EMMS afterward. Integer-only paths can propagate incoming condition bits, while x87/MMX paths are not proved to reproduce one common status/tag/stack output. The current audit does not classify an undefined or altered condition bit as a deterministic kill, validate all byte-count/overlap inputs, or qualify the reconstructed C function for game integration.

This resolves the specific local batch/copy boundary without executing it. The outstanding caller qualification is now the track-map calls `0048cb50`, `00477d90`, `0048cc60`, RPM ancestry, other outer returns/indirect callers and asynchronous observers. No new direct dependency on the reconstructed helper's differing C bits has been demonstrated, and no whole-game absence claim follows. The [manifest](evidence/audits/line-boundary-batch-status.json) retains opcode/address witnesses and all three baseline identities; no C, game, probe or Ghidra change occurred.

## Track-map local bodies and updated frontiers

The audit now additionally checks five complete bodies, **624 bytes identical across all three baselines**. Total retained byte identity for this bounded caller follow-up is1997, not a count of changed game code or a completion percentage.

| Range, end exclusive | Local finding / next boundary |
|---|---|
| `0048cb50..0048cc60` (272 bytes) | Call-free indexed HUD point transform. FLD/arithmetic/FXCH/FSTP plus integer operations; no explicit status/environment read or condition-bit test. |
| `0048cc60..0048cce8` (136 bytes) | Centered rectangle preparation; local arithmetic/stores do not read condition bits. Calls `00487620` at `0048ccd9`, which remains a frontier. |
| `00477d90..00477df0` (96 bytes) | Integer pose-interpolation wrapper. Inactive path returns0 without an x87 operation. Active path calls `00477a10` twice then `00477990`. |
| `00477a10..00477a42` (50 bytes) | Integer-only, call-free sample-pointer lookup; neither reads nor replaces x87 condition bits on normal return. |
| `00477990..004779d6` (70 bytes) | Integer/local-address setup, then calls `00477850` twice, `004b6a30` and `004b6ca0`; those implementations remain frontiers. |

The HUD transform performs arithmetic under its incoming control state, so its byte identity does not establish numerical equivalence under original/Modern precision policies. Nor are arithmetic instructions treated as guaranteed C0/C2/C3 kills merely because no explicit reader appears. The inactive pose path and pointer lookup simply propagate the tracked bits; active-path conclusions stop at the listed unreviewed calls.

**Targets at that checkpoint:** rectangle submission `00487620`, pose unpacking `00477850`, interpolation/matrix targets `004b6a30` and `004b6ca0`. The subsequent follow-up resolves those local boundaries; RPM ancestry and outer-return/indirect/asynchronous boundaries remain. This replaces the former blanket uncertainty for `0048cb50`, `00477d90` and `0048cc60` with inspected local contracts. No actual incoming-C-bit consumer or whole-game absence has been proved by this extension.

Manifest schema2 stores each identical body's raw bytes, disassembly and call list **once** in `canonical_bodies`, with separate byte/hash references under each of the three pinned baselines. The script still independently reads and decodes every baseline and asserts complete body equality; this avoids triplicating identical instruction records without replacing evidence with a claim. No C, probe, target execution or Ghidra change occurred.

## Named track-map callees: integer leaves and fresh comparison

The next extension resolves the four specific targets from the preceding checkpoint. The audit adds **711 identical bytes** in three complete call-free integer routines, plus a **43-byte identical entry prefix**, across original, official Modern and local analysis EXEs. Total retained scope is2751 bytes. Exact opcode sets, no-call assertions and the prefix ordering proof are in the same manifest.

| Range, end exclusive | Condition-bit finding |
|---|---|
| `00477850..004778c0` (112 bytes) | Relative-position unpacking with integer shifts/adds and MOVSD copies; no status read, x87 instruction or outgoing CALL. |
| `004b6a30..004b6ba6` (374 bytes) | Packed interpolation via integer multiplication/carry/shifts and stores; no x87/MMX instruction or outgoing CALL. |
| `004b6ca0..004b6d81` (225 bytes) | Fixed rotation-matrix construction via integer arithmetic; no x87/MMX instruction or outgoing CALL. |
| `00487620..0048764b` (43-byte prefix only) | Straight-line entry reaches fresh FCOMP at `00487646`, then first FNSTSW at `00487648` and SAHF at `0048764a`. No earlier branch, CALL or status/environment read occurs in this prefix. |

Under the admitted normal, non-faulting x87 contract, that **FCOMP defines fresh C0/C2/C3 before the status reader**. The rectangle submitter therefore does not read the line helper's incoming values at its first status test. Later branches/callees can use the new comparison results, but need not be analysed as observers of these particular earlier bits solely because a later FNSTSW exists. This is an entry-dominance argument about three tracked condition bits, not a declaration that the whole1025-byte rectangle submitter has been qualified.

The three integer leaves preserve live x87 condition bits on normal return; they do not make the bits dead. Their enclosing pose wrappers were already locally checked, so the named active/inactive pose paths no longer stop at anonymous interpolation calls. Liveness may still propagate back to the enclosing track-map routine and its callers. Pending exception handling, x87 stack/tag/C1/other status state, arbitrary inputs, indirect entry into a body and asynchronous observers remain outside this argument.

**Updated stopping point:** no incoming-C0/C2/C3 reader has been identified along the reviewed local batch/copy/track-map branches. The remaining qualification is outer track-map return/call ordering, RPM ancestry and unreviewed indirect/asynchronous observers, together with the reconstructed function's full ABI/memory/FPU contract. Do not describe resolved local targets as still pending, or turn their resolution into whole-game machine equivalence. No runtime probe or game run occurred.
