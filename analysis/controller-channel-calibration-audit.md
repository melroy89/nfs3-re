# Controller channels and axis calibration audit

## Scope and result

This is a static audit of the exact installed NFS III tree at `nfs3_decomp.rep/Electronic Arts/Need For Speed III`. The executable analyzed was `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. The ephemeral REA/Ghidra session was closed without a snapshot; no persistent analysis project, executable, input device, or gameplay state was changed.

The producer-to-consumer mapping for the four-byte sample is established, but this installation does not statically bind the first two positive channels to named actions. Channel byte `+1` is evaluator slot 2; byte `+2` is evaluator slot 3. They are independently assigned to vehicle bytes `+0x504` and `+0x505`, then smoothed and normalized before motion consumers. The vehicle field consumers support throttle/engine-response and brake/wheel-response roles, but the analyzed path does not identify which field is which; mode/profile transformations and arbitrary bindings prevent a stronger label. The menu names physical axes and exposes dead-zone controls, but it does not establish which axis is assigned to either channel.

## Producer and consumer chain

The established issue 14 chain in `analysis/detailed-analysis-notes.md` is:

1. `ApplyConfiguredBindingsToActionSlots` maps a mode-specific set of 13-DWORD binding records to runtime slots.
2. `CollectBoundPlayerInputsAndActionHistory` evaluates the first four slots into a four-byte sample:
   - sample `+0` = low byte of arithmetic-shift-right(binding 1 result minus binding 0 result, 1);
   - sample `+1` = low byte of binding 2 result;
   - sample `+2` = low byte of binding 3 result;
   - sample `+3` = eight-bit action mask.
3. The player-control callback/replay handoff supplies those bytes to `UpdatePlayerVehicleControls`. That routine copies `+1/+2` to vehicle `+0x504/+0x505`, sign-extends `+0` into `+0x518`, and sends `+3` through action/shift handling.
4. Vehicle update code smooths `+0x504/+0x505` to `+0x508/+0x509` and stores byte/255 normalized floats at `+0x5f0/+0x5ec`. `+0x5f0` feeds engine response, wheel response and damping; `+0x5ec` feeds four-wheel integration and damping. These consumers indicate control roles, not a unique action identity.

Accordingly, **exact channel labels are unresolved**. “Accelerator/throttle” and “brake” are plausible role descriptions from downstream uses, but assigning either to `+1` or `+2` would exceed the evidence. Likewise, channel 0 is steering-related by its signed treatment and consumers, but its physical axis is not identified.

## Binding evaluator and transformations

The six-entry dispatcher table at `00554e34` maps binding classes 0–5 to zero, axis range, joystick button, POV, keyboard and digital dispatcher. The same dispatcher supplies the first three sample channels and the eight per-player action bits. For class 1, the axis evaluator result is preserved in channel 1/2 before low-byte truncation; nonzero results also set the corresponding action bit. This is separate from the fixed 32-action history path, whose class-1 branch turns the axis result into 255 only when signed result is greater than 128.

Parent original-byte review of `00431740..004317c2` refines the evaluator formula (REA evidence `ev_38811aac8364bc648193fabe709d4028d7ee1915b36ca19aa51c4e0d184972b9`). Let a=(binding>>16)&255, b=(binding>>8)&255 and x=arithmetic_shift(cached_axis,8). Device/axis nibbles select the cache at005eff80. The exact return is:

- a<b: x<a returns0; x>b returns255; otherwise return x when a=0, or2*(x-a) when a!=0.
- a>b: x<b returns255; x>a returns0; otherwise return a-x when a=255, or2*(a-x) otherwise.
- a=b: return0.

Interior values can therefore reach508 (for example a1,b255,x255), while the collector retains only the low byte. This is asymmetric saturation, not255 on both sides and not distance to the nearest bound. Default endpoint bounds0/255 avoid the doubled branch, but actual installed binding decoding and runtime axis units remain unresolved.

The collector's channel-0 difference/2 is the only proven centering-like operation in the live sample path. It is a difference between two independently evaluated bindings, not evidence of a physical joystick center calibration. No supported evidence establishes a universal live dead-zone, center, or inversion transform after the axis evaluator. In particular, the frontend axis cache at `005f3d50` is used by binding capture and is distinct from the in-race bound-input evaluator; do not treat the frontend capture path as live race calibration.

## Installed menu and configuration evidence

The installed `FEDATA/MENUS/deadzone.mnu` includes a `DZ_JOYSEL` device list and sliders for X/Y/Z, X/Y/Z rotation, and two slider axes. Each slider uses `percenttype=0`, `snap=0.01`, `r0_step/r1_step=0.01`, and `r0_val=r1_val=0.10`. The localization keys name these controls “X Axis”, “Y Axis”, “Z Axis”, “X Rotation Axis”, “Y Rotation Axis”, “Z Rotation Axis”, “Slider A”, and “Slider B”. The screen labels and defaults establish editable per-axis percentage settings in the menu, not their effective value in the race evaluator.

The related wrapper at `00435b40` (`SetAxisPropertyPercentWithSaturationInversion`) transforms `100 - percent` only for axis selector 1, then calls the DirectInput axis-property accessor. The accessor chooses numeric property 5 for selector 0 and property 6 for nonzero selectors, and clamps the resulting signed percentage to 0..100. Existing call-site evidence places these operations in `RefreshDirectInputDeviceCapabilityCache`. This supports an inversion/saturation operation in the device-property capability/cache setup. It does **not** prove that the racing binding evaluator applies this wrapper's property to its cached axis samples or that inversion is a user-selectable live-channel option.

The installation's `FEDATA/CONFIG/config.dat` is 8,432 bytes (mtime 2026-10-10 16:08:07 +0200). Its leading bytes include `f0 20 00 00`, `06 00 00 00`, and `76 1c 00 00`; later bytes contain apparent binary records and textual profile records. No verified parser-to-offset mapping was found for this file in the bounded issue 14 evidence, so these bytes are recorded only as installation identity/data, not claimed as the selected player binding table. Menu files contain the axis labels and slider defaults above, but do not encode the selected live bindings in readable action-name form.

## Remaining questions

- Which actions the installed profile assigns to binding slots 2 and 3, and whether its selected mode uses the same record row at runtime.
- Whether the player’s current `config.dat` data is the active profile and how its bytes map to the 13-DWORD records.
- Whether device-specific DirectInput property 5/6 values affect live race samples, including center, dead-zone, saturation and inversion.
- Actual device axis ranges, centers, orientation, and whether drivers expose consistent values. These require controlled hardware/runtime observations; they cannot be inferred from menu defaults or the static evaluator.

## Evidence boundary

The producer/consumer and evaluator statements above are static binary evidence corroborated with the prior issue 14 notes; menu keys/defaults and file bytes are direct observations from the installed tree. No gameplay, runtime input, or hardware sampling was performed. The install's localized labels describe axes, not action-slot identities. No claim is made that the inspected `config.dat` is the current user's active configuration beyond its presence in this installation tree.
