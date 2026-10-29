# Placement and environment-query refresh lifecycle

## Scope

Static review of active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows the unresolved vehicle `+0x184` segment-override/clearance gate and byte `+0x88` refresh marker through placement, query initialization, and ordinary reset/update paths. It uses the established `004a0aa0` register, fixed-point offset, and local/world basis contract as context. No game execution, live-memory changes, configuration/executable writes, or persistent Ghidra edits.

## The two fields are separate gates

- Vehicle DWORD `+0x184` is read by clearance helper `004a0440`: nonzero returns `100.0` immediately; zero computes clearance from the vehicle basis and position. Placement `004a0aa0` subtracts that result from world Y. Separately, update helper `004a08c0` skips its nested query-update branch when `+0x184 != 0` **and** vehicle DWORD `+0x20 == 0`; the `+0x20` exception lets the branch continue. This proves a conditional skip and fixed clearance, not a universally reachable nonzero value.
- Vehicle byte `+0x88` is read as a pending update marker. `004a0580`, called by `004a08c0`, consumes it under distance and global/count gates. It is not the `+0x184` override.

## Placement order and query freshness

`004a0aa0` initializes query state at vehicle `+0x0c` through `0041e940` before it prepares placement geometry and world position. `0041e940` clears the query's cached quad/material pointers (`+0x14/+0x18`), cached change flags (`+0x68/+0x6a`), query status (`+0x6c`), and cached index (`+0x70`), then calls `0041e8f0` to bind the track block and segment-derived data pointer. That binder does not write the cleared cached quad/material pointers or status fields. This discards a prior cached quad result for this query context. It does **not** clear vehicle byte `+0x88`.

Placement next calls `004a08c0`. For an active vehicle (`byte +0x89 != 0`), `004a08c0` first calls `004a0580`. If that helper takes its close-distance branch while byte `+0x88` is nonzero, it clears the marker and calls `0049fe70` itself; because initialization cleared the old cached quad, this first query request must take the refresh/search path (`0041f650`). After `004a0580` returns, `004a08c0` runs `0049fe70` unless the then-current fields satisfy `+0x184 != 0 && +0x20 == 0`. That helper converts current world XYZ to fixed-point and calls `0041f6e0` with reuse mode `1 - byte[vehicle+0x88]`. A mode-1 call with no cached quad refreshes; a later mode-1 call can reuse a quad populated earlier in this same placement pass if the requested point remains inside it. The close-distance helper can also clear `+0x184` before the later gate is evaluated. Thus initialization excludes reuse of a pre-placement quad, but the later update may reuse a fresh same-placement result or be skipped by its gate; this audit does not establish that every placement refreshes.

After `004a08c0`, placement calls `0049ffa0` independently when the vehicle is active. It calls `00420230` to extract the selected segment/query basis and populate placement basis fields. This is basis extraction; it does not itself perform the `0041f6e0` query refresh. Thus the `+0x184`/`+0x20` gate can skip the nested refresh while placement still executes basis extraction from the freshly initialized query/segment context. Whether that context yields a useful basis on every admitted path is not established here.

At placement end, `004a0aa0` calls `004207e0` only if byte `+0x88` is zero; otherwise it stores `1` to `+0x188`. `004207e0` checks query pointers/status and can set query reuse index `+0x74` to `-1`; it does not run a surface/segment search. It should not be counted as a refresh.

## Marker consumption and clear order

`004a0580` is the sole direct caller of this distance-gated placement-side environment update, via `004a08c0`:

1. If global `006fd3b0 != 0`, or the race vehicle count `005efda4` is at least 3, it clears byte `+0x88` and distance `+0x84`, then returns.
2. Otherwise it computes and stores an XZ proximity value in `+0x84` (and in the two-vehicle case takes the smaller corresponding distance).
3. If the distance is at or below its threshold and byte `+0x88` is nonzero, it clears `+0x88` **before** calling `0049fe70`, `0049ffa0`, and the related environment/height helpers. This branch later calls `004294c0`, which clears `+0x184` and a related recovery value.
4. If distance is above the threshold, it updates the `+0x188/+0x18c` status when required and clears selected other fields. It still reaches the common clear of byte `+0x88` before return.

The byte is therefore consumed/cleared before a requested refresh, and is also cleared on the far-distance and bypass paths. `0041e940` resets query-cache fields but leaves vehicle byte `+0x88` untouched; `004a0580` clears the marker on its local exits, including before a close-distance refresh.

## Producers, resets, and the remaining source gap

The direct stores to the vehicle fields in the reviewed placement/reset paths are clear operations:

