# Controller device slot lifecycle

## Result

The selected executable has an in-bounds DirectInput device-index domain of `0..15` in its primary 16-pointer interface table, capability records, and state reader. The normal registration callback uses a running successful-device count as its next index. Therefore ordinal 15 is not excluded by the examined normal setup: if the DirectInput enumeration call supplies at least 16 devices that pass the game's creation, data-format, and cooperative-level setup, the sixteenth successful device is stored at slot 15 and the enumerated count becomes 16.

The paths diverge afterward. The initial capability query explicitly traverses all 16 indices, and the race state reader accepts index 15. The separate frontend/config-cache refresh loops only over ordinals `0..14`. Thus slot 15 is statically eligible for device registration and race input reads, while its frontend cached name/property record is not refreshed by that routine. No runtime or hardware enumeration was performed, so actual availability or use of slot 15 is unobserved.

## Normal registration and cache path

`InitializeDirectInputSubsystem` (`00434f20`) clears the 16 interface pointers at `005f1fb8..005f1ff7`, initializes a field in each corresponding record slot, and resets the DirectInput successful-registration count at `00554ef8` to zero. The capability/state record base begins at `005f1ff8` with stride `0x88`; the capability word for ordinal `i` is at `005f2038 + 0x88*i`.

On its first unpopulated call, `InitializeAndEnumerateJoysticks` (`00435600`) invokes the DirectInput interface method at vtable offset `+0x10` with raw arguments including numeric device type `4`, callback `00436980`, and trailing numeric flag `1`. After enumeration it explicitly calls `00435690` with EAX=`0x10`; that query's `index==16` branch processes indices 15 down through 0. The helper queries only nonnull interface slots, including slot 15 when registered, and records device capabilities and supported-axis properties in the 16-record capability area. The initialization then visits registered records for its force-feedback setup.

`RegisterEnumeratedDirectInputJoystick` (`00436980`) computes its next ordinal from `00554ef8`. It creates a temporary device interface for that ordinal, applies the installed data-format descriptor, then calls the device's vtable method at `+0` with GUID `0056b918` and output slot `005f1fb8 + 4*ordinal`. The resulting interface is stored in that pointer table. It calls `00436610` for cooperative-level setup; that helper accepts indices below 16 and uses the corresponding pointer slot. The callback increments `00554ef8` only after the setup succeeds and releases the temporary device interface. Device-create, data-format, and interface-query failures do not increment the count; a cooperative-level failure returns the enumeration stop result without incrementing. For ordinal 15, the table arithmetic remains within the declared 16 pointer and record slots.

`RefreshDirectInputDeviceCapabilityCache` (`00472b60`) receives the count from `00435600`, stores it at `006fd204`, then has a separate fixed loop whose condition is `index < 0x0f`. It therefore refreshes or clears the configuration-side cache only for `006fc970 + 0x88*i`, `i=0..14`. This is distinct from the 16-record live interface/capability domain. If enumeration count is 16, the public count can be 16 while this refresh skips cache record 15.

## Slot 15 consumers

- `ReadDirectInputJoystickState` (`004358f0`) checks `0 <= index < 0x10` and then reads `g_pDirectInputDevices[index]`. Index 15 passes this bound. On a successful state read it copies the eight axis DWORDs to the caller's extended record.
- The race sample builder `004315a0` walks the configured device-index list at `005eff20`. The binding writer derives the device index from the packed binding and `00431690` stores distinct indices in that list. A mapping with device nibble 15 can therefore reach the reader; the evaluator's index is the binding's device nibble, not the frontend cache ordinal. The race sample cache remains separate from the configuration/UI cache.
- The frontend list-label helper `0043d9f0` checks `index < 006fd204`. When the count is 16, index 15 takes its populated-slot path and reads the name from `006fc974 + 0x88*15`. This proves its local count predicate admits slot 15, but not that the cache name is current or that a particular menu interaction enumerates that list entry. The cache refresh loop above does not refresh that row.

These edges distinguish “enumerated/usable” domains: slot 15 is within the DirectInput table and race reader, and can be referenced by a configured binding; its configuration-side label and property values may remain from previously loaded/stored cache contents because the normal refresh helper stops at index 14.

## Bounds and open questions

- The fixed internal pool and consumer check support 16 indices, `0..15`. This audit follows only those in-bounds indices. The callback does not show an explicit `<16` guard before indexed registration; any additional enumeration result is outside this report's normal in-bounds conclusion.
- A real count of 16 requires 16 successful callbacks, including successful device creation, data-format setup, and cooperative-level setup. Static code does not establish that the host DirectInput provider has 16 attached devices or will enumerate them in that order.
- No device was connected, no input was polled, and no configuration was changed. Slot 15's physical presence, successful runtime registration, displayed label, property values, and race-input behavior remain hardware/runtime questions.
- No conclusion is made about more than 16 callbacks, adjacent data aliasing, or any capacity-failure consequence.

## Evidence

- Exact target: selected `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
- Subsystem initialization and 16-slot clearing: `00434f20`, Evidence `ev_1065c118ecb5b2b8ec772ef5cea45ba3f4c4d82d526a36dd083c0bff4328c809`.
- Enumeration dispatch with EAX=`0x10`, followed by all-slot capability query: `00435600`, Evidence `ev_8193bccafc31737a83f244a16a8db2047af708f6fb45c95c926f22dde133498d`; query implementation `00435690`, Evidence `ev_9923b5c62659cb3e36ea23603aca759e28829b744ffa05298ac26bbaa0ecd706`.
- Callback registration/count increment and its setup gates: `00436980`, Evidence `ev_12b8ba3ad0840cf7592a81020d863529a59fb0858df1934fb30b185cf7d1d52a`; indexed cooperative-level helper `00436610`, Evidence `ev_1c4c28fa57d11002af7493024c4c82bab9f68b0e6dc40814ec67f6985463fbb4`.
- Configuration-cache refresh limit and count publication: `00472b60`, Evidence `ev_ea257fdd7ded7639cfdce513e751e0b59272d8db755a6bb0f9569b15dbba7f16`; the full instruction listing confirms the loop compares index against `0x0f` and exits at index 15.
- Reader bound/copy contract: `004358f0`, Evidence `ev_c9a638511415f95d0a5696ed50b5fd50cbb2bece0d2cfe3e48a4b782f9e0b4b7`; count-indexed dynamic label helper `0043d9f0`, Evidence `ev_dcc4cace4fb9485965809f9c87eb9189d2b65763f4c5b71f5eba41ccbae383ca`.
- Race binding/device-list producer: `00431690`, Evidence `ev_f51d52288c1d43865e69b48937cc7a0b5f07831e44c61db7f64d8f0de27a228d`; race acquisition chain and cache distinction are detailed in [controller axis runtime source map](controller-axis-runtime-source-map.md).
- Prior record-layout and bounded enumeration evidence is in the “Input-device menu label and slot-state updates” and “DirectInput enumeration index 16 storage alias” sections of `analysis/detailed-analysis-notes.md`. This report deliberately does not extend into the out-of-bounds case.

No executable, configuration, device, or persistent Ghidra project was modified.
