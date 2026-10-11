# Continuation handoff

## Scope and authoritative state

Continue the full open/partial Astra backlog in the game-directory
SCRATCHPAD.md and analysis/astra-backlog-context.md. Close only bounded
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
Read-only sampler: analysis/runtime/read_memory_sampler.py, opens proc mem
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
Retained: runtime/reverse-active-strip.json, reverse-strip-contact.json,
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