- `004a0d20` initializes the vehicle environment state, clearing `+0x88` and `+0x184` before setting active byte `+0x89` to 1. Its direct caller is setup routine `0042bcb0`.
- `00428970` clears `+0x184` during vehicle reset/recovery.
- `00428f90` clears `+0x184` when its recovery branch runs; its caller is `00429260`.
- `004294c0` clears `+0x184`; `004a0580` calls it after the close-distance update path.
- `004a0580` clears `+0x88` on all its exits, with the relevant close-distance branch clearing it before refresh.

A bounded direct-displacement scan over the exact executable (`objdump -d -M intel '<selected nfs3.exe>'`, filtering instructions that reference `[base+0x184]` or `[base+0x88]` and separating stores from stack-frame accesses) found no nonzero store to these fields in the vehicle placement/reset chain. It did find two same-offset stores that must not be misidentified as vehicle producers: `00468010` writes `+0x184` in the `FCEFILE` object-loading path (`00468860`, case 4), and `004667d0` writes byte `+0x88` in a frontend mouse-drag object whose `+0x98` is a clock value. The later [activity-field audit](vehicle-activity-lifecycle.md) identifies its UI drag inputs and raw frontend caller. Those bases have different observed roles from the vehicle base where `+0x98` is world X. A renderer routine also stores a float at its own object `+0x184`.

**Unresolved:** no normal vehicle writer that sets `+0x184` nonzero, or `+0x88` nonzero, was identified in this bounded direct-field scan and caller chain. Bulk copies, aliases, indirect dispatch, and other vehicle lifecycle paths could still supply those values. The ordinary placement logic establishes what happens conditionally if either gate is set; it does not prove how often that state occurs or that a normal game path reaches it.

## Evidence

Evidence is from the exact executable above; pseudocode/assembly are provider analyses of that shipped artifact.

- Placement `004a0aa0`, including its ordered callees: `ev_0c1f2da9e0630f138bb40661086f0beb3439837c648887702f3b47899b2c6694`.
- Query initializer `0041e940` and track-data binder `0041e8f0`: `ev_987263b647a3ab6902fb8b426648b75250c668d7bc84ccc5a0236351334bfa54`, `ev_958d8f35098e912f85c8ea56d3c755cf808cd39e99bc9ba0ca7752d91b0077a7`.
- Placement updater `004a08c0`: `ev_f465bdc4dae87bb10aabe28d47f29a4bd6f81a7a498284fb7d9388fa06f85355`.
- Distance/marker handler `004a0580`: `ev_e6934d5b80ecb63e3ee86ab171f7ee11f766fb29a92757ba4680fbff959310a5`.
- Clearance gate `004a0440`: `ev_10d13e9c9a793e5d2b45e4052ff2a9930a0056877633141d6397341e265acd0b`.
- Query-mode wrapper `0049fe70`: `ev_e04a5f22a0770c5b561e1fb8cc08abd6a1d213605cd3cb7e4678b978536239bd`.
- Cached-quad/requery branch `0041f6e0`: `ev_c2e8cbf7ae0cac5f4221a950527f27e4ff62befc87821dfca76d8bf8cb0f5065`; refresh/change helper `0041f650`: `ev_900e121b2adb1d7bcf610dc131902d10330f1fbcceca979a24bad5f37acab584`.
- Basis extraction `0049ffa0` / track-query basis builder `00420230`: `ev_e92a12c2b66a89feed0a413f2b2eeba79ad1dae5895c8ffe6650e2e81f7b8f4e` and `ev_be33f58a93ad75fa64a1e610ad339b9836e1992d9899b659215b29671642a39f`.
- Vehicle initialization/reset and recovery writers: `004a0d20` `ev_b6a2f4936e2484663a19f739300236439eb26e1100b2fb14d0bf778a2eb11f2c`; `00428970` `ev_2bf3f4aef2e5ad956c42ba97c4b04851a21ca68c91393f83800227e10cf53d49`; `00428f90` `ev_b67de89bfa075f8cc3e4058ecef0ac0bdc2cb00cec5950071cbaa2f656684441`; `004294c0` `ev_0bcc78f6cab28f98974177873ac3540cea54f8e1a3a27dfb6431be24438235f6`.
- Same-offset nonvehicle candidate check: `00468010` `ev_de7287730fd5e5371d037a093a3a231fb58e8e9ec4a5becc2631e62f62450da6`; event/timer record `004667d0` `ev_a982be753c05d627babbcee3677fa6d372f59bf7ad372f7a837b8ba09c68226d`.

No persistent Ghidra comments, labels, types, or program data were changed.

Parent reviewed query initializer/binder0041e940/0041e8f0, reuse logic0041f6e0 and distance/environment helpers004a0580/004a08c0. Placement callsites004a0ab6/004a0c7d/004a0c86 establish the order; saved EOL comments distinguish clearing a pre-placement cached quad from possible same-placement reuse and distinguish vehicle+88 from query fields. No runtime refresh was observed.
