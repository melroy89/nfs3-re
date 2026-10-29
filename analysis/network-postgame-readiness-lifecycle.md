# Postgame network readiness and next-race lifecycle

## Finding

On the selected active executable (`nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`), postgame runs the shared frontend menu loop. That loop calls the common per-frame renderer, which can invoke `RenderNetworkLobbyPanelAndProcessRaceStart` (`00441040`) in an active network session. The invocation is conditional on the renderer's priority/context gates, and the panel itself requires initialized resources. When session settings are settled and host/client readiness synchronization succeeds, the panel frees its two transient buffers, performs its roster handoff, and returns action `6`; the shared frontend loop can carry that action to the postgame wrapper and then into race preparation. This is a statically supported postgame route, not evidence that every postgame frame or every online session satisfies the gates.

## Postgame enters the shared menu and renderer

The postgame frontend wrapper `004732b0` calls `0044b230` (the shared frontend menu loop) and then runs its post-loop cleanup. The installed `FEDATA/MENUS/postgame.mnu` resource binds its Race Again button to `codelink=racenow`; it has no `nextmenu` declaration. The shared loop initializes the menu and, during each active frame, calls `0044a4f0` before processing ordinary input. `0044a4f0` invokes registered entry render callbacks and has an additional network-panel branch.

For the ordinary menu-loop path, `0044b230` sets `00559234=0`. In that mode, `0044a4f0` reaches `00441040` when its priority pass reaches priority `8`, the network-session marker `007a22e0` is nonzero, and the current descriptor name is not `ipx`. At `0044a618..0044a629`, the code compares descriptor field `+0x14` with literal `ipx` at `00538fc4`; `004ee310` returns zero for equal strings, and the `JZ` at `0044a627` skips the panel call on equality. The postgame descriptor names `00537d94`, whose active bytes are the NUL-terminated string `postgame`, so it is not filtered out by this comparison. Thus postgame reaches the shared network-panel call path when the priority and active-network gates also hold; whether a particular frame calls the panel remains conditional on those gates. Separately, the panel returns `6` only if its resource pointer is present, settings processing `0049a520` reports no pending change, and `0049abd0` reports readiness.

This is distinct from the Race Again button's direct Enter handler: the menu resource routes that button through `00461270`, while the panel is reached from the common frame renderer. The panel action is retained by `0044a4f0` and the frontend loop. The conditional forwarding chain into the postgame wrapper and application race-preparation state is documented in [the next-round state report](network-series-next-round-state.md#conditional-frontend-action-forwarding); it depends on no intervening dialog or action override.

## Buffer lifecycle

The menu-entry path `0044ab40` calls `0044a960`; when the network marker is set, that helper reaches `00440970`. `00440970` releases any existing buffers at `005f3fdc` and `005f3fd0`, allocates fresh storage for both through `004e1620`, and initializes them through `004e0640`. In the ordinary menu context (`00559234 == 0`), it also clears `006fd508`. This ties the buffers to menu entry/transition setup rather than to a permanent process-wide allocation.

`00441040` calls `00441950` while rendering the network panel. The latter checks that both resource pointers are nonzero before drawing the network participant rows. On the successful readiness/action-6 path, `00441040` frees both pointers via `004e1890` and zeros each global before calling `0049acd0`; that routine performs the participant data handoff into the race setup records and calls frontend cleanup `00445f10`. The pointers are not retained by the panel after it returns the start action. A later menu entry can allocate fresh buffers through the entry path above.

## Readiness and synchronization gates

Before checking readiness, `00441040` calls `0049a520` to process changed network profile/race settings. If that helper reports a change, the panel does not start a race on that frame. Only a zero result proceeds to `0049abd0`.

The panel caller already requires active network marker `007a22e0`. The helper `0049abd0` itself has a distinct no-session branch: if that marker is zero, it jumps to its common success return and returns `1`. On the active-network path it requires the signed WORD at `007a2276` to be at least `2` (`CMP WORD [007a2276],2; JGE`); lower signed values return `0`. Its role-specific checks are:

