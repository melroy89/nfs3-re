# Traffic density and option behavior

## Player setting: two states, not a density slider

The shipped `main.mnu` Opponent button opens `opponent.mnu`. That page defines a Traffic arrow tab and cascade, both with `listname=traffic` and `codelink=hostonly`. The static list parser at `00442c80` walks five-DWORD entries from `005563e8`: each entry's first DWORD is the list-name key, the second points to its WORD text-ID array, and the fifth (entry `+0x10`) is the selected-index storage returned through the parser's output parameter. The `traffic` entry is at `0055667c` (index 33, stride `0x14`): its value-array pointer is `005561ca`, and its selected-index storage is `006fd4e8`. The array is `[0x00e4, 0x00e5, 0]`; installed `text.eng` resolves these IDs to **On** and **Off**. The menu event path at `00461347..0046138a` calls the parser with the row's `listname`, uses that returned storage pointer for the current index, and cycles through the returned label array. Thus index 0 is On and index 1 is Off. This resolves the earlier misleading adjacent-pointer reading: the next table entry at `00556690` is the separate `oppnumber` key.

The roster consumer uses the same field as an enable gate despite its zero-for-On polarity. `BuildRegularRaceRoster` (`00473bf0`) creates traffic records only when `006fd4e8 == 0`; a nonzero value skips the traffic loop. `BuildHotPursuitRoster` (`00474640`) uses a common final gate that similarly clears the traffic count when this selector is nonzero. The installed `config.dat` stores DWORD zero at file offset `0x19a8`, matching `006fd4e8`'s offset (`006fd4e8 - 006fbb40`) in the full `0x20f0` configuration blob and therefore representing the On selection if this file is accepted. Its SHA-256 is `e9e67b195cd90214ae33986ed6d1593e200f067e1b859cd2706e1af9ee0a449d`. The executable's default initializer also writes zero. These are stored/default values; neither establishes the final accepted configuration or current menu choice in a running game.

The `hostonly` token adds a network-role gate. The static menu-style handler disables the corresponding input control for the client-side state it checks; it does not prove that the control is hidden. Race setup reconciliation forces the Traffic index to Off in modes 1 and 2, while ordinary race mode 0 is not forced off there. Hot Pursuit's mode 3 is also not forced off by that specific reconciliation branch. The shared opponent-menu asset plus the mode and roster code support the setting's ordinary-race and Hot Pursuit semantics; the exact menu presentation/reachability for every mode was not runtime-sampled.

## Why Traffic can be unavailable in Single Race

`UpdateRaceOpponentSelectionControls` (`00427190`) looks up `TRAFFIC_BUTTON` and `TRAFFIC_CASCADE` and applies an additional opponent-count gate. In ordinary race mode0, selector `006fd4d0 == 2` (Full Grid) sets button disabled bit0 at `004271ce` and cascade flags `0x1001` at `00427208`. Other ordinary opponent counts clear those masks at `004271d4` and `00427210`. Thus selecting None or One re-enables the controls in this path; Full Grid disables them. This is separate from the roster arithmetic that also leaves no traffic slots with Full Grid.

Modes other than0/3 set these disabling masks, consistent with the series policy. Mode3 skips these particular mask updates, leaving its other initialization/role gates separate. The same routine disables the opponent-number controls in mode3. These are exact menu-state writes, not a claim that flag0x1000 alone means hidden or that every menu interaction was observed. The user reported Traffic unavailable with ordinary Full Grid selected; the concurrent read-only capture confirmed race mode0, opponent selector2 and TrafficOff while still at setup. Switching the controls and the resulting roster are separate runtime checks.

## Ordinary-race roster budget

`BuildRegularRaceRoster` constructs the human racer(s), then AI opponents, then fills any remaining slots with traffic when Traffic is On. Its supported opponent choices come from the installed `opponent.mnu` list and localization: None (`0`), One (`1`), and Full Grid (`2`). For a normal single human racer and ordinary mode 0, the roster arithmetic is:

