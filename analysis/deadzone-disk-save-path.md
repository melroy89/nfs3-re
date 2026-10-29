# Dead-zone disk-save path audit

## Finding

On the selected installed executable (`nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`), Done/Escape on the dead-zone page do **not** directly write `config.dat`. They preserve the edited values in the in-memory configuration cache and DirectInput device properties. Leaving the enclosing Options page also has no direct call to the disk-save routine in its descriptor row or button definition.

The ordinary frontend path saves later: after the main-menu frontend loop returns, `004730d0` calls `00473080`, which calls `00472820`. The postgame frontend wrapper `004732b0` also calls `00473080` after its frontend loop returns. Neither wrapper is a pause-menu wrapper. Whether a particular session reaches either wrapper depends on the later top-level menu action; returning from Options to its parent does not itself return from the outer menu loop.

## Menu route and exit callbacks

The installed resources establish this normal route:

```text
options.mnu --nextmenu=control1--> control1.mnu
control1.mnu --nextmenu=deadzone--> deadzone.mnu
deadzone Done/Escape or Cancel --> control1
control1 Done/Escape --> options
options Done/Escape --> previous parent menu
```

The relevant descriptor rows and callback bytes in the active executable are:

- `options`, row `00555c48`: row callback fields `+0x0c/+0x10/+0x14` are copied to descriptor callbacks `+8/+0x0c/+0x10`; the row has `00442aa0` only in its `+0x0c` field (descriptor entry/init callback), with zero transition and per-frame callback fields. `00442aa0` only resolves and updates menu item flags before returning; it does not call `00472820`.
- `control1`, row `00556050`: its row callback fields `+0x0c/+0x10` map to descriptor entry callback `0043d4d0` at `+8` and transition callback `0043d5f0` at `+0x0c`; the row's `+0x14` per-frame callback is null. The transition routine refreshes the mode-specific control-map pointer and either copies staged key-map values or calls `0043c040` to rebuild those values. `0043c040` reads the mapping table through `004904d0` and `0043c000`; neither it nor the inspected `0043d5f0` body calls `00472820`.
- `deadzone`, row `005560b0`: entry callback `004432c0`; transition callback `00443430`. Cancel clears the dead-zone restore gate and the transition callback restores the entry snapshot. Done and Escape leave the gate set, so the transition callback skips restore. These values and effects are detailed in [dead-zone preference commit lifecycle](deadzone-preference-commit-lifecycle.md).

The Options and Controls resources use generic `nextmenu` transitions for their tabs and Done/Back entries; they do not define a disk-save callback. Their codelinks and transitions therefore return to the enclosing menu stack while `RunFrontendMenuLoop` remains active. The saved values are still only in memory at that point.

## Disk writer and established callers

`SaveConfigurationBlob00472820` performs these steps:

1. Calls header refresher `004723f0`.
2. Returns if `006fd3a0 != 0`, if the `0x20f0`-byte reservation through `004516a0` fails, or if `0055e88c != 0`.
3. Copies `0x20f0` bytes from configuration blob `006fbb40` into the allocated buffer.
4. Clears only buffer DWORD `+0x1860`, formats the `config.dat` path using `007a3034`, and passes the buffer to the file writer.

The direct callers in the analyzed active build are `004466a0`, `00446990`, `00473080`, and `004c4820`; xrefs show the corresponding call instructions at `004466ab`, `0044699f`, `004469f0`, `004730b4`, and `004c4823`. The main frontend route is the one tied to ordinary menu completion:

```text
004730d0 -> 0044b230 (outer frontend menu loop) -> 00473080 -> 00472820
004732b0 -> 0044b230 (postgame frontend menu loop) -> 00473080 -> 00472820
```

`00473080` runs after `0044b230` returns, not after each nested menu transition. Consequently, the normal Options → Controls → Dead Zone → Done/Escape route has a later save edge only if the outer frontend loop subsequently exits through a caller path that reaches one of these wrappers. The save routine itself then still applies the three gates listed above. This is static reachability, not proof a save succeeded in a particular session.

The other direct save callers (`004466a0` and `00446990`) lie in a frontend command-handling region, but the examined callsites do not identify either as the installed Options/Controls/Dead Zone Done path. `004c4820` is reached through `004c4830` from a separate `004a35d0` lifecycle routine; no menu resource or callback link inspected here connects it to leaving Options. These edges are retained as other save routes rather than attributed to this UI flow.

## Limits

- No immediate save on Dead Zone Done/Escape or on Options Done/Escape was identified in the reviewed menu rows, menu resource, and transition handlers.
- A later top-level frontend return reaches the save wrapper in the ordinary callers shown above, subject to `00472820` gates. Exact user action and successful filesystem write were not observed.
- The installed candidate `config.dat` and the executable's `0x20f0` load/save schema are documented in [control binding persistence audit](control-binding-persistence-audit.md). That establishes layout, not successful load/save of the candidate or persistence of this specific slider edit.
- Direct caller enumeration and the selected menu descriptor rows bound this trace; it does not rule out future build differences or runtime hooks outside this executable.

## Evidence

- Active executable identity and save-function analysis: `00472820`, Evidence `ev_a7800462df990baf58a68dc10dac10f1e6159d60a5ba2fbb85193bacdfcd2978`.
- Direct caller evidence: callers Evidence `ev_3ebcc5fb8d42b52c705d06ab121499e671d687071c7b5d4b5ceae5b481adb505`; xref instruction Evidence `ev_beb4ff1f97f25c5f30cc6fdc1fde46170c218dba4e3559a0a074949b40b1506b`.
- Main-menu wrapper `004730d0` and postgame wrapper `004732b0` both call `00473080`; evidence is `004730d0` `ev_d6ef8d9e42128c4d71b9cbb5f24b73f2727b3fe2bf94ade3bad74085f3bac9ee`, `004732b0` `ev_7a72f15c7790c4a366150fa7909070c75706dae6cd31ee5bcf2943f7e41e4bd3` and `ev_333c4e6167e5c665e830d340f2d07e9e8b0acb88eb8fb3b1ebe618c036f04f0f`; `00473080` evidence is `ev_195d9702f48d4639406c812cb9201239424b974ec887f20908ac8b123afb37c8`.
- The separate `004c4820` route is supported by `004a35d0` Evidence `ev_bb5b190f6fbb0314e1dd2b3917527eff5351a2aa36844831bacdbcca108dc7e6`.
- Control-map transition helper `0043c040`, Evidence `ev_ed310b82456bf57444300913bce6b99676ec18bad0c2ecfa408ac727ace1b67f`; descriptor bytes and menu route were checked against the selected executable and installed `FEDATA/MENUS/options.mnu`, `control1.mnu`, and `deadzone.mnu`.

No executable, user configuration, or persistent Ghidra project was modified.
