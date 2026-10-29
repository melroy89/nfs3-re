# `006fd50c` network-motion feature flag ownership

## Scope and target

This read-only audit follows direct references to `006fd50c`, its ordinary initialization/session writers, and the AI/network motion consumer. Target: the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. No game/runtime/config changes or persistent Ghidra edits were made. The REA import was ephemeral and closed after inspection.

## Direct writer inventory

The ephemeral REA/Ghidra direct-xref query for `006fd50c` returned 28 instruction references (`ev_bd28197a98dcfee3c917ea0ffb0793c96cb2a2d548994f8739c40597ddbbdd44`). The parent’s separate saved-Ghidra review reports 29 direct references; that list does not include the two raw-block stores at `00452d57` and `00452f34`, which were verified in the active executable bytes. The counts therefore describe different analysis databases, and neither count is treated here as a complete writer proof. The writer table below combines direct xrefs with those independently disassembled raw stores:

| Store site | Observed value and context |
| --- | --- |
| `0043f43e`, `0043f451`, `0043f45e` | `InitializeNetworkTransportSelectionMenu` (`0043f320`) writes zero for selector values 0, 1 and 2. It then builds a two-choice toggle. Its callers include the Host Game path (`0043f65f`) and another menu entry (`0043fbc4`). The menu's selector/text mapping does not expose `006fd50c` as a standalone labeled catch-up option. |
| `0043f927` | Menu completion path stores zero before returning through its frontend callback. |
| `00452d57`, `00452f34` | Two network/session menu setup paths set zero while initializing their adjacent session/transport state, then call shared menu initializer `00452bd0`. |
| `004726b0` | Default game-configuration initializer stores zero. |
| `00472b1f` | Configuration-load completion stores zero after importing the `0x20f0` configuration blob. Thus the live flag is explicitly reset even on the accepted config-file path; the persisted blob value does not by itself establish the runtime flag. |
| `0049e0ac` | `0049e080` stores one along with network session fields (`007a22e0=3`, `007a22e4=2`, race/session mode `006fd3b0=4`). Its two direct callers are `0049e220` and `0049e2e0`, reached from the main-menu/network setup flow. REA caller evidence: `ev_ca5cab8115c0b40f929c6eae11e0950ef415f8c2053bb71968a3bea609f95bbd`; call-site references: `0049e24b` and `0049e30b`. |
| `004a663a` | Shared network-session cleanup path stores zero. Direct callers listed by REA include `0049e220`, `0049e800`, `004a3690`, `004a6ce0` and `004c3f90`; this supports use during connection/session cleanup, not a separate user setting. |
| `004c3fc6` | The mode-3 branch of `InitializeNetworkSessionConnection` (`004c3f90`) clears the flag while selecting transport/session state 2. Its caller is the network setup callback at `0043fa85`. |

This is a bounded direct-address writer inventory, not an alias-aware proof against arbitrary memory copies. The configuration default/load and network profile import paths can also copy the whole configuration block; the reviewed `config.dat` load explicitly resets the flag afterward. The existing TRN/KOT import path copies the whole blob and its preserved ranges do not overlap this field, so such a profile can replace the live DWORD on successful import. No profile was loaded or tested.

## Motion consumer behavior

`CalculateNetworkVehicleMotionScale` (`00408f10`) starts with a neutral float of `1.0`. If `006fd50c` is zero it returns that value without entering the correction-response body. If nonzero, it reads the network correction record through `ReadVehicleReplicationCorrection` (`004c8040`), which supplies the received/local progress delta and motion data described in [network motion correction coordinate units](network-motion-coordinate-units.md). The routine applies its existing delta and role gates; on the qualifying response path it computes a scale from `1 + (2 - delta) * 0.03`, floors negative results at zero, and may call `ApplyNetworkVehiclePositionCorrection` (`0040bd80`) for the large one-sided negative-delta case. In other qualifying branches it changes vehicle desired speed at `vehicle+0x7b0` or updates vehicle response flags. The network-motion report bounds the delta in segment-progress steps, not physical distance.

