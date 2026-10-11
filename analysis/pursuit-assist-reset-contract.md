# Pursuit-assist reset contract

Assembly-reviewed functions00405220,00429100,00428d60,00401500,0042b900 and both direct caller sites. This report establishes static behavior; no new runtime reset was captured.

## Selection and request ordering

RequestResetNearLeadingParticipant00405220 scans participant pointers005efc48 with count005efda0. It rejects categorybit01 participants in state3 or4. It chooses the first strict minimum signed+2bc below initial10000; equal values retain the first, and all values>=10000 mean no candidate. This is a ranking-field comparison, not a geometric nearest-car search.

Only session0, effective copassist006fd4a8 nonzero, signed tick>1152 and a selected participant cause requester+1c to be overwritten by selected segment-1, with one negative wrap. This write004052b7 precedes every ordinary reset guard. EDX force only bypasses the requirement for a selected participant before invoking00429100; it does not bypass that callee's rejection checks. Nor is copassist required for invoking the ordinary reset.

Player input00431545 tests input bit02; categorybit20 routes to this helper with force1 at0043155e, other vehicles call ordinary reset. Stop cleanup00404250 uses force0 for a group member with categorybit04, after clearing its group+628 and target+624 at004041f7/00404201. Thus the police target-group rejection cannot apply to that cleared target on this sequential path; other rejection checks remain. Categorybit01/group validity must be considered separately.

## Ordinary rejection and accepted state

00429100 rejects any nonzero cooldown+524, categorybit01 with racer state3, race-start flag0, or nonzero+184. State4 alone is not this function's terminal-state rejection; higher-level caller/admission rules remain relevant.

In race_mode3, categorybit20 with a nonNULL target is rejected if target.group+1c==2; categorybit01 is independently rejected if its own group+1c==2. CheckPursuitGroupStopPhase00401500 dereferences+628 without a localNULL guard. These predicates are phase checks, not generic nonempty-group checks.

After admission, requested segment becomes current reference plus direction*005efdcc. The sole returned direct writer initializes that offset to5 at0042c606. One wrap follows. With a valid selected segment and ordinary track length, copassist initially requests leader+4 forward or leader-6 reverse modulo track length; it is not simply leader-1 placement.

FindAndApplyVehicleResetPlacement00428d60 first tests center, then at most10 lateral segment passes, advancing in race direction. Exhaustion still invokes placement at the original requested segment with zero offsets; it does not cancel reset. Final accepted segment can therefore differ from the first request. Geometry/basis/occupancy correctness remains a separate question.

The caller zeros linear velocity+a4/+a8/+ac, raises Y by default1.5 (half to0.75 when00420bf0 qualifies), resets motion/contact state, then writes+174=64 and+524=32. These writes identify completion of this static branch; a segment write alone does not.

## Cooldown units and cadence

0042b900 reads+524 and decrements every nonzero value once at0042b91f, before active-state tests. It is not a positive-only saturating decrement. The inactive branch later clears it at0042b971. Other direct writers include initialization/reset-to-zero and network position correction setting32 at0040bf37; literal-offset search does not exclude aliases.

The function is vehicle callback+61c, registered at priority50 on007d3690; that list dispatches on even simulation ticks. Under stable normal registration and no competing writes, positive32 requires32 invocations, not32 simulation ticks. A player-control reset at priority21 precedes priority50 on that same tick, so its32 can become31 in the same tick; it reaches0 after the callback at tick+62, with the next normal priority21 opportunity at tick+64. This is simulation ordering, not a wall-clock seconds claim. An inactive branch or other writer changes that timing.

## Status and next runtime evidence

Closed statically: selection/tie/sentinel policy, force semantics, pre-guard reference write, rejection predicates, initial directional offset and conditional cooldown cadence. Pursuit-assist remains partial until runtime verifies a requested/accepted reset and a rejected request, especially segment versus world-position consistency and subsequent environment refresh. Capture +1c, world position, +524, +174, +184, category/state, group phase, input, effective assist, direction and selected leader before/after; asynchronous observations must distinguish caller-only changes from completed placement. No executable or live memory was modified.

## First runtime two-tap test

[Retained samples](runtime/police-reset-two-taps.json): session0/mode3/track1, effective copassist1, reverse0, overrides0, local LCOP/category0x24. User tapped R twice, reported seeing two resets and smooth gameplay. At tick1381 local segment68, cooldown0 and position approximately(925.096,23.087,215.962); selected participant5 had segment94. Tick1384 inputbit02 is sampled, local segment98 (leader94+4), position(1104.3203,18.0751,210.8401), cooldown31, reset state63. This corroborates accepted leader-relative placement and same-update decrement after writing32/64.

Between samples tick1400 and1403 the local reference changes98->95 while X/Z remain exactly1104.3203125/210.84007263183594. Cooldown decreases23->21 without restarting; selected participant advances96->97. Reference95 is compatible with the earlier leader96-1 pre-guard write. The second short input pulse was not sampled, so this is corroboration of the predicted sequence, not direct proof that the guard rejected that precise input. Cooldown reaches0 by sampled tick1448; intervening observations follow even-tick cadence. Vertical motion continues while the car settles.

User-visible two resets must not be rewritten as one visual reset. The data shows one sampled horizontal relocation and a later reference change, with no observed second cooldown restart. Camera/geometry refresh or an unobserved transient may explain the visual report; neither is established. Accepted reset placement for this scenario is corroborated; exact second-input rejection and visual consequences remain open. Capture stopped after test; no game memory or executable writes.

## Follow-up cooldown rejection corroborated

The higher-frequency focused capture [records both reset input pulses](runtime/police-reset-cooldown-rejection.json). At tick2345, inputbit02 is set, reference221, cooldown31 and world position(925.99462890625,13.321635246276855,-133.575439453125). At tick2367, inputbit02 is set again,22 ticks later; reference changes221->219, cooldown continues to20 and horizontal X/Z remain exactly unchanged. Tick2369 clears input and cooldown becomes19. No second cooldown restart or horizontal relocation is observed. The user independently reported that quick tapping appeared to reset only once. Static00405220 prewrites the leader-relative reference, while00429100 rejects nonzero cooldown; the observed states corroborate that bounded accepted/rejected sequence. These are asynchronous samples, not a breakpoint trace.

The reference later returns to221 at tick2383 during ordinary updates, with only small position movement. This establishes recovery of that field in this case, not a universal geometry/camera invariant. Earlier follow-up presses at ticks1901/2015 were114 ticks apart and both reset after expiry; they are distinct from the quick double-tap and from the first test's visual report.

**Closed for this normal-direction local police scenario:** accepted leader-relative reset, cooldown-based rejection of the second rapid request, pre-guard reference change without second observed relocation, and subsequent reference recovery. Remaining: reverse-track placement, other rejection gates, camera/visual effects in the initial report, dense occupancy fallback, multiplayer and exceptional state. The sampler was stopped after capture; game left running.

Independent repeat in the same race: [confirmation capture](runtime/police-reset-confirmation.json) observes R pulses at ticks2565/2585,20 ticks apart. First relocation gives reference254, cooldown31 and X/Z763.0594482421875/-239.42218017578125. Second changes reference to252, cooldown21 and identical X/Z; next tick2587 sample has cooldown20. User explicitly confirmed double-tapping R and seeing only one reset. This repeats the bounded cooldown rejection observation. Capture stopped; no additional player action is required for this normal-direction cooldown question.
