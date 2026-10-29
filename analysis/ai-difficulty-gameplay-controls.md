# AI difficulty and profile controls

## Scope and target

This is a static mapping of player-facing AI skill, per-driver profile metadata, and separate feature/role flags into race setup and AI tuning. It follows the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) through two concrete runtime tuning paths. No game execution, configuration edits, executable changes, or persistent Ghidra edits were made.

## What the menu selects

The installed [opponent menu](../nfs3_decomp.rep/Electronic%20Arts/Need%20For%20Speed%20III/FEDATA/MENUS/opponent.mnu) binds the Skill Level button and cascade to `listname=ai`. The installed selector text-ID table at `005562bc` contains WORD IDs `0xaf`, `0x8f`, then zero; the indexed language tables resolve the two entries as **Normal** and **Aggressive**. The selected ordinal is stored as `g_dwAISkillSelection` at `006fd4f0`: 0 means Normal and 1 means Aggressive.

Setup code can override that menu choice:

- Default initialization writes 0 (Normal).
- Mode-one builder `00474310` and mode-two builder `00473ee0` each write 1 at entry, so those modes force the Aggressive ordinal.
- Hot Pursuit builder `00474640` writes 1 only when byte `0055eb2e & 0x20` is set. On that branch the same setup path also changes AI police/traffic budgets and clears the traffic-disabled value. When the bit is clear, this builder does not assign the skill global; its value is inherited from preceding setup.
- The regular-race builder does not assign the skill global in its entry path; its consumers use the currently selected/default value.

Thus the menu is a two-value global selector, not an independent setting guaranteed to survive every race-mode builder.

## Per-driver profile metadata and tuning row

Profile records are 24 bytes at `0055226c`. The DWORD at record+0x10 is the tuning key read by `InitializeVehicleIndexedAIProfileTuning` (`00404690`). Raw bytes in the shipped image give keys by profile index 0..14:

| Profile indices | Tuning keys |
|---|---|
| Racer profiles 0..6 | 2, 2, 5, 5, 1, 4, 2 |
| Police profiles 7..14 | 4, 2, 1, 2, 3, 4, 2, 3 |

The police constructor `00473890` calls `SelectPoliceDriverProfile` (`00473570`), which requests one of eight least-used choices and adds 7. This profile variety selection is separate from the global skill ordinal and from police model-variant selection. Profile key values are per record; they are not police-role bits.

The tuning initializer is keyed by vehicle profile index `vehicle+0x220` (the profile record index is at that record+0x30) and writes a 20-byte per-vehicle-index row at `0056ea70 + 0x14*(vehicle+0x1f0)`. It performs this work only when `vehicle+0x200 & 0x04` is clear. This is the exact local mask gate; it is not, by itself, a semantic proof that the vehicle is or is not police.

For keys 0..5, the initializer assigns three useful row fields:

| Profile key | Response threshold (row+8) | Countdown reload (row+0x0c) | Auxiliary value (row+0x10), Normal → Aggressive |
|---:|---:|---:|---:|
| 0 | 110 | 64 | 5 → 4 |
| 1 | 100 | 96 | 4 → 3 |
| 2 | 60 | 96 | 3 → 2 |
| 3 | 20 | 128 | 1 → 0 |
| 4 | 15 | 128 | 1 → 0 |
| 5 | 10 | 192 | 1 → 0 |

The +0x10 value is reduced by one only when `g_dwAISkillSelection == 1`. Its initializer is the only direct code reference found for that field; no direct reader was identified. Its behavioral significance is therefore unknown. The +8 threshold and +0x0c reload are read by the downstream response routine. Their values are integer callback counts; source code does not establish elapsed-time units.

## Concrete Aggressive response and acceleration path

`UpdateVehiclePursuitTargetAndResponseTimers` (`00404a00`) reaches the profile threshold/reload logic only under a compound gate: special feature bit `0055eb2e & 0x20` is clear; the current countdown at vehicle+0x6e4 is nonpositive; target vehicle flags include bit0x04 and omit bit0x20; the current vehicle has bit0x08; global skill equals exactly 1; and `CheckAIVehicleWithinOpeningProgressWindow(vehicle, 100)` returns zero. It resets the per-target counter at vehicle+0x6e8 when target identity changes, increments it, and compares it with the profile row's +8 threshold. Only when the counter is greater than that threshold does it reset the counter and load the row's +0x0c value into vehicle+0x6e4.

The state-1 helper `UpdateOpponentTargetCountdownAndProximityEvent` (`00404840`) decrements a positive +0x6e4 once per invocation for vehicles with category bit0x08. It also has a separate startup path that can load 50,000, so a positive timer is not uniquely evidence of the Aggressive response path.

`CalculateAISpeedIndexedAcceleration` (`004064f0`) consumes that timer: if +0x6e4 is positive, it multiplies the selected speed-indexed acceleration by float `0x3fa66666`, approximately 1.3. Separately, when the global skill is zero and signed vehicle field+8 is greater than 100, it applies float `0x3f666666`, approximately 0.9. The code therefore supports two conditional tuning effects:

- Normal applies the 0.9 modifier under the field+8 gate; nonzero skill skips that modifier.
- Aggressive can enable the profile-threshold response timer under the stated gates; while positive, that timer selects the approximately 1.3 acceleration multiplier.

