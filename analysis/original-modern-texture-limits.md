# Original versus official Modern: texture extent limits

## Scope and artifacts

Static comparison of the supplied original executable and official archive Modern executable. This follows the Modern `AllowHugeTextures` value into dimension-building paths and records limits that bypass or reduce it. Renderer DLL behavior and successful rendering are outside the executable-only comparison.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

## Modern setting and renderer-dependent reduction

In the official Modern settings loader, `004b56d5–004b56f1` reads `AllowHugeTextures` (key at `0053f6d0`) with default zero. Values 0–3 produce `256 << value` and store 256, 512, 1024, or 2048 at `007a278c`; unsigned inputs outside 0–3 (including negative integer bit patterns) use shift zero and therefore produce 256. This is the configured extent before subsequent renderer initialization.

After renderer initialization obtains a descriptor at `007a3a5c`, code `004b5bd6–004b5bf5` takes the unsigned minimum of descriptor DWORDs `+0x14` and `+0x20`. It repeatedly halves `007a278c` until the value is no greater than that minimum, then writes the reduced extent back. This makes the configured setting an upper request, subject to the two descriptor values. For the paired final Voodoo2 adapter, both fields are populated from Glide's maximum texture-width query. Other drivers and live values remain unqualified. See the [Voodoo2 producer trace](original-modern-dll-candidates.md#shared-adapters-after-the-provider-split). If their minimum is zero, this reduction writes zero; the dimension builder can then accept initial zero for nonnegative inputs. Its fallback to 1 applies when halving reaches zero, not when the starting extent is already zero. Ordinary positive descriptor invariants are not established by this code alone.

## Concrete changed dimension builder

A clear executable before/after comparison is `0049cea0`, called from the same two sites in both binaries (`0049d1c0` and `0049d3de`). Its callers pass source dimensions and output records; the call instructions and surrounding argument setup are unchanged in the inspected span.

- **Original `0049cea0`:** reads the first stack dimension into EDI. If EBX is greater, it writes that dimension to both output width/height. Otherwise it rounds EBX down through fixed thresholds 256, 128, 64, 32, 16, 8, 4, 2, or 1 (`0049ceb9–0049cf75`). There is no read of `007a278c`; this branch's largest hard-coded result is 256.
- **Modern `0049cea0`:** reads the first stack dimension, loads `007a278c`, and halves the configured extent until it is no greater than both EBX and the stack dimension; it substitutes 1 if repeated halving reaches zero. It writes that selected extent to both output dimensions (`0049cea5–0049cec1`) and calls the same resampler at `0049cd00`.

For example, if both dimensions supplied to this helper are exactly 512 and the Modern configured extent is 512, Modern selects 512, while original takes its fixed-threshold path and selects 256. This is a direct static comparison of the helper's arithmetic, conditional on its inputs. It is not proof that a particular asset supplies those dimensions or that a renderer accepts the resulting texture.

The original helper has **no universal 256 ceiling**: its EBX-greater-than-stack-dimension branch passes the stack dimension through unchanged. For inputs EBX=1024 and stack dimension=512, original can select 512; Modern with configured extent 256 selects 256. These examples are arithmetic consequences, not executed probes. The change both raises the fixed-threshold path when configured and consistently applies the configured extent to a path that originally bypassed those thresholds.

A second matched caller change occurs in the track/setup route at `0041db79–0041db87`: original passes immediate `0x80` (128) in EBX to `004d4080`; Modern instead loads `007a278c` into EBX before the same call. The alternate branch at `0041db70–0041db77` is unchanged in both: when bit 1 of `007a3a58` is set, it calls `004d41a0` and bypasses this configured-extent call. In both binaries, `004d41a0` calls `004d4120`, whose unchanged threshold logic caps its result at 256 (`004d4129–004d4192`). The setting therefore does not lift every texture path's local cap.

## A separate vehicle-texture branch

`LoadVehicleModelWithTextureReuse` at `004b7d30` also changes its extent source. Original always selects EBX=256 when the selected table comparison matches, otherwise EBX=128 (`004b7d43–004b7d60`). Modern first loads `007a278c`; if DWORD `006fbc1c` is zero it keeps that configured value. If `006fbc1c` is nonzero, it restores the original 256-versus-128 choice (`004b7d43–004b7d6b`). This is the exact branch condition: the configuration is used only on the zero path. The comparison does not identify which vehicle models or texture assets reach either path.

## Retained evidence and reproduction

