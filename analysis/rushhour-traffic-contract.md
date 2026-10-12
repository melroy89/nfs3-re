# RUSHHOUR traffic configuration contract

Static assembly review of cheat input, roster creation, configuration setter/getters and reactivation. No RUSHHOUR runtime run is claimed.

## Activation and survival

Encoded keyword005594a2 contains bytes5b5e5c5151585e5b, which subtract9 to RUSHHOUR. Dispatch index13 sets006fd4fc bit08 at00452825. Frontend cheat admission permits session0/1 and race0/3. Regular roster00473bf0 preserves override flags only for session0; Hot Pursuit00474640 masks them with0x10 at00474c42, removing RUSHHOUR. Consequently Hot Pursuit is not a valid runtime test of this override even when the menu accepts the keyword.

## Allocation is separate from reactivation

Regular roster reads opponent selection006fd4d0: zero gives0 AI opponents, nonzero signed values below2 give1, and values>=2 fill8 minus human racers. With traffic enabled (006fd4e8==0), traffic allocation is max(0,8-human racers-AI opponents). No RUSHHOUR flag is consulted in this allocation.

For ordinary session0 with one human, opponent selections0/1/2 yield respectively7/6/0 traffic slots when enabled, and0 when disabled. Thus RUSHHOUR cannot produce15 traffic vehicles through this roster. Its cap15 exceeds the maximum ordinary solo allocation7. This is a roster/cap distinction, not proof of actual visible density or valid frontend reachability for every setting.

Installed FEDATA/MENUS/opponent.mnu contains TRAFFIC_BUTTON and TRAFFIC_CASCADE bound to list traffic. Menu visibility/disable dispatch is not proved by file presence alone. The reconciliation writer0044c0b4 forces traffic disabled in modes1/2; regular mode does not receive that particular forced write. A later runtime test must first confirm that a nonzero traffic roster exists.

## Cap and delay

ConfigureTrackAIParameterRecord0040e3c0 sets record+0=15 and+4=0 under bit08. GetConfiguredTrafficVehicleLimit0040ef10 returns the selected record+0 without a weather/night adjustment. GetTrafficReactivationDelayRange0040eed0 adds200 for nonzero006fd4cc and400 for nonzero006fd4c8 after reading base delay. Therefore RUSHHOUR ranges are0/200/400/600, not universally0.

Deactivation00405d40 writes countdown1+((range*u)>>16), with u in0..65535. These four ranges cannot overflow the multiplication. Base-only0 yields1; other ranges bound countdown to1..200/400/600. The override does not remove the tick>=1920 gate in0040c210. At eligible checks, positive countdown decrements; only1->0 evaluates the cap. A failed cap check leaves0; next call writes2 and rejects, followed by2->1 rejection and then1->0 retry. Thus repeated cap checks are separated by three eligible invocations after failure, absent competing writes.

The compared count is signed registered traffic005efd8c minus shared inactive AI0056ebc0, not a direct scan of active traffic. If the registered traffic count is<=7 and the shared inactive count is nonnegative without arithmetic overflow, the cap15 cannot reject. This conditional inequality does not prove counter invariants globally.

## Remaining population contract

Returned direct xrefs show the shared inactive counter is cleared by0040cb20/0040cb50-family helpers, incremented on deactivation and decremented on activation. The activation controller serves traffic, police, opponents and nonlocal humans; police reactivation bypasses the traffic cap. Therefore traffic-only accounting requires mode/state invariants, not just the counter's use in the cap test. Reset+630 writes and aliased state remain relevant.

Closed statically: keyword/flag, mode filtering, ordinary solo roster0/6/7 distinction, cap-versus-allocation separation, delay modifiers and retry cadence. Open: actual RUSHHOUR loaded configuration and traffic activation, menu availability, mixed/network-human accounting, shared-counter consistency, multi-human placement and retry termination. No binary, assets or live memory were changed.

