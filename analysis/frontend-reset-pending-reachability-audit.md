# Frontend reset pending-request reachability audit

## Scope and result

Static inspection of the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) examined all direct references to `ResetFrontendObjectResourceLoadState` (`00467ac0`), the frontend service/selection gates, and its initialization and teardown blocks. The exact artifact was analyzed in an ephemeral REA/Ghidra session; no executable, runtime, or persistent Ghidra state was changed.

**Result:** normal selection-change servicing is gated against restarting while the loader active byte is set, and the observed loader failure resets occur after the current submit reports failure. However, separate initialization and teardown callback bodies reset and free nested loader state without checking the active byte or request IDs. Their lifecycle dispatch sites and concurrency/serialization contract could not be resolved from the inspected references. Thus static evidence does not prove either a pending-request reset path or complete serialization.

## Reset callsite inventory

REA xrefs to `00467ac0` returned eight direct instruction sites (`ev_2f76a91280d4bc83c172e5b3701dac389464c76003a29b20cecae2630663034f`):

| Callsite | Context | State at reset / finding |
|---|---|---|
| `00467c61` | Selection/name preparation helper `00467c40`, called from loader service phase 1 | Reset precedes preparation of archive/member names. The normal service only reaches phase 1 after starting from its initial request state; preceding phases poll/consume request completions before moving to later submissions. |
| `00468904`, `00468954`, `004689a8`, `004689fc`, `00468a50` | Failure exits in loader service `00468860` | Each follows a read-submission failure branch. These are zero-return submit failures, not evidence that a nonzero request remains outstanding. The request-6 failure path has a distinct no-reset exit. |
| `004677a5` | Initialization/reinitialization block beginning `00467700` | The block first clears outer `+0xb1` active, initializes state fields, and then, when nested `+0xb8` is nonnull, resets it and frees it. No request-ID or phase check is present. |
| `0046796a` | Teardown block beginning `00467930` | After a guard, clears outer `+0x88` and flag bit 2, then, if nested `+0xb8` is nonnull, resets and immediately frees it. No request-ID, phase, or active-byte check is present. |

The lifecycle blocks call `0044a660` before proceeding. Its body (`ev_390447fab00cd125cfbd7a906d11f68df05a27908371c21e423bf4b1de2685b5`) returns allowed when global `00559234` is zero, or when outer flag bit `+5 & 8` is clear; it returns blocked only when the global is nonzero and that outer bit is set. It does not inspect loader activity or request state. This gate therefore does not establish pending-request serialization.

## Concrete selection-change gate

`UpdateTimedFrontendSelectionChangeFlags` (`00468670`) compares a mode-specific selected item against cached outer `+0x9c`. On a change, if outer byte `+0xb1` is nonzero, it returns without scheduling a new request. Otherwise it sets `+0xb0`. The common scheduling path then requires outer `+0xb2 != 0`, `+0xb0 != 0`, and `+0xb1 == 0`; it sets `+0xb1=1`, clears `+0xb0`, and writes nested request phase `+0x198=1`.

The regular frontend service (`00468860`) calls this helper and proceeds into loader dispatch only when `+0xb1` is nonzero. This provides a concrete guard against a rapid menu-selection change re-entering phase 1 while the same outer context is marked active. It does not show that teardown/reinitialization cannot execute from another lifecycle path or thread.

The setup block at `0046785e` repeatedly calls the loader while `+0xb1` is active, loader return is nonzero, and nested completion phase `+0x19c != 8`. That is synchronous state polling in this caller, not a worker join. Its observed loop does not execute ordinary event handling internally. Whether another callback can run concurrently or re-enter is unresolved.

## Lifecycle entry gap

The byte range at `00467700` initializes outer state, then checks nested `+0xb8`, calls reset, frees the nested object, and clears `+0xb8`; `00467930` is a teardown block with the analogous reset/free sequence. Neither block is represented as a Ghidra procedure, so ordinary procedure-caller analysis does not recover their invokers.

Exact pointer bytes at `00557390` (`ev_2b5a38bc006f0a58fd01d00976e7f75d37204698458b5e7bf69ad9f896e93458`) contain `00467700` at slot `00557398` and `00467930` at `0055739c`. Xrefs to each code address point to its respective table slot (`ev_f97bac3aa0638c63bf672ac9576a16523184b777fb7d753be23eef2e31c6740a`, `ev_0feee1e5d2ed20df33c580c26022adc43083dabbefde6c27e6f06553f0e71ff3`). Xrefs on the table slots themselves yielded no additional caller locations. This supports callback-table membership, but does not identify the table consumer, lifecycle event, thread, or whether dispatch is excluded while loader state is active.

Accordingly, there is **no statically demonstrated scenario** of “menu changes rapidly, then reset frees a buffer while its request is pending.” The menu-change route itself blocks new loader scheduling while active. The plausible unresolved route is an initialization/reinitialization or teardown callback dispatched while a nested object still has a nonzero request ID. Existing bytes show these callbacks reset/free without checking those IDs, but do not establish that such dispatch can overlap an active operation.

## Read/worker qualification

The worker-ordering audit has been corrected: the read helper calls `ReadFile` with a NULL `OVERLAPPED` argument, and on error 997 calls `SleepEx(1, TRUE)` then retries `ReadFile`; it does not call `GetOverlappedResult`. The supported narrow statement is that the single worker remains in the current helper before dequeuing another job. Do not infer guaranteed OS I/O completion on unusual pending/abort/error paths from that ordering alone. This correction does not change the frontend reachability gap above.

## Evidence boundary and next discriminator

**Established:** normal selection updates do not schedule phase 1 when outer `+0xb1` is set; loader submission failures call reset after a zero submission result; the two lifecycle callback bodies reset and free nested state without checking active/request fields; each lifecycle block is stored as a callback-table entry.

**Not established:** what consumes the callback table; whether those callbacks are same-thread, serialized, or permitted during a loader operation; whether a live nested request ID can coexist with invocation of either callback; whether an unusual read-helper error leaves OS I/O referencing the released destination.

The precise next static discriminator is the code that reads/dispatches table `00557398/0055739c`, followed through its event/phase gate and caller context. If that path does not encode exclusion, a passive runtime trace would need to correlate, for the same nested object, callback entry, outer `+0xb1`, phase `+0x198/+0x19c`, request IDs `+0x160/+0x164/+0x170`, worker helper entry/return, and reset/free. This bounded static pass did not execute the game or collect such a trace.
