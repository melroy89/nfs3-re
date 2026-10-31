# Original versus Modern: race initialization call sequences

The [audit](evidence/audits/race-initialization-difference.json), reproduced by `python3 analysis/scripts/audit_race_initialization_difference.py`, captures complete setup counterparts **original`004c45f0..004c4733`**, **Modern`004c45f0..004c471a`**, and reset counterparts **`004c4740..004c481d`** in both binaries. Ends are exclusive. Exact baseline hashes, all direct CALL sites/targets and original no-op bodies are retained. No race or instruction execution.

## Initialization removes placeholder calls

Modern removes calls to original targets **`00404660`**, **`00401220`**, **`0040c150`**, **`00408ad0`**, **`00404c40`**. Four are five-byte PUSH EBP / MOV EBP,ESP / POP EBP / RET stubs. The first is a wrapper that calls another such stub,`00404650`, then returns. Thus these deleted calls do not establish removal of five substantive simulation algorithms.

After filtering those five targets from the original sequence, the complete direct-call target order equals Modern's. Modern shortens the body by25 bytes and adjusts the conditional skip-to-epilogue branch accordingly. Earlier global writes and retained calls remain present; their callees can differ independently. Removed CALL/prologue/epilogue instructions still alter transient stack writes and execution time, so this is not a full machine-state-equivalence claim.

## Reset adds calls as well as removing placeholders

Modern removes original no-op calls to **`00401230`**, **`0040c140`**, **`00408ae0`**, **`00404650`**, **`00405fb0`**. It adds calls to **`004c7130`**, **`004dbbc0`**, **`004cb6f0`**, **`0047b350`**, **`004dcdf0`**, and changes the later target **`004bc8b0`→`004bc530`**. The exact retained-call order is checked after accounting for those edits.

Unlike the removed original stubs, the five new targets have substantive bodies; they must not be dismissed as equivalent placeholders or treated as proven new physics features from these addresses alone. Their complete effects, initialization ordering dependencies and the changed final target's correspondence remain explicit follow-up work. The paired wrapper bodies establish where those calls enter the race setup sequence, not whether every callee is new, relocated or changed from another original route.

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

The direct difference is therefore **reset sequencing of retained state-management routines**. These bytes do not show a new physics formula. Equally, unchanged callee code does not make the new invocation irrelevant: timing/order, globals and initialized data can change subsequent behaviour. Their other original callers have not been inventoried here. The later changed target`004bc8b0`→`004bc530` still needs its own counterpart check. No reset or zero-fill code was executed.