The sole direct caller in the current Ghidra call xrefs is `00409330` (`ev_7890c1b3be4326eedbc4bc0f6cc78f4f4a2b875d5e0a27fe783a108454f16a1c`). At `004093fa`, it calls `00408f10`; the returned x87 scale is multiplied into the other response terms and stored in `vehicle+0x7bc` (`00409414–00409449`). The combined value then multiplies `vehicle+0x7b0`, storing the adjusted desired speed back to `vehicle+0x7b0` (`0040945e–00409476`). A separate `006fd4fc` bit `0x20` can force `+0x7bc` to `1.0` after that combined calculation, so the flag-gated response is one contributor within a larger vehicle-response calculation.

This establishes that nonzero enables a network correction/AI response factor that contributes to the desired-speed update and can select position correction. It does not establish that the flag is an “AI catch-up” setting, a player-adjustable feature, or a globally consistent on/off switch: the same DWORD is also consulted by input-ring, transmission, replay, postgame, and speech-related code.

## Ordinary setting and lifecycle interpretation

The installed multiplayer menu gives a visible Host Game route into `InitializeNetworkTransportSelectionMenu` (`0043f320`) and its transport callback (`0043f7e0`); the Join Game route reaches `JoinSelectedNetworkGameAndAwaitRoster` (`0049e800`). The common network-session initializer `0049e080`, which sets the flag to one, has direct callers `0049e220` and `0049e2e0`. The static evidence reviewed here does not close the exact user-selected transport/service callback from those visible choices into one of those two initializer callers, so this remains a bounded call-path gap. The selector initializer resets `006fd50c` for selectors 0–2, while setup and cleanup paths clear it again. This is the strongest supported ownership chain: it is a shared cross-path session/configuration control whose nonzero state is established during a network-session setup path and then consumed by multiple subsystems. The installed menu initializer presents a two-choice toggle, but the localized values and callback do not prove a direct semantic mapping from either visible choice to this DWORD. The normal installed config loader also zeros the field after reading, so stored `config.dat` alone is not its runtime owner.

## Evidence and remaining uncertainty

- Exact direct references: ephemeral REA xref evidence `ev_bd28197a98dcfee3c917ea0ffb0793c96cb2a2d548994f8739c40597ddbbdd44`; the distinct parent Ghidra reference count is reported above, and raw-block stores are listed from active-byte inspection.
- Transport-selector assembly: `0043f320`, `ev_02ebb9bd5c5fef23088586b9f9a9162a62fa24c217e47cf01b38ecb887ba15a`; established UI route in [`multiplayer-discovery-options.md`](multiplayer-discovery-options.md).
- Network initializer assembly: `0049e080`, `ev_ebf8df1266b5c6b363b07e8484f92e8e17a8cebbf6db935cd07abdcb95531555`; caller list `0049e220` / `0049e2e0` in `ev_ca5cab8115c0b40f929c6eae11e0950ef415f8c2053bb71968a3bea609f95bbd`.
- Motion consumer assembly: `00408f10`, `ev_1329ce7b794bf06d048fcc721335827c76fe2df2375554a1e8dd51e6994ef81a`.
- Type-3 session transport branch: `004c3f90`, `ev_915590da993d38bd366c229a0a88ea3a925194d9852589185d15f26d0504aa11`.
- Input, transmission, replay, speech, and vehicle-motion cross-references are summarized in [`detailed-analysis-notes.md`](detailed-analysis-notes.md#type-6-participant-input-frame-construction-004c60c0-004c6870-004c61e0); segment-relative correction inputs are in [`network-motion-coordinate-units.md`](network-motion-coordinate-units.md).

The remaining gap is the visible name and exact user action that selects the nonzero session state in a normal supported network setup, plus runtime confirmation of when the several consumers observe it. No catch-up label or single feature owner is assigned here.

## Parent caller refinement

The saved shared project lists exactly one direct call to each wrapper: `00473239 ->0049e220` and `00473249 ->0049e2e0`, both inside `RunFrontendSetup`. Parent active-byte review of `004731d0..00473265` establishes the gates: `0055b03c != 0`, nonempty endpoint at `007a1fa0`, and signed participant-number selector `007a1ffc > 1` for the client wrapper (otherwise host wrapper). Both wrappers reach `0049e080`, which sets the flag. Existing first-entry byte evidence identifies `0055b03c` as file-backed1 and cleared before ordinary menu entry. This provides a concrete first-entry direct-network producer route; it is distinct from clicking ordinary Host/Join controls. No direct menu-to-wrapper edge was found in the current xref scope, and indirect callers are not excluded. Runtime connection success and any user-facing name for the flag remain unverified.
