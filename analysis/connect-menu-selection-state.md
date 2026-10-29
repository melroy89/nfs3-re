# Connect menu selection-state callback

## Scope

Read-only static trace against active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Focus: descriptor slot `+0x10` (`00440730`), where the frontend invokes it, ordinary disabled-item navigation, and the RaceNet entry's fallback when its item callback is absent. No runtime, network, registry, executable/configuration, or persistent Ghidra changes.

## What `00440730` does

The active `connect` descriptor row at `00555f00` stores `00440730` in its second callback slot, `+0x10`; the first slot `+0x0c` is initializer `004405c0` (see [dispatch crosswalk](connect-menu-dispatch-crosswalk.md)). `RunFrontendMenuLoop` (`0044b230`) loads the active descriptor at `00559230` and invokes `[descriptor+0x10]` at `0044b37c` when nonnull. The loop also invokes this slot after processing a selection/navigation path at `0044bcee` (`0044bb00..0044bdc0`). These are descriptor callbacks, separate from each menu item's `+0x64` callback.

In `00440730`, the callback:

1. Computes selected entry index as signed high words of descriptor `+0x16` and `+0x18` added together.
2. Locates entry record `00604ee0 + index*0xbc`.
3. Clears DWORD `g_nSessionMode` (`006fd3b0`) to zero.
4. Only continues if entry type DWORD is 5 and its codelink pointer at `+0x10` is nonnull.
5. Maps the codelink into a selection-state value: `modem`→2; `serial`→3; `ipx`, `tcp`, and `racenet`→4. The callback returns zero on all paths.

This observes a selection-state update; it does not itself open a provider dialog or establish a connection. The same value 4 is assigned to TCP, IPX, and RaceNet, so it cannot be read as a unique transport identity from this callback alone.

## Disabled items and RaceNet fallback

During `connect` initialization, `004405c0` calls the catalog-presence check for selector 3 before dealing with the RaceNet item. If selector 3 is absent, it looks up `racenet` and ORs bit `0x01` into the item's flags at `+4`, which the item-state code treats as disabled input. The reviewed service-catalog builder creates selector 1 and conditionally selector 2; no selector-3 store was found in those known builder functions. This makes “selector 3 absent” the result of the reviewed builder path, but other writers or externally supplied catalog state were not exhaustively excluded. See [service selector crosswalk](network-service-selector-crosswalk.md).

The ordinary menu-navigation scan in `0044a6b0` iterates the frontend entry records, skips records marked by its entry-state filters (including record byte `+5` mask `0x04`), and excludes candidates whose accumulated flag word intersects `0x1101`. Earlier static review associates these filters with disabled/nonselectable-entry handling. The general action dispatcher `0044a2d0` does not apply a universal per-item disabled-bit test before invoking the selected action. Thus the normal candidate scan rejects disabled entries, while a retained/current or modal selection path is not proven to recheck the item's `+4` disabled bit at every dispatch point.

For RaceNet, `004405c0` does not populate item callback `+0x64` in active `nfs3.exe`; code at `004406c7` jumps over NOPs to the TCP lookup, as recorded in the crosswalk. If a RaceNet item nevertheless reaches Enter dispatch, `HandleFrontendButtonInput` (`00461270`) sees no specialized callback, recognizes neither special command `racenow` nor `exitprogram`, and returns generic transition action 5 when item `nextmenu` (`+0x40`) is nonnull. Installed `connect.mnu` sets `nextmenu=mainmult` for RaceNet. This is a generic menu transition to `mainmult`, not the TCP Connection dialog (`0043fe50`) and not a RaceNet provider dialog. The descriptor selection callback may set `006fd3b0=4` when RaceNet is current, but that state write does not supply the absent per-item callback.

## Evidence boundary

Active instruction ranges reviewed: `00440730–00440809`, `0044b230–0044b382`, `0044bb00–0044bdba`, `0044a6b0–0044a85f`, `0044a2d0–0044a428`, and `00461270–004613da`; connect menu item data is from installed `FEDATA/MENUS/connect.mnu`. The normal disabled-candidate filter is observed, but selection-state persistence and all modal/exception paths were not exhaustively traced. Selector 3 has no producer in the reviewed catalog builder, not a whole-binary proven absence. No live frontend click was performed.

Parent verified the two descriptor-callback invocation instructions, the complete selected-build00440730..00440808 body, and the generic button action5 branch. Parent recovered UpdateConnectMenuSessionMode00440730 and saved its ABI/selection comment. The shared006fd3b0 is named g_nSessionMode in the current project; its value4 groups IPX/TCP/RaceNet rather than identifying one transport. No live selection was observed.
