# Continuation handoff

## Scope and authoritative state

Continue the full open/partial Astra backlog in the game-directory
SCRATCHPAD.md. Historical evidence is retained in
analysis/detailed-analysis-notes.md#consolidated-context-findings. Close only bounded
questions with evidence; do not declare the whole goal complete. Work is
Ghidra metadata/docs and read-only runtime inspection. No executable, assets
or live-memory writes. No commit/push in this batch. Preserve all uncommitted
analysis and Ghidra database changes, including database file rotation.

Repo/project: /home/melroy/Documents/projects/nfs3-re, nfs3_decomp.gpr/.rep.
Persistent Ghidra MCP program: nfs3.exe. Use native Ghidra MCP to annotate
this project; REA temporary analysis is separate. Ghidra is installed at
/home/melroy/Documents/ghidra. Save through save_program after changes.
SCRATCHPAD.md lives in the game directory, outside the Git repo.

## Runtime state and collaboration

Game PID105382 was last verified running. Rediscover before using it.
All samplers stopped; exec session21560 ended successfully after Ctrl-C,
and pgrep found no read_memory_sampler.py. User paused after successful
reverse strip/ticket test. Do not claim passive monitoring is still running.
Wine prefix: /home/melroy/.local/share/winegui/prefixes/NFS3.
Runner: /home/melroy/.local/share/winegui/runners/wine-proton-11.0-2-amd64/bin/wine.
Read-only sampler: analysis/scripts/read_memory_sampler.py, opens proc mem
O_RDONLY, no suspension. Credentials must never enter docs or commits.
Start and verify samples before asking user to drive. Give one precise action
and pause point. Bounded captures expire; inspect handle and fresh rows.

## Latest closed reverse test

Earlier three reverse assignments moved away then switched to pursuit; this
was not universal failure. Later active deployment is now proven:
- tick72596, reverse1, mode3, track1, N1463: master4/policeindex2 state4,
  command0/start357/span3; strip record2 active at360/lane7, arming72056.
- initial assignment/activation transition was missed.
- tick73463 player mask0->3 at360; user confirms front tyres again.
  Unassigned strip owner joins existing player pursuit group, members1->2.
- link appears73634; ticket74022 gives stops2->3, mask/link clear.
-74025 controller2/category05/cooldown30; racer state0, limit9.
- capture ends paused74061, cooldown12.
Raw: /tmp/nfs3-reverse-deployment-kAJugn/samples.jsonl.
Retained: evidence/runtime/reverse-active-strip.json, reverse-strip-contact.json,
reverse-strip-ticket-recovery.json. Ghidra00403030/00401650/00405740 saved.
Scratch has separate Closed rows for active reverse deployment and local
contact/nonterminal recovery. Initial approach, roadblocks, seams, side
identities, handling and repeatability remain open.
User also reported oncoming police not U-turning in reverse: unresolved.
00402910 handles reverse explicitly; do not conflate with004028e0 assignment
sign mismatch. See spike-strip-runtime.md for evidence and limits.

## Pending GO18 test

User has not confirmed preparing it. Request already sent: regular solo
race, normal direction, normal registered road car, default tuning, type
GO18 before start, no GOFAST, pause during countdown. First verify actual
profile/override/category/callback/gates, then request driving.
Static route proven: selector18+483 selects501/pursuit0002; regular session0
preserves override, pursuit strips it. Same archive supplies physics text;
registered basename car ->carp.txt exists. Default tuning preserves torque21=0.
Do not use ordinary human-police selection as a501 test.
004aaed1 now UpdateEngineRPMAndComputeDriveResponse. Full dispatcher path
requires category bit02 clear,+8a0, signed rawDWORD+10c>=3f666666. Actual
torque reads additionally bypass when gear1, signedSHORT+510>0 orSHORT+164!=0.
Current RPM call004ab4c5 differs from overspeed-redline/idle calls.
A static eligible path is not a live instruction trace or a handling defect.
Details: police-torque-runtime.md; go18-archive-provenance.json.
Sampler now includes override_selector, direction_state_5f4, desired_speed_7b0,
signed_motion_7c0,motion_7c4,state_164,shift_state_510. Syntax checked, new
direction fields successfully used in latest live reverse capture.