| Opponent choice | Human racers | AI opponents | Traffic records when On | Traffic records when Off |
|---|---:|---:|---:|---:|
| None | 1 | 0 | 7 | 0 |
| One | 1 | 1 | 6 | 0 |
| Full Grid | 1 | 7 | 0 | 0 |

The formula when enabled is `max(0, 8 - humanRacers - AIopponents)`. Here 8 is the ordinary local roster's shared budget, not a dedicated traffic-density value or a proven backing-array capacity. For selector values 0/1/2 the AI counts are 0/1/`8-humanRacers` respectively. This explains the practical control: selecting fewer opponents lets enabled traffic use more of the roster budget; Full Grid leaves no traffic slots. Traffic Off suppresses all traffic records through the common gate.

## Hot Pursuit roster behavior

Hot Pursuit uses role-specific budgets rather than the ordinary eight-slot formula. In local single-player with Traffic On, a human racer receives one AI racer, six AI police and four traffic records (12 total including the human); a human police driver receives six AI racers, no AI police and one traffic record (8 total including the human). With Traffic Off, the common construction gate removes those traffic records. These are configured roster totals, not a claim that every record is simultaneously visible or active.

A separate special configuration bit, `0055eb2e & 0x20`, changes the local Hot Pursuit role budget: it selects Aggressive skill, sets three traffic records and two AI police while retaining the role-specific AI-racer count, and clears the Traffic-Off selector so the traffic records pass the final gate. The bit's player-facing identity is unresolved, so it should not be treated as an ordinary Traffic menu setting. The RUSHHOUR cheat is distinct: the Hot Pursuit roster masks its retained override flags with `0x10`, dropping RUSHHOUR's bit `0x08`.

## Track limits and reactivation

The track tuning initializer (`0040e410`) sets a per-track traffic threshold and reactivation-delay range for modes 0 and 3. For track IDs 0–8, both modes use cap values `[8, 6, 9, 5, 7, 6, 5, 5, 12]`. Their base delay ranges are respectively:

- Ordinary mode 0: `[40, 120, 80, 100, 40, 120, 80, 80, 20]`.
- Hot Pursuit mode 3: `[40, 120, 80, 100, 40, 120, 80, 80, 20]`.

The mode 3 track-4 initializer call at `0040e6b7..0040e6cf` passes delay range `0x28` (40) and cap 7 for row base `0056f000`; this corrects an earlier 120 entry. Its complete mode 3 vector now matches mode 0.

Modes 1 and 2 initialize both fields to zero. The cap is returned by `GetConfiguredTrafficVehicleLimit` (`0040ef10`) and is used only by `CheckTrafficVehicleReactivation` (`0040c210`), after the race tick reaches 1920 and the vehicle's `+0x650` countdown reaches its check point. The test compares `g_nTrafficVehicleCount - g_nInactiveAIVehicleCount` with the selected track cap. The latter counter is shared across AI classes, so this operand is not a direct visible-traffic census. The gate controls later reactivation; it does not allocate the initial roster. The delay range is fed into per-vehicle countdown initialization, with weather/night-style modifiers able to add 200 and 400 to the selected base range. Consequently roster option, initial registered-record count, per-track cap, countdown timing, cross-class inactive counter, and what the player sees are separate quantities.

RUSHHOUR sets `006fd4fc` bit `0x08` in its accepted local cheat path. The track-record setter `ConfigureTrackAIParameterRecord` (`0040e3c0`) responds by setting cap `15` and base delay `0` for the configured record, taking precedence over the normal row values. The existing helper can still add 200 and/or 400 to the delay range. The regular session-0 roster does not consult this flag when calculating traffic slots: with one human, the ordinary opponent choices still allocate at most 7, 6 or 0 traffic records. Thus RUSHHOUR raises the reactivation threshold; it does not request 15 new traffic vehicles. Its cap also exceeds the ordinary solo roster's maximum traffic records. The flag is retained for ordinary session 0 but removed by the Hot Pursuit roster's mask, so it does not override Hot Pursuit's cap path.

## Evidence, bounds and remaining gap

