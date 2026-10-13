# Contact recovery countdown

Static scheduling chain:0042c400 stores0042b900 at vehicle+61c
(0042c455).0042c830 registers that callback at priority50 on007d3690
(0042c8e7..f9). Race tick dispatch004c4a6a..7f runs this list only on
even pre-increment simulation ticks. No wall-clock frequency is established.

0042b900 calls UpdateVehicleContactRecoveryCountdown00429260 only when
byte+88 is zero and byte+89 nonzero. Its inactive arm never calls it.
The separate+524 cooldown decrements independently and must not be
confused with recovery countdown+8a0.

For signed+8a0>0, four conditional deductions (-1,-2,-8,-1) can stack
to0..12 units per invocation. The first depends on raw signed float bits
+10c, field+184 and category bit04; the second on+20/+24 or queried
material0/14; the third on ordered b8+conditional_abs(a8)<1 with+184
and WORD+164 zero; the fourth additionally requires bit04, input byte
+504>200 and raw+10c<0.1. All deductions precede the expiry test.

Expiry with bit10 clear calls00428f90, clears+8a0 and returns. With bit10
set it clears and continues, allowing same-call reload. Inactive countdown
and dot/material/+184 gates reload512 for nonzero+184, otherwise default
global005efdc0=700 or alternate005efdc4=175 when bit04 and006fd4a0 are set.
These defaults are conditional countdown units, not seconds. Progress may
remain unchanged; recovery success, placement freshness and real collision
responses remain unresolved. No runtime capture or binary modification.

## Same-update impact state ordering

Wrapper0042b780 calls0042b480 before0042ac40, preserving vehicle inEDX
and reloadingEAX. First stage may increment or reset+8d4; the later stage
compares that post-stage value at0042ad28 before initializing impact state.
A same-call reset may therefore admit that gate, subject to its other tests.
This is static ordering, not an observed collision outcome.

A bounded parsed-instruction scan of0042ac40 found only the+8d4 comparison
at0042ad28 and address formation0042ad4b. Its continuous-state branch is
not established as another+8d4 consumer. Counter meaning, physical units
and runtime reachability remain unresolved. Ghidra0042b780 records this
ordering and limitation.

## Recovery attempt versus relocation

Assembly00428f90–004290f2 clears+8d4 and increments+2c0 before its relocation predicate. Thus+2c0 counts entry attempts here, not exclusively successful relocations. The healthy branch still increments it. Threshold tests on+10c,+e4,+ec,+15c are raw signed integer float-bit comparisons, not absolute-value tests; WORD+164 uses unsigned>5. The body has no manual-reset cooldown/start/stop-phase guards and no direct+524 write; shared callee effects remain separate. This prevents interpreting every recovery attempt as an R-style reset. Ghidra plate refined; runtime collision test remains pending.

## Barrier proximity capture

[Retained samples](evidence/runtime/barrier-proximity-recovery.json) contain309 distinct sampled ticks,2049–3042, in the local LCOP reverse Redrock session. The user reports hitting the left barrier, then clarified that subsequent sliding was very close to it rather than in sustained contact. Both recovery+8a0 and reset cooldown+524 were zero in every retained local sample. This establishes no observed activation in this capture, not a universal wall-contact rule or proof that a brief transition could not occur between50ms samples. Collision timing/contact geometry were not directly traced. This run does not close the collision/recovery backlog.
