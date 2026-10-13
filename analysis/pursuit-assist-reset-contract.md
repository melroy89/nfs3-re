# Pursuit-assist reset contract

Assembly-reviewed functions00405220,00429100,00428d60,00401500,0042b900 and both direct caller sites. This report combines the static contract with the bounded runtime captures below.

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

[Retained samples](evidence/runtime/police-reset-two-taps.json): session0/mode3/track1, effective copassist1, reverse0, overrides0, local LCOP/category0x24. User tapped R twice, reported seeing two resets and smooth gameplay. At tick1381 local segment68, cooldown0 and position approximately(925.096,23.087,215.962); selected participant5 had segment94. Tick1384 inputbit02 is sampled, local segment98 (leader94+4), position(1104.3203,18.0751,210.8401), cooldown31, reset state63. This corroborates accepted leader-relative placement and same-update decrement after writing32/64.

Between samples tick1400 and1403 the local reference changes98->95 while X/Z remain exactly1104.3203125/210.84007263183594. Cooldown decreases23->21 without restarting; selected participant advances96->97. Reference95 is compatible with the earlier leader96-1 pre-guard write. The second short input pulse was not sampled, so this is corroboration of the predicted sequence, not direct proof that the guard rejected that precise input. Cooldown reaches0 by sampled tick1448; intervening observations follow even-tick cadence. Vertical motion continues while the car settles.

User-visible two resets must not be rewritten as one visual reset. The data shows one sampled horizontal relocation and a later reference change, with no observed second cooldown restart. Camera/geometry refresh or an unobserved transient may explain the visual report; neither is established. Accepted reset placement for this scenario is corroborated; exact second-input rejection and visual consequences remain open. Capture stopped after test; no game memory or executable writes.

## Follow-up cooldown rejection corroborated

The higher-frequency focused capture [records both reset input pulses](evidence/runtime/police-reset-cooldown-rejection.json). At tick2345, inputbit02 is set, reference221, cooldown31 and world position(925.99462890625,13.321635246276855,-133.575439453125). At tick2367, inputbit02 is set again,22 ticks later; reference changes221->219, cooldown continues to20 and horizontal X/Z remain exactly unchanged. Tick2369 clears input and cooldown becomes19. No second cooldown restart or horizontal relocation is observed. The user independently reported that quick tapping appeared to reset only once. Static00405220 prewrites the leader-relative reference, while00429100 rejects nonzero cooldown; the observed states corroborate that bounded accepted/rejected sequence. These are asynchronous samples, not a breakpoint trace.

The reference later returns to221 at tick2383 during ordinary updates, with only small position movement. This establishes recovery of that field in this case, not a universal geometry/camera invariant. Earlier follow-up presses at ticks1901/2015 were114 ticks apart and both reset after expiry; they are distinct from the quick double-tap and from the first test's visual report.

**Closed for this normal-direction local police scenario:** accepted leader-relative reset, cooldown-based rejection of the second rapid request, pre-guard reference change without second observed relocation, and subsequent reference recovery. Remaining: reverse-track placement, other rejection gates, camera/visual effects in the initial report, dense occupancy fallback, multiplayer and exceptional state. The sampler was stopped after capture; game left running.

Independent repeat in the same race: [confirmation capture](evidence/runtime/police-reset-confirmation.json) observes R pulses at ticks2565/2585,20 ticks apart. First relocation gives reference254, cooldown31 and X/Z763.0594482421875/-239.42218017578125. Second changes reference to252, cooldown21 and identical X/Z; next tick2587 sample has cooldown20. User explicitly confirmed double-tapping R and seeing only one reset. This repeats the bounded cooldown rejection observation. Capture stopped; no additional player action is required for this normal-direction cooldown question.

## Reverse-direction police reset corroboration

Retained [event samples](evidence/runtime/reverse-police-reset-events.json) cover session0, mode3, Redrock track1, reverse1, copassist1, overrides0 and local LCOP/category0x24. The user reports two resets with roughly two seconds between them, then pausing. The sampled relocations are approximately4.69 wall-clock seconds apart; treat the user's interval as approximate, not a measured timing claim.

At tick1546 local segment1389 has cooldown0 and position(100.5771,14.4801,200.2742). Participant6 is the eligible minimum ordering value1, segment1367. At tick1549 local segment1361 equals1367-6, position jumps to(-28.5807,19.8883,117.0248), cooldown30. The first input pulse was not sampled.

At tick1846 local segment1362 has cooldown0; selected participant6 is segment1330. At tick1849 inputbit02 is sampled, local segment1324 equals1330-6, position jumps to(-238.5998,17.7540,160.0061), cooldown31. Both events therefore corroborate the accepted reverse leader-relative placement branch after cooldown expiry. They are not a rapid-repeat rejection test.

These50ms asynchronous snapshots are not an instruction trace. They do not establish exact input duration, the precise placement-search path, dense occupancy fallback, all reverse tracks, or visual road alignment. User confirmation of two resets supports the relocation interpretation; visual placement quality remains unreported. Sampler stopped after capture; executable and live memory were not written.

## Pending police arrest reset-guard validation

Current targeted Astra question: does the local police reset request remain rejected during target-group phase2, independently of cooldown and race-start rejection? The capture must establish local categorybit20, race_mode3, nonNULL local target+624, and that target's group+628 phase+1c==2. Other gates must be clear: local+524==0, race-start flag nonzero, +184==0, and no applicable racer state3 gate. Ask the player to pause during the arrest before pressing R; verify these fields first.

