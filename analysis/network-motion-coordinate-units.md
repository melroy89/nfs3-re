# Network motion correction coordinate units

## Established producer-to-consumer chain

This static audit uses active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. No game, network traffic, configuration or executable changes were made.

`UpdateVehicleSegmentProgressCoordinate` (`0042ce10`) produces vehicle DWORD+8 as `vehicle204*N + segmentTerm`, or zero when vehicle208 is positive. `N` is the track segment count; the segment term is current segment or `N-currentSegment` in reverse mode. This establishes segment-step progress rather than physical distance. See [AI progress units](ai-acceleration-gameplay-units.md).

`PackLocalVehicleReplicationPair` (`004c8310`) builds four bytes from the local selected player's vehicle:

| Pair offset | Source | Encoding |
|---|---|---|
| +0 | signed longitudinal motion scalar vehicle+7c0 | x87 truncate-toward-zero helper, integer conversion, low16 bits |
| +2 | progress coordinate vehicle+8 | low16 bits copied unchanged |

`BroadcastSequencedVehicleUpdate` (`004c7bd0`) places that pair in its ordinary type11 update, alongside the sequence and input-state byte. Host and client paths additionally handle AI progress words/history differently; this report does not equate their role ownership.

The type11 receiver `ReceiveNetworkSequencedParticipantUpdate` (`004c7d30`) decodes the pair through `DecodeNetworkShortPair` (`004c8350`): the first signed short becomes a float at pending-record+0, and the second becomes an unsigned DWORD at+4. Ready pending rows at `007dd070` are copied by `ConsumeReplicatedParticipantUpdates` (`004c8250`) into display rows at `007dd010`, preserving those fields.

`ReadVehicleReplicationCorrection` (`004c8040`) uses those rows in its player-row branch (index below runtime count005efda4). It copies the motion float to correction+8, copies the progress WORD to correction+4, then stores the low16-bit difference `localVehicleProgress - receivedProgress` at correction+0c. Consumers interpret that difference as signed16. A zero received progress word locally zeroes the returned motion/delta fields; this is a helper convention, not a claim about global startup behavior.

## Meaning for the correction routines

The player-row correction delta is therefore a signed16 difference of segment-progress coordinates. The reader does not convert it into metres, seconds, a percentage or a track-normalized shortest distance. Normal lap/seam behavior still depends on the progress counters and their producers on both peers; this audit does not establish seam correctness.

`CalculateNetworkVehicleMotionScale` (`00408f10`) consumes that delta with its existing one-sided negative thresholds20/50 and response `max(0, 1+(2-d)*0.03)` on the qualified path. Those threshold and gain inputs are segment-step delta values. This connects the existing arithmetic to its source coordinate; it does not establish a universally appropriate correction strength.

`ApplyNetworkVehiclePositionCorrection` (`0040bd80`) separately clamps a requested delta to±200 and derives a track-segment placement from it. It can choose the decoded motion scalar or a track AI sample according to its role/delta gates. The compact pair thus feeds track-relative correction rather than directly supplying world XYZ in these fields. Other replication/state messages remain separate.

The motion scalar is quantized to an integer before transmission in this path. Its source and decoded value are longitudinal track-axis motion, while physical calibration and axis normalization remain qualified. No universal metres-per-second interpretation or player-visible smoothing effect is established.

## Ordinary update ordering and simulation cadence

The race-loop sequence at `007d36b0` controls this path. In the normal step branch, `RunRaceLoop` calls `004c81c0` with that sequence at `004c53d2..004c53d7`, calls the simulation-step helper `004c48d0` at `004c53e1`, then calls the type11 sender at `004c5457` only when `(sequence & 31) == 0`. It increments the sequence at `004c545c`. Other loop branches can advance simulation or sequence differently, so this is the identified normal branch, not a promise of one send every32 rendered frames or a measured time interval.

`004c81c0` admits pending-to-display consumption only on odd incoming sequence values, playback selector `006fd3a0 <= 1`, session mode other than0/1, and enabled `006fd50c`. The sender has the same playback/session/feature gates. These are separate from the simulation callback counter `007d3684` used for vehicle-list scheduling in [ghost collision feasibility](network-ghost-collision-feasibility.md).

For ordinary participant updates, the sender uses the low byte of local roster slot `007a2278` as packet byte1, the incoming sequence as DWORD+4, the packed local vehicle pair at+8, and input-state byte at+0xc. The packer selects the local index `006fd4f4` through the player vehicle table `005efa48`. The receiver uses packet byte1 to select a20-byte pending row at `007dd070`; it rejects an incoming sequence only when the stored sequence is **signed greater** (`004c7d56..004c7d59`). Equal sequences pass this comparison. Accepted records replace the row sequence, decoded pair and state byte and set its ready flag to1. This is a latest accepted record per row, not an observed interpolation queue.

Consumption loops human indices below `006fd514`, skips the local index `006fd4f4`, and copies only ready rows into12-byte display rows at `007dd010`. It clears each consumed ready flag. If no new ready row exists, it leaves that display row unchanged. A future-sequence condition can call `0042dc40` before copying; the inspected code still continues to the copy afterward. This establishes direct branch behavior without assigning a time unit or assuming helper return timing.

