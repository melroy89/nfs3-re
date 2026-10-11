# Spike-strip identity, arming and removal

Target: `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Addresses refer to the saved Ghidra project at image base `00400000`.

## Static identity proof

Previously generic timed-track-event functions can now be identified as spike-strip functions:

1. Localization table pointer `00562334` points to `kTextKeySpikeStrip` at `00542774`, text ID `0x1bc` relative to table `00561c44`.
2. Controls UI jump table `0043c8c8`, entry 11, points to `0043cc38`, which loads text ID `0x1bc`. The UI reads the corresponding binding field at `0043ccc3`–`0043ccd4` and passes that label at `0043ccd6`.
3. `0048f47a`–`0048f482` maps source binding field 11 (`+0x2c`) to runtime slot 11. Collector `0048f550` packs slots 4–11 into action bits 0–7.
4. Action bit `0x80` maps to vehicle input byte `+0x512` at `00431507`–`0043151b`; `00404e40` consumes its rising edge with latch `+0x513`.

The controls UI region starts at `0043c900` but was not defined as a function in the current database. Its relevant instructions were checked against the executable with objdump; no function boundary was created in this pass.

## Timing and independent removal paths

The 80-byte record at `007dd850 + 80 * policeIndex` contains active flag `+0`, segment `+0x34`, lane `+0x38`, and an arming tick at `+0x4c`.

- Creation supplies simulation tick plus 192. This is a tick count, not an established duration in seconds.
- Contact search rejects records while signed current tick is below `+0x4c` (`004ca17d`–`004ca189`).
- Pressing the input again before that threshold selects denial sound 18. At or after it, another rising edge clears the active flag (`00404e80`–`00404e90`). The field therefore also sets the earliest manual-removal time; it is not an expiry timestamp.
- Stop cleanup independently clears a human officer's strip: `00404243` tests human category bit 4, then `00404255`–`0040425b` passes the police index to the clear helper. Disappearance alone cannot prove a hit.
- Contact dispatch `004297d0` clears a matched record, sets vehicle byte `+0x621` bit `0x40`, ORs the candidate mask into `+0x99c`, then calls `00401650`. Exact correspondence of its four mask bits to individual wheels remains unresolved.

## Live observations

Melroy drove Diablo SV police in Hot Pursuit on Redrock Ridge and used the spike-strip control. Selected transitions and the bounded sample count are in [runtime/spike-event-observations.json](runtime/spike-event-observations.json).

- A strip was already active when expanded sampling began at tick 14666, with stored threshold 12770. Its persistence beyond that threshold corroborates that the threshold is not an expiry time. Initial deployment predates this capture.
- It cleared at sampled tick 15469 as the officer's completed-stop counter advanced from 3 to 4, with input/latch zero. This is consistent with the independently verified stop-cleanup path; there was no sampled contact mask.
- Input was sampled high at tick 17349; the record was active at tick 17351, segment 675, lane 5, threshold 17542. Another input was high at tick 17775; it was inactive at tick 17777. These observations corroborate deployment and later manual removal.
- A further deployment was sampled at tick 19987, segment 1049, lane 7, threshold 20178; removal followed at tick 20945 with the input latch set.
- No nonzero vehicle `+0x99c` mask was observed in the bounded capture. This does not prove that no physical contact occurred between samples and does not validate tyre damage, wheel-bit identity or all contact geometry.

Reads were asynchronous and did not suspend the process. Tick and field changes may be sampled on opposite sides of an update. No instruction breakpoints, memory writes or executable edits were used.

## Saved function names

| Address | Name |
| --- | --- |
| `00404e40` | `ProcessVehicleSpikeStripInputEdge` |
| `004c9dd0` | `InitializeSpikeStripRecord` |
| `004c9f50` | `ClearSpikeStripRecordActiveFlag` |
| `004ca160` | `FindSpikeStripContactCandidates` |
| `00401650` | `UpdatePursuitAfterSpikeStripContact` |
| `00403df0` | `UpdatePoliceSpikeStripPassage` |

Existing numerical, register and capacity caveats remain in their Ghidra comments. Follow-up: capture an actual strip hit and inspect mask consumers before assigning wheel names or damage semantics.

The read-only [sampler](runtime/read_memory_sampler.py) uses this executable's fixed address map. Rediscover the live `nfs3.exe` PID before each run; invoke it with the required local read permissions and an explicit output file. It defaults to a bounded 900-second capture and never writes process memory. Raw temporary captures remain outside this repository.


## Static wheel-render mask mapping

Assembly of `004bae00` establishes the following conditional draw calls to
`0049de20`. A set mask bit skips the corresponding wheel part.

| Vehicle +99c bit | Model part index | Position in model at vehicle +8a4 | Rotation helper | Vehicle vertical offset |
| --- | --- | --- | --- | --- |
| 1 | 1 | +108 | 004b9140 | +93c |
| 2 | 2 | +114 | 004b9140 | +93c |
| 8 | 3 | +120 | 004b9280 | +940 |
| 4 | 4 | +12c | 004b9280 | +940 |

The tests are at `004baf61`, `004bafb8`, `004bb027`, and `004bb07e`.
The explicit EDX part indices precede the respective draw calls at
`004bafae`, `004bb005`, `004bb074`, and `004bb0cb`.

`004b9140` takes EAX=vehicle, EDX=matrix output, EBX=steering enabled.
It integrates angle +938 from tick delta and +598/+4f4, then combines X
spin rotation with Y steering rotation when enabled and +51c is nonzero.
`004b9280` integrates +934 from +594/+4f4 and tightens the nominal rate
clamp from +/-0.5 to +/-0.05 when handbrake field +50d is nonzero. It emits
X rotation only. Positive tick delta and respective +59c bits1/2 govern
integration. These are render rotations, not evidence of physical tyre forces.

Names saved in Ghidra:

- `BuildWheelSpinMatrixWithOptionalSteering` at 004b9140.
- `BuildHandbrakeLimitedWheelSpinMatrix` at 004b9280.
- `RenderVehicleBodyAndUnmaskedWheelParts` at 004bae00.

The steering and handbrake behavior supports front/rear pair interpretation,
but left/right identity is not yet established. Model-part indices are not
interchangeable with contact-wheel indices: the final two mask bits appear
in reversed order in this renderer. Actual hit capture, complete mask/flag
consumer tracing, anatomical identities, and handling consequences remain open.


## Force-feedback consumers and conditional anomalies

A whole-program parsed-instruction search for operand substring `0x99c`
returned 24 matches across 341,115 instructions, without truncation. This
bounds the direct displacement search; aliases or computed addresses are not
excluded. Consumers include rendering, effects, audio, viewport selection,
reset/contact mutation and the two force-feedback helpers below.

`UpdateVehicleConditionForceFeedback` (`00471860`) constructs a hardware
condition-effect payload, then calls `UpdateDirectInputEffectParameters`.
At `00471917..00471939`, its predicate is `(mask & 3) != 0 && mask != 3`,
with the second comparison against the **whole DWORD**. When true, bit1
selects offset -10000; otherwise offset +10000. Thus masks7,11,15 also
select -10000 even though both low wheel bits are set. Mask3 skips this
override, as do masks0,4,8,12. This is not an exclusive-or of the low pair.
No left/right physical sign or hardware effect has been demonstrated.

`UpdateVehicleSurfacePeriodicForceFeedback` (`00471af0`) obtains a scaled
magnitude from00472110, stops slot1 below2, otherwise chooses a base
frequency5..17 and magnitude2500..5000. Any nonzero contact mask overrides
surface class00678bf4 to17 at00471c95. Jump-table entry17 routes to00471d08:
frequency -=5, capped at10 using unsigned comparison, magnitude +=6000.
For finite scaled magnitude in [2,5), frequency5 therefore becomes0.
If the effect update is required,00471d5b converts that zero to x87,
00471d5e computes1000000.0/frequency, then adds0.5 and truncates/stores the
period before calling the effect wrapper. There is no intervening zero
guard. Constants0053af9c/0053afa4 were read as doubles1000000.0/0.5;
thresholds0053af64/0053af68 are floats2/5. The first comparison uses the
live x87 result while later bands use its stored float copy, so boundary
rounding must be preserved in exact emulation.

This establishes a conditional zero-divisor path, not a demonstrated crash
or haptic defect. x87 exception masks, conversion outcome, backend handling
and live reachability with supported hardware remain unresolved. Input
magnitude units are not established. The caller00471e10 applies readiness,
vehicle-state and configuration gates; periodic updates require006fd1f4,
and the condition path requires006fd200 with006fd1fc disabled. Cached state
also suppresses unchanged periodic payloads. Neither helper directly writes
vehicle steering controls or tyre forces.

Separately, existing verified viewport selector00426560 chooses override
mode7 for a nonzero mask after higher-priority pause/+9a4 gates. Its visible
camera behavior remains untested. These static contracts narrow the
remaining consumer audit without closing actual-contact or handling work.


## Pursuit-state and reset cleanup boundary

Direct displacement searches returned76 instructions mentioning0x621 and37
mentioning0x620, both untruncated. The latter includes wider accesses that
can cover the flag byte. These searches are bounded evidence, not proof
against aliases, computed addresses or bulk copies.

The accepted contact dispatcher004297d0 sets +621 bit40, ORs +99c and calls
00401650. For category bit1 vehicles that helper writes group+1c=2 before
its terminal-state/attachment tests. Player state machine00405740 checks
group stop phase in ordinary state2, enters state6, sets a tick+320 deadline
and category bit2, then follows pull-over/stop control paths. This is an
identified route from strip contact into pursuit control. It does not
establish a separate per-wheel tyre-force reduction.

Cleanup helpers004056e0 and00409b40 were verified in assembly. Both clear
group phase to0 before conditionally requesting00429100 when strip flag40
is set. Player helper also clears category bit2 and sets controller state2;
opponent helper sets state1 and preserves category. Neither helper checks
a reset success result or clears mask/counter directly. If the reset is
refused by cooldown/start/state/contact/pursuit guards, the earlier
controller/group writes remain. Accepted reset calls00428970:
00428a2d zeros+99c,00428a37 zeros+9a0,00428a98 clears +621 bit40.
Therefore leaving the pursuit stop state is not itself proof of completed
repositioning or immediate strip-mask removal. Later actual-hit recovery
captures below establish specific accepted cases, not universal acceptance.

Audio consumer00417390 also gates a periodic sound path on nonzero mask,
WORD+164 zero, ordered+10c>0.9 and+b8>5, with further cadence/state checks.
Exact audible layer identity remains unresolved. No direct per-wheel
physics-force writer has been established by this pass; absence from these
specific searches must not be generalized to absence of all handling effects.


## Contact geometry and record selection

Assembly004ca160 scans eight records in ascending index, skipping inactive,
unarmed or non-neighboring-segment records. It returns the first nonzero
four-wheel mask at004ca433..004ca444, with no nearest-distance ranking or
union across strips. Only that record is cleared by the caller.

For each wheel it tests four transformed vertices against six axis-aligned
planes at +/-0.5. It accepts when their outcodes have no shared bit. Equality
is inside; unordered comparisons set the negative-face bits, assuming the
x87 operation continues. The test does not clip edges or test additional
separating axes. Transposition is only an inverse rotation if the vehicle
matrix has the required orthonormal properties.

[Analytical witness](spike-strip-geometry-witness.json): identity rotation,
wheel at origin, quad vertices(0.375,+/-0.25,0.875) and
(0.875,+/-0.25,0.375). Outcodes are32,2,2,32, whose intersection is0,
so the candidate test accepts. Every point on the quad has x+z=1.25,
whereas every cube point has x+z<=1.0. Thus the shapes are disjoint by a
0.25 separating-plane margin. All values are exactly binary representable.
The quad has height0.5, matching constructor00540360's vertical extrusion;
its reachability from installed track endpoints is not established. This
proves the conservative predicate can produce false positives, not that
such a false hit has occurred in-game.

A focused `--spike-only` sampler mode retains event records, vehicle rotation,
fixed-point wheel positions, contact mask/counter and controller state,
while skipping repeated physics-profile reads. Captures remain asynchronous
and read-only; transient fields may span different updates.


## Captured opponent hit without an arrest

[Retained runtime evidence](runtime/spike-contact-and-recovery.json) contains
536 samples spanning ticks8370..9070 from the existing LCOP police race on
Redrock Ridge, normal direction. Capture used `--spike-only --interval0.02`;
reads were asynchronous and did not suspend the game. The sampler was stopped
after the user reported the hit and absence of an arrest.

- Tick8437: strip0 sampled active at segment1054, arming threshold8628.
- Tick8671: strip clears; AI master1 FM50 acquires mask2, flag+621bit40,
  effect counter1 and group phase2. This closes the first actual-contact
  capture question. Model-part mapping associates mask2 with part2; anatomical
  left/right identity remains open.
- The deploying officer already targets a different racer. The hit opponent's
  group member count remains0 in every retained sample with nonzero mask.
  At contact, officer segment1068 versus opponent1053 differs by15, and raw
  opponent+6f0 exceeds0x40000000. Static00401650 nevertheless requires officer
  +624==0 before attaching human police. Its existing target therefore
  explains the missing attachment in this capture; this is corroborated
  control-flow inference, not an instruction trace.
- Tick8679: opponent controller state2 becomes5, the pull-over state.
- Tick8999: controller returns1, mask/counter/flag clear, position relocates,
  speed becomes0 and reset cooldown is31. Ticket count remains0. This is
  consistent with state5's no-officers branch00409f8d calling00409b40 and
  an accepted00429100 reset. State2 entry uses tick+320, unlike state1's
  strip-specific tick+640 branch; deadline itself was not sampled.

Melroy reported that an opponent appeared to hit the strip but no arrest
followed. Memory independently confirms contact and no ticket increment.
A strip hit therefore need not produce an arrest in this captured setup:
the deploying officer was occupied with another target. Do not generalize
that result to unassigned police or all pursuit configurations.


## Captured hit, automatic officer attachment and arrest

[Second capture](runtime/spike-contact-and-arrest.json) retains688 representative
samples (one per sampled tick) from3500..4400 after the user restarted the
same police race. Stop limit remained1. Although the instructions aimed at
an existing pursuit target, the recorded officer target was0 immediately
before contact. This capture therefore validates the **unassigned officer
attachment** branch, not the already-attached branch.

- Tick3557: strip0 active, segment347, arming threshold3748.
- Tick4019: officer target0, opponent master3 DIAB mask0 and group member0.
- Tick4021: mask3 and flag40 appear, group phase2/member1, officer target
  becomes that opponent's address005e2e24. Segment difference is8 (<20).
- Tick4028: controller state5 and sampled pull-over deadline4346. State2
  entry supplies tick+320; asynchronous sampling means the state transition
  itself occurred before the sampled global tick4028.
- Tick4131: controller state6, the stopped phase.
- Tick4327: opponent stops0->1, racer state0->4 (Busted), officer arrests
  0->1, target and group membership clear, mask/flag clear. Opponent reset
  cooldown remains0, distinguishing this cleanup from the first capture's
  no-officer repositioning/cooldown31. Controller later becomes1 then4.

The user paused after the hit, resumed at our request, then paused after
completion. The sampler was verified live throughout and stopped afterward.
This closes the bounded local unassigned-human-officer strip-hit/arrest
sequence. Existing-target contact, other role combinations, anatomical
wheel identities and exceptional contact geometry remain unresolved.


## Offline reconstruction from captured geometry

[Reconstruction script](reconstruct_spike_contact.py) reads only the retained
JSON captures and writes [results](spike-contact-reconstruction.json). It
uses the last active strip geometry and first sampled nonzero-mask vehicle
pose, transposes the matrix as in004ca160, and preserves the explicit float
store stages. Python double intermediates are not a full x87 emulator.

- Recovery capture: strip geometry tick8669, vehicle tick8671; reconstructed
  mask2 equals observed2. Clipping the transformed quad to the four test cubes
  gives intersection for wheel index1 only.
- Arrest capture: strip geometry tick4019, vehicle tick4021; reconstructed
  mask3 equals observed3. Clipping gives no cube intersections at that sampled
  pose. An independent XZ separating-axis certificate gives positive gaps
  approximately1.3674 and0.8140 for the two accepted wheel candidates. These
  gaps are in transformed coordinate units; no physical-unit claim is made.

The second result is consistent with the verified conservative plane-rejection
algorithm accepting a disjoint quad. It is not an instruction-level proof of
an erroneous live contact: sampling does not freeze the process, input fields
can span updates, and exact contact-time geometry is unavailable. It also does
not establish physical tyre geometry or the designer's intended tolerance.
Both masks are independently reproducible from nearby captured poses.


## Automatic AI deployment contract

The only resolved direct initializer callers are player input00404f30 and
AI helper00403db2. Renamed00403d30 to `DeployAISpikeStripAndAdvanceCounter`.
Its assembly passes the **current tick** in ECX at00403da3, whereas the
player path supplies tick+192. AI-created records therefore have no explicit
player-style arming delay; this has not yet been captured in-game.

The helper returns if its indexed record is already active. Index bit0
selects lane6 when set,7 otherwise. Radio selector is0/2 respectively,
with index bit1 overriding it to1. Reverse mode transforms lane to14-lane
and radio selector to2-selector. After creation it increments the low-nibble
counter only below15 (implemented as whole DWORD increment) and clears
+711 bit20. The counter is not a local deployment-limit gate.

Its sole resolved direct caller004036ae is police AI state3 transitioning
to4 after `IsVehicleOffsetOutsideEncodedSegmentBand` succeeds, provided
+711 bit08 is set. Intercept assignment004039c0 sets that flag. The verified
assignment contract requires zero configured human police, an existing
pursuit target, no group+58 intercept link, and escalation score>=4:

`group+14 + (memberCount-1) + (targetStops-2) + ((tick-group+20) SAR11)`.

Arithmetic is signed DWORD with the original overflow behavior. First
eligibility announces via radio and sets group+54 bit02; a later call can
select an officer. Candidates exclude human officers, already-targeting
officers and existing strip assignments. The chosen candidate is the first
strict minimum raw direction-adjusted segment gap in (50,3*N/4), not a
wrapped-distance minimum. This preserves the existing reverse/seam backlog.
Successful assignment sets +711 bit08 and group+58. Higher-level scheduling,
assignment execution and live AI strip placement remain unvalidated.

A later runtime scenario must use a racer-side Hot Pursuit session with AI
police. The two human-police captures establish contact behavior but cannot
validate this assignment path, whose configured-human-police guard excludes
them. No additional runtime action is currently requested.


## Assignment-to-deployment transition

The intercept command is0 with start=candidateSegment-6 (single wrap) and
span3 in both race directions. Setter00403830 writes auxiliary target+730
and the eight-byte assignment record, not active pursuit target+624.
Dispatcher00403030 command0 enters state3 only when00402fd0's interval test
accepts. For valid normalized inputs and positive span3 this is the inclusive
cyclic interval[start,start+3], four integer segment positions. Otherwise it
updates direction and uses state1. Forward/reverse movement into that window
still needs runtime evidence; the identical start formula is not proof of
identical behavior.

State3's eventual deployment gate is the signed **lane index** at+638,
not physical distance. Predicate00402f70 accepts outside the inclusive band
[7-highNibble(segmentByte13),6+lowNibble(segmentByte13)]. Equality is inside;
no reverse-mode global is consulted. Encoded byte0 creates an empty[7,6]
interval and thus returns outside for every lane, although installed-byte
reachability for this deployment context has not been checked.

Assembly0040368e..004036c0 establishes ordering: after lane-selection helpers,
outside-band success writes state4, then checks+711bit08 and calls the strip
initializer. An already-active record causes the initializer to return but
does not undo state4. A nonnull pursuit target finally overrides state to5.
These details close the static transition contract, while AI assignment
activation, lane convergence and reverse/seam execution remain open.


## Racer-side roadblock request interrupted by pursuit

User reported a roadblock announcement, then no visible roadblock. This is
separate from spike-strip deployment, which remains unobserved in this run.
Read-only local racer LSTM, Redrock normal capture shows group+54 bit04 by
tick11883. Expanded assignment sampling starts while paused at12294.

Retained `runtime/ai-roadblock-assignment.json` contains776 representative
samples, ticks12520..15025 (50ms asynchronous reads). At12540 masters6/7
receive command4 with common start258, span0, auxiliary target005e1120
(player), opposite policybytes1/0. Both reach state8 by12543. Master6 reaches
state9 by13286. Master7 switches to command2 and player-target/state5 by13555;
master6 acquires the OTHER racer005e1acc by13626, state5 by13629 and stop
state6 by14095. Both later return to patrol. Neither is sampled in state10/11
in this retained interval, so a completed stationary roadblock is not proved.
The user observation agrees with assignment being diverted into pursuit.
Do not claim instruction-level tracing or rule out brief unsampled states.

This corroborates paired assignment, travel/positioning and pursuit override
paths from00403b20/004032e0, while completed roadblock placement, reverse/seam
behavior and AI spike deployment remain open. Original capture is outside
the repository at /tmp/nfs3-ai-strip-FPDMiT/assignments.jsonl.


## Racer-side strip request without deployment before race finish

The completed local LSTM/Redrock normal run contains11482 raw samples across
ticks9..22501 (6942 unique sampled ticks). Neither an active strip record nor
police+711bit08 appears in any raw sample. The player group's strip-request
bit02 first appears at20663. This is a memory flag observation, not a claim
that the user heard a spike-strip announcement; the user reported a roadblock
request and later no visible obstacle.

At21490 the player is at segment1378 on a1463-segment track. Free officers
at526/1263/871/1254 have raw forward differences-852/-115/-507/-124, so none
satisfies the strip selector's strict positive>50 requirement. Some would
be ahead under a cyclic interpretation, but004039c0 uses raw subtraction.
After the line crossing, by22199 the player has result state3 and zero group
members; the race finished before this yielded an observed strip assignment.
This supports a specific request-without-deployment explanation, not proof
of every missed scheduling opportunity or a general deployment defect.

Retained late-run samples and full-run counts are in
`runtime/ai-strip-request-no-deployment.json`. Both samplers are stopped;
raw captures remain in /tmp/nfs3-ai-strip-FPDMiT. AI strip placement and
arming timing remain open. No game memory or executable was modified.


Runtime-backed naming refinement:00403b20 is now
`AssignRoadblockPolicePairAheadOfPlayer`. Its return1 means two assignments
were installed, not that a roadblock was completed. Comments on004032e0 also
record the observed state8/9 pursuit override and distinguish auxiliary+730
from actual pursuit+624, which can point at different racers. For the next
AI strip test, use a longer racer-side Hot Pursuit race: this run reached the
request threshold late and ended before placement. No new run is requested
yet; confirm a fresh sampler before giving gameplay instructions.


## Reconstructed pair selection and cancellation boundary

`roadblock-assignment-reconstruction.json` evaluates the verified selector
against tick12536 fields and compares tick12540 assignment bytes. Captured
police indices0..5 confirm scan order. Occupied officers2/4/5 are excluded;
free officer3 has wrapped gap-418. Officers6/7 have positive gaps252/67 and
are successive strict minima. Their segment positions351/166 yield midpoint
166+truncate(185/2)=258. Both observed command4 records contain258, span0,
direction0 and policy1/0 respectively. This sample corroborates the pair
and midpoint calculation; it does not distinguish the general record-minima
algorithm from nearest-two selection, since both select the same pair here.

Cancellation refinement: at13552 officer7/player segments220/225 give-5,
with command4,flags0410,state8. At13555 segments221/226 still give-5, while
record is command2,start0,span0,direction1,policy0,auxiliary target0 and
flags0010. Active pursuit now targets the player in state5. Direction1 agrees
with police index5 parity. These samples match00403ed0's [-N/4,-5] window
and subsequent pursuit acquisition, without proving instruction timing or
excluding earlier eligible samples. State10-specific cancellation speech is
not covered because this officer was in state8.


## Roadblock reorientation proximity gate

Helper00403180 scans005efc48/count005efda0. Registration00428700 populates
this list for human racers and AI racers at00428821/004288ae; ordinary
police and traffic branches do not. It does not locally filter racer status,
visibility or category80. Role exclusivity and list validity remain assumed.

For finite inputs,004965b0 forms binary32 absolute XYZ differences, combines
X/Y as max+0.25*min with a float store, then combines that result with Z the
same way. Reorientation requires all resulting rounded absolute estimates
to be at least240; equality passes, unordered comparison rejects. These are
position units, not established metres or Euclidean distance. The distance
helper runs twice per racer, rereading positions, so its first sign decision
and second distance can observe different live data.

Offline sampled estimates for officer6 to player/opponent are414.956/349.545
at13286,115.253/61.857 at13552, and44.776/4.832 at13626. The officer remains
state9 in those samples and then acquires the opponent. Thus this provides
proximity context only; it does not establish execution or rejection of the
state10 reorientation gate. Next successful-placement testing must capture
state10, the scanned racer positions, and transition11 before claiming closure.


## Group tactic scheduling and announcement suppression

Assembly0040379b..004037e8 requires signed wrapping tick-group+24>320,
after target/upright/no-human-police checks. It updates group+24 before any
selector. If the current officer equals group+5c, it clears that marker,
skips both tactic selectors and calls support recruitment004043a0. Otherwise
strip selector004039c0 gets first chance, then roadblock00403b20; a successful
assignment returns, while both failures fall through to support recruitment.
The timestamp advances even without assignment. A different officer does
not take the same-officer suppression branch, so this is a group timer with
a caller-specific marker, not independent per-officer timers.

`runtime/police-tactic-scheduling.json` retains the announcement transitions:
stored scheduling ticks11880/12208/12536,328 apart. The first has roadblock
announcement bit04 and caller marker6174672 (master4), the second marker0,
and the subsequent capture shows paired command4 assignment. This agrees
with the announcement/suppressed-check/later-assignment path. It does not
prove an invariant328-tick cadence or exact instruction execution times.

Support-path annotation correction:004043a0 calls midpoint helper00404340,
which supplies command3 in EBX and span8 as its first stack argument to
SetPoliceAssignment. The older caller comment incorrectly called this
command8. The corrected Ghidra comment distinguishes this support assignment
from paired roadblock command4. The captures do not establish the exact
caller for every observed command3 record.

## Longer racer-side run: first roadblock attempt

The ongoing longer Hot Pursuit run captured another user-reported roadblock
recommendation. Retained evidence is in
[long-pursuit-roadblock-announcement.json](runtime/long-pursuit-roadblock-announcement.json).
At12634 masters6/7 receive command4,start297,span0,policy1/0 and the player's
group has announcement bit04. Both are state8 by12637. Master7 changes to
command2/state5 targeting the player at13091; master6 does so at13949.
No state9/10/11 is sampled for this pair in the retained window. This again
corroborates assignment followed by pursuit diversion, not completed placement.
Later master6 command3/span8/state7 at14310, then state5 targeting the other
racer at14358, belongs to a separate support sequence. Ghidra00403b20 records
these observations. Sampling is non-atomic at50ms; brief intermediate states
may be missed. The capture continues for later strip/roadblock attempts.

## AI deployment, human front-wheel hit and nonterminal recovery

The same run subsequently captured the complete bounded sequence in
[long-pursuit-ai-strip-deployment.json](runtime/long-pursuit-ai-strip-deployment.json).
The AI racer's group first shows strip-request bit02 at24966; the human
player's group does not. This coincides with the user's reported permission
announcement, without an audio instruction trace. Master5 receives command0,
start700,span3 and flags0800 at25291; state3 appears25320. At25329 it is
state4/flags0801 and the strip is active at segment703,lane6, with stored
arming tick25326. This corroborates the AI current-tick arming contract.
The user saw the strip. Its auxiliary target was the AI racer, but this did
not prevent the human racer from contacting it.

The local LSTM player's mask changes0->3 at25987 after deliberately crossing.
Melroy reports damage to both front tyres. Together with the static steering
pair mapping, this corroborates the front pair as bits01/02 for this vehicle;
individual left/right ordering remains open. The deploying AI officer had
no pursuit target before the hit and acquires the human racer. By26055 the
player has a reciprocal stop link and the officer is state6.

At26449 the player's stop count changes0->1, remains result state0, clears
mask and stop link, and has reset cooldown31. The cooldown reaches0 by26513;
Melroy confirms control returned. The configured stop limit is9. This closes
the observed nonterminal AI-strip/player-stop sequence, not every stop-limit
or recovery path. In particular, recovery includes reset cooldown, unlike
the earlier terminal AI-racer capture; do not describe it as cleanup without
reset. Samples are non-atomic and do not establish instruction timing.

Comments at00403d30 and00401650 were updated and the project saved. The
sampler is now stopped. Reverse/seam deployment, individual wheel sides,
quantified handling effects and completed roadblock placement remain open.

### Why the player recovery includes a reset

Assembly004059d1..004059f5 supplies a separate state7 release path: when the
group stop-phase predicate returns zero, it sets controller2, clears category
bit02, and calls00429100 without testing the strip flag. This differs from
the flag-gated helper004056e0. Finalization clearing flag40 therefore does
not prevent the state7 direct reset. The reset's own refusal guards remain.

At26445 the player is controller7/category07/mask3/stops0/cooldown0; at26449
it is controller2/category05/mask0/stops1/cooldown31. Retained samples from
26436 through26458 have input_bits0. These observations and the static call
path corroborate automatic release recovery, without claiming an instruction
trace or excluding unsampled input. Ghidra00405740 now records the distinction.

### Successful officer selection reconstructed

[Reconstruction](ai-strip-assignment-reconstruction.json) uses tick25288:
AI target master1 is at352, N1463. Masters2/3 already pursue a target and are
excluded. Master4 gap761 qualifies first; master5 gap354 replaces it.
Master6 gap-315 fails and master7 gap771 is not nearer. The predicted selected
master5/start706-6=700 matches the command0/span3 record at25291.

The original AI racer's group+58 is set to officer005e417c at25291 and still
contains it at26449, after the human racer hits the strip and completes a
ticket with that officer. Thus this pointer alone does not prove an active
strip or attachment to the original racer. Its eventual clearing and impact
on future assignments remain open. Ghidra004039c0 records both the successful
selection reconstruction and this bounded lifetime observation.

### Contact bypasses one assignment-pointer cleanup path

Assembly establishes the ordering:0040165f clears officer+711 bit08 before
contact attachment004016df. Attachment0040190c tests that same bit and, when
clear, skips the old auxiliary group's+58 clear at0040192f. The observed
retention is therefore consistent with a specific skipped cleanup path.
At26537 the original AI racer's group still holds officer005e417c, although
that officer's auxiliary+730 is now0 and its assignment bit08 is clear.

Selector00403a10 rejects nonzero group+58 before scoring or allocation. Any
later invocation while this value remains will therefore return without a
new strip assignment. This does not prove permanent suppression: subsequent
group reset, indirect writes and an actual repeat-allocation attempt remain
unverified. Other explicit clears are guarded passage00403e9f and cleanup
00404187. First-attachment phase initialization00401969..0040198e clears
several fields but not+58. The bounded direct-displacement search found243
instructions containing+0x58], six in00400000..0040ffff; aliases/bulk writes
are not covered. Comments at00401650/004018b0 preserve the causal distinction.

## Reverse roadblock scan-order witness

The reverse run's user-reported roadblock announcement corresponds to
command4 assignments at12209. [Retained samples](runtime/reverse-roadblock-announcement.json)
and [reconstruction](reverse-roadblock-reconstruction.json) establish a
distinguishing case: at12205 player segment1385, N1463, free masters2/3/4 at
689/1248/1081 have reverse wrapped forward gaps696/137/304. The scan keeps
record minima2 then3. Master4 is closer than2 but does not replace it, since
304 is not a new minimum after137. Observed pair2/3 therefore differs from
nearest eligible pair3/4.

The pair delta689-1248=-559 passes the signed>=400 rejection test despite
absolute distance559. Half toward zero is-279;1248-279=969 exactly matches
both assignment records, with side policies1/0. This corroborates the reverse
selection and signed-distance asymmetry; completed placement remains open.
The snapshot is non-atomic, not an instruction trace. Ghidra00403b20 is saved.

### Reverse strip assignments cancelled by pursuit acquisition

[Reverse capture](runtime/reverse-strip-announcement.json) retains two attempts.
At19849 master2 changes from roadblock command4 to strip command0,start230,
span3,flags0910 and the player's group+58 points to it. At20358 it acquires
the other racer, enters state5, clears assignment bit0800 and the original
player group+58 becomes0. At22763 master7 gets command0,start1167,span3;
at23723 it acquires the player, enters state5 and clears the group pointer.
Neither retained attempt contains an active strip. Melroy reports hearing
both announcements but seeing neither a roadblock nor a strip.

These ordinary acquisition cancellations corroborate the old-group cleanup
path in004018b0, contrasting the prior actual-hit path that clears bit08
before attachment and leaves the old pointer. They establish two observed
cancellations, not a general inability to deploy in reverse. The sampler
continues; Ghidra004018b0 records the comparison.

### Third reverse attempt and capture endpoint

[Third attempt](runtime/reverse-third-strip-attempt.json) targets the AI racer:
master7 receives command0,start126,span3 at32309 (officer segment132).
By32315 it is at133, still state1; by33756 it is at255 and switches to
state5 with that racer as pursuit target. Thus sampled movement is toward
increasing segment indices, away from the nearby interval126..129, before
pursuit overrides the assignment. Earlier attempts similarly moved236->272
for interval230..233 and1173->1247 for interval1167..1170.

Static00403030 requires interval membership before command0 enters state3.
Outside it,00403000 passes the start segment to004028e0, which sets direction
flag+621bit10 from a negative wrapped start-minus-current delta, with no local
reverse adjustment. The complete downstream direction/speed transformation
has not yet been established; do not attribute a universal reverse defect
solely to these samples. No active strip appeared in13821 samples covering
10820 unique ticks406..35359. This is bounded non-observation, not proof that
reverse deployment is impossible. The sampler is stopped; successful reverse
placement/arming remains open.

### Reverse assignment sign mismatch

The local speed-sign chain is now resolved in assembly.004028e0 sets
vehicle+621bit10 when wrapped assignment-start minus current segment is
negative, without consulting reverse mode.00401430 computes/caps cruise
speed, then XORs its float sign for reverse at0040147e and for bit10 at
00401496. For positive finite base speed:

| Reverse | Direction bit10 | Output sign at00401430 return |
| --- | --- | --- |
| 0 | 0 | Positive |
| 0 | 1 | Negative |
| 1 | 0 | Negative |
| 1 | 1 | Positive |

Thus a nearby lower assignment start sets the bit, but reverse mode cancels
that sign reversal. [Eight retained witnesses](reverse-assignment-direction-evidence.json)
show bit10 set during the three attempts, with increasing segments away
from the lower target intervals. This closes the local sign-composition
question and corroborates the movement mismatch. It does not prove all
reverse strips fail: desired+7b0 was not sampled,0040bff0 can subsequently
adjust or replace it, and full dynamics/collision effects remain separate.
No physical speed units are inferred from+4f4. Ghidra004028e0/00401430 record
the proof and limits. Successful reverse placement remains unresolved.

### Reported absence of reverse-track pursuit U-turns

Melroy reports that oncoming police did not visibly turn around during this
reverse-track race. He also heard another strip announcement without seeing
a strip after the sampler stopped. These are user observations, not additional
memory captures; no deployment or universal reverse-track failure is inferred.

Ordinary pursuit uses `UpdatePoliceTrackRelationFlag` at00402910, which
explicitly negates the wrapped own-minus-target segment delta for reverse
at00402992. It therefore differs from assignment direction helper004028e0.
It only updates bit10 with a linked target, target+7c4 at least3.0, and
differing ordered-negative predicates of own/target+7c0. Producer00401780
builds0056ea5c from target category+200 bit04, either target+5f4==0 or
target+621 bit10 clear, then XORs reverse. Chase response004025c0 can also
change direction or detach, so this helper alone does not establish a U-turn.

A focused follow-up needs synchronized target acquisition, own/target+7c0,
target+7c4, target+5f4, direction flags and desired+7b0 around an oncoming
encounter. The current capture lacks the signed-motion and desired-speed
fields. Causality remains open; the distinction is saved in Ghidra00402910.

Melroy subsequently reported receiving a ticket in the same reverse run,
while still seeing neither roadblock nor strip. Sampling was stopped, so
this does not add a captured stop transition or resolve deployment state.

Follow-up capture preparation: sampler now decodes desired+7b0, signed
motion+7c0, motion+7c4 and direction state+5f4 from the vehicle block it already
reads. These fields add no per-vehicle memory read. Old captures do not gain
these fields retrospectively; fresh paired normal/reverse encounters are needed.
Syntax checked; process inspection found nfs3.exe PID105382 and no running
read_memory_sampler.py. No new capture started during this preparation.

### Active reverse strip finally captured

After Melroy heard a later deployed announcement, a fresh read-only capture
found an active strip at tick72596: reverse1, mode3, track1, N1463. Master4
(police index2) is state4, flags0841, command0/start357/span3, segment357,
lane4. Its auxiliary target is AI racer005e1acc, pursuit target zero. Strip
record2 is active at segment360/lane7 with arming tick72056. This establishes
that reverse deployment can succeed; the earlier three failures were bounded
observations, not a universal inability.

At72956 the human is segment366/lane6, tyre mask0, stops2; Melroy reports
being close to the strip. [Retained samples](runtime/reverse-active-strip.json)
include the first/latest observations. The initial assignment/state3/activation
transition was missed. We cannot reconstruct its approach from these samples
or infer why this attempt succeeded. The fresh sampler is live for a requested
single crossing; contact and recovery are not yet established. Ghidra00403030
is updated and saved.

### Reverse strip contact and front-pair damage

[Contact capture](runtime/reverse-strip-contact.json): at73460 the player
is undamaged with stops2/controller2. At73463, segment360, mask becomes3
and the active strip clears. Melroy reports the front tyres affected again,
corroborating the front-pair mapping in reverse as well as the normal run.
Controller changes to6 by73466 and7 by73495.

The strip owner master4 had no pursuit target before contact. At73463 its
target becomes player005e1120 and it joins the player's existing group: member
count1->2, adding005e37d0 beside005e4b28. Its prior auxiliary target remains
AI racer005e1acc at that sample. By73554 officer state5 and player controller7
are captured, but stop_link remains0 and stops remain2. Contact attachment
is established; completed ticket/recovery is pending. The non-atomic reads
do not establish exact instruction ordering within73463.

### Reverse nonterminal ticket recovery completed

[Recovery capture](runtime/reverse-strip-ticket-recovery.json) closes the
local reverse contact-to-release sequence, configured stop limit9. At73634
the player has controller7/category07, mask3, stops2 and link to master4.
At74022 stops becomes3, mask and link clear, while controller7/category07
are still sampled. At74025 controller2/category05 returns with cooldown30.
Racer state stays0. The user reports paused again; capture ends74061 with
cooldown12. The sampler was explicitly stopped afterward.

This independently corroborates nonterminal reset/release in reverse after
front-pair contact. It does not resolve left/right individual bit identity,
initial deployment approach, all handling effects, seam placement or universal
repeatability. Existing master4 attachment expanded an already occupied
player pursuit group, unlike the earlier empty-group case. Ghidra00401650
and00405740 preserve contact and recovery evidence respectively.
