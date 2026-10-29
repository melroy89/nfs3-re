# In-race controller axis source map

## Scope and result

This is a static trace of the selected installed executable `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. It follows the racing sample path from configured joystick-device selection through DirectInput state acquisition, the per-device cache, and axis evaluator `00431740`.

The in-race path reads the device state into a race-specific buffer and copies the eight raw axis DWORDs into the cache consumed by `00431740`. The path shifts the cached value right by eight in the evaluator, but no center subtraction, dead-zone operation, or axis inversion is visible between the DirectInput read and that evaluator. Device-reported ranges, center values, and any driver-level transformations remain unknown. The frontend binding-capture cache is separate and is not the source read by the racing evaluator.

## In-race producer and cache

1. `ApplyConfiguredBindingsToActionSlots` (`0048f1f0`) maps the selected mode's binding record into evaluator slots. Its slot writer, `0048f940`, stores each packed binding at `0079c340 + 4*slot`. For nonempty, non-keyboard bindings, it extracts the device nibble from the packed binding and calls `00431690`.
2. `00431690` adds each distinct referenced device index to the signed-byte list at `005eff20`, terminated by `-1`. `00431580` resets this list and clears the associated race input-state area before bindings are rebuilt.
3. `CollectBoundPlayerInputsAndActionHistory` (`0048f550`) calls `004315a0` (`RefreshBoundJoystickSamples`) before evaluating the player's bindings. `004315a0` walks the configured device list and calls `ReadDirectInputJoystickState` (`004358f0`) for each device, using the per-device race-state destination at `005eff30 + 0x84*device`.
4. On successful state acquisition, `004358f0` copies eight DWORD axes from the DirectInput state at offsets `+0x00..+0x1c` to the extended state at offsets `+0x50..+0x6c`. Thus axis `j` is cached at `005eff80 + 0x84*device + 4*j`, exactly the address family read by `00431740`. It initializes the button word separately and derives POV direction codes from the four POV fields. These POV/button operations do not transform the eight axis values.
5. If the state query fails, `004315a0` clears that device's `0x84`-byte race-state record, so a failed read does not retain the previous successful axis sample. This behavior differs from the frontend capture refresh described below.

The source routine calls the device interface's operation at vtable offset `+0x64`, then obtains a `0x50`-byte device state through the operation at `+0x24`. The static evidence establishes these calls and the copied offsets; it does not require naming the interface methods beyond the DirectInput state-read path.

## Evaluator transformation

`00431740` extracts the device index from the packed binding's high nibble and the axis index from the next nibble. It reads the corresponding DWORD from `005eff80 + 0x84*device + 4*axis`, then applies arithmetic shift-right by eight. The shifted signed value is compared with the two packed byte bounds and mapped using the asymmetric saturation/interior rules documented in [controller-channel-calibration-audit.md](controller-channel-calibration-audit.md). The evaluator's bounds are binding data; they are not proof of a hardware center calibration.

The collector stores the relevant evaluator return values as the `Accelerate` and `Brake` sample bytes for slots 2 and 3, per [controller-action-label-crosswalk.md](controller-action-label-crosswalk.md). Those action labels identify configured actions, not a fixed physical axis assignment. Which device and axis feed either action depends on the selected binding.

No live-path instruction in the traced chain subtracts a device center, applies a dead-zone threshold, rescales a reported range, or negates an axis sample. The arithmetic shift is a scale reduction by 256 before byte-bound comparison; it is not evidence that DirectInput values are normalized consistently across devices. Likewise, the `100-percent` inversion wrapper and axis-property percentage access described in the calibration audit are in capability/property setup, not in this sampling-to-evaluator chain. Their effect on raw race samples is not established here.

## Separate frontend binding-capture cache

`RefreshFrontendJoystickAxisSamples` (`0043d920`) calls the same `ReadDirectInputJoystickState` helper, but writes shifted axis values into the distinct frontend cache based at `005f3d50`. The frontend poller `0043be40` consumes that cache to detect a newly moved axis while capturing a control binding. It updates only enabled axes and leaves cached values unchanged on failed reads. Neither the cache address nor its retention behavior matches the race path at `005eff80`; frontend capture samples therefore cannot be used as evidence for the live evaluator's cached input or failure handling.

## Configuration and evidence limits

The persistence audit establishes the installed candidate's binding record layout and the executable's mode-dependent loader/setup schema, while explicitly leaving the active runtime file and player/mode selection unresolved. The action-label crosswalk establishes slot 2 as Accelerate and slot 3 as Brake, but does not bind either action to a physical axis. Accordingly, this report establishes the source path and visible transforms, not the selected device/axis, current binding, or effective device calibration.

The DirectInput state values originate from the installed runtime/device interface. No controller was polled and no game was run. This static trace cannot establish the actual range, center, orientation, noise, driver calibration, or whether a particular device behaves as expected. The precise remaining runtime observation, if needed, is to record the same device's eight raw values returned by `004358f0` and the corresponding `005eff80` entries during neutral, negative/positive extrema, and controlled dead-zone movement, then compare those values to the selected binding bytes and `00431740` output. That observation would resolve hardware behavior; it is not part of this audit.

## Source notes

- Target identity: selected installed `nfs3.exe` SHA-256 above.
- Prior static axis evaluator review: `00431740..004317c2`, evidence `ev_38811aac8364bc648193fabe709d4028d7ee1915b36ca19aa51c4e0d184972b9`.
- The in-race binding/evaluator chain, frontend cache distinction, and device sampling behavior are recorded in `analysis/detailed-analysis-notes.md` under “Frontend joystick-axis sample refresh,” “Input binding consumer follow-up,” and the axis/evaluator entries, and are cross-referenced by the three controller audits listed above.
- No executable, configuration, runtime input, or persistent Ghidra state was modified for this report.
