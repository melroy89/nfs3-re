# Arrest/R relocation audit: reset-reference consumers

## Finding

The accepted-reset completion counters do **not** gate the two contact routines reviewed here. The pre-guard segment write can feed their track/contact queries while `+0x524` and `+0x174` remain zero. That creates a plausible path for the changed reference to alter subsequent contact or motion calculations, but the reviewed paths do not establish the large sampled XYZ relocation: neither routine directly writes world position on the sampled `recovery_gate_88=0` path. The arrest snapshots are asynchronous and do not identify the writer that moved the car.

## Evidence and traced paths

The existing [reset contract](pursuit-assist-reset-contract.md) places the requester `+0x1c` segment prewrite at `004052b7`, before the ordinary reset checks in `00429100`. The later completion writes are `+0x174=64` and `+0x524=32`; their absence does not undo the earlier reference write.

### `UpdateActiveVehicleTrackContactMotion` (`004a2830`)

The shipped bytes decode as a prologue at `004a2830`, through a common exit at `004a2bad`. Fresh REA auto-analysis did not recognize a procedure boundary there (`ev_03aa44a8cda0da21407cd67d00994047f8fc57067b76001c4b76731ceecf9a4e`), but the exact entry has an xref from `0042c42d` (`ev_61cf9d3e92971b86e6bbcb2246978b85ac052fe029339baaf2dd4d0256d8cd80`), consistent with the previously documented callback registration at vehicle `+0x60c`.

- `004a283d` compares the simulation tick at `007d3684` with `0x200`; `004a2847` branches to the exit when signed tick is below that threshold (`ev_f308ad52923cd59a5131066366b8acff233f3accb69f414afce6dcfa1e94ac4a`).
- `004a284d` checks active byte `+0x89`. `004a285a` checks recovery/alternate-path gate byte `+0x88`; `004a2861` branches to the normal path when it is zero (`ev_62adef2089b9abc5275fd22438f32320f92c3222b5ba6259d8f6dbc56d8138f8`, `ev_df053c800f74a90f03cbb6738595f7b39963a1cdf2a7d601ae3e91bf5d87bd57`). If this gate is nonzero, `004a2865` calls `004a2630` and skips the normal body (`ev_502b33a96fc2354c96e577de36cbf2d333ec60445a249ab56b2c7bf11a1b80d7`). `004a2630` can write world Y at `+0x9c`; this branch was not selected by the sampled arrest state (`recovery_gate_88=0`).
- On the normal path, `004a2885` calls `004a21a0` (`ev_7d5ebcc5c75d66efcfcbdf5869cd5b83ef6345b5eead629eb3b620c3e9bbec53`). Its decompilation reads vehicle XYZ at `+0x98/+0x9c/+0xa0` and supplies those coordinates plus vehicle segment `+0x1c` to `00420bf0` (`ev_73e8d74f474026d549acf368056a1a818db6d28b617bc0e72161d039ca2fa3ab`, `ev_540164c5a5c85932a0995bfbb79e51c466f1acdf731d427d117612e5f94d793a`). Thus a pre-guard reference change can affect the query. The returned condition can reach `004a20c0`, whose body clamps/writes motion-response fields `+0xe4/+0xe8/+0xec`, not XYZ (`ev_f0f15696fa455c6807ce267fd8cd94bfe1a4dc39e7880422e02c330361a711bd`).
- The routine later calls `004a1610` directly at `004a2b78` (`ev_b3812f29c113c32c606a01bd692c4cd39f6b6834871fad3862432d3122e9c73d`). Its own main-body stores include velocity `+0xa4/+0xa8/+0xac`, not position; the disassembly has no direct stores to `+0x98/+0x9c/+0xa0` on this normal path.

The sampled vehicle state at ticks 18947–18953 meets the early static gates (tick well above 512, active byte represented as active=1, recovery_gate_88=0). Those observations do not prove that the `+0x60c` callback executed in the 50 ms interval.

### `ApplyPredictedTrackContactCorrection` (`004a1610`)

REA decompilation evidence is `ev_72966064057ef22df7e48a3df4aa9faa1a5b76ded8d09a2fbefd53355fc8946e`. The entry computes a predicted point from the current world position and velocity, and calls `00420bf0` with the vehicle's current `+0x1c` segment reference. This makes the pre-guard reference available to its track/contact query without consulting reset cooldown `+0x524` or completion state `+0x174`. The body has other admission gates, including contact/query result fields, category/material checks, blocker `+0x184`, orientation state, and motion thresholds.

Its direct vehicle writes are to motion/contact fields: linear velocity `+0xa4/+0xa8/+0xac`, correction components `+0xe4/+0xec`, and related state such as `+0x15c`. It reads XYZ to construct the predicted query but does not directly store to `+0x98/+0x9c/+0xa0`. This function is directly called by `004a2830`; its invocation is not tied to `004ad7a3`'s reset counters.

The retained sample identifies `physics_callback=004ae4c1` and the sampled category `0x24` as selecting the non-AI physics callback path documented elsewhere. That identification does not establish execution of the separate `+0x60c` contact callback or of any instruction inside `004a1610` during the arrest interval.

## Correlation with the retained arrest/R capture

The [retained event capture](evidence/runtime/police-arrest-reset-guard-events.json) records samples every 50 ms, not an instruction trace. At tick 18947 the local segment is 571, target group phase is 2, input is clear, and cooldown/state are `0/0`. At tick 18950, input bit `0x02` is sampled, the selected leader (ordering value 1) is at segment 464, and the local segment becomes 463, matching the established leader-minus-one pre-guard write. The target remains attached in phase 2, while cooldown/state remain `0/0`. Over that interval local XYZ changes from approximately `(-760.237, -2.863, -607.053)` to `(-388.315, -2.872, -289.370)`. At tick 18953 input is clear, target remains in phase 2, counters remain `0/0`, and position changes again to approximately `(-394.963, -2.899, -409.041)`.

Only at tick 19011, after the target pointer is gone, do the ordinary completion values appear (`+0x524=31`, `+0x174=63`), consistent with the known stop-cleanup reset path and same-update cooldown decrement. This places the observed large position change before sampled ordinary reset completion. It does not prove whether the pre-guard request, contact callback, an unsampled transient, or another writer caused the relocation. The ordinary `+1/64` velocity integrator is not enough to explain the sampled hundreds-of-units change from the near-zero velocities at tick 18947; no new movement-integration identity is inferred here.

## Boundary and next discriminating observation

Static evidence supports **reference consumption without reset counters**, but not direct relocation from either reviewed routine. On the sampled `recovery_gate_88=0` branch, their direct world-position stores are absent; the alternate-only helper that can store Y is skipped. Indirect helper effects and other position writers are not exhaustively excluded.

A discriminating runtime capture would set a write watch on the local vehicle's `+0x98/+0x9c/+0xa0` and log the writing PC/call stack, while sampling `+0x1c`, `+0x524`, `+0x174`, input bit `0x02`, target/group phase, category, `+0x88/+0x89`, and simulation tick. Breakpoints at `004052b7`, the rejection branches in `00429100`, callback entry `004a2830`, its `004a2b78` call, and the XYZ write watch would distinguish a reference-only prewrite from a separate relocation writer. Current retained snapshots cannot provide that distinction.

No executable, runtime memory, or persistent Ghidra project was modified.

Parent capture review confirms recovery_gate_88=0 at18947/18950/18953. This is distinct from the sampler field alternate (byte+8a), which also happens to be0 in these samples; only recovery_gate_88 supports the +88 branch argument.
