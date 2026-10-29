# Dead-zone preference commit lifecycle

## Scope and result

This audit uses only the selected installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, and its installed `FEDATA/MENUS/deadzone.mnu` resource. No game, device, network, configuration write, or persistent Ghidra project was used.

The menu keeps an entry snapshot of all eight axis-property pairs for every enumerated device in staging memory at `00660bc0`. Slider edits write immediately to the live cache and DirectInput property setters. On leaving this menu, its descriptor transition callback restores the snapshot only when the Cancel handler has cleared `00660fc0`. The Done button and the Escape alias resolve through the ordinary button path and leave that flag set, so the transition callback skips restore. In this sense Done preserves the immediate changes in the in-memory preference cache and device properties. This does not establish when or whether the configuration blob is serialized to disk.

## Menu registration and lifecycle callbacks

The menu resource declares `[button] codelink=escape done` for the localized Done item and `[button] codelink=DEAD_CANCEL` for Cancel. It declares `DZ_JOYSEL` and eight `SLDER_*` controls. The raw `deadzone` descriptor row at `005560b0` is:

```text
c87d5300 00000000 00000000 c0324400 30344400 00000000
```

Interpreted as six DWORDs, this is name pointer `00537dc8`, two zero fields, and callback pointers `004432c0`, `00443430`, and null. The installed generic binder copies descriptor-row fields `+4..+0x14` to descriptor fields `+0..+0x10`. Thus `004432c0` is the descriptor `+8` initialization callback and `00443430` is its `+0x0c` transition callback. `InitializeFrontendMenuDescriptorAndEntries` calls descriptor `+8` when a descriptor is entered; `ProcessFrontendMenuMenuTransitionCallbacks` calls nonnull descriptor `+0x0c` on transition. The ordinary menu loop reaches that transition handling when it leaves a child menu.

At `004432c0`, the entry callback first sets `00660fc0=1`. For each device it copies `0x40` bytes from the device cache at `006fc970 + 0x88*device + 0x48` to `00660bc0 + 0x40*device`. The eight axis pairs are therefore snapshotted together, across all enumerated devices. The subsequent control setup resolves the eight slider codelinks and initializes their UI values from the selected device's cache.

`00443430` begins by checking `00660fc0`; any nonzero value returns without restoring. When the value is zero, it loops the enumerated devices, copies each `0x40`-byte staging record back to the corresponding cache range at `006fc970 + 0x88*device + 0x48`, then for each supported axis calls `00435b40` twice using the staged pair and selectors 1 and 0. This restores both cached properties and their device setters from the entry snapshot. The copy helper `004ea4f0` is an overlap-safe byte-range copy on this call path; it is not a zero-fill operation.

## Done, Cancel, Escape, and device selection

| User action | Static path | Effect established |
|---|---|---|
| Enter on Done | The `done` codelink uses the generic button input handler `00461270`; with no menu target field, the ordinary button path returns the child-menu exit action. The menu loop runs the descriptor transition callback. | The flag stays `1`; `00443430` returns without restoring. Slider changes already written to cache/device remain in memory. |
| Enter on Cancel | Initialization at `00443306..00443321` resolves `DEAD_CANCEL` and replaces that item's `+0x30` input callback with `00442db0`. On Enter (`BX==0x0d`), that wrapper clears `00660fc0` and calls `00461270`. The normal child-menu exit then runs the descriptor transition callback. | The flag is `0`; `00443430` copies the entry snapshot to all device cache records and reapplies supported-axis properties. This is an explicit rollback path. |
| Escape | `0044a2d0` looks up the enabled entry carrying the `escape` token and dispatches that entry's `+0x30` handler. The `escape` token is on the same Done resource item as `done`, not on `DEAD_CANCEL`. | Escape uses the Done item's generic handler; it does not clear `00660fc0`. The transition callback consequently skips restore. |
| Change selected device | `DZ_JOYSEL` is wired through the menu droplist callback wrapper at `00443260` (or its alternate input wrapper `00443290`). When the selected device index changes, the wrapper calls `00443070` to populate controls from that device's cached settings. | Device change itself does not clear the flag or call the restore block. Slider edits continue to update the selected device's cached pair and setters. A later Cancel restores the snapshots for every enumerated device; Done/Escape retain the edited in-memory values. |

The button action and callback behavior above is static code-path evidence. It does not depend on guessing meanings from addresses: the menu codelinks and localized button names are present in the installed resource, the Cancel callback is installed by an exact codelink lookup, and the `escape` token is attached to the Done item.

## Limits

- “Done” is an in-memory commit boundary: changes are live as the sliders move, and Done suppresses the menu-exit rollback. This audit does not show the exact subsequent disk-save event or prove persistence after process exit.
- The resource and code show Cancel and Escape key routes. They do not establish mouse, joystick, or window-close behavior beyond the ordinary input dispatcher branches inspected here.
- Device enumeration and property setters are not exercised. The rollback path only issues setters for axes whose cached capability bits are set.
- The installer resource is read from the selected installation and the executable hash is stated above; no conclusion is made about other game builds or modified menu resources.

## Evidence

- Active-image identity, parser/callback mechanics, and menu-transition sequence: `InitializeFrontendMenuDescriptorAndEntries` at `0044ab40` (`ev_5ffc54bf360c40552b7ad479e8c722b6924d846ae8803eb6f34b7829ede28389`), menu loop at `0044b230` (`ev_ef5f84d825c8bea5e8f0efe64cf9257dfbb3d0b9bdfb10a0be9455d102e0694c`), and transition callback orchestration at `0044aa30` (`ev_8b0bde0246e67733aaf3b960f1645ee7a724b7d0851303e0fb752cd04b53a433`).
- Generic button handler `00461270` (`ev_041453c232137e55bbab48f7abfcfcdf6a4e7269c8107267ebce96260db587ae`) and input/escape dispatch in `0044a2d0` (`ev_f428eb550c7f52c8c91a636aea5be4f67d08f748aebbaad8726a474e8cb84aac`).
- Raw instruction evidence for `004432c0..004434ee`, `00443260..004432b9`, and `00442db0..00442dcc` was checked against the selected executable with `objdump`; relevant instruction ranges are included above. `004ea4f0` byte-copy helper analysis: `ev_4d5a3d24bfd670f96cf148fd7afe6c705ab231aa508dac1e751fc2c2e4535b10`.
- Slider-to-cache/device writer and prior property layout: [controller axis property setup audit](controller-axis-property-setup.md), especially callback and cache writer evidence listed there.
- Descriptor row interpretation and generic binder behavior are corroborated by the existing [series terminal menu contract](series-terminal-menu-contract.md) and its `BindFrontendMenuCallbacksByName` findings.

No executable, configuration, hardware, or persistent Ghidra project was modified.