- **Client (`007a22da == 0`):** readiness succeeds only when session state `007a229c == 1`.
- **Host (`007a22da != 0`):** it loops against the signed high WORD of `007a2274` (`SAR EAX,0x10`; signed `JGE` comparison). For each roster entry, it resolves a participant with `004a6690` and requires the resolved slot's ready byte at `0079f5f8 + 0x60*slot` to be nonzero. It then sets the local synchronization marker `0055e710` and also requires `007a01ec == 0` (through `0049f680`) and `007a229a == 0`.

After those checks, the host executes additional synchronization helpers `0049ee50` and `0049aa80`. Both roles then call `0049a8e0`, `004e070c`, and two `004a6a10` waits before the readiness helper returns success. The successful panel path subsequently frees the UI buffers, invokes `0049acd0`, and returns action `6`.

The separate renderer `0049ab60` is an availability/readiness predicate: it requires active network state, at least two participants, and nonzero ready bytes for the other enumerated participant slots. It is not the full start gate: host-only pending-state and synchronization checks reside in `0049abd0`, and settings changes are handled first by `0049a520`.

## Evidence and limits

- Active executable identity as above; no executable, runtime, network, or persistent Ghidra changes were made.
- Postgame wrapper `004732b0`: `ev_390601e5f0f88e61b39eed960c242e632cc0dec40c7ed3f05ef9b49d22a70c47`; shared menu loop `0044b230`: `ev_b680f3a154a4612786dd2a176634b503fd052347ee10f1740216f70a54c36a8d`.
- Menu renderer `0044a4f0`: `ev_87b818822f3fe614ff52c839a81feaf8a0e5d3c976c6f7d6d261118b155e1992`; its exact priority-8 string-filter assembly is `ev_1adfc189c81d74ed19453d0d7fdba83126b671cece4be5807fd7b3260ef55dc2`. Literal `ipx` bytes are `ev_46253178658ef5e317e42e87ca8b82f4301ee9f4f88f0a37b43bd109ec47c4e2`; postgame name bytes are `ev_5b3f72b4815fe5e0eea1e5bfa969ed31f516e4ee15c3d02f9402fec3958de384`. Panel `00441040`: `ev_4c60b9eb4c2e63f2f542a3dda2a5e0dce2ae124448b2b4208efb280ba4d25b56`.
- Entry setup `0044ab40`: `ev_d1c42d51fb086d369f38b76e1460e129b1d8ca8f5c03f8de5030fb92842f0e52`; buffer allocation `00440970`: `ev_8729c111d4c7d9583166035e6852286bd6104e7898eaafa690998267644dfa8a`; participant-row rendering `00441950`: `ev_5bf0dd2fe134c9549a6fb41cf89e67a99d44eb030892abb6c6badf9cbbdf7e21`.
- Settings-change processor `0049a520`: `ev_43aa30e40d7dfb305fab9ba9b84d354ce26cfba87a7b0ca2a2e5239ce93ff237`; readiness/synchronization gate `0049abd0`: `ev_a919c804b4a78765e7c9baf6216d6b6894aa160798a6012735c268090501f2fa`; its signed count and no-session branches assembly: `ev_c5249dc0d2d6f2d2f7ed0662fd72e7e65249e0680c2bfe2a128ffba7db8d2e16`; display/readiness predicate `0049ab60`: `ev_8f5195e0151cb8f6591631de98bcf35b8ffe32cb952bfd9170bba65e2332c30e`.
- Post-success setup snapshot `0049a8e0`: `ev_02b24917f1092318af38dcae061e52bab787b2cbdbabf2273cad069e8bf3f393`; roster handoff/cleanup `0049acd0`: `ev_cf7708d60bb100f2258643a0fc10242ffe2c7c220976e12540b8be3008677d07`.
- Resource-to-handler details are in [series terminal menu contract](series-terminal-menu-contract.md). Action forwarding into the next race is bounded in [network series state at next-round setup](network-series-next-round-state.md).

Static control-flow establishes the postgame integration and role-dependent readiness checks. It does not establish that readiness packets arrive, that a user session reaches the specific gate in practice, or that all peers subsequently initialize and run the next race successfully.
