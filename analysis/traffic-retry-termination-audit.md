# Traffic spawn retry termination audit

## Scope and target

This is a static audit of traffic placement on the selected `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) plus a small integer model of the observed loop. No target was executed, no runtime memory was read, and no persistent Ghidra project or executable bytes were changed. Existing installed COLL inventory was reused; it was not regenerated.

## Retry and proximity contract

`InitializeTrafficVehicleAIState` (`0040c590`) assigns the traffic vehicle's `+0x6d8` reference. With one configured human it copies `0056ebb8`; with more than one, it calls `SelectLeastLoadedPlayerVehicleForTraffic` (`0040c4f0`). It then calls `SelectTrafficSpawnTrackSegment` (`0040c160`). This is the target human used to seed the candidate search, not the full set checked for proximity. Evidence: `ev_44127dc5ee694cb2d79624013c7c8d1ad327b2b22ae18083017ac6db5c912ef3`.

The multi-human selector counts, for each configured human, registered traffic records that are active and whose `+0x6d8` assignment equals that human. It chooses the least-loaded human, retaining the first on ties. The loop has no local `humanCount` bound. Its stack tally is addressed one-based (`1..humanCount`) in a 15-DWORD local span; `2..15` fits that span, while `humanCount >= 16` writes beyond it. It initializes its best load to 10,000 and starts with a fallback pointer; if every tally is at least 10,000, it never selects a human row. Those are exact source conditions, not evidence that such counts occur. Evidence: full body `ev_bbc54292d9b42c3f8199471000bb87e2eea9b8b9935247a1b669937a812783a8`.

`SelectTrafficSpawnTrackSegment` (`0040c160`) derives one direction sign at entry, starts with signed displacement `±61`, calls the one-wrap track-position helper, and asks `FindNearbyHumanVehicleForTrackSegment` (`00405c80`) whether any configured human is close. If any is close, it adds `±20` to the displacement and retries. If none is close, it stores the candidate directly to traffic vehicle `+0x1c`; there is no retry counter, end-of-track exit, or post-selection range check. Evidence: aligned body `ev_bc9aa7512c72a30b23adaff94ce6bc3d89f50d7a2f82152588a5560616128822`.

The near-human helper scans all rows `0..humanCount-1`, computes wrapped candidate-to-human segment distance with `GetWrappedTrackSegmentDelta` (`0040e120`), and treats absolute distance **below 50** as occupied. Equality at 50 is clear because the assembly continues only for `distance < 0x32`. Evidence: `ev_6ace5f25980f3fcb1c94b2bb9b9dcc8bcb26bca5218134ab1345543884caa44c`; distance helper `ev_f3e82358b1f7493ae4773619c96237df481a307b821a65964eefccef777254c0`.

Both helpers correct by at most one track length. `0040e160` adds or subtracts the current segment count once when the candidate crosses an end. `0040e120` adjusts a segment difference by one track length when it exceeds the half-track threshold. They are circular-distance operations only when the segment count is positive and the candidate/human indices are valid enough for that single correction. Neither helper implements an unbounded modulo operation. Evidence: `ev_02f55f7ec2f2bfe89fcc668668afbf228f877c8d58a3f08336c45a4198b55c09` and `ev_f3e82358b1f7493ae4773619c96237df481a307b821a65964eefccef777254c0`.

## Sufficient termination condition for the installed-track, canonical-human domain

Let `S` be the positive segment count, `p` the selected human's valid segment, `H` the configured human count, and `q_j` the valid segment for each human. While the direction and globals remain stable, the retry displacements are `d_k = sign * (61 + 20k)`. The one-wrap candidate is `W(p,d_k,S)`, formed by adding `d_k` to `p` and correcting by `S` at most once. Each candidate is accepted exactly when every human has wrapped distance at least 50.

For the installed tracks, the retained COLL inventory reports nine counts from 959 to 1723. After the displacement first crosses one track boundary, the one-wrap helper yields a monotonic candidate run across at least `floor(S/20)` distinct in-range indices before a second crossing can leave the range. This is at least 47 positions for every installed track. Choose exactly the first floor(S/20) consecutive candidates in that run. Their linear spacing is20 and their circular seam gap is S-20*(floor(S/20)-1), which is at least20. Therefore even a neighborhood crossing the track seam covers at most five chosen candidates: the strict <50 interval spans99 integer positions (-49..49), while six chosen points require at least100 units from first to last. Do not apply this five-point claim to an arbitrarily longer run with a shorter seam gap.

Therefore, if all of the following hold, an in-range candidate must be found and the retry terminates:

- The loaded segment count is one of the installed positive counts (or otherwise satisfies `floor(S/20) > 5H`).
- `1 <= H <= 8`; all human pointers and segment indices are valid and stable during the search.
- For multi-human placement, the selector returns a valid human pointer (in particular, its minimum tally is below 10,000 and `H <= 15`).
- The target pointer, candidate direction, track direction state, and segment count remain stable through the retry.

With `H <= 8`, at most 40 positions in the post-wrap run can be rejected, while the shortest such run contains at least 47. The first safe in-range candidate is thus no later than the 41st candidate in that run. Across the installed counts, the target can require at most 84 checks before the first boundary crossing; adding 41 gives a conservative sufficient ceiling of 125 proximity checks. This is a derived static bound under the listed conditions, not a measured execution time or a bound for all input states.

The count data came from existing [installed-track-map-segments.json](evidence/inventories/installed-track-map-segments.json), produced by [inventory_track_map_segments.py](scripts/inventory_track_map_segments.py). The COLL initializer reads the type-15 WORD count and record base without a local minimum-count or extent check (`0041e370`; see [detailed notes](detailed-analysis-notes.md#installed-track-map-segment-count-admission)). The inventory establishes file extents for the nine installed files, not that a live session loaded one of them.

## Realizable versus synthetic domains

**Canonical supported path, conditionally sufficient.** The local network roster constructor produces 1..8 humans, and stable eight-ID mode-one/mode-two matching also limits accepted rows to at most eight. Ordinary local split-screen/race paths likewise target a small human roster. These observations make `H<=8` a supported canonical domain. They do not prove that every ingress preserves it: the received signed roster count is not normalized, and regular/pursuit count builders lack the eight-ID filter. The network-capacity report records that distinction. No universal `H<=8` admission invariant is established for arbitrary received counts or mutated state.

**Synthetic overlap model.** To test whether overlap can cover every candidate in the one-wrap valid range, a bounded integer model used `S=959`, `p=0`, positive direction, and `d_k=61+20k`, applying exactly one subtraction of `S` when needed. Ten hypothetical human positions `[0,93,193,293,393,493,593,693,793,853]` cover all 93 in-range candidates generated before the helper's one-wrap result exceeds `S-1`. Thus every valid candidate is rejected in this synthetic `H=10` configuration. This is a constructed arithmetic case, not installed participant/position evidence.

The executable does not stop when its one-wrap result leaves `0..S-1`. In that synthetic model it keeps retrying; at `k=100`, displacement is 2061, the helper returns candidate 1102, and the one-correction distance helper sees nearest-human distance exactly 50. The caller accepts and stores 1102 even though `1102 >= S`. This demonstrates why synthetic full coverage is not evidence of an infinite loop: the code can instead accept an out-of-range candidate. No downstream bounds failure or runtime defect is claimed.

## Runtime gap

The conditional termination proof depends on a stable, valid segment count, at most eight valid human rows, valid target pointers/indices, stable callback state, and the usual roster producer. Static code proves the retries and arithmetic; it does not prove those runtime preconditions universally. The regular/pursuit received-count paths, the live source of all human segment indices, concurrent updates, invalid/custom track resources, and the consumer contract for a stored out-of-range candidate remain unresolved. Consequently, the precise result is: **bounded termination with an in-range candidate on the stated canonical domain; no universal termination or valid-result guarantee from the inspected instructions alone.**

Parent review independently reproduced the synthetic case:93 valid candidates rejected; first accepted k100/candidate1102/nearest distance50. Parent tightened the proof to an explicitly chosen floor(S/20)-candidate subset so the seam gap is at least20; the five-candidate neighborhood bound then holds across the seam as well.
