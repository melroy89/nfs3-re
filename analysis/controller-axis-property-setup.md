# Controller axis property setup audit

## Scope and finding

Static review of the selected installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) traced joystick device creation, capability/property queries, property writes, and the live state-read path. The game records per-axis capability and two numeric axis properties during DirectInput device capability refresh. The code uses raw property selectors `5` and `6`, stores/query values in percentage units scaled by 100, and has a selector-1 `100 - percent` transformation on writes.

The inspected setup does not establish a configured physical axis minimum, maximum, or center. It does not show a call using numeric property selector `4` or other explicit range endpoints. The in-race read path copies driver/runtime-provided axis DWORDs unchanged into its sample cache; its evaluator separately applies binding bounds and arithmetic shift-right by eight. The installed dead-zone menu has per-axis sliders whose initial values are `0.10`; the UI callback path does link their two slider slots to raw property selectors `5` and `6` and to the cached device record described below.

## Device creation and data format

`InitializeDirectInputSubsystem` (`00434f20`) clears the 16 device-pointer slots at `005f1fb8` and associated records, then creates the DirectInput interface. `InitializeAndEnumerateJoysticks` (`00435600`) enumerates devices through the interface call at vtable offset `+0x10`, with callback `00436980`.

The enumeration callback (`00436980`) creates a device interface and places it in the indexed pointer table. It calls vtable offset `+0x2c` with the static data-format descriptor at `0052f300`, then uses the cooperative-level helper `00436610`. The descriptor begins with bytes `18 00 00 00 10 00 00 00 01 00 00 00 50 00 00 00`; these fields encode descriptor sizes/flags and a `0x50` state size in the structure consumed by the call. This is an input data format declaration, not a min/max/center calibration call. No range endpoints are passed through this creation path in the reviewed body.

## Capability and per-axis property query

`QueryAndCacheDirectInputDeviceCapabilities` (`00435690`) requests the device capabilities through vtable offset `+0x0c`. It then probes the eight axis object offsets `0, 4, 8, 0x0c, 0x10, 0x14, 0x18, 0x1c` using the device method at vtable offset `+0x38` and a 20-byte property header. Successful axis probes set corresponding bits in the axis-capability word at `005f2038 + 0x88*device`.

For each supported axis, it calls `00435ae0` twice. That helper obtains selectors `0` and `1` via `00436b10` and caches the resulting percent values in the device record at `005f2040 + 0x88*device + 8*axis` and `+4` respectively (the latter is stored as `100 - returned_value`).

`00436b10` builds a 20-byte property structure with header size `0x10`. For axis indices 0–7, `dwObj` is the listed byte offset and `dwHow` is `1`. Its raw selector mapping is:

| Selector passed to property method | Raw property identifier | Getter/setter behavior |
|---:|---:|---|
| `0` | `5` | Reads the value; on write, clamps the requested percent to `0..100`, multiplies by `100`, then calls the device method at vtable offset `+0x18`. |
| nonzero (`1` at observed call sites) | `6` | Same header and percentage representation; the wrapper path may invert the requested percentage before the write. |

The getter path calls vtable offset `+0x14`, then returns the property field divided by `100` if the call succeeds; failures return `-1`. The report retains identifiers `5` and `6` as numeric property IDs and does not assign SDK symbolic names to them.

## Property write path and call-site boundary

`SetAxisPropertyPercentWithSaturationInversion` (`00435b40`) changes the value to `100 - percent` only when its selector is `1`, then invokes `00436b10` in setter mode. During `RefreshDirectInputDeviceCapabilityCache` (`00472b60`), the fresh capability record from `00435690` is compared against the cached record at `006fc970 + 0x88*device`. When the record enters the in-place comparison branch, a difference in either axis property causes the **cached** value to be sent back to the live device through `00435b40` (`00472c28` or `00472c52`). If leading identity/record fields differ, the refresh copies the fresh record into the cache. Thus the cache is the user-setting source in the in-place refresh branch; the query value is not the source of that write-back.

The recognized-function xref result for `00435b40` lists `00472c28` and `00472c52` inside `RefreshDirectInputDeviceCapabilityCache`. Direct instruction reads also reveal calls from unrecognized frontend code regions: the axis-slider change handler at `00442e35` and `00442e4a`, plus a separate per-device/per-axis property-apply block at `004434c2` and `004434d4`. The latter reads values from a separate per-device staging table at `00660bc0` and writes properties through selectors `1` and `0`; its triggering callback/lifecycle was not resolved, so it is not assigned a Done/Cancel meaning here.

