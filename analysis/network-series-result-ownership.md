# Network series result exchange and local progression

## Scope and finding

Static review of active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. No game, network, executable, configuration or live-memory changes were made. This joins the ordinary result pipeline to the network participant-state exchange for issue #3; it does not validate an online series.

The result builder contains no host-only gate around tournament scoring or Knockout progression. It first invokes a conditional network state exchange, creates local result snapshots, normalizes/ranks them, then runs the selected series updater. The host role controls additional nonhuman state transmission and packet relay in that exchange. The inspected call structure performs progression locally on an executing peer after its gates; it does not establish that one host sends a final authoritative standings table or that every peer necessarily reaches the same gates.

## Ordinary result call path

`RunRaceSession` calls `BuildRaceResultSnapshotsAndUpdateProgression` at `004a385f` when its local context at `[EBP-4]` is zero and race exit state `007d36b4` is zero (`004a3852..004a385d`). The result builder at `00455410` skips the whole pipeline when playback selector `006fd3a0` is nonzero. Otherwise the order is:

1. `00455423`: call `SendParticipantStateControlMessages` (`004c7ea0`).
2. `00455437..0045544d`: copy participant result snapshots into the two local categories through `00455210/00455280`.
3. `00455456/64`: build result order maps through `00455c10`; `00455469` normalizes results through `004552f0`.
4. Race mode1 calls `00455070` at `00455477`; mode2 calls `00455140` at `00455485`. Neither call has a host/client-role test around it.

Mode1 updater separately returns early when `004cef80` is nonzero. It awards per-round WORD points from `00454f10` and adds them to cumulative WORD scores `006fd44e + 2*identity`; the first eight award values are `[30,25,20,16,12,8,4,0]`. It rebuilds the cumulative ordering then increments progression `006fd40c` at `00455129`. Mode2 updates eligibility/order and increments `006fd3bc` at `00455200`. See [normal series lifecycle](series-normal-terminal-lifecycle.md) for endpoint/reset details. This trace does not establish what every helper outcome means for disconnects or abandoned races.

## Role-dependent state exchange

`004c7ea0` runs its exchange only when `006fd50c != 0` and signed session mode `006fd3b0 > 1`. It brackets sends with synchronization markers `(0x5a,0x22)` and `(0x5a,0x23)`. It sends a type12 (`0x0c`) packet of `0xc4` bytes: byte1 identifies a participant, and packet+4 contains `0xc0` bytes from that vehicle+`0x224`.

Each executing peer sends its selected local participant using pointer table `005efa48[006fd4f4]`. When host flag WORD `007a22da` is nonzero, the sender additionally visits master-table indices from human count `006fd514` to total count `006fd510`, sending each nonnull entry from the distinct table `005efac8`. Thus the extra host loop covers the configured nonhuman suffix; identity/table equivalence and actual callback delivery remain separate requirements.

The type12 handler is selected by pointer `004c7f90` in table slot `0055ecec`. It copies packet+4 into `005efac8[packet.byte1]+0x224` at `004c7fb0`. Host role additionally relays the same `0xc4`-byte message at `004c7fc8`; the client branch returns after the local copy.

The copied vehicle range is `+0x224..+0x2e3`. It includes comparison/result scalars such as `+0x238`, `+0x2c4`, `+0x2cc` and `+0x2d4`; it excludes the local identity/descriptor pointer at `+0x220`. It also does not directly carry the separate configuration-global cumulative score/eligibility/progression arrays. Those distinctions explain why matching participant identity and local setup remain necessary even if every type12 payload arrives.

## What remains

- Establish actual marker completion and matching result/identity state on both peers before local scoring.
- Trace next-round setup synchronization of cumulative score, eligibility and track progression; this packet alone is not that proof.
- Resolve ordinary disconnect, tie and abandoned-race policy across all peers. The existing result comparator includes multiple metrics and fallback ordering; this report does not invent a new tie policy.
- Verify a complete supported online Tournament and Knockout with and without AI, including last-round termination. No first-race or full-series runtime result is claimed.

Parent independently reviewed full shared-Ghidra instruction bodies for `00455410`, `00455070`, `00455140`, `004552f0`, `00455c10`, `00455840`, `004c7f90`, the call region of `004a3690`, and active bytes of tables `0055ecec`, `00455810` and `00454f10`. Existing sender evidence is retained in detailed notes under Participant-state control-message emission. No security/adversarial follow-up was performed.