Run `python3 analysis/scripts/audit_texture_extent_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-texture-extents.json) records both binary identities, caller/builder spans, setting/reduction instructions and byte-equality assertions for the two unchanged limit helpers and two shared builder callsites. Raw assembly remains under ignored `analysis/captures/modern-differences/texture-extents/`.

## Evidence boundary

- Direct Modern references found for `007a278c` are the settings store, the renderer-dependent reduction, `0049cea0`, the track/setup caller at `0041db7b`, and vehicle loader `004b7d43`. This is a bounded direct-reference inventory, not proof that no other producer receives the value indirectly.
- In the inspected paths the executable builds/selects dimensions and passes them to its texture preparation/resampling flow. It does not establish that a selected Thrash driver or Glide wrapper accepts, allocates, uploads, or renders every configured size. DLL-specific texture-memory preflight and upload behavior are deliberately not attributed to `nfs3.exe` here.
- The registered descriptor can reduce the configured extent; local branches such as `004d4120` can impose smaller limits; some vehicle branches retain fixed values. No configured value or descriptor value was read from a running process, and no visual output was checked.
- Existing Modern-side renderer inventory and source-specific bounds are documented in [installed renderer capability inventory](installed-renderer-capability-inventory.md). Its installed-build and driver observations are not substituted for evidence about the official archive binary beyond the code paths rechecked above.

No game, probe, or test was run. No executable or Ghidra project was modified.

## Outside-body removed tail and split instruction

The outside-function interval **`0049cedd..0049cfa0`** consists of195 Modern NOP bytes, all195 differing from original. It begins **inside original instruction`0049cedb`**, `MOV DWORD PTR [EAX+4],128` (`c7 40 04 80 00 00 00`). Remaining original bytes belong to its fixed-threshold dimension selection, resampler-call/epilogue through exclusive`0049cf91`, and alignment. The [outside-body manifest](evidence/audits/outside-function-differences.json) now checks the NOP interval and boundary instruction and links the complete paired builder evidence.

Modern’s shorter complete body ends exactly at`0049cedd`; the removed tail therefore does not represent removal of square texture building or resampling. Those operations remain in its configured-extent counterpart described above. This closes interval routing while retaining zero-descriptor, source-dimension, helper and driver/runtime limitations. No boundary repair or executable/Ghidra edit was made.

## Historical track extent and experimental setting are separate changes

The [three-build audit](evidence/audits/texture-extent-history.json), reproduced with `python3 analysis/scripts/audit_texture_extent_history.py`, pins140/150/151 EXE archives and INI hashes. It captures the selected track caller, square-builder prefixes and151 setting/wrapper. It dates these local mechanisms without claiming complete historical producer or renderer equivalence.

|Build |Selected track call at0041db86 |Effective extent source on that branch |
|---|---|---|
|140 |004d4080 |EBX immediate128 at0041db7b |
|150 |004d4080 |EBX immediate256 at0041db7b |
|151 |0041dbb4 |Wrapper loads EBX from007a278c, then tail-jumps004d4080 |

The151 caller itself again loads128. Reading only that immediate would incorrectly suggest a return to the old effective limit: the11-byte wrapper overwrites it before the original callee receives control. The alternative bit1 branch to004d41a0 remains distinct, with the previously documented local cap; do not apply this selected path's extent universally.

The150 square-builder prefix retains a fixed256 threshold and a dimension-pass-through branch.151 instead reads007a278c and halves it to fit both supplied dimensions, matching the later configured policy documented above. The pass-through branch means absence of the new setting in150 is **not** proof of a universal256 ceiling.

151's checked key literal at0053edc0 is `AllowHugeTextures`; its packaged INI contains `AllowHugeTextures=0`. The selected reader supplies caller-default EDX0. Its unsigned0..3 mapping produces256/512/1024/2048; out-of-range bit patterns choose256. The literal and INI entry are absent from the checked140/150 release members. This is a bounded literal/package comparison, not exclusion of computed keys, hidden producers or all larger-texture routes. Renderer-dependent reduction, assets and actual uploads still constrain a requested size.

**MP150-012:** historical140→150 now directly dates128→256 at the selected track call, strengthening its existing partial support. **MP151-003:** the new key, mapping and wrapper date the experimental configurable extent to150→151, strengthening the existing static-supported setting claim. Actual high-resolution rendering remains untested.

**MP150-013 remains vendor-only:** no beta package has been inspected. These release builds distinguish the track argument change, later setting and driver table expansion, but cannot establish that512/1024 textures were exclusive to a particular beta or impossible through every release path. Required follow-up is an identified/hash-pinned beta EXE and corresponding producer/driver comparison, followed by behavioral evidence for acceptance. No beta source or functionality is inferred from a release-note sentence.

No target instructions, driver/API calls, asset loads, compilation or Ghidra writes occurred; executable/database bytes are unchanged.

## DX6 format-count bound is separate from texture dimensions

This subsection adds **renderer-local format-count evidence**, distinct from the executable extent policy above. The source's MP120-016 bullet belongs under “Changes in the dx6.dll thrash driver”; its condensed catalogue description alone does not identify that component. It must not be attributed to DX5 or confused with a maximum texture side length.

The [DX6 callback audit](evidence/audits/dx6-texture-format-bound.json), reproduced with `python3 analysis/scripts/audit_dx6_texture_format_bound.py`, pins120 `drivers/dx6/dx6.dll`, SHA-256`81cc2b24972d37efca68ad277b714f5053672994df1ed266c529e1e24cd3420f`. This is also the known131 driver identity, not an authenticated unpatched NFS4 predecessor.

|Local contract |Evidence |
|---|---|
|Callback registration |60006e65 supplies60007090 to the object call at60006e75, vtable+20h |
|Initial count |60006e6b clears DWORD6001b880 before that call |
|Admission bound |60007092 loads count;6000709a compares unsigned with100; JAE60007225 exits before record writes |
|Record addressing |600070ab multiplies admitted index by156; table base6003d188 |
|Initialization/copy |Clears156-byte record; copies32 input bytes into record+48h |
|Ordinary completion |6000721c increments count and publishes it at6000721e |

At count100 or any unsigned larger value, the early route has EAX0 and returns through the shared RET8 without the record initialization/copy. With fresh synchronous enumeration and no intervening writes, admitted indices0..99 occupy15,600 bytes ending exclusive60040e78. This is a local arithmetic/storage-span statement, not proof of every loader mapping, external write or consumer bound. The manifest records the containing section metadata without reading virtual zero-fill as file bytes.

The full410-byte callback is retained. Channel-mask parsing and other fields remain part of its contract; this count guard does not establish that arbitrary malformed descriptors terminate or validate safely. Count writers outside the registration/reset and callback, reentrancy, synchronization, device acceptance and full storage lifetime remain unverified.

**MP120-016 advances vendor-only→partial:** the claimed component contains a concrete pre-write format-count guard consistent with bounding enumeration. The inspected reference bundle and110 archive do not supply the claimed NFS4 DX6 predecessor, so this audit does **not** prove that120 introduced the guard, identify the prior overflowing array or reproduce the reported crash. Required follow-up is an identified prepatch DX6 binary and paired callback/layout comparison, followed by a controlled scenario for runtime acceptance. No driver, API, game, instruction probe or Ghidra database was executed/changed.

### The EXE clamp first appears in retained 1.5.1

Search the file-backed executable sections of the retained EXEs for the
clamp-loop bytes `8b1d8c277a0039d87304d1eb75f8891d8c277a00` and
disassemble the preceding descriptor reads. There is one match per
retained release from 1.5.1 onwards and no exact match in the hosted
reference or retained 1.1.0–1.5.0 EXEs.

| Release | Clamp-loop start | Descriptor source immediately before the field reads |
|---|---|---|
| 1.5.1 | `004b5b60` | Fresh `THRASH_about` call through `009ef980` |
| 1.5.2–1.5.3 | `004b5b70` | Same fresh call |
| 1.6.0 | `004b5b61` | Same fresh call |
| 1.6.1 | `004b5be7` | Cached descriptor at `007a3a5c` |

The matched blocks all compare unsigned dwords at descriptor offsets
`+14h` and `+20h` before the same halving loop. The [Voodoo2 producer](original-modern-dll-candidates.md#shared-adapters-after-the-provider-split)
starts publishing Glide's maximum texture size into those fields in
1.5.0. The exact consumer above follows in 1.5.1, alongside the
configurable-extent change. The negative exact-byte search does not
exclude a differently encoded limit in earlier builds.

The adjacent initializer disassembly confirms insertion on the shared
renderer setup tail. In 1.5.0, jumps at `004b5a6a` and `004b5ae5` reach
`004b5b29`, the `POPAD; RET` immediately after the last set-state call
at `004b5b23`. In 1.5.1 those jumps move to `004b5a8e` and
`004b5b09` and target the new about-and-clamp block at `004b5b4d`.
The third path falls into the same block after its set-state call at
`004b5b47`. The clamp therefore extends these three existing setup
paths. The 1.5.0 paths return without applying an equivalent operation
at this point. This comparison leaves limits at unrelated call sites
outside its scope.