The device-record base `006fc970` is at offset `0xe30` within the configuration blob based at `006fbb40`. Each axis property pair is at record offset `+0x48 + 8*axis`: slot `+0` holds selector-0 value; slot `+4` holds selector-1 value in the complemented representation maintained by the menu path. The full-blob save routine copies `0x20f0` bytes, so these locations lie within the byte range copied by that save. This address identity does not establish that an arbitrary existing `config.dat` was accepted at runtime or when the dead-zone page is saved.

## Dead-zone menu callback to cached record and device

The installed resource `FEDATA/MENUS/deadzone.mnu` names eight axis controls with codelinks `SLDER_XAXIS`, `SLDER_YAXIS`, `SLDER_ZAXIS`, `SLDER_ROTXAXIS`, `SLDER_ROTYAXIS`, `SLDER_ROTZAXIS`, `SLDER_SLIDEA`, and `SLDER_SLIDEB`. In the executable, the initialization block at `0044336c..004433ef` resolves these exact tokens using `00442a40` and stores their widget/control objects in `00558a10..00558a2c` by ordinal.

The setup routine at `00443070` walks those eight controls for the selected device. When the cached capability bit for an axis is present, it reads the cached pair at `006fc970 + 0x88*device + 0x48 + 8*axis`, converts each integer to a UI fraction by multiplying by `0.01`, and seeds the two slider values. Setup passes `00442ef0` to the generic slider setup helper `0046cac0` and stores `00442ff0` in the control object at `+0x2c`. The two routines have distinct roles: `00442ef0` is the value-change path; `00442ff0` polls joystick state and updates the slider indicator. Unsupported axes receive the generic `0046cae0` callback setup path. The device-selection wrappers at `00443260` and `00443290` refresh the axis controls when the selected device changes.

The slider value-change body at `00442ef0..00442fe9` reads the two widget slots through `0046c9b0`, checks whether values changed, and calls `00442dd0` with the two values, selected device index, and axis ordinal. `00442dd0` multiplies each float by `100.0` (`00538a10`) and uses x87 `FISTP` to store an integer percentage. It compares and updates the cached axis pair before invoking the property setter:

| UI slot read by callback | Cache field updated | Setter selector | Raw property identifier |
|---:|---:|---:|---:|
| first slot (`0046c9b0`, selector 0) | record `+0x48 + 8*axis + 4` | `1` | `6` |
| second slot (`0046c9b0`, selector 1) | record `+0x48 + 8*axis` | `0` | `5` |

For selector `1`, `00435b40` applies `100 - percent` before calling the setter helper; selector `0` passes the percentage directly. The property cache and device setter are therefore both reached from the visible axis sliders. The first slot's complemented cache representation is the reason its UI-originated value passes through that inversion.

The value-change callback is tied to the selected/active axis control through the generic frontend slider dispatcher. The separate callback at `00442ff0..00443069` polls the device input state and refreshes the slider indicator; it contains no call to `00442dd0` and does not perform the cache/property write described above. The raw slider configuration gives `snap=0.01`, step `0.01`, and initial values `0.10`; the menu resource does not by itself show the final saved value, nor does this static trace observe a UI event or storage commit. No values from unrelated portions of the configuration blob were read or emitted.

Xrefs to `00436b10` resolve to the two getter calls in `00435ae0`, the two wrapper calls in `00435b40`, and an internal special-selector branch. The axis UI-to-cache-to-device callback path is also visible in instruction bytes even though these code regions are not declared as Ghidra procedures in the temporary REA analysis.

## Relation to live axis samples and menu values

`ReadDirectInputJoystickState` (`004358f0`) obtains the `0x50`-byte device state and copies its first eight axis DWORDs to the extended state at `+0x50..+0x6c`. `RefreshJoystickSamplesAndSyntheticKeyMask` (`004315a0`) places this extended state in the race buffer. `00431740` reads the copied axis value, shifts it arithmetically right by eight, and applies the binding's two byte bounds. No instruction in this sample-to-evaluator chain reads the stored property pair directly. The sliders instead write through the device property setter; how the installed DirectInput implementation uses those device properties to affect subsequent state values is not specified by the game's caller code.

The installed `FEDATA/MENUS/deadzone.mnu` contains `DZ_JOYSEL` and eight axis slider records (X/Y/Z, three rotation axes, Slider A/B). Each slider has step and snap `0.01` and initial `r0_val`/`r1_val` `0.100000`. Static code links those slider objects to the cached property pair and setters as described above. The default values are resource initialization values; this does not prove what values are active after user changes, whether a save committed them, or which physical device profile the runtime selected.

