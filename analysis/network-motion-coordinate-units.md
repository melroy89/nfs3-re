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

## Evidence and remaining work

Parent Ghidra readback covered the progress producer, full pair packer004c8310..004c834d, mixed-type decoder, sender, receiver, pending/display copy, correction reader and both motion/position consumers. Instruction anchors: pack stores004c8336/004c8344; pending-to-display004c82da/db; reader copies004c8078..004c8099 and subtracts at004c80a4. These are selected-program static observations, with custom register ABI retained.

**DONE:** player-update motion/progress field provenance and segment-step units of its correction delta.

**OPEN:** peer ownership and ordering, sequence/history behavior across seams, stale-reference lifecycle, reverse correction direction, physical motion calibration, actual network timing and rendered smoothing. No two-peer test or packet execution occurred.
