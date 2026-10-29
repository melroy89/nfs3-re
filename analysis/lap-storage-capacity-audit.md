# Lap-count admission and per-lap storage audit

## Scope and evidence

Target: PC nfs3.exe SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Parent live Ghidra review of004ce280/004ce5a0 corroborated the old-index timing store, signed metric fence, count-controlled initializer and index8 aggregate alias.

This audit follows the decoded lap-count DWORD `006fd4b4` into live vehicle lap bookkeeping, the initializer, race progression, and saved-result storage. It uses the shipped `nfs3.exe` static findings recorded in [lap-count-producers.md](lap-count-producers.md), [stored-records-contract.md](stored-records-contract.md), and the Issue #7 trace in [detailed-analysis-notes.md](detailed-analysis-notes.md#decoded-lap-count-direct-reference-census--issue-7). No runtime execution or executable/database modification was performed.

## Admission into gameplay

The decoded total is a DWORD. The ordinary frontend decoder reads only the low WORD of a separate selector at `006fd4b0` and maps selector values `0`, `1`, and other to totals `2`, `4`, and `8`. In the normal setup menu loop, `ReconcileRaceSetupMenuConstraints` runs before input/action dispatch. Thus, when that reconciliation path controls race launch, the per-lap indices requested by the total are `0..1`, `0..3`, or `0..7`.

That is not a universal admission rule. Other observed writers are: mode 1's `2` or `4`; mode 2's `2`; a zero-extended network packet BYTE (0..255); and the supplied transport setup's full DWORD from `-LAPS`. The `-LAPS` parser has no local 2/4/8 comparison, although the ordinary setup loop later normalizes the selector before a UI-driven launch. Type-2 network settings copy the wire BYTE directly into the DWORD, and the packet path itself does not establish a gameplay cap. Replay/ghost bulk-copy paths and the playback-loaded handoff also remain outside a proved common validation gate. See the producer report for ordering details and limits.

## Live lap index and progression

`InitializeVehicleRaceState` (`0042bcb0`) clears vehicle `+0x204` and initializes adjacent DWORD `+0x208` to 0 forward or 1 reverse. `UpdateVehicleTrackWrapCounters` (`0042cc20`) changes `+0x204` at directional track-boundary transitions when the `+0x208` condition permits it; its wrap bookkeeping has no comparison with `006fd4b4`. `CopyLinkedVehicleMotionState` (`00408520`) copies both counters from linked object `+0x624`, so the initialization and geometry path are not the complete writer set absent a linked-object lifecycle proof. The traced fields are DWORDs; the selector's low-WORD decoding and the packet's BYTE width do not make the live index a WORD or BYTE.

`UpdateParticipantLapProgressAndRaceState` (`004ce280`) copies the current DWORD `+0x204` to `+0x234`. Its metric update checks signed `+0x234 >= 8` and skips the `+0x298 + 4*i` float store in that case; there is no corresponding lower-bound test. A distinct lap-transition path stores the prior tick at `+0x240 + 4*oldIndex` without a local upper-bound test, then updates `+0x234`. Completion compares the new index for exact equality with the decoded total, subject to its state and flag gates; this is not an admission clamp. Therefore UI totals 2/4/8 fit the metric indices 0..7, but only if the live index remains in that range. No static check enforces that invariant at these stores.

The two base offsets are `+0x240` and `+0x298`, a difference of `0x58` bytes or 22 DWORD strides. Consequently timing index 22 aliases metric index 0 by address arithmetic. This establishes a conditional overlap point, not a declared 22-element timing array or an allocation size. A count of 23 or more would reach that address in raw-count loops, but neither reachability nor backing extent is established.

## Initializer and consumers

