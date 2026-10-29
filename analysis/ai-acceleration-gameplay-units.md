# AI acceleration progress and speed-table units

## Scope

This read-only static pass follows the Normal-skill `vehicle+8 > 100` acceleration gate, identifies ordinary producers of `vehicle+8` and `vehicle+0x7c4`, traces their race-loop schedule, and checks whether `006fd50c` is a player-visible catch-up setting. Target: installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. The worker pass performed no game/runtime execution or persistent Ghidra edits; parent annotations are described below.

## Progress field `vehicle+8`

The ordinary producer is at `0042ce10`; the vehicle-update loop calls it at `0042cfd6` inside `0042ce70`. Let `N = DWORD[005dd940]`, the track segment count. If `vehicle+0x208 > 0`, the producer stores zero. Otherwise it uses `vehicle+0x1c` as the segment term, or `N - vehicle+0x1c` when `006fd4c0 != 0`, then stores:

`vehicle+8 = vehicle+0x204 * N + segmentTerm`

This is a signed integer progress coordinate in track-segment steps. The `+0x204` term contributes an `N`-sized lap-like offset, and `006fd4c0` selects the reverse-direction segment adjustment. These instructions establish the formula and unit increment; they do not establish the full semantics or valid domain of `+0x204`/`+0x208`, or any physical-distance conversion.

`CalculateAISpeedIndexedAcceleration` (`004064f0`) applies its Normal-only acceleration multiplier when signed DWORD `vehicle+8 > 100`. `CalculateOpponentCatchUpSpeedFactor` (`004090a0`) compares two vehicles' `+8` coordinates using skill-dependent gaps (10/15 in one branch and 50/70 in another). `CheckAIVehicleWithinOpeningProgressWindow` (`0040f050`) combines `vehicle+8` with `14 * vehicle+0x1fc` and compares the result with a threshold derived from segment count and a caller-supplied allowance. These uses support the progress-coordinate interpretation; 100 is not established as metres, seconds, or a percentage of a lap.

The `0042ce70` callback iterates the registered race-vehicle table, skips entries whose byte at `+0x89` is zero, and calls the progress producer only when WORD `[vehicle+0x74] != 0`. The formula therefore describes the ordinary update when that vehicle-local gate is true.

## Acceleration-table input `vehicle+0x7c4`

Two ordinary producers were inspected. The active-motion producer is in callback `0042ce70`; the AI integration producer is `004066c0`, called by wrapper `004068a0`:

1. The active vehicle update producer is in callback `0042ce70`; there signed `vehicle+0x7c0` is calculated by projecting the velocity vector at `+0xa4` onto the track-motion axis at `+0x13c`; a sign-selected magnitude-like value is stored at `+0x7c4`. This is longitudinal track-axis motion, not a 3D speed norm. Axis normalization is not established on every placement path.
2. AI integrator `004066c0`, called by `004068a0`, updates signed `+0x7c0` toward desired `+0x7b0` using its selected acceleration, then writes the sign-selected magnitude of the resulting `+0x7c0` to `+0x7c4`. This is the producer paired with the AI acceleration lookup.

`004064f0` takes `+0x7c4`, adds the stored double `-0.5` at `00536254`, converts with `FISTP`, clamps the integer index to `0..111`, and reads one of 112 floats from the per-vehicle table rooted at `vehicle+0x528`, offset `+0x2ec`. There is no intervening scale multiplication: the table uses raw `+0x7c4` units with the half-unit bias and conversion. The effective edge behavior depends on the active x87 rounding mode, which this function does not set.

A participant-measurement formatter multiplies the same field by about 2.2369 or 3.6 in two display paths. This suggests metres-per-second if the track axis is normalized. Since normalization on every placement path and the visible labels are not established here, that is an inference; one metre-per-second per table slot is not proven.

## Callback cadence

`0042ce70` is installed in the shared race callback list at priority 8 by `004c45f0`. Per-vehicle AI callback `004088f0` is installed at priority 30 by `0042c830` for vehicles selected by constructor flag gates. Race-loop helper `004c48d0` calls dispatcher `004be3a0` for that list when the low bit of tick `007d3684` is clear, then increments the tick. The dispatcher invokes registered entries without a per-second conversion or interval check.

These update paths therefore run on even race-loop ticks, subject to their vehicle gates. The inspected outer loop (`004c4e40`) does not establish a stable wall-clock interval. No updates-per-second rate can be derived from this evidence.

## `006fd50c` and catch-up labeling

The existing xref ledger leaves `006fd50c` unnamed. It is read across input, replicated vehicle/AI motion, replay, and speech paths; writers include configuration, session/menu setup, and shutdown. In `00408f10`, nonzero selects a vehicle-response branch that can modify desired speed `+0x7b0`; zero returns the neutral factor in that routine. This establishes a code-path effect, not a player-facing “AI catch-up” meaning.

The inspected menu initializer `0043f320` sets `006fd50c=0` for transport selectors 0, 1, and 2 while setting adjacent network transport state. It builds a two-choice toggle with localized text IDs. The reviewed local menu files do not supply a catch-up label for this global. Current evidence does not identify a dedicated catch-up menu choice or a single semantic owner, so the global remains an unnamed cross-path control.