The host-role branch (`WORD[007a22da] != 0`) can relay a received type11 update to roster peers1 through count-1, excluding the packet's participant slot, when transport `007a22e4 != 2` (`004c7d5f..004c7d99`). Independently, a received packet for slot0 supplies the AI progress/history rows at `007dd2a0` (`004c7df3..004c7e37`). The sender's non-host branch records local AI progress in a20-row history ring indexed by signed `(sequence >> 5) % 20`; the correction reader requires an exact stored sequence match before comparing received AI progress with that history (`004c810f..004c8189`). These paths support a role-dependent progress comparison; they do not establish universal peer ownership or successful delivery.

**DONE:** normal-branch sequence cadence, equal-sequence acceptance, pending/display replacement, local-row skip, and direct role-dependent relay/history branches. **OPEN:** complete roster-to-vehicle identity across all modes, provider callback ordering, live packet timing, progress seams/reverse behavior and visible smoothing. No packets were sent and no game/runtime-memory changes were made.

## Directional seam arithmetic: bounded normal case

The wrap updater `0042cc20` compares current segment `vehicle+0x1c` with previous segment `vehicle+4`. Forward mode increments `+0x208` when previous is exactly0 and current is greater than500. A forward crossing from previous greater than500 into current0..50 instead decrements a positive `+0x208`, or increments `+0x204` when `+0x208 <= 0`. Reverse mode increments `+0x208` on the greater-than500 to0..50 crossing; its opposite crossing (previous at most50, current greater than500) decrements positive `+0x208` or increments `+0x204`. It then stores current as previous. These are exact asymmetric threshold tests, not a general shortest-path calculation.

With `N > 501`, adjacent seam segments0 andN-1, and incoming auxiliary counter0, the intended-direction arithmetic is:

| Mode | Previous → current | Wrap result | Progress before → after |
| --- | --- | --- | --- |
| Forward | N-1 →0 | increment lap/progress counterL | LN+N-1 →(L+1)N |
| Reverse | 0 →N-1 | increment lap/progress counterL | LN+N →(L+1)N+1 |

Both increase the unquantized coordinate by1 under these assumptions. At the opposite-direction seam, the updater increases the auxiliary counter, and producer `0042ce10` outputs0 while that counter is positive. Returning across the qualified intended-direction seam can reduce the auxiliary counter instead of incrementingL. Initialization `0042bcb0` startsL at0 and auxiliary at0 forward/1 reverse (`0042be1b..0042be3b`); linked-motion copy `00408520` can replace both from another vehicle. Thus startup, wrong-direction crossings and linked vehicles need their own state history.

This resolves only the arithmetic of the stated adjacent-segment seam. It does not prove actual segment numbering, jump/teleport ordering, loaded-track count agreement, packet ordering, or rendered correction continuity. On the wire only low16 progress bits survive, and the reader uses a signed16 difference; correct unquantized seam arithmetic alone does not prove synchronization at every seam.

## Requested relocation segment and reverse-mode boundary

The correction reader gives player delta `d = signed16(localProgress - receivedProgress)`. In `0040bd80`, after the global `007d3680 != 0` and vehicle `+0x184 == 0` gates, `d` is clamped to[-200,200]. The requested segment is then `s - d` (`0040bdf5..0040be04`), where `s` is the current segment. The body does not negate this requested delta according to `006fd4c0`. If `d <= 0`, it subtractsN once when the result is at leastN; if `d > 0`, it addsN once when the result is negative. This is one conditional wrap, not a general modulo operation.

That requested segment is passed to placement search `00428d60`. The search can choose another segment and lateral offset; after an unsuccessful initial candidate it advances search segments by+1 forward or-1 reverse (`00428f07..00428f30`). Both an initially accepted center and exhausted search use the original requested center path at `00428f43`; placement receives the reverse flag at `00428f6a..00428f76`. Thus reverse-aware orientation/search exists downstream, while the initial `s-d` arithmetic is unchanged.

For a same-lap, no-wrap coordinate comparison, the forward progress formula makes `d = s_local - s_received`, so `s_local-d` equals the received segment. The reverse formula instead makes `d = s_received - s_local`, so that same expression is `2*s_local-s_received`. This algebra identifies the direction question precisely; it does **not** establish the final relocated segment, a reachable gameplay defect, or the helper's complete geometry effect. Actual reverse-mode relocation, producer identity and placement-search outcome remain unobserved. No correction or binary change was made.

## Evidence and remaining work

Parent Ghidra readback covered the progress producer, full pair packer004c8310..004c834d, mixed-type decoder, sender, receiver, pending/display copy, correction reader and both motion/position consumers. Instruction anchors: pack stores004c8336/004c8344; pending-to-display004c82da/db; reader copies004c8078..004c8099 and subtracts at004c80a4. These are selected-program static observations, with custom register ABI retained.

**DONE:** player-update motion/progress field provenance and segment-step units of its correction delta.

**OPEN:** peer ownership and ordering, sequence/history behavior across seams, stale-reference lifecycle, reverse correction direction, physical motion calibration, actual network timing and rendered smoothing. No two-peer test or packet execution occurred.