## Physics parser findings

physics-parser-defaults.md links retained evidence:
- empty input exits before defaults; incomplete nonempty input applies defaults;
- any absent AI section resets all112 acceleration floats;
- missing field79 default erroneously writes+1b8 (field11), not+1bc;
- all47 installed profiles match all80 header slots; max normalized line450
  versus2000-byte buffer. Some final bytes are spaces after CRLF.
- full default image is1196 initialized file-backed bytes at0055f874; all
  match Ghidra. Direct operand scan found no destination writer, but writable
  data and aliased mutation remain outside that proof.
- direct loading chain is locally synchronous, not a global thread guarantee.
- abort policy initial1; HandleGameAbort can return for recursion guard or
  suppression callback0, otherwise normal path terminates. Actual suppressed
  missing-entry continuation in race loading remains unproved.
Named004b1380 ParseCarPhysicsTextProfile,004b0940
MatchCarPhysicsHeaderToDescriptorSlot,004b09d0 ReadNormalizedCarPhysicsLine,
004b0900 IsCarPhysicsValueLine. Last classifier accepts first digit or minus
only in saved character table; it is not full numeric validation.
Comments saved at defaults004b0bb0, abort00401010 and wrapper004ea290.

## Next work

If user prepares GO18, capture that first. Otherwise continue open contracts
in SCRATCHPAD, including parser malformed input/ownership, network lifecycle,
series actions, collision, traffic, capacities and secondary historical work.
Do not repeat already captured normal/reverse spike hits. Remaining parser
work can trace suppressed-abort callers, allocation/entry bounds and shared
state ownership. Latest abort and classifier findings have been saved.
Executable last verified SHA256:
2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb.

Final allocator refinement:004e1620 clamps working payload0..7 to8; zero
request is not automatically rejected. Original size remains in metadata
and physics copy/parser arguments, so empty-input early return still applies.
Comment saved; physics-parser-defaults.md updated. No new runtime capture.

Zero-byte copy refinement completed: all three direct forward backends
return without payload access at count0, including alignment prefixes.
004ea4f0 comment and parser report saved. Remaining missing-entry question
is actual suppressed-error reachability, not zero-count copy behavior.

## Static continuation after runtime shutdown

The user may close the game; no sampler is running or needed for current
static work. New uncommitted Ghidra/database and report changes follow the
saved commit. Resource wrapper normal-return policy restoration is verified
and has a bounded Closed row in SCRATCHPAD. Global/nonlocal restoration and
parser reentry remain open: optional loading services audio callbacks,
timed callbacks, job-provided completions and alertable sleeps under policy0.
Two Luna workers are tracing completion-target provenance and TRN/KOT
caller file-admission checks. Parent alone applies annotations and saves.

New names include resource callback registration00518040, async I/O
initialization004f0da0, pathfinder sound start004e6f0c, audio top-up request
004ff670, TRN/KOT preparation import00446800/004465e0 and local car archive
shape metrics00488a80. Preparation import copies0x20f0 only after identifier
resolution, without a local loaded-length check; failure discards partial
resolver writes in the heap buffer. Upstream admission remains unresolved.
See detailed-analysis-notes.md and physics-parser-defaults.md for evidence.

Frontend/secondary continuation: recovered button render callback004607c0
and reverse navigation00449f30 plus cursor placement00449ea0. Offline
racenow disable stores in initializer0044efd0; render refresh requires
network host. Local helper contracts are closed in SCRATCHPAD, but descriptor
registry binding and lifecycle/retention remain open. Current table bytes
show postgame name00537d94 at00556038 and initializer at00556044; do not
mistake this registry for runtime descriptor layout without parser proof.
A third Luna worker now reviews camera/CCM independently. Other workers
cover registry binding and FFB period producer; parent applies all changes.

## Latest static continuation

Saved Ghidra proof refinements for multiplayer type5 framing004c6080,
music stream ownership004e4b50, camera increment00422610, recovery
countdown00429260, same-update impact ordering0042b780 and sound host
callback004e1adc/voice progression00500c80. Relevant reports:
contact-recovery-countdown-contract.md, ccm-camera-contract.md,
runtime-menu-hang.md and detailed-analysis-notes.md. SCRATCHPAD includes
bounded Closed rows for camera increment, recovery cadence and installed
DLL callback route. Wider runtime outcomes remain open.

