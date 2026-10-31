# Original versus Modern: race initialization call sequences

The [audit](evidence/audits/race-initialization-difference.json), reproduced by `python3 analysis/scripts/audit_race_initialization_difference.py`, captures complete setup counterparts **original`004c45f0..004c4733`**, **Modern`004c45f0..004c471a`**, and reset counterparts **`004c4740..004c481d`** in both binaries. Ends are exclusive. Exact baseline hashes, all direct CALL sites/targets and original no-op bodies are retained. No race or instruction execution.

## Initialization removes placeholder calls

Modern removes calls to original targets **`00404660`**, **`00401220`**, **`0040c150`**, **`00408ad0`**, **`00404c40`**. Four are five-byte PUSH EBP / MOV EBP,ESP / POP EBP / RET stubs. The first is a wrapper that calls another such stub,`00404650`, then returns. Thus these deleted calls do not establish removal of five substantive simulation algorithms.

After filtering those five targets from the original sequence, the complete direct-call target order equals Modern's. Modern shortens the body by25 bytes and adjusts the conditional skip-to-epilogue branch accordingly. Earlier global writes and retained calls remain present; their callees can differ independently. Removed CALL/prologue/epilogue instructions still alter transient stack writes and execution time, so this is not a full machine-state-equivalence claim.

## Reset adds calls as well as removing placeholders

Modern removes original no-op calls to **`00401230`**, **`0040c140`**, **`00408ae0`**, **`00404650`**, **`00405fb0`**. It adds calls to **`004c7130`**, **`004dbbc0`**, **`004cb6f0`**, **`0047b350`**, **`004dcdf0`**, and changes the later target **`004bc8b0`→`004bc530`**. The exact retained-call order is checked after accounting for those edits.

Unlike the removed original stubs, the five new targets have substantive bodies; they must not be dismissed as equivalent placeholders or treated as proven new physics features from these addresses alone. Their complete effects, initialization ordering dependencies and the changed final target's correspondence remain explicit follow-up work. The paired wrapper bodies establish where those calls enter the race setup sequence, not whether every callee is new, relocated or changed from another original route.

This closes the wrapper-level comparison and prevents its36 changed bytes in each saved function from being misread as a physics formula rewrite. For reconstruction, preserve version-specific call ordering until the named callee effects are established. Runtime race startup, simulation equivalence and multiplayer/replay compatibility remain unverified.