Then capture the R actionbit02, local reference and world position, reset state+174 and cooldown+524 before/after. A reference prewrite alone may occur through00405220 and does not prove relocation. Absence of movement without sampled action/input-path evidence cannot identify the rejecting guard. UpdatePlayerVehicleControls00431430 has no local phase-based early return before its R test, but its input callback runs first and controller/callback admission can still suppress the action. This is a test plan, not a completed result. Retain the backlog row as Partial until captured evidence supports a bounded conclusion.

## Police arrest reset input: mixed relocation evidence

[Retained snapshots](evidence/runtime/police-arrest-reset-guard-events.json) capture local LCOP/category0x24, session0, mode3, reverse Redrock, copassist1 and overrides0. User acquired a DIAB target, reported catching it, and paused at tick18894. Target6167244 had group phase2; race_started1, cooldown+524=0, blocker+184=0 and reset state+174=0. The local category has no racer bit01, so its state3 gate does not apply. The user was asked to unpause, press R once and pause again, and subsequently confirmed pausing. The user then explicitly confirmed that the car visibly teleported. This corroborates relocation rather than a reference-only or purely sampled display artifact; it does not identify the executing placement path.

At tick18947 position was(-760.2371,-2.8627,-607.0535), segment571. Tick18950 samples inputbit02 with target phase2 still present, cooldown0 and reset state0, but position is already(-388.3151,-2.8723,-289.3703), segment463. Tick18953 input clears, phase remains2, position becomes(-394.9630,-2.8986,-409.0408), segment497 and recovery countdown+8a0 becomes700. At tick19007 the target remains attached and reset counters remain0. Tick19011 has target0, segment449, position(-146.8298,-15.9018,-534.9230), cooldown31 and reset state63; these are consistent with the ordinary reset completion writes32/64 and subsequent decrement after target removal.

This corroborates an R action while the phase guard predicates were sampled, with no simultaneous ordinary-reset completion counters. It does NOT establish absence of relocation: world coordinates changed substantially during phase2. The static pre-guard segment write alone cannot directly explain all observed world-coordinate changes. Subsequent environment/recovery consumers or another placement path require tracing. The later reset counters are compatible with the known stop-cleanup reset path after target clearing, but asynchronous50ms snapshots do not identify the exact caller. Do not classify either change as a proven execution trace, immediate successful manual reset, or clean no-movement rejection. The pursuit-assist item remains Partial. Read-only sampler stopped; no executable or live-memory writes.

### Recovery countdown interpretation

At tick18950 material+18c is13, sampled orientation dot(+130,+cc) approximately0.999790, +184=0 and recovery+8a0=0. At tick18953 material becomes14 while dot remains approximately0.984925 and +184 remains0; +8a0 becomes700. This matches the material14 reload predicate in UpdateVehicleContactRecoveryCountdown00429260 without requiring an orientation-threshold failure. Reloading the countdown is not itself relocation. Recovery-attempt counter+2c0 remains0 across these samples; RecoverVehicleFromInvalidContactState00428f90 increments it on entry, before its placement decision. The observations therefore provide no positive evidence of that recovery routine completing the initial position jump. Sampling and untraced writers prevent treating the unchanged counter as an exhaustive execution exclusion.

### Leader selection and dispatch cross-check

The eligible minimum ordering value is1 for participant4/FM50 in the relevant snapshots. At tick18950 that participant has segment464 and local segment463, exactly the leader-minus-one reference prewrite. At tick19011 the leader has segment455 and local segment449, exactly the accepted reverse offset leader-minus-six. This supports the user's observation that police R sends the car close to the leading opponent; selection is by race-order field, not proximity to the current pursuit target. The target at the manual input remains participant1/DIAB, a different car.

Local category0x24, controller00431430, physics callback004ae4c1, alternate byte0 and upright approximately0.99979/0.98493 persist at sampled ticks18947/18950/18953. Consequently the sampled state selects the non-AI full-physics branch004ad7a3 in UpdateVehiclePhysicsDispatch, rather than ProcessAIVehicleDynamics004088f0. An AI-only +1c-to-control-vector chain must not be offered as this event's demonstrated explanation. Its helper004071a0 writes velocity, not XYZ position, in any case. Exact transient execution remains unobserved.

ClearPolicePursuitGroupLinks004040e0 clears member+628/+624 before its categorybit04 branch calls00405220 at00404250. This is a concrete static candidate for the later target0, cooldown31/reset63, leader-minus-six state; asynchronous samples do not prove that caller executed. The initial phase2 world-position change remains unresolved.

### Ordinary position integrator recovered

Created the previously undefined90-byte callback004a2c60 as `IntegrateActiveVehicleWorldPosition`, after verifying registration at0042c437 into vehicle+610 and its complete assembly. EAX supplies the vehicle. Byte+89==0 skips writes; otherwise XYZ+98/+9c/+a0 receive velocity+a4/+a8/+ac multiplied by float0053c8ec=1/64, stored in Y,Z,X order. It reads no track reference+1c and writes no reset174/cooldown524 fields. This is an exact per-invocation arithmetic contract, not a claim about tick cadence.

The small velocities sampled before/during the initial jump do not explain hundreds of position units through this integrator alone. Unsampled velocity transients and other position writers remain unresolved. The non-AI physics body004ad7a3 was reviewed at pseudocode level: it computes wheel/drivetrain forces and updates linear/angular motion fields, but this pass did not establish a direct discrete XYZ relocation there or exhaustively audit its callees. Keep the initial teleport open rather than substituting an AI-only controller explanation.