REA target remains eacsnd.dll; persistent GhidraMCP target is nfs3.exe.
Installed DLL callback chain: setter004013d8 argument5 ->0040a914,
fill00402110 -> host004e1adc ->00500c80. Backend fill eligibility/cadence
and historical slowdown cause remain unresolved. Game need not run now.
Multiplayer worker is tracing004f6b00 provenance for connection+10/state+4
configured length cap; previously inspected initializers did not establish it.
Changes remain uncommitted; preserve rotating Ghidra database files.

## Sol and Luna boundary for later Astra work

User clarified that the current session is Sol6.1. Straightforward
static contracts and conservative names continue here with Luna;
complex unresolved contracts stay Open/Partial for Astra. Do not
repeatedly expand difficult branches merely to avoid a handoff.

- Camera finish transition: constructor00422cf0 enables request17
  only from modes1..7,11..13. Determine ordinary runtime eligibility
  through00422610 and lifetime at00426680. Capture base pointer/mode,
  scene+4/+8,+69, vehicle flags/status and fields+110..11c before/after
  finish. Conditional mode19 target/rate/effect aliases are documented
  in ccm-camera-contract.md; no actual stall has been shown.
- Render arena: configured8MiB allocation, capacity0x7fff9c. Viewport
  entry004bc470 resets cursor; builders accumulate within a viewport.
  World-effect builder alone is at most600*160 bytes. Astra should
  establish aggregate builder maxima and pre-write capacity invariants,
  including weather/spatial batches; existing peek/commit ordering
  does not prove a runtime overflow.
- Weather: enable flag006fd4cc gates a separate track-source byte
 008ca1e8; zero-extended byte modulo3 yields mode0..2. Rain/snow
 identities need actual HRZ/WEATHER.FSH or observed mode/appearance.
 Do not infer atmospheric names from numeric renderer branches.

Latest Ghidra names include InitializeRaceViewportSceneRecords,
AdjustViewportScaleSettingAndExtent and AdjustScaleSettingsForLocalViewports.
Project saved, changes uncommitted. No game runtime needed for these
static findings; future captures must be live before player instructions.

View toggle labels deferred after bounded Sol/Luna review:00484260
changes006fbc50-class settings (action12/13),00484450 changes
006fbc5c-class settings (action11),004844c0 rebuilds view/HUD
quad state and00422aa0 gates eligible view behavior. Exact visible
feature identity lacks direct menu/asset mapping; retain numeric
fields rather than assert mirror/HUD/camera names. Astra can use
controlled individual action presses with setting/quad snapshots
if static menu binding remains insufficient.

Integrity refresh: executable SHA256 remains
2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb;
eacsnd.dll remains
63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3.


## Astra audio validation entry points

See [audio conversion contract](audio-conversion-contract.md) for the current
resolved/remaining split. The x87 stack question is deferred after bounded
review of all direct reader bodies; do not repeat those listings as new evidence.

1. Establish the actual DLL callback ABI and dispatcher entry state for
   converter004e1ae4 and signed16 helper005008a0. The helper grouped path
   pushes eight x87 values before any pop; the reviewed direct callers do
   not initialize the stack. Absence of local setup is not a fault.
2. Prefer an isolated instruction-equivalent check with controlled x87 tag
   word/control word and valid disjoint buffers. Distinguish empty-stack
   success from deliberately occupied-stack behavior; neither proves game
   reachability. Keep such checks separate from installed runtime evidence.
3. If actual runtime validation is necessary, prepare a bounded capture of
   the incoming x87 tag/control state at the converter and actual conversion
   count/format. Memory-only polling cannot establish x87 register state.
   Describe any tracing overhead before asking Melroy to play; avoid an
   unbounded trace or another progressive audio/menu slowdown. No binary
   patches, live-memory writes or arbitrary audio settings changes.
4. Separate allocation-base/subrange callback arguments from numeric tests.
   Record original count, start/end, allocation pointer and working pointer
   for a naturally occurring conversion before claiming a reachable issue.

