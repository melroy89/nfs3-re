# Police torque profile reachability

Target: `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Addresses refer to the saved `nfs3_decomp` Ghidra project, x86 image base `00400000`.

## Question and corrected test design

The earlier backlog identified a doubled comma in the AI police `TRAFFIC/PURSUIT/0002/CAR.VIV` physics torque field. Static parser analysis predicts zero at torque index21, corresponding to5376RPM in `004a8a99`. This is not sufficient evidence of a gameplay defect: the profile must reach a controller that actually consumes that table.

An ordinary human-police selection does not automatically use this AI police profile:

- `00473722` selects player-one settings; `00473734`/`0047373d` copy the selected registry model into participant+14.
- Hot Pursuit calls the human constructor at `0047471f`, tests the model police flag at `00474729`, and adds the police role at `00474732` without replacing the model.
- This local human-police branch sets AI police count to zero at `00474749`, six AI opponents at `0047474f`, and one traffic record at `00474755`. Allocated traffic and active traffic are distinct.
- Archive resolver `0042c950` distinguishes registry models0..49 (`0042c9d9`–`0042ca01`) from special police models500..599 (`0042ca06`–`0042ca32`). Separate AI police constructor `00473890` selects501 for track1/5 when its variant predicate is zero.
- Archive override flag006fd4fc bit02 can select501 through an alternate path, but Hot Pursuit clears that flag and its selector at `00474c3a`–`00474c4a`. This review does not exclude later override writers or modified resources.

## Observed human-police baseline

Melroy selected Diablo SV police, Hot Pursuit, Redrock Ridge. Live track selector was1 and session mode0. An elevated sampler opened `/proc/<rediscovered game PID>/mem` read-only and used `pread`, without suspending the process or writing its memory.

The bounded interval66.077591–104.996331 seconds from sampler start contains1911 eight-vehicle snapshots:

- Local vehicle005e1120 was model21, resource`LCOP`, category0x24; physics profile005eabe0.
- Physics callback was004ae4c1 throughout. In all1911 snapshots, categorybit02 was clear, byte+8a was zero and signed raw+10c met the full-drivetrain dispatch gate. This establishes sampled state, not execution of a particular instruction.
- Torque samples20/21/22 were581.0/600.0/596.039978; sample21 remained600.0 throughout.
- EngineRPM samples ranged0–7400, including11 snapshots in5120–5632. 1263 snapshots had squared sampled velocity magnitude greater than1; no physical unit is assigned to that threshold.
- The roster contained the human police car, six AI racers and one inactive traffic record at the inspected baseline. No sampled model was501.

The human-police run therefore corroborates the model/controller distinction and does not reproduce or disprove the separate AI501 table anomaly.

## AI-police live profile confirmation

Melroy then selected an ordinary racer on Redrock Ridge, Hot Pursuit, traffic Off, and reported pausing during the countdown. A retained [baseline snapshot](runtime/ai-police-torque-baseline.json) has tick376, track1, session0 and eight registered vehicles. Local vehicle0 is model6 (`FM50`) with full-physics callback004ae4c1.

Four police vehicles (master indices3,4,5,7) are model501, resource`0002`. Each has live torque sample21 equal to0.0 and physics callback004088f0 (`ProcessAIVehicleDynamics`). Two other police vehicles use model504/resource`0005`; the remaining vehicle is an AI racer. Thus the malformed AI501 table entry survives normal startup in this installed build.

This closes the live loading/persistence question for the observed roster. It does **not** demonstrate a torque-related driving defect: the sampled AI police callbacks bypass the full-drivetrain torque interpolator. Ordinary human police uses a different registry profile, as established above. A legitimate alternative path consuming this exact profile through the full drivetrain remains unproven; such a test should not be presented as routine human-police gameplay.

## Human-police stop completion

While this run continued, a second sampler added simulation tick, pursuit target/group, reciprocal stop links and stop counters. The first arrest was already complete when this expanded capture began; its transition was not observed. The second arrest was captured. Selected observations are retained in [runtime/police-stop-observations.json](runtime/police-stop-observations.json).

| Sample tick | Human officer | AI target (master index2) | Shared group |
| --- | --- | --- | --- |
| 6818 | Completed stops1; target005e2478; no stop link | Stops0; racer state0; no stop link | Members1; processing counter0 |
| 6826 | Reciprocal link to target; police flags0x80 | Reciprocal link to officer005e1120 | Processing counter1; deadline7014 |
| 7017 | Completed stops2; target/group/link cleared | Stops1; racer state4; link cleared; cooldown7976 | Members0; processing counter0; fields+14/+1c cleared |

The sampled configured stop limit was1. Assembly of `FinalizePoliceStop` confirms officer+2cc increment at00402039–00402046, target+2c8 increment at00402060–00402075, target state4 at0040209e, reciprocal link cleanup at004020bc/004020ce and group cleanup at004020ed–004020fb. The observed cooldown7976 is consistent with completion tick7016 plus row-one value960 at005521c4; this is an inference, not an observed instruction timestamp. The human stop deadline uses a192-tick offset in `BeginPoliceStop`; asynchronous observations do not identify its exact invocation tick.

This corroborates one human-police/AI-racer terminal stop lifecycle. It does not establish player-racer arrest presentation, repeated acquisition after terminal state, maximum ticket counts, multiplayer ownership or all cancellation paths.

## Player-racer first ticket and return of control

Melroy reported receiving a first ticket, regaining control, driving briefly and pausing. The restarted sampler captured completion from the already paused stop; it did not capture pursuit acquisition or entry into the stop. Selected samples are retained in [runtime/racer-ticket-completion.json](runtime/racer-ticket-completion.json).

| Sample tick | Player category | Player stops / racer state | Stop linkage |
| --- | --- | --- | --- |
| 5580 | `0x07` (temporary AI bit set) | 0 / 0 | Reciprocal link to officer index2; two group members and processing count2 |
| 5669 | `0x07` | 1 / 0 | Reciprocal link cleared; group membership/processing counts zero; cooldown6628 |
| 5671 | `0x05` (temporary AI bit cleared) | 1 / 0 | Link remains clear |
| 5864 | `0x05` | 1 / 0 | User reports driving and pausing; sampled velocity is nonzero |

Configured stop limit was3, so this first ticket did not set terminal racer state4. Control callback00431430 and physics callback004ae4c1 remained unchanged across all four retained observations. The release is consistent with clearing the temporary category bit, not replacement of these callback pointers. The observed intermediate state separates ticket finalization from control release; the two-sample tick difference is not a universal timing guarantee.

Officers2 and5 were both in police state6 during the stop, then returned to state1 with cleared target/link fields and each had officer completed-stop count1. The player acquired only one ticket. This corroborates the distinction between group participation, individual officer counters and the target's ticket count. Cooldown6628 is consistent with inferred completion tick5668 plus row-one960; asynchronous sampling does not prove an instruction timestamp.

This validates one nonterminal player-racer ticket completion with user-confirmed return of control. Terminal third-stop behavior was subsequently captured below; repeated terminal acquisition and all cancellation paths remain untested. The sampler had expired during the earlier absence and was explicitly restarted before this observed completion; no missed interval is counted as captured evidence.

## Evidence and limits

The local temporary captures are `/tmp/nfs3-astra/torque-live.jsonl` and `/tmp/nfs3-astra/pursuit-live.jsonl`, produced by successive versions of `/tmp/nfs3-astra/sample.py`. These files may disappear. The torque summary above is bounded explicitly so later samples do not silently change its counts. Sampling targets50Hz but actual intervals depend on scheduling. Reads across fields/vehicles are not atomic; startup transitions are included, and callback pointers/dispatch conditions are not instruction-level traces. No executable or asset bytes were changed.

Remaining torque question: establish whether an unmodified, reachable path ever consumes the AI501 profile through the full drivetrain. Loading/persistence and its ordinary AI callback have been observed; changing the game to force a different callback would be a separate experiment, not evidence of normal reachability.

### Second player-racer ticket

The same capture also recorded the user-reported second ticket. At sampled tick8576 category changed0x05->0x07; the reciprocal stop link appeared by8605. At8997 the target stop count advanced1->2, the link cleared and cooldown became9892; racer state remained0. At8999 category returned to0x05. The configured stop limit remained3. This independently corroborates nonterminal release after the second ticket; the terminal third stop was subsequently captured below. Selected evidence: [runtime/racer-second-ticket.json](runtime/racer-second-ticket.json). Tick differences describe these asynchronous observations, not guaranteed update delays.


### Third stop: terminal player arrest

Melroy reported “Busted” on the third stop. The same read-only capture shows temporary AI category0x07 at sampled tick10695, reciprocal stop linkage by10702, then at11100 target stops2->3 and racer state0->4. Category was0x05 again, the reciprocal link cleared, group membership/processing counters were zero and cooldown was11860. Control00431430 and physics004ae4c1 callback pointers remained unchanged. Selected evidence: [runtime/racer-terminal-arrest.json](runtime/racer-terminal-arrest.json).

This directly corroborates the configured limit3 terminal branch in `FinalizePoliceStop`: the first two tickets leave racer state0; the third sets state4. Clearing the temporary AI-control bit also occurs at terminal completion, so that flag alone does not imply that ordinary driving has resumed. No intermediate category0x07/state4 sample was observed; sampling cannot establish that no such intermediate state existed.

The scenario now covers two nonterminal ticket releases and one user-confirmed terminal arrest in the same local racer run, alongside the earlier human-police stop observations. The beginning of the first stop was missed while the previous sampler had expired; its completion and the later stops were captured. Post-terminal reacquisition, unusual stop limits, multiplayer and cancellation paths remain unresolved. The sampler was stopped after preserving this evidence; the game was left running.

## GO18: built-in candidate for full-drivetrain reachability

Static verification identifies a testable unmodified route, not yet a runtime
result. Menu parser004524e0 accepts GO followed by two decimal digits0..21
in session0/1 and race mode0/3. GO18 sets006fd4fc bit02 and selector006fd500=18.
Archive loader0042c950 adds483 for selectors17..20 (0042c993/0042c9a4),
so18 resolves model501 and the previously verified pursuit0002/car.viv mapping.
Regular roster00473ea8..00473eb9 clears the override only when session!=0;
Hot Pursuit00474c3a..00474c4a retains onlybit10 and zeroes the selector.
Therefore the targeted scenario is a regular single-player race, not pursuit.

The loader substitution does not itself prove physics-profile ownership.
Initialization0042bd03..0042bd23 copies three override model words into
config+5c..64; this block alone does not establish every subsequent category
or profile mutation. Dispatcher004ae4c1 routes category+200 bit02 to AI
dynamics, otherwise reaches004ad7a3 only when+8a is zero and signed raw
DWORD+10c>=0x3f666666. Its resolved direct call004adc0a invokes004aaed1.

Next runtime test: regular single-player race, normal direction, default
tuning, GO18 entered in setup, no GOFAST, paused during countdown. Before
requesting driving, verify override/index, actual human profile and torque[21],
category, callback+608 and dispatcher gates. Then capture engine RPM and
derived drivetrain outputs during acceleration. A profile match or eligible
callback alone is not an instruction-level call trace. Full-drivetrain
consumption and handling consequences remain open. Ghidra0042c950 records
the route and its limits.

### Override archive supplies physics text

The local source chain is resolved:0042c700 calls override-aware0042c950
before0042c350. The latter installs vehicle+528 and calls0042c2a0; at0042c2bd
that function reads global archive00553070, extracts the requested entry,
and at0042c2fe passes its bytes to parser004b1380 with destination[vehicle+528].
The override is therefore not limited to appearance. The entry filename still
comes from the original descriptor model+14 basename in0042c350, so matching
entry availability and subsequent tuning remain relevant. An unchanged roster
model ID alone cannot disprove replacement physics. Ghidra0042c2a0 records
this static provenance; live GO18 profile and execution remain unverified.

### Registered-car filename compatibility resolved

00439300 returns literal `car` for a registered starting model. Raw Ghidra
bytes verify templates00537330=`%sp` and00537334=`%s.txt`, yielding `carp.txt`.
The installed pursuit0002 archive contains that exact entry at offset120,
length5014, within its validated extent. [Archive provenance](go18-archive-provenance.json)
retains hashes and member bounds. Thus the original descriptor basename does
not prevent this physics substitution for a registered starting car.

The tuning function004a78d6 skips engine shaping at default engine tuning.
Its already-reviewed finite nondefault shaping preserves a zero torque sample
for installed501 idle900/redline6000 (A16,B26,denominator10); GOFAST is not
needed for this test. This closes local filename compatibility, not runtime
activation or full-drivetrain consumption. Ghidra0042c350 is saved.

Capture preparation: the read-only sampler now records override selector006fd500
and vehicle signed state+164 / shift state+510 in every mode. These distinguish
the004aaed1 free-rev branch (gear1, positive shift state, or nonzero+164) from
its torque-interpolation branch. Existing RPM, gear, profile and dispatch fields
remain available. Syntax checked; no live GO18 capture has been made.

### Full-drivetrain entry versus actual torque interpolation

Renamed004aaed1 to `UpdateEngineRPMAndComputeDriveResponse`, retaining its
original ABI and adding an evidence plate. Assembly004ab13f..004ab162 bypasses
all three interpolation calls when gear byte+50b==1, signed short+510>0, or
short+164!=0;004ab3fa jumps to the final resistance/return path. A stationary
rev or countdown sample alone therefore does not establish torque consumption.

With those gates clear, after the gear helper,004ab493 uses profile redline
when entry RPM exceeded redline; otherwise004ab4c5 uses current engine RPM.
A later below-idle case at004abc75 can replace the result using idle RPM.
Thus the501 hole at5376RPM requires the current-RPM call, not simply any
interpolation call. Later clipping/scaling/replacement also means a zero
interpolated sample does not prove zero final response or a driving defect.
The sampler captures the gate fields; non-atomic snapshots still do not
constitute an instruction trace.