## Singleton target initialization boundary

Single-human traffic initialization copies0056ebb8 into vehicle+6d8 without
validation. Its only observed direct writer00404ccb updates the progress
context only on the last-human callback and qualifying nonnegative progress
(or police-role handling). No direct reset reference was found. Therefore
the first-offset61 acceptance argument requires a valid sole-human pointer
already established; it is not an unconditional initialization proof.

Track segment count is loaded from selected type15 block WORD+6, without a
local minimum check. Relative-offset arithmetic wraps once, while retries
increase offset20 with no explicit bound. Installed track-count provenance,
callback ordering, stale-reference exclusion and multi-human coverage remain
open; these are conditional contracts, not demonstrated runtime failures.

## Callback ordering boundary

RegisterVehicleUpdateCallbacks0042c830 walks master pointers005efac8 in
ascending index and inserts each vehicle+600 callback into007d3690 at priority21
(0042c864..0042c876). InsertCallbackByPriority004be250 preserves equal-priority
order, and dispatcher004be3a0 visits entries forward. The list runs on even
pre-increment ticks at004c4a6a..004c4a7f. Thus an earlier-index ordinary human
control callback precedes a later traffic callback on that dispatch; the
scheduler does not assign separate human/traffic priorities.

This alone does not establish roster ordering, human callback identity, or
successful progress refresh. UpdatePlayerVehicleControls00431430 conditionally
calls pursuit state00405740, whose progress refresh00404c80 can retain the old
pointer. Full singleton-target initialization remains open pending roster and
constructor evidence. No stale-pointer occurrence is asserted.

## Ordinary solo roster and gate refinement

BuildRegularRaceRoster00473bf0 mode0 constructs the human first, opponents
next and traffic last (00473c82..00473cc0,00473e3e..00473e73). Ascending setup
processing0042c700 and master append00428700 preserve that order. Callback
setup0042c400 retains ordinary human controls in session0 and assigns traffic
AI controls to traffic. Together with priority21 stable dispatch, this closes
human-before-traffic controller ordering for this ordinary completed setup.

Traffic registration004288d0..004288fd increments the AI count later stored
at005efd98 (00428958). Thus traffic alone enables the player state-machine
gate00431438..0043144a, even without opponents or police. The remaining
singleton-pointer question is state-specific refresh/initialization, not
missing priority separation or the absence of opponent cars. States outside
the inspected refresh cases, unsuccessful candidate selection and unusual
setup/lifetime remain unresolved.

## Startup refresh precedes ordinary traffic reactivation

ResetVehicleAIAndPursuitFields0040cb90 zeros human state+6e0 at0040cbe5.
On the first ordinary racer callback, default state stores2 at004057a0 and
returns; the next state2 call invokes progress refresh00404c80 at004057c4.
CheckTrafficVehicleReactivation0040c210 rejects simulation tick<=1919.
With normal mode0 setup, stable even-tick callback dispatch and nonnegative
human starting progress, the sole-human refresh therefore writes0056ebb8
before traffic can reactivate. Traffic registration enables that player gate.
This closes the ordinary initialization ordering under those explicit
preconditions; it does not prove malformed placement validity, later state
lifetime, all modes or aliased pointer ownership.

## Solo target lifetime refinement

With one human in master slot0, successful0056ebb8 refresh always chooses that
same human. Traffic+6d8 is a separate cache:0040c60a assigns the singleton,
DeactivateAIVehicle00405d53 assigns master slot0, and00405d20 can assign NULL
when cached/fresh proximity checks find no human. Reset0040cb9f clears it.
The global singleton itself has no direct reset found. Static vehicle storage
is reused on the next setup, and the delayed ordinary traffic activation
follows early human refresh; no pre-refresh stale singleton read is established
in the zero-opponent/zero-police solo traffic route. Other modes, invalid
progress, indirect/asynchronous teardown/setup consumers remain unresolved.