`InitializeRaceLapEstimates` (`004ce5a0`) is called from `FinalizeRaceVehicleStates` (`004ce750`) at `004ce7c9` for an AI-category record when its `+0x200` bit `0x10` is clear and its `+0x2c4` status is not 3. Status 4 qualifies. The initializer uses the decoded signed count directly in loops over timing entries `+0x240 + 4*i` and metric entries `+0x298 + 4*i`; there is no local count clamp. Its metric loop seeds aggregate `+0x2b8` from metric entry 0 and then processes the requested count. Since `+0x298 + 4*8 == +0x2b8`, count 9 or greater makes the indexed metric sequence address the aggregate field. Again, this is a proven offset alias and conditional access, not proof of allocation or of an admitted count reaching it.

The lap-time popup (`0046d180`) and `UpdateStoredRecordsFromVehicleResult` (`00450fe0`) also scan timing entries using the configured count without a local upper cap. The popup seeds from entry 0 even for nonpositive counts. The result updater selects the minimum nonzero per-lap time and stores aggregate values into the saved-record path; it does not allocate or store one saved-record slot per lap. The metric popup scans the configured metric count and has the local eight-index-related layout concern recorded in Issue #7 notes.

For a positive ordinary UI total of 2, 4, or 8, the initializer's requested metric indices are 0..1, 0..3, or 0..7, all before the known `+0x2b8` alias at index 8. This is a sufficient index-domain statement for avoiding that specific alias and the callback's `>=8` metric fence. It does not prove the independent `+0x240` backing allocation is large enough, guarantee the live index domain, or bound every consumer.

## Separate capacities and counters

| Object | Observed extent / rule | What it means |
| --- | --- | --- |
| Live timing sequence at vehicle `+0x240` | DWORD stride; count-driven accesses; no local upper check in initializer, transition store, popup, or result scan | No declared extent proved. `+0x298` begins 22 strides later, so indices 0..21 precede that neighboring region by address arithmetic only. |
| Live metric sequence at vehicle `+0x298` | DWORD/float stride; callback rejects signed index `>=8`; initializer has no local clamp; index 8 aliases `+0x2b8` | Callback fence bounds that callback store, not initializer or the whole field. Ordinary 2/4/8 totals request indices 0..7. |
| Live lap state `+0x204`, `+0x208`, `+0x234` | DWORD fields; `+0x204` is initialized, geometry-updated, and copied from a linked object; `+0x208` participates in wrap bookkeeping | These are counters/state, not array capacities. The wrap code does not compare against total laps or saturate at it. Exact lifetime and all indirect writes remain open. |
| Saved-record row | `0x31c` bytes; 10 rows per database block | Record slots, not lap slots. Insertion replaces index 9 only when count equals 10; qualification does not prove count is in 0..10. The updater stores summary fields, not a row per lap. |
| Result snapshots | 16 rows per category, each `0x9ac` bytes; two categories | Participant snapshot capacity, not per-lap capacity. Copy helpers lack a local 16-row admission check. |
| Menu selector / network field | Selector low WORD decoded to 2/4/8; network decoded total transported as BYTE | Input representation widths, not live index width or storage extent. |

## Bounded conclusions

- **Sufficient ordinary-menu lap domain for known metric accesses:** totals 2, 4, or 8, provided the live progress index corresponds to laps `0..N-1`. These totals stay below the `+0x298` index-8 alias and within the callback's eight-index metric fence.
- **Not established:** a universal maximum total, the actual allocation extent of `+0x240`, a common pre-initializer admission gate for network/replay/supplied values, or a hard bound on the live lap index. No universal “22 laps” or “8 laps” storage capacity follows from current evidence.
- **Counter width:** live progress and wrap fields are DWORDs; total laps are a DWORD. No WORD lap counter or total-lap storage was identified in these traced paths. The selector uses low-WORD semantics, while the network settings field is one BYTE.
- **Next evidence needed for a stronger capacity claim:** allocator/constructor layout for the live vehicle record around `+0x240..+0x2b8`, and an end-to-end admission proof for each non-menu producer and playback handoff.
