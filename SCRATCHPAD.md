# NFS III reverse-engineering scratchpad

## Current focus

Continue evidence-backed static analysis in the saved Ghidra project, prioritizing gameplay systems represented by GitHub issues #1–#15. Improve names, types and comments only when supported by code evidence. Do not implement features or modify the executable.

Detailed findings belong in `analysis/detailed-analysis-notes.md`; focused network admission findings are in `analysis/network-roster-admission.md`.

## Recent analysis state

- Traffic reactivation: `g_nInactiveAIVehicleCount` is shared across traffic, police, opponent and nonlocal vehicle-controller paths. The traffic reactivation cap uses `g_nTrafficVehicleCount - g_nInactiveAIVehicleCount`; this is not established as a traffic-only active or visible count. The saved Ghidra global comment was audited after save.
- Knockout progression: `EliminateLastEligibleResultAndUpdateOrder` clears/ranks the 16-entry profile tables, may clear eligibility and set vehicle field `+0x2c4`, then increments the WORD progression unconditionally. Direct profile indexing has no local bounds check. Its only direct caller is gated by the result path; invocation count and valid profile-ID domain remain unknown.
- Post-race records: `UpdateStoredRecordsFromVehicleResult` now names/types its vehicle pointer, returned update mask and minimum nonzero lap value. Result-bit meanings and timing units remain unverified; see the stored-record and issue #7 notes.
- Lap/race-state finalization: `FinalizeRaceVehicleStates` applies caller-supplied fallback status values across player and AI-category lists, while preserving observed states 3 and 4 under specific gates. The race-completion call passes EAX=3; numeric states are not a full enum. The lap-estimate initializer's double constants are now named and typed: 6.0 scales track segments and 64.0 multiplies the estimate numerator; units remain unknown. The lap-metric popup now has typed/named locals; its highlight index is uninitialized if no positive metric is found. Details and REA evidence are in the issue #7 section of `analysis/detailed-analysis-notes.md`.
- Controller input: recovered and named `RunRaceInputCollectionWorker` at `0041d7e4`; startup passes it as a native thread callback. It gathers bound player input only after event signals, including the race-clock callback path. The event handle is now typed `HANDLE` and documented. No wall-clock sample rate or runtime behavior is inferred.
- Serial/COM and modem: static tracing connects the COM1–COM4 menu values to the type-3 serial provider, `\\.\COM%d` opening, overlapped ring I/O, and the type-3/type-6 modem callbacks. Worker dispatch now grounds command2 as receive purge (`PurgeComm(0x0a)` plus receive-ring reset) and command3 as transmit purge (`PurgeComm(0x05)` plus transmit-ring reset); the wrappers are named and saved in Ghidra. UI callback reachability, device/TAPI lifecycle, provider selection, lock/worker teardown and real hardware behavior remain unresolved; see the serial and modem sections in `analysis/detailed-analysis-notes.md`.
- Network admission: slot-8 name-copy destination conditionally overlaps the `g_szGameIniPath` address if the first five source byte pairs are nonzero. Peer-event admission copies a 20-byte scratch payload after initializing only its first byte. These are static conditional boundaries, not demonstrated runtime corruption; see `analysis/network-roster-admission.md`.
- Network input throttle: `ShouldDeferParticipantInput` has distinct session/transport gates. With `006fd50c` set in modes 2–4, a lead comparison is executed but the branch still returns “do not defer.” Lead limits count sequences, not seconds; wrap and runtime invariants remain open.
- The network packet review records fixed-size receive copies and missing local length/index checks as conditional static boundaries. Framing, reachability and runtime consequence are unresolved.
- Ghidra project save succeeded for `/home/melroy/Documents/projects/nfs3-re/nfs3_decomp.gpr`; the open program is `nfs3.exe`. The executable SHA-256 remains `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

## Astra / runtime follow-up

- Validate network admission slot-8 reachability, source-name provenance/termination, adjacent INI-path lifetime and runtime consequence.
- Resolve whether the peer-event's remaining 19 payload bytes have indirect or provider-side consumers, and whether admission events can overlap or race.
- Validate network packet framing and delivery paths before drawing conclusions from fixed-size copies or absent local bounds checks.
- For issue #1, validate sequence-counter wrap, synchronization timing and input-provider coverage before making runtime claims about the session/transport throttle.
- Establish runtime invariants for traffic activation counters and Knockout progression/profile IDs if those questions remain important after static analysis.
- For issue #14, if a runtime pass is needed, compare keyboard and analog bindings for center/deadzone, extrema, inversion and mode transforms; separately test race-input worker wake/stop timing. Static tracing shows event-driven sampling but cannot establish wall-clock rate or teardown quiescence.

## Working rules

Keep analysis static unless a specific runtime question needs a controlled game observation. Do not write to live game memory. Keep executable changes out of scope. Record evidence and limitations in the detailed notes; treat conditional static findings as hypotheses until runtime or stronger control-flow evidence confirms reachability and effect.
