# Original versus Modern: race initialization call sequences

The [audit](evidence/audits/race-initialization-difference.json), reproduced by `python3 analysis/scripts/audit_race_initialization_difference.py`, captures complete setup counterparts **original`004c45f0..004c4733`**, **Modern`004c45f0..004c471a`**, and reset counterparts **`004c4740..004c481d`** in both binaries. Ends are exclusive. Exact baseline hashes, all direct CALL sites/targets and original no-op bodies are retained. No race or instruction execution.

## Initialization removes placeholder calls

Modern removes calls to original targets **`00404660`**, **`00401220`**, **`0040c150`**, **`00408ad0`**, **`00404c40`**. Four are five-byte PUSH EBP / MOV EBP,ESP / POP EBP / RET stubs. The first is a wrapper that calls another such stub,`00404650`, then returns. Thus these deleted calls do not establish removal of five substantive simulation algorithms.

After filtering those five targets from the original sequence, the complete direct-call target order equals Modern's. Modern shortens the body by25 bytes and adjusts the conditional skip-to-epilogue branch accordingly. Earlier global writes and retained calls remain present; their callees can differ independently. Removed CALL/prologue/epilogue instructions still alter transient stack writes and execution time, so this is not a full machine-state-equivalence claim.

## Reset adds calls as well as removing placeholders

Modern removes original no-op calls to **`00401230`**, **`0040c140`**, **`00408ae0`**, **`00404650`**, **`00405fb0`**. It adds calls to **`004c7130`**, **`004dbbc0`**, **`004cb6f0`**, **`0047b350`**, **`004dcdf0`**, and changes the later target **`004bc8b0`→`004bc530`**. The exact retained-call order is checked after accounting for those edits.

Unlike the removed original stubs, the five new targets have substantive bodies; they must not be dismissed as equivalent placeholders or treated as proven new physics features from these addresses alone. The follow-ups below resolve retained bodies and wrapper-expanded order; transitive state effects remain outside this comparison. The paired wrapper bodies establish where those calls enter the race setup sequence, not whether every callee is new, relocated or changed from another original route.

This closes the wrapper-level comparison and prevents its36 changed bytes in each saved function from being misread as a physics formula rewrite. For reconstruction, preserve version-specific call ordering until the named callee effects are established. Runtime race startup, simulation equivalence and multiplayer/replay compatibility remain unverified.

## Added reset calls target retained original implementations

The audit now captures all five target bodies and asserts byte identity across the supplied original and official Modern (**1,161 bytes total**). They are newly called **at this wrapper location**, not functions newly introduced by Modern:

| Target | Complete bytes | Observed local work |
|---|---:|---|
| `004c7130..004c7149` | 25 | Call`004c7150`, then`004c70f0`; copy global`007d3684` to`007d5750` |
| `004dbbc0..004dbbd6` | 22 | Pass destination`008b7ba0`, byte count`0d00h` to zero-fill entry`004e070c` |
| `004cb6f0..004cb723` | 51 | Zero-fill`12c00h` bytes at`007ddfd0`, `6400h` bytes at`007f0bd0`; clear globals`007f6fd0/4` |
| `0047b350..0047b37a` | 42 | Copy`007d3684` to`0055d154`, call`00494360`, then store the zero-state EDX into three environment globals |
| `004dcdf0..004dd1ed` | 1,021 | Initial calls clear blocks`008ca22c/5ch`, `008c0be8/4b00h`, `008c08c0/320h`; subsequent configuration-dependent state construction remains outside this summary |

Ends are exclusive. The zero-fill entry clears EBX then invokes shared fill code; its entry witness is retained. Function labels for spatial/effect/weather roles come from existing analysis and do not establish full layout or every semantic effect. The `00494360` register contract and other transitive callees remain dependencies rather than being assumed harmless.

The direct difference is therefore **reset sequencing of retained state-management routines**. These bytes do not show a new physics formula. Equally, unchanged callee code does not make the new invocation irrelevant: timing/order, globals and initialized data can change subsequent behaviour. Their other original callers have not been inventoried here. The later changed target`004bc8b0`→`004bc530` is resolved in the follow-ups below. No reset or zero-fill code was executed.

## Final-target resolution: bypassed wrapper and hoisted calls

The final CALL change **`004bc8b0`→`004bc530`** is not a moved-body counterpart. Complete original`004bc8b0..004bc8dd` is a wrapper with these direct targets in order:

`00434ae0`, `00421480`, `004c7130`, `004dbbc0`, `004cb6f0`, `0047b390`, `004dcd10`, `004bc530`.

Complete final callee **`004bc530..004bc559` (41 bytes)** exists in both binaries and is byte-identical. It clears`0055fe3c`, supplies output-cell pointers`007a3d00`, `007a3cf8`, `007a3cfc` with ECX0 to`00435310`, and restores its saved frame. Complete meaning of those cells and its callee remain external dependencies.

A one-level comparison of this route therefore establishes:

| Original nested route | Modern direct route | Interpretation |
|---|---|---|
| `004c7130`, `004dbbc0`, `004cb6f0` inside wrapper | Same targets now called by race reset | Hoisted retained calls, not three extra implementations |
| `0047b390`, `004dcd10` | `0047b350`, `004dcdf0` | One-call environment/weather wrapper bypass, verified below |
| Wrapper-prefix `00434ae0`, `00421480` | No corresponding direct calls on this compared route | Locally bypassed original no-op leaves, verified below |
| Wrapper ends by calling`004bc530` | Race reset directly calls`004bc530` | Unchanged final callee reached without the wrapper |

This refines the earlier direct-call inventory: “five added calls” described the outer wrapper’s instruction list, **not five net additional operations after expanding original nested calls**. Three are relocation of invocation level; two use different targets. Preserve this distinction in any reconstruction plan or patch summary. The final follow-up resolves skipped-prefix bodies and target wrappers; timing and transitive effects still prevent a complete runtime-equivalence claim. No initializer or target instructions were executed.

## Wrapper expansion closes the remaining target questions

The final two old targets are now fully inspected: **`0047b390..0047b39a`** simply calls`0047b350` between EBP save/restore; **`004dcd10..004dcd1a`** likewise calls`004dcdf0`. Original wrapper-prefix entries **`00434ae0..00434ae5`** and **`00421480..00421485`** are five-byte no-op leaves. The audit retains these complete original bodies and verifies their call targets.

After removing original no-op leaves and expanding those original one-call wrappers plus`004bc8b0`, the **entire substantive direct-target sequence equals Modern’s**. Additionally, masking CALL displacements makes the full221-byte reset-wrapper bodies byte-identical: no additional non-CALL operand/arithmetic/global-store change remains in that wrapper. The earlier outer-level “added calls” and two “changed environment/weather targets” are therefore resolved as **invocation hoisting and wrapper bypass**, not net added reset operations.

This closes the bounded local call-tree comparison for these two initialization/reset wrappers. It does not establish transitive behaviour equality: retained callees may encounter different inputs, global initialization, resources or floating-point state. Removing stack frames changes transient stack memory and timing even where substantive target order is retained. Preserve original register/flag assumptions and choose explicitly whether reconstruction models logical effects or exact machine state. No initializer was run and no whole-simulation equivalence is claimed.
