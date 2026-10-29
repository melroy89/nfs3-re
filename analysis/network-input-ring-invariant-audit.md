# Multiplayer input-ring invariant and signed-counter boundaries

> **Deferred draft:** preserved with the final session checkpoint. Not reviewed or qualified as completed in the current research pass.

## Scope and target

This audit follows the eight-row input sample/ready rings, their signed absolute sequence counters, lead throttle and remote correction, and the reset path at race-session entry. It uses static REA against the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) and the retained Issue #1 findings in [detailed-analysis-notes.md](detailed-analysis-notes.md#remote-participant-input-lead-correction-preserves-the-occupied-window). No game execution or executable/persistent Ghidra changes were made.

## Ring layout and reset

- Samples start at `007d3714`; ready DWORDs start at `007d4714`. There are eight rows with `0x200`-byte stride, each holding 128 four-byte samples and 128 ready entries. Both address paths select a slot with `sequence & 0x7f`.
- Producer counters are signed `int[8]` at `007d5718`; the shared signed consumer counter is at `007d5714`. These are full 32-bit counters, distinct from their modulo-128 slot indices and the compact type-6 lead byte.
- `ResetAndSynchronizeInputRings` (`004c63f0`) runs only when playback selector `006fd3a0 <= 1`. It initializes each row's ready slots 0..3, clears the remaining readiness and sample storage, sets each row producer to4, then sets consumer0 and latest-available input sequence3. It also enters/leaves synchronization and related setup helpers.
- For playback selector `>=2`, the reset routine returns early after clearing `g_nLatestAvailableInputSequence` (`00560104`) only. Producer counters, consumer, and ready flags are left as they were at entry.
- Its only direct caller is `RunRaceSession` (`004a3690`), at `004a37de` immediately before `RunRaceLoop`. The call is inside the session's loop, so a return that leaves loop-control `007d3698` set reaches reset again on the next session-loop pass. There is no periodic rebase during one uninterrupted race loop. The playback early-return makes that reset cadence inapplicable to selector values `>=2`.

## All traced mutations and admission gates

The producer-counter direct reference list has 23 instruction sites; the consumer list has eight. Inspection in the Issue #1 pass classified producer mutations as follows:

1. **Reset:** all rows receive producer4; consumer is set0.
2. **Regular append** (`AppendParticipantInputSample`, `004c6530`): first calls `ShouldDeferParticipantInput`; on a non-deferred path it requires the current producer slot's ready value to be clear, copies one sample, sets ready, and increments that row's producer by1. A deferred or already-ready slot returns without appending. Session-mode branches also update the separate latest-available scheduler value.
3. **Remote lead-corrected append** (`AppendRemoteInputSampleWithLeadCorrection`, `004c66a0`): calls the same throttle, requires the producer slot ready flag clear, and may decrement the row producer temporarily during the shift. It then restores the original producer value after replacing/compacting sample contents; net producer change for this helper is zero. If it does not take the correction branch, it writes/marks the producer slot and increments the producer by1.
4. **Frame fallback** (`BuildNetworkInputFrameWithFallback`, `004c6870`): after the local row append, fills a missing per-row frame slot from that row's preceding sample, sets the ready flag, and increments that row producer when the target slot is not ready. The routine's shared target slot presumes participant rows are aligned with the host frame sequence; it does not validate that premise.
5. **Consumption** (`ConsumeParticipantInputSequence`, `004c67a0`): for playback selector below2, copies the requested `sequence & 127` slot to current samples on rows selected by `006fd50c`, clears that sequence's ready flag for every configured human row, then increments the common consumer once. It has no local “slot is ready” test before copying/clearing.

No other producer/consumer counter writes were found in the direct xref inventory. This is a bounded in-image direct-reference result; pointer aliases, unusual bulk writes, unsynchronized execution and later runtime state are outside the proof.

The throttle (`ShouldDeferParticipantInput`, `004c6ae0`) uses signed comparisons and mode-specific gates:

- Session mode0 defers when `C + sharedLimit <= P0` for any requested row. Mode1 applies this same condition only to row0.
- In modes2..4 with cross-path flag `006fd50c != 0`, the relevant compare is followed by the false return: that branch does not defer.
- With that flag clear, transport/role branches either defer selected rows during synchronization, or use signed producer/consumer limits. In one branch it compares `C + participantLimit` against `P[row]`, then compares `C + sharedLimit` against signed `min(P0,P1)`. In the other, row0 uses the shared-limit test. The limits are sequence leads, not established time units. Exact enum-to-user-facing mode meanings remain unresolved.

In `AppendRemoteInputSampleWithLeadCorrection`, with `P=P[row]`, `B=P0`, and tolerance `T`, the correction gate is the strict signed test `P > B + T`. On that path it temporarily stores `P-1`, copies source samples for signed sequence values `s` in `[B,P-1)` from `(s+1)&127` to `s&127`, writes the incoming sample at `(P-1)&127`, sets readiness there, and increments the temporary producer back to `P`. Under the contiguous-window conditions below, this replaces the tail-side span while retaining the occupied ready interval. The adjusted slot is not independently re-admitted after the shift; the original ready check and invariant must suffice.

## Sufficient contiguous-window invariant

For each row `r`, let `C` be the current consumer and `P[r]` its producer, interpreted as signed linear counters **before any signed wrap**. A sufficient ring invariant is:

1. `0 <= P[r] - C <= 128` for every active row, with the subtraction understood in a wider mathematical domain rather than machine `int` arithmetic.
2. For every sequence `s` in `[C, P[r])`, ready slot `(s & 127)` is set and contains the sample for that sequence; slots for sequences outside that interval are clear (except at the reset instant, where the stated interval is exactly `[0,4)`).
3. Producers append only at `P[r]` after confirming its ready slot is clear; consumers advance `C` only when the requested sequence is valid/ready for all rows they will consume; the producer and consumer operations are serialized or otherwise coordinated so those checks cannot race with their writes/clears.
4. No active row's producer or the consumer crosses a signed 32-bit boundary, and the signed additions used for lead thresholds do not overflow.

The reset establishes items1–2 exactly: each row has `[C,P)=[0,4)` and precisely those four ready slots set. For an append, if the pending interval remains valid and shorter than128, the producer-slot clear check, sample write, ready set, and `P++` preserve the interval. If its length is128, all modulo slots are occupied, so the clear check blocks another append. For a consumer advance, clearing the old head and incrementing `C` preserve the interval **only if** that head was ready and the consumer's row policy matches the producer/readiness state. The consumer function itself does not check readiness, so item3 is a caller requirement, not a locally enforced fact.

The remote correction preserves interval occupancy when its gate is computed without overflow and the pending samples form that contiguous interval: it changes sample contents at the tail side and leaves ready membership unchanged. The fallback builder can preserve one shared frame slot across rows when each row's expected producer alignment and ready prefix hold. Neither helper independently proves the all-row alignment premise. Thus this invariant is sufficient for no ring-slot alias/overwrite under the stated conditions, but the current code evidence does not establish every condition across transports, callback interleavings or playback.

## Signed arithmetic boundaries

Modulo slot selection continues through signed wrap because the low seven bits of a two's-complement counter still cycle. Full-width ordering does not. From a normal reset:

- A producer initialized at4 first wraps when an append increments `0x7fffffff` to `0x80000000` (signed `-2147483648`), after `2,147,483,644` successful net increments for that row.
- Consumer initialized at0 first wraps on its `2,147,483,648`th increment.
- Signed lead sums overflow even earlier. `C + sharedLimit` first overflows at `C = INT_MAX - sharedLimit + 1`; for a configured shared limit4 this is `C=2,147,483,644`. Likewise `B + T` in the remote-correction test overflows at `B=INT_MAX-T+1` (for `T=2/4/16`, respectively `2,147,483,646 / 2,147,483,644 / 2,147,483,632`). The sole writer `ConfigureInputBufferLeadLimits` sets remote tolerance to2,4,or16 in session-mode4 transport branches; other modes preserve the incoming value, so those three figures are conditional configured values.

