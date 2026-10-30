# Original versus official Modern: texture extent limits

## Scope and artifacts

Static comparison of the supplied original executable and official archive Modern executable. This follows the Modern `AllowHugeTextures` value into dimension-building paths and records limits that bypass or reduce it. Renderer DLL behavior and successful rendering are outside the executable-only comparison.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

## Modern setting and renderer-dependent reduction

In the official Modern settings loader, `004b56d5–004b56f1` reads `AllowHugeTextures` (key at `0053f6d0`) with default zero. Values 0–3 produce `256 << value` and store 256, 512, 1024, or 2048 at `007a278c`; unsigned inputs outside 0–3 (including negative integer bit patterns) use shift zero and therefore produce 256. This is the configured extent before subsequent renderer initialization.

After renderer initialization obtains a descriptor at `007a3a5c`, code `004b5bd6–004b5bf5` takes the unsigned minimum of descriptor DWORDs `+0x14` and `+0x20`. It repeatedly halves `007a278c` until the value is no greater than that minimum, then writes the reduced extent back. This makes the configured setting an upper request, subject to the two descriptor values. The descriptor fields' exact API meaning and their live values are not established here. If their minimum is zero, this reduction writes zero; the dimension builder can then accept initial zero for nonnegative inputs. Its fallback to 1 applies when halving reaches zero, not when the starting extent is already zero. Ordinary positive descriptor invariants are not established by this code alone.

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