These are code-level acceleration changes. The acceleration's physical units, the meaning of vehicle fields+8 and+0x168/+0x7c4, callback cadence, and whether players perceive a consistent handling/speed difference have not been established. The response timer is conditional, not a general “Aggressive makes every AI faster” scalar.

## Separate flags and police escalation

Three controls must remain distinct:

1. `g_dwAISkillSelection` (`006fd4f0`) is the Normal/Aggressive ordinal. It affects the gates and values described above.
2. `g_bCrossSystemFeatureFlags` at `0055eb2e` is a separate byte. Its bit0x20 is the Hot Pursuit special-setup gate above. In the acceleration helper, the same bit also enables a separate path when vehicle bit0x20 is set and float vehicle+0x7c4 is greater than double20.0; that path multiplies acceleration by double0.5. The value20.0 may be a speed threshold, but the unit interpretation is not proven. The mapped byte is zero in the shipped image; its player-facing owner and runtime reachability are unknown.
3. `006fd4fc & 0x20` is the separate MADLAND override. Its traced consumer `ComputeTyreTuningWeatherResponseScale` (`004abde0`) selects alternate tyre/weather coefficients; it is not the Normal/Aggressive selector and the inspected branch does not establish an AI skill effect.

Police participation is a role/profile construction path, not a separate difficulty level. Police profile selection uses indices 7..14 and their per-profile keys; model selection is independent. The police stop-escalation rows at `005521ac` are indexed by target stop count at target+0x2c8, with other police logic testing officer+0x711. Direct references to the global skill selector do not include those stop/escalation consumers. This supports keeping the shared AI skill/profile tuning distinct from police-stop escalation; it does not prove that no indirect or copied influence exists.

## Findings and remaining uncertainty

**Established statically:** the menu's Normal/Aggressive ordinals; mode-builder assignments; profile-key values; per-key response thresholds and timer reloads; the exact aggressive-response gates; the timer decrement path; and conditional 0.9/1.3/0.5 acceleration multipliers.

**Not established:** the user-facing meaning/ownership of CrossSystem bit0x20, a direct consumer for the per-profile +0x10 value, time/physical units for tuning constants, runtime callback ordering, a live Normal-versus-Aggressive behavioral comparison, or a dedicated police-difficulty setting. No runtime behavior was sampled.

## Evidence

REA/Ghidra evidence from the exact installed executable:

- Skill ordinal table bytes at `005562bc`: `ev_db027c66f09675bd968c4929f62fce51cd6e2271c54d4ce0216c1b53e7ac958e`; direct reference inventory for `006fd4f0`: `ev_62f1d963c639fc62b3e7cf438f81ddce0123364f3f88c0b7afa3bee0f184a0f0`.
- Mode-one `00474310`: `ev_1177cfa0db616cc889667ec63d0a29752c9e033c5d16e1b5b09bb3e093117748`; mode-two `00473ee0`: `ev_59430b4d7d0284329805ff1406a16a8ce8776ee6655154a8665d4845028e7a45`; Hot Pursuit `00474640`: `ev_00f5792cd621d0167cd6d2b295549b6e147d94b92488f60bbd5111e3fae96187`.
- Profile table bytes `0055226c..005523d3`: `ev_a409890cb79354422701e944e422a4ac60609feb82c31fc6270d36e30b1131d6`; police selector `00473570`: `ev_da68d8b91e77697a1fe1301f49204cbdec0c01f35e1af3cba2d6ed1f6219e0b4`; police constructor `00473890`: `ev_5ef80a8cf42e241ef6893e061220fe049a0cb5d1b16f63c0d59a9ff0780989f3`.
- Per-vehicle tuning initializer `00404690`: `ev_7d01a629c3a76f883d2f53e81ecdd018ae7cf6d4d46de7b205a61cedcf16f6b4`; response threshold/countdown `00404a00`: `ev_5d4703a97909406699d732c6906cb63aa356908a32ac3dc8390ac89242554c6e`; timer consumer `00404840`: `ev_3c2c4fe4187d793958a54393015aaea2dfd3b452272cf86720d6a7170238ea87`; acceleration consumer `004064f0`: `ev_f62921fa51a571182e08b5cc60c66bdfa35395061dbffcda1df1f6dd0e2b4698`.
- Acceleration constants: `0053625c` (`ev_38886716799b9aa0c8543c92414d442050a864fc779462d85d3bdcb52e7c5472`), `00536260` (`ev_e112b52a1924c554f17b7e8e2295f8b3d1becc23b9080a68256c4f2654ee2b0b`), `00536274` (`ev_d83dea4bb22734b092d2e1a54f42e15622113adfe57aae518ae8bc102854300a`), and `0053627c` (`ev_fed7d90132d53470c02f68731c020cf72af5425082c6fbcc67b6454d6179f849`).

The menu-resource mapping and cross-system/MADLAND lifecycle are also summarized in [detailed-analysis-notes.md](detailed-analysis-notes.md#latest-verified-findings), including language-table and mode-gating coverage. Evidence is static; no player-visible runtime comparison was performed.

Parent review corroborated the core initializer, response and acceleration functions in the persistent Ghidra program, checked skill/target-gate and multiplier assembly, and read the installed menu binding. This confirms static control flow, not a live behavioral comparison.