Conditional rate selection, finite final pitch truncation and zero/INT_MIN
factor results are resolved locally. Full ownership, input admission and
exceptional numeric equivalence remain Open.


## Original frontend scope remains open

SCRATCHPAD now explicitly indexes the historical dialog/cursor/profile
contracts, which were not closed by the series-terminal button work. Retain
choice count and row-height admission, callback/index/close-byte ownership,
AL-only validator ABI, mode4 layout/count schema, tooltip timing/state,
profile insertion/list/file capacities and string-arena ownership.
Starting addresses and exact questions remain under the historical unresolved
contracts in detailed-analysis-notes.md. Review those questions individually
before any closure; ordinary successful menus do not establish all bounds.


## Secondary ledger coverage

Read-only Luna audits and parent source review expanded the generic historical
row into explicit Partial items for DirectInput/force-feedback, cones/cached
surface geometry, scene/effect callbacks, and aggregate render/weather pools.
These rows preserve original unresolved scope; they do not represent new
closures or a change to the goal. Focused camera/render/weather reports state
the narrower established findings. Hardware outcomes, global ownership and
full numeric equivalence remain Astra work.


## Latest ledger reconciliation

Personality/palette and car/track-capacity rows now read Partial because
existing bounded findings were already established. Their complex residuals
remain Astra work. Focused reports personality-selection-contract.md and
track-width-contract.md distinguish live assembly verification from saved
resource inventories. Ghost producer/loader boundaries are in
pose-ghost-contract.md; endpoint convention and lifecycle remain unresolved.
No runtime capture is needed for the completed documentation reconciliation.


## Status meaning after reconciliation

The network motion, admission/provider, collision/recovery, escalation,
audio-conversion and frontend rows now read Partial, since each already
contains established bounded findings alongside explicit residuals. This
is status normalization, not six completed investigations. No broad row
was closed. The generic secondary historical audit stays Open because
its full preserved scope has not been exhaustively reconciled.

Next Astra work should address a specific remaining contract with its own
evidence requirement, rather than repeating the local proofs now indexed.
The goal remains active. No current gameplay or sampler is implied by these
static/documentation passes.


## Preserved historical scope gaps

Direct review of the historical unresolved section restored explicit table
wording for RAS/role-election contracts, NPS type/header/registry admission,
orientation correction bounds, frontend parser/callback ownership, STRM
generation/locking,17-entry setup normalizer provenance and unidentified
spatial-cache payload. These topics were previously hidden behind broad
umbrella wording; none is resolved or removed. Starting addresses remain
in detailed-analysis-notes.md#historical-unresolved-contracts.


## Saved-state integrity check

Ghidra save_program(nfs3.exe) succeeded after the latest annotations.
Current installed binary hashes still match the baseline recorded above:
nfs3.exe2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb;
eacsnd.dll63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3.
All48 Closed ledger rows have explicit evidence links; linked repository
files/anchors were checked. This verifies traceability and preservation,
not the full substantive proof of every historical claim.36 Partial rows
and the historical umbrella remain unresolved; the overall goal is active.
Uncommitted report and rotating Ghidra database files are intentionally kept.


Luna historical coverage audit additionally restored explicit ledger scope
for performance timing/result persistence, spatial audio, music resource/fade
semantics, timed-event record/contact geometry, surface-query ABI, frontend
file/render/token history, adaptive sorting and general stream cancellation.
These are unresolved questions, not new discoveries or closures. Original
entry points remain in the historical section; table counts are unchanged.


## Result notification bounded closure

Parent verified0044ea60 full assembly/jump table and normal-return ECX
preservation through00500e20/004ffc9c/00500e7c. A bounded Closed ledger
row now covers local slot bound, numeric priority, one-group attempt and
post-attempt flag consumption. Larger record/audio contracts remain Partial.
Latest names: UpdateStoredRecordsFromVehicleResult00450fe0,
ConsumePendingResultAnnouncementFlags0044ea60,
StartIndexedResultAnnouncementSound004c9990 and
CheckResultAnnouncementVoiceExpired004c99f0. All saved/read back.
See stored-records-contract.md and race-completion-contract.md.
Earlier ledger counts are snapshots; this closure adds one Closed row.
