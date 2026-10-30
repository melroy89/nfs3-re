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
- **Tinted-triangle clipping `00487a30`:** after clipper call `00487c2d`, the next call `00487c40` immediately enters a fresh compare; after that, `00487c52` does likewise. After the third clipper returns, there is no further local status read. Paths may return at `00487fd6`/`00488025`, or invoke `QueueTintedQuad` (`00486f70`) / `AppendTintedTriangleToBatch` (`004870c0`). Those two emitters do not locally read status, but call unreviewed `0049bcd0` and `0049bd30`. They must not be treated as proven transparent solely because their own visible stores are ordinary vertex data.
- **Track-map ancestor `0048d4c0`:** post-line-append paths from `0048dd78`, `0048def2`, `0048e0ea` reach calls including `0048cb50`, `00477d90`, `0048cc60`, or another line-append call before a guaranteed local status overwrite. Those calls are unresolved boundaries in this pass. Later own comparisons at `0048e568` and beyond do not prove that no earlier callee observed the live bits.
- **RPM-needle ancestor `00489e00`:** after tinted-triangle call `0048a206`, it reaches `RET` at `0048a214` without a new local status read or comparison. The caller of this outer function remains a propagation boundary.

These are real limits of the reviewed scope, not evidence that a caller actually depends on the bits. No raw status read of helper-produced C0/C2/C3 was found in the locally traced paths; a positive dependency or whole-game absence claim would require following the unresolved boundaries.

## Decision and next gate

| Question | Finding / confidence | Status and affected stage |
|---|---|---|
| Do six known direct sites use the differing condition bits? | No, verified from saved local control flow. | **Done:** direct-caller audit. |
| Can the mismatched bits leave those two callers? | Yes, verified return paths preserve live state. | **Done:** propagation identified. |
| Are all downstream observers excluded? | No; render/transform callees, outer returns, indirect callers and asynchronous state observers were not proved safe. | **Pending — runtime/integration qualification:** follow these specific boundaries, recording the next consumer or definite producer before return. |
| Is a game-facing replacement justified now? | No. This review does not prove full machine-state equivalence, and the original-register replacement adapter and broader ABI/input/FPU requirements remain separate. | **Not qualified — linking/runtime integration.** |

The next bounded investigation can inspect the first unresolved batch helpers `0049bcd0`/`0049bd30` and the identified outer return/transform paths. If incoming status is saved, inspect the exact masks/uses to establish whether C0/C2/C3 matter; do not treat every status-word read as a semantic dependency. If an actual dependency exists, reproduce the required outgoing bits or explicitly redesign only an authorized interface. Do not silently discard the mismatch, and do not broaden this into unrelated scratchpad work or a game patch.