- Executable identity: installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
- Exact list parser: `00442c80`, REA evidence `ev_1ce244f81fcb46aed67a3cb930baf5f466d7ee7085e4bef0cc106576912d03ac`. It reads each key at table-entry `+0`, returns the array at `+4`, and returns the selection-storage pointer at `+0x10` through its EDX out-parameter. The `traffic` entry bytes at `0055667c` are `607f5300 ca615500 00000000 00000000 e8d46f00` (`ev_8bd8303436c9f8bc319f22379dca557a8602500ee5432f9cb530d47eb22f1ef0`). The text key bytes at `00537f60` are `traffic\0` (`ev_4944d42c39ea8180baa2b40fd077808136aa916bb7bef202ac46931685940a3b`); the list WORDs at `005561ca` are `[0xe4,0xe5,0]` (`ev_485b4d09b82fd7aae90770e022d05c62e6e52fca8027491b9d083a160cf2ee68`).
- Menu event/list navigation: `00461270` (`ev_041453c232137e55bbab48f7abfcfcdf6a4e7269c8107267ebce96260db587ae`), including parser call at `0046134c` and selected-index/list traversal through `004613a8`.
- Installed menu assets: `main.mnu` SHA-256 `9bdd70113881cff5b6161cb7dd9400b43d38a4ab062042e8c1946b80ea042ed9`; `opponent.mnu` SHA-256 `83aad629e611f452f64067dde3834738a4a4bc0e615a6a5a754520c71b344626`. The latter defines the Traffic button/cascade, `listname=traffic`, and `hostonly` gate. Installed `text.eng` SHA-256 `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`; IDs `0xe4/0xe5` resolve to On/Off.
- Traffic setting, default and roster: default initializer `00472404`, `ev_cd1a4597296719d435a8516fa11418aca03e126352be0c44188a676d48446a25`; ordinary builder `00473bf0`, `ev_83abf63fc2182a25420e4144b70234dd8d87ce378fcaa0a80a2c0207a1092f58`; Hot Pursuit builder `00474640`, `ev_64dd9774dc7918b05677551e73ceb1dd30baa5caf710d787d6ca7fd2da7e969c`; setup reconciliation `0044be60`, `ev_c3d2e53dc8969de23587fb38754de3a7d542e6da253017baa46dd27e4de97cfe`.
- Track behavior: tuning initializer `0040e410`, `ev_316ee8111e793458871a14552871afebc9b4528d8d24c6287679256e51c5ed4d`; setter `0040e3c0`, `ev_ae442809c7653f3c5bba0885d2576ed76ea442acbcca437c03a9d4ba1dea9cb7`; cap getter `0040ef10`, `ev_4554a6d81495f6cacc0dfe3ca9f97548b466c4661f45bc684646cab032c10087`; delay getter `0040eed0`, `ev_e86f3ed14827cd83dd94e937511871dbb2ab7ed708c63e714da2f4b05b33e090`; reactivation gate `0040c210`, `ev_546454f4971be8bfafe086a7f4b34344c63f4b448720fa939abc7de5105bfef8`.
- Configuration path: loader `00472980` (`ev_af8be2b2697b26ab1daa45dc0b5b05013ceb6e98ddd6fe12b461c0dc66adcc12`) and saver `00472820` (`ev_a7800462df990baf58a68dc10dac10f1e6159d60a5ba2fbb85193bacdfcd2978`) move the complete `0x20f0` blob at `006fbb40`; for `006fd4e8`, the relative location is `0x19a8`. The installed candidate has DWORD zero there. The load path accepts only an exact-size blob, and no runtime file-open/read or final selection was observed.

Static analysis closes the supported option values, ordinary local roster arithmetic, local Hot Pursuit role counts, and the track reactivation controls. It does not establish the number of cars simultaneously active in a rendered scene, the visual spacing/streaming cadence, the selected language/profile, or that the candidate config was loaded. No gameplay run, configuration write, executable write, or persistent Ghidra edit was made.

Parent review corroborated ordinary/Hot Pursuit roster construction, reactivation and delay getters, descriptor parsing and RUSHHOUR setter. Raw EBX/EDX instruction review confirms the mode0/3 cap and delay vectors, including track4 delay40. No rendered population or runtime setting was observed.