## Findings and limits

Established: `vehicle+8` is a segment-step progress coordinate and the Normal acceleration test is strictly signed `>100`; `+0x7c4` is a longitudinal track-axis scalar used raw to index a clamped 112-entry acceleration table after a `-0.5` bias and integer conversion; the relevant callbacks run on even race-loop ticks.

Unresolved: physical calibration of segment steps and the `+0x7c4` axis; full meanings/domains of `+0x204` and `+0x208`; x87 rounding mode at lookup; wall-clock callback frequency; and player-visible label/ownership for `006fd50c`. No runtime comparison or timing capture was made.

## Reproducible evidence

All REA evidence below is from the exact executable identified above.

- Progress producer bytes `0042ce10..0042ce62`: `ev_eb5f1529e988264c28a138a1b4c5aaf60007028317a729d1aa54e05a0dad8e15`. Bounded raw decode: `objdump -d -M intel --start-address=0x42ce10 --stop-address=0x42ce63 '<selected nfs3.exe>'`.
- Vehicle loop bytes `0042ce70..0042cfe2`: `ev_c1b77850a2fe9a01b07197242ec03038c3de203e285bbc06fc2a6ab953fd68b1`; callback registration reference `ev_6d4596fd3f83df16ed86bcef3bfcbde30613bff1efd5439c066450a09e0f5c4c`; scheduler setup `004c45f0`: `ev_291c9ca8ccbccb7db17018a2720c41c8d59d2688ef5242e2ff67205b411b1674`.
- Vehicle callback installation `0042c400`: `ev_e82e4cb256f2342b8ce012051fcc9e981eac58eb4c53c6da06d0f37d8d3ea4350`; callback-list registration `0042c830`: `ev_2d6f054284e206897b23926b259f443feaa057f9399c8690554057dae26d449e`.
- Race-loop dispatch `004c48d0`: `ev_2594f99c8b2b00f2be6c94e785cbf406df3fe731b027476a38f6d45ec2e38314`; list dispatcher `004be3a0`: `ev_cabe2170daf041def7fd24c01459826feabc51e77212ca6405425d7afcd58d1a`; caller `004c4e40`: `ev_7753f05973a93907eb2af1926cb98734e9eceb911701c33435fdbccad0614fbd`.
- AI integrator `004066c0`: `ev_979f806ef3de28ea4c8959222c0f50409e04930f44df04b0baba45fead45cb60`; wrapper `004068a0`: `ev_6b2b87e835c0270044a2480f52ed4755a6d0b17a0c8f100c3efe649511212e9c`; table consumer `004064f0`: `ev_f804b4b261152625e806de321d216132d06182361cd395220a958d4895a65bd3`.
- Progress comparators `004090a0`: `ev_9f24417fed58c035403e8562e88b2cf55131c2f44cafe86e47f48082b060d06a`; opening-window check `0040f050`: `ev_8c3ab96d5e85343ceeb3069e499a6f502a4e5b959b3dc5920529a7f67aab0ed9`.
- `006fd50c` direct xref list: `ev_bd28197a98dcfee3c917ea0ffb0793c96cb2a2d548994f8739c40597ddbbdd44`; transport-menu initializer `0043f320`: `ev_19961182839827086b61efb63905a79799400d226938ba126e55973e4109c2fb`. Cross-path menu meaning remains unresolved in [the detailed notes](detailed-analysis-notes.md#network-transport-selection-menu-initialization).
- Conditional m/s inference and projection provenance are also discussed in [the detailed notes](detailed-analysis-notes.md#pursuit-roles-budgets-and-stop-lifecycle), with formatter evidence `ev_84880f4ed0d0b3e30a4cfe09edd47bb1238ac0be2c9e9f086dfe10aa878fbf90`, `ev_1094edef19679c9cff8631711ab193983aa381111d12d5f40468c9f8aeaf492e`, and `ev_f099c4348f9ca0daca7b21f4b9721fa9487e12519213b4e17664116a084dca94`.

Parent readback corroborated progress producer0042ce10 against original selected-executable instructions and motion callback0042ce70/AI integrator004066c0 against the shared Ghidra program. Segment-step units and magnitude-like longitudinal motion are established; physical calibration and per-second cadence remain qualified.

## Observed counter cadence in one ordinary race

The completed read-only Hometown/forward/None/TrafficOn capture provides a bounded wall-clock comparison. Its first positive-stepping block contains342samples and advances simulation counter `007d3684` from0 to2196 over34.247765seconds of monotonic sample time, averaging64.120972ticks/second. A shorter post-pause block advances210ticks over3.412413seconds, averaging61.540027ticks/second. Race sequence `007d36b0` equals the simulation counter in every retained block sample.

[Cadence evidence and segmentation rule](evidence/runtime/ordinary-race-counter-cadence.json) retain both blocks, endpoints and full raw-capture hash. The requested sample interval is0.1seconds, fields are asynchronous, and pause/start boundaries affect short-block averages. This supports approximately64counter increments/second in the longer observed local block; it does not prove a universal fixed frequency, rendered FPS, direct callback counts, physical motion units or multiplayer lead/latency timing. The known even-tick callback gate remains a separate static fact.