## Remaining limits

- No explicit physical axis range or center value was found in the reviewed enumeration, property-query, property-write, or live read path.
- The data format defines state layout/size, not calibration values.
- Numeric IDs `5` and `6` are preserved literally; assigning external API names would require separate corroboration and is not needed to establish the binary's own behavior.
- The exact parser/dispatcher lifecycle for `DZ_JOYSEL` and the final menu Done/Cancel persistence behavior remain untraced. The axis-slider callback chain itself is resolved to the cached record and raw property setters.
- The effective ranges, neutral point, extrema, dead-zone behavior, and driver transformations for any attached device require hardware/runtime observation. None was performed.

## Evidence

- Target identity: selected installed executable SHA-256 above.
- Enumeration and data-format setup: `00435600` evidence `ev_f0812b32ad2b642aa018934af2ca0a83d8278e43f18a88613ed076e0b845f88a`; `00436980` evidence `ev_d755f89708c26462f531c91dc946ec9ac82780061a1bb6efeb6c0c087b643399`; descriptor bytes at `0052f300` evidence `ev_b9d33de2edc804c18fc2eb8ec8e726b851e1fe4765f6e12c41adf92dc6970269`.
- Capability and property query: `00435690` evidence `ev_c6dc7999e28d4eca2ba65fbf01885c1294e0ccc2fb6041b78abb6168df14882a`; getter/setter helper `00436b10` evidence `ev_db66da653ed5a5e4f09c6579e255fade5a5283d7ae805ee98c0960476060b578`; per-axis cache helper `00435ae0` evidence `ev_97a5d2ced03e0bf537a9eb58dd967549b2d1e6eed5a1ae81759d2771ea20bac3`.
- Inversion wrapper and call sites: `00435b40` evidence `ev_a0f90e76ac5c83d1f0c0cf12039e04af6f349910d9316887b045d8449ec7354e`; direct xrefs evidence `ev_1d0aa22e0af1b62cde3dd1959fa3387cfdfa50d38d07f8d9cd0684da915d3f59`; capability refresh `00472b60` evidence `ev_f0ab254e4ea2c36a25bee00fe14dd4f0522ad633011b698b277e45bd14f85c1a`.
- Dead-zone widget setup and callbacks: token-resolution/configuration block `0044335d..004433fd` evidence `ev_ab06ad5bec58e40e67015be751bfb0cb7263701e659f3666e605abb379d9f313`; slider setup `00443070..00443207` evidence `ev_1d1988d28d84eb4a98ba6e75595871d11f76582eb3e0613bcf109c8c545a766e`; value-change handler `00442ef0..00442fe9` evidence `ev_b8d568e0109126c929ed57cf92b771a6bd231e5071b4efa7b0c07a4d8177e059`; joystick-poll/indicator callback `00442ff0..00443069` evidence `ev_a87f53f77d1aef5a1a79c09ff57822c35448d80ae62699adf5b261831f7752f0`; cache/device writer `00442dd0..00442e57` evidence `ev_86a48edc8bc9e37ceb11074aff9ed45e5828bd23e9ac59dffe8258e30f07eeb2`.
- Additional property-apply block `00443430..004434ee` evidence `ev_1ca74e3b9bbd9fa87647ea00e45786c501493b9b4a02f408ab6730e7a86be482`.
- Input subsystem and data-format call boundaries: `00434f20` evidence `ev_496896b788d3925445809e1d6ffe4ca79776830c448c3f53ed7bd61385bf4b4f`; mouse setup evidence is separate and was not used to infer joystick calibration.
- Live state read: `004358f0` evidence `ev_1aa39bf10c16939963a4bd15f09dafbe1c73a0812d76041779305d0a19e66e0f`; live evaluator `00431740..004317c2` evidence `ev_38811aac8364bc648193fabe709d4028d7ee1915b36ca19aa51c4e0d184972b9`.
- Menu values: `FEDATA/MENUS/deadzone.mnu`; the slider-to-cache/setter path is established by the selected-build code above.

No executable, user configuration, hardware device, or persistent Ghidra project was modified.

Parent original-byte review corroborated cached-versus-fresh direction00472c28/52, slider setup00443070, value-change00442ef0, indicator00442ff0 and cache/property apply00442dd0. Parent recovered/named those four routines plus axis-widget lookup00442e60 and saved ABI/operation comments. Cache006fc970 is offset0xe30 within the20f0-byte configuration snapshot, so the schema includes these preferences; no successful save/reload or driver property application was observed.