At the first producer wrap, any still-positive nearby producer or consumer is no longer ordered consistently against the wrapped negative counter by signed comparisons. The mode0/shared and other lead comparisons can stop throttling when `C` is positive but `P` has wrapped negative; `min(P0,P1)` can select the wrapped counter as the signed minimum regardless of its true modulo order. For remote correction, if `B` is negative after wrap while `P[row]` remains positive, `P[row] > B + T` can become true for counters that are actually only a few ring slots apart. The subsequent signed loop `s=B; s<P[row]-1; s++` then spans nearly the full 32-bit range (up to roughly `2^32` iterations) instead of the small lead window. This is a conditional static arithmetic consequence, not evidence that runtime scheduling can reach that mixed-sign state or that a hang was observed.

The separate scheduler counter `g_nLatestAvailableInputSequence` (`00560104`) is also signed 32-bit but is not interchangeable with `P` or `C`. In one append branch it is overwritten with `signed_min(P0,P1)-1`, so it may move backward. `RunRaceLoop` forms a 32-bit `latest*2` target; that multiplication overflows for latest values at or above `0x40000000`, before the absolute input counters themselves wrap. Its state/epoch relationship to the ring and runtime reachability are not established here.

## Remaining evidence gap

The static trace establishes the reset values, direct producer/consumer mutation sites, modulo-128 storage, signed lead predicates, readiness checks on append, and the consumer's unconditional clear/advance. A complete ring safety guarantee still needs evidence that the run-loop scheduler only consumes sequences present and ready in every configured row, that network/frame producers keep rows aligned, that relevant operations cannot race, and that the normal race loop cannot remain active long enough to approach signed arithmetic boundaries. Playback selectors `>=2` also skip the ring reset, so their incoming state requires a separate lifecycle proof. No runtime reachability or multiplayer behavior is claimed.

## Evidence used

REA/Ghidra shipped-artifact dossiers: reset `ev_1bcbbccaabb1f5146bb6b67cb7456fcb236c95dc8653d3876ec6efae81c8740f`; regular append `ev_169f3e6194e86622b9be3d7ad0146b5ced7aa698572372cb757a47d43a794611`; remote append `ev_f4762ed7471b9fcb12d3db1428686bceab338a87db4307bdb25d7d9a5f2bad88`; throttle `ev_44464544c1bc7c567e07a488ecb3948ad942736561599021861d30e5ba39b10b`; consumer `ev_a3a11c29c4a7c2a26d344c109ec36cb8a9f53df687347a3b7a39713c7698f5b6`; frame fallback `ev_c9b6d23ed2c5d49aa182f0c9320bbe94c9ffcbc902ae018f26e73aa643d168fa`; session caller `ev_159ff56cda5e7e94d77c4e3422f7a43073a38ee590cce96d1f118d5c9d45291f`; `RunRaceLoop` `ev_c6c2af0916205a137ade5a7aa067b4a8122fee7c11058846ddf89d88ac2549e6`; lead-limit configuration `ev_07fb6d531b070360c4f240b1e99dbf0ead65527fdf259efbe5e75c76ae627177`.

Direct reference queries: producer counters `ev_026e33cc29c39c912a8ee25291d5591684cbe89e1812c5029e550ea01245d92d`; consumer `ev_4f9164441f7147c9fec4cc7021684b43eec02536bd686bdcc7361abeb9c51781`; separate scheduler `ev_3304e2b66a6089ef3424752b267c329e1e3bd4688947f3e0222df867c81ca358`. Earlier Issue #1 notes retain the ready-array xref census and function-level review. All evidence is static and uses the same executable digest.
