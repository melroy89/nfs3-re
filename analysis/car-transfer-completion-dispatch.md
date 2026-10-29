# Car-transfer completion dispatch and registry reload

## Scope and artifact

Question: does the ordinary received-car completion flow enter `UpdateCarVivArchiveAndRefreshRegistry` (`0043ae60`), and if so, through which handler or callback?

The only executable inspected was the installed active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This was a static-only pass: no transfer was run, no asset or configuration was changed, and the REA binary session was closed afterward.

## Ordinary received-car completion route

`DispatchNetworkControlPacket` reads the packet type into the table index and performs an indirect call through `0055ecbc + 4*type` at `004a645e`. The exact instruction is `CALL dword ptr [ECX*4 + 0x55ecbc]` (REA evidence `ev_7b937e84c29fe78dd7c0bca6bea9d54ef5ccef4460c31d4fe0cd5c9b74c99d08`). The 19 file-backed DWORD entries at `0055ecbc..0055ed07` were read from the active target (evidence `ev_a1ed93da5a6c6b7514ae6020bb384ed60348468568dfd3cbe8ba566e345656f6`); the control dispatcher has a resolved data reference to the table at `004a645e` (xref evidence `ev_64807f73299cdb0149814ab3823fb4261e9056d7cfdd95da54cb486ea265bcf5`).

The relevant adjacent table entries are:

| Packet type | Table slot | Handler address | Observed role in the receive path |
| ---: | --- | --- | --- |
| 15 | `0055ecf8` | `0049b3e0` | Transfer setup wrapper; paired role direction |
| 16 | `0055ecfc` | `0049b500` | Chunk wrapper; decrements payload length and calls `0049b5f0` |
| 17 | `0055ed00` | `0049b470` | Transfer setup wrapper; complementary role direction |
| 18 | `0055ed04` | `0049b520` | Chunk wrapper; decrements payload length and calls `0049b5f0` |

Types15/17 are paired role-direction setup handlers, and16/18 are equivalent chunk wrappers; their type numbers do not independently identify file versus metadata stages. The shared accumulator implements a two-stage receive sequence. `0049b5f0` appends each chunk to its current state and takes the completion path when the accumulated length equals the stage's expected length. After the metadata stage reaches that equality, the direct call sequence at `0049b7aa..0049b7ef` is:

1. `CALL 0043ba20`
2. `CALL 00452a00`
3. `CALL 0043baa0`
4. `CALL 00439d90` (registry discovery/reload)
5. `CALL 0043bc00`, `0043bc40`, `0043bc70`, and `0043bc90` (named setters reading the retained last-discovered model)
6. `CALL 00439d90` again

The body has no call to `0043ae60`. REA's resolved direct-callee list for `0049b5f0` is `0x4385a0, 0x439d90, 0x43ba20, 0x43baa0, 0x43bc00, 0x43bc40, 0x43bc70, 0x43bc90, 0x4529a0, 0x452a00, 0x49b540, 0x4eb1d0, 0x4ee100, 0x4ee2f0, 0x4eebd0` (evidence `ev_dfa196cf4deaf4bc88a591fde426e6305a0cafca0e28edf729b63897f0f8abc4`). This report does not infer a `car.viv` archive rewrite from these names or calls. The earlier receiver-stage notes describe the metadata and file stages separately; this finding is limited to the code path into registry reload and setters.

The loader return is not tested at the `0049b7c7` callsite before the setter sequence. As already recorded in the same-artifact notes, setters use the nonzero last-discovered-model value, so the static sequence does not prove that a failed reload selected the newly received model. This is a target-selection/order limitation, not evidence of a failed transfer or runtime defect.

## Search for ingress to `0043ae60`

REA's reference query for `0043ae60` returned no xrefs; its address is not in an analyzed procedure in this fresh session. The original-byte check provides a bounded corroboration:

- `.code` is VA `00401000`, file offset `0x400`, size `0x133000`. Scanning its raw bytes for x86 near `CALL` (`E8 rel32`) and near `JMP` (`E9 rel32`) destinations inside `0043ae60..0043b29c` found one result: internal `JMP 0043b0ad -> 0043b192`. There is no external direct near call/jump into this body.
- Searching the complete file for any little-endian absolute DWORD value in the body address range found no matches, including the relevant entries of the control-packet handler table.
- The preceding code at `0043ae53` returns; the next bytes at `0043ae60` begin a separate prologue. A full `objdump -d` search for direct call/jump destinations in the body likewise found none from outside it.

These checks establish no statically encoded direct ingress from the selected executable's direct-call/branch or absolute-pointer forms. They do not rule out a runtime-computed target, a callback address formed outside those encodings, or an indirect path not represented by the observed table. In particular, the known table-driven receive-completion route above is positively traced and does not select `0043ae60`.

## Conclusion and remaining boundary

No ingress from ordinary received-car completion to `UpdateCarVivArchiveAndRefreshRegistry` is established. The concrete packet route dispatches types 17/18 to `0049b470`/`0049b520`; exact-length completion in `0049b5f0` calls the registry loader and setters directly, with no call to the candidate archive updater. The bounded direct-reference search also found no other encoded entry into that body.

What remains open is whether some separately computed runtime callback or nonstandard dispatch reaches `0043ae60`. Resolving that would require tracing a concrete indirect dispatch source or observing the relevant completion event under controlled runtime conditions; neither is established here.

Parent corroborated exact selected table slots17/18, wrapper0049b52a and reload/setter callsites0049b7c7..0049b7ef. The packet-type role labels above avoid assigning separate file/metadata stages to the paired directions. No actual transfer, registry refresh or UI redraw was observed.
