# Original versus Modern: input-worker lifecycle

## Evidence and correspondence

The original callback is **`0042dc20..0042dc40`**, selected by original startup at **`004b6200`**, followed by thread-creation call `004b6205`. Modern startup instead supplies callback **`0041d7e4..0041d813`** at `004b5d55`, with creation call `004b5d5a`. Both use descriptor **`007a3aac`**. Original `0041d7e4` lies inside the [parameter-preset implementation](original-modern-parameter-preset.md); a same-address comparison would falsely pair unrelated code.

Modern **`0042dc20..0042dc3c`** is now a shutdown helper, not the original callback. Reproduce the static comparison with `python3 analysis/scripts/audit_input_worker_difference.py`; the [manifest](evidence/audits/original-modern-input-worker.json) retains baseline hashes, callback/startup/shutdown witnesses, primitive wrappers and each executable’s actual import mapping. No target code or scheduling test was run. Existing [worker research](detailed-analysis-notes.md) describes the Modern descriptor publication ordering and unresolved readiness handshake.

## Worker loop changes

Both create an unnamed, auto-reset, initially nonsignaled event through **`004dfb00`**, store its handle in **`005efdf0`**, wait through **`004dfb70`**, and call collector **`0048f550`**. The wrapper import mappings identify `CreateEventA`, `WaitForMultipleObjectsEx`, `SetEvent`, `CloseHandle` and `TerminateThread` separately in both binaries.

| Operation | Original callback | Modern callback |
|---|---|---|
| Handle used for each wait | Reload global `005efdf0` | Local EBX saved from event creation |
| After wait | Always call collector | Test descriptor DWORD0 at `007a3aac` |
| Nonzero sentinel | No sentinel check | Call collector, repeat wait |
| Zero sentinel | No cooperative exit | Close local event, return EAX=0 |

The original normal loop unconditionally jumps back; its trailing epilogue is not reached through that loop. Modern checks the sentinel **after waking**, so clearing it alone is insufficient to release a successfully blocked wait. Event-creation and wait results are not tested before proceeding. A persistent failure can therefore permit repeated collection while the sentinel stays nonzero; this is a conditional code-path observation, not a reproduced failure.

The collection routine itself is not established equivalent by this lifecycle comparison. Neither version’s loop proves a fixed sampling frequency, determinism, or multiplayer/replay compatibility.

## Shutdown changes and remaining synchronization limit

Original shutdown supplies descriptor pointer `007a3aac` to **`004df870`** at **`004b6274`**. The retained ordinary nonnull/non−1 descriptor path dereferences its first DWORD, calls **`TerminateThread(handle,0)`**, then **`CloseHandle(handle)`**. This wrapper prefix does not signal or close the callback-created event. Its diagnostic branches and all exceptional shutdown routes remain outside the retained prefix; no universal leak claim is made.

Modern shutdown calls new helper **`0042dc20`** at **`004b5d98`**. That helper:

1. Calls `004dfc00`/`CloseHandle` with the stored thread handle.
2. Clears descriptor DWORD0 at `007a3aac`.
3. Loads global event handle `005efdf0` and signals it through `004dfb30`/`SetEvent`.

After the wake, the worker can observe zero, close its locally retained event handle and return. Closing the thread handle is **not a join**: this helper contains no wait for worker termination, no ready handshake, and no checks of close/signal results. Startup/shutdown timing and global-event publication remain material unknowns. If another component still uses the global event after the worker closes it, the stale global value would require lifecycle analysis; no such execution is asserted here.

The ordinary signal-entry **`0042dc40..0042dc57`** continues to load event handle `005efdf0` into EDX and call `004dfb20`, whose path forwards EDX to `SetEvent`. Full caller ordering, thread creation failure handling, descriptor reuse, shutdown completion and collector reentrancy require follow-up.

This is a confirmed static lifecycle change from forced worker termination to a cooperative sentinel-and-event exit route. It is not proof that every shutdown race is solved, that the game no longer uses forced termination elsewhere, or that input behavior is otherwise unchanged.

## Collector body and initial callback table are retained

The expanded audit compares complete **`0048f550..0048f69a`**,330 bytes, and finds it byte-identical. Both end with the same register-restoring epilogue and RET. The file-backed six-entry callback table at **`00554e34`** is also identical: `004318b0`, `00431740`, `004316c0`, `004316f0`, `004317d0`, `00431800`. This proves equality of these initial pointer values, not the complete pointed-to bodies, all later table writes or valid binding indices.

The retained collector invokes indirect callbacks selected by sign-extending the low byte of each binding DWORD, while passing the complete binding in EAX. No local bound check establishes that arbitrary low-byte values index those six entries safely. It writes packed per-player input bytes starting at **`0079c338`**; session value `006fd3b0==1` takes a two-player loop, while the other local route collects one. It also assembles32 action bits, increments DWORD **`0079c4ac`**, stores the mask in **`0079c2b8 + 4*(counter & 31)`**, then calls **`0048fa10`**. The raw shift/subtract and byte truncation operations are retained; they must not be replaced by assumptions about signed-C overflow or saturation.

Thus no collector-body rewrite is identified in this pair. This does not establish equivalent device results: called helpers, callback bodies, bindings, globals, concurrent updates and sampling time can differ. The lifecycle delta remains independently meaningful, and neither unchanged local instructions nor the initial callback table proves replay/network determinism. Follow-up should compare callback bodies and their device/backend dependencies before claiming unchanged input semantics.

## Initial callback implementations and immediate dispatch

The expanded audit verifies byte equality for these saved function ranges in both executables (ends exclusive):

| Entry / ranges | Existing analysis name |
|---|---|
| `004315a0..00431686` | RefreshJoystickSamplesAndSyntheticKeyMask |
| `004316c0..004316f0` | EvaluateJoystickRawButtonBinding |
| `004316f0..00431732` | EvaluateJoystickPovDirectionBinding |
| `00431740..004317c3` | EvaluateJoystickAxisRangeBinding |
| `004317d0..004317fd` | EvaluateKeyboardBindingAndClearAuxiliaryKey |
| `00431800..00431885`, `0043188d..004318b0` | EvaluateDigitalPackedControlBinding |
| `004318b0..004318b7` | EvaluateUnassignedBindingAsZero |
| `0048fa10..0048fa97` | DispatchCollectedPlayerInputs |

These names are existing research labels, not additional proof of device semantics. The two digital-binding ranges are recorded separately; bytes in the intervening gap are excluded, rather than silently counted as that function’s instructions. Each range has its own paired hash and disassembly capture in the manifest.

The immediate dispatcher’s retained branches are also concrete. Signed `006fd3a0 > 1` tests `007d36a0` and `007d36a8`, then increments `00560104` only when both are zero. On the other route, nonzero `00560108` returns immediately. Otherwise session `006fd3b0==1` submits player0’s four-byte buffer at `0079c338` to `004c6530` and submits player1’s buffer at `0079c33c` only if the first call returns nonzero. Session0 submits the first buffer using index `006fd4f4`; other session values pass it to `004c60c0`. Queue routines, state meanings and delivery timing are not established by these branches alone.

This resolves the earlier specific unknown about equality of the initial callback instruction ranges: no changes were found there. Remaining input questions are transitive device/backend implementations, later pointer-table writes, binding/global initialization, queue consumers, timing and concurrency. It would be incorrect to relabel all input behavior as unchanged or infer original/Modern multiplayer compatibility from these retained ranges.
