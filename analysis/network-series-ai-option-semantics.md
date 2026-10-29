# Network Tournament and Knockout opponent-option semantics

## Scope and target

Static analysis of the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows the ordinary opponent controls through setup reconciliation, network option serialization, and mode-one/mode-two roster construction. No game, network, executable, configuration, live-memory, or persistent Ghidra changes were made. No online race was executed.

## Player-facing opponent-count selector

The installed `FEDATA/MENUS/opponent.mnu` provides an Opponents page. Its opponent-count arrow and cascade use `listname=oppnumber` and carry `codelink=hostonly` (with the extra `OPPNUM` / `OPPNUM_CASCADE` tags). The descriptor at `00556690` points to text IDs at `005562ac` and stores the selected ordinal in `006fd4d0`. The IDs are `0x90`, `0x91`, `0x92`, then zero; installed English text resolves them to **None**, **One**, and **Full Grid**. The same page's Skill Level control uses `listname=ai` and presents **Normal/Aggressive**. This establishes an installed control and labels. The `hostonly` gate disables input for a network client under the observed frontend gate; it does not by itself show which network setup screens expose the page or what a player sees at runtime.

For ordinary racing, `BuildRegularRaceRoster` (`00473bf0`) consumes `006fd4d0`: 0 creates no AI opponents, 1 creates one, and values >=2 request enough AI racers to bring the human-plus-AI count to eight. That is the direct meaning of the menu's three choices on that builder. It should not be generalized to series rosters.

## Tournament/Knockout setup reconciliation

`ReconcileRaceSetupMenuConstraints` (`0044be60`) has two adjacent policies with different gates:

- The `006fd504` normalization is network-session-gated. At `0044c00d..0044c014`, the reconciler skips that block when `006fd3b0 < 2`. Inside it, race mode `006fd3b8` equal to 1 or 2 changes `006fd504` from 3 to 0 (`0044c02a..0044c035`) and applies the corresponding car-eligibility filter. This field is byte-staged at network settings offset `+3`; its exact player-facing name was not established, and this filter is not evidence that it is the opponent-count or AI-fill control.
- The Full Grid/traffic policy is outside that session-mode block. After the `JL 0044c095` skip at `0044c014`, the common branch tests race mode at `0044c095..0044c0a3`; for either mode 1 or 2, it stores 1 to traffic-disabled global `006fd4e8` and 2 to opponent-count selector `006fd4d0` at `0044c0a5..0044c0bc`, then applies filter mask `0x884`. Thus these writes apply to series race modes generally, subject to the reconciler's top-level `00662968` guard; they are not conditional on `006fd3b0 >= 2`. In `oppnumber`, ordinal 2 is the installed **Full Grid** label.
- `BuildRaceModeOneRoster` (`00474310`) stores AI skill ordinal 1 (Aggressive) to `006fd4f0` at `00474328`; `BuildRaceModeTwoRoster` (`00473ee0`) does so at `00473eff`. These stores occur at builder entry and override the generic Skill Level menu choice for these builder paths.

The selector can be sent in network settings: `0049aa80` stages the low byte of `006fd4d0` at `0079f908` (record offset `+0x18`), while `0049a520` loads that byte back. The adjacent byte at record offset `+3` carries `006fd504`. This proves settings serialization and local application, not the exact ordering of every settings update and reconciliation call on every peer. Even where a menu selection writes a transient opponent ordinal, the series reconciler's explicit policy restores Full Grid when it runs for mode 1/2.

## What the series roster actually builds

The network branches of both series roster builders are distinct from the ordinary builder's `006fd4d0` arithmetic:

- They walk the signed advertised participant count and match each monotonically increasing participant ordinal against the fixed eight-WORD participant identity map (`FindNetworkParticipantSlotById`, `004a6690`). Under a stable map, no more than eight remote human rows are accepted.
- They then initially construct AI rows up to a local total of eight, using the number of matched human rows rather than consulting the None/One/Full Grid selector. This is the code's forced-fill policy for Tournament and Knockout setup, not a user-chosen AI count.
- Knockout subsequently reduces the AI count according to its generated series order and per-profile eligibility state. The result can be fewer than a full grid after eliminated profiles are excluded. That reduction is independent of the ordinary opponent-count menu. Existing detailed bounds and the progression/eligibility caveat are in [network capacity and admission audit](network-capacity-admission-audit.md).

The series result path runs its local mode-specific updater after local result ranking without a host-only scoring gate; the next-round setup exchange copies the host's configuration block to clients. Those facts support a local series setup/synchronization path, not proof of successful online Tournament or Knockout runtime support, a complete player-visible flow, or identical race outcomes. See [network series result ownership](network-series-result-ownership.md) and [network next-round state](network-series-next-round-state.md).

## Practical conclusion and limits

The installed menu contains a shared opponent-count selector, but its ordinary-race meanings do not govern the Tournament/Knockout roster builders. For race modes 1/2, setup reconciliation forces the selector to **Full Grid** and disables traffic regardless of the session-mode gate used by the separate `006fd504` normalization. The mode-specific builders set AI skill to **Aggressive**. The initial series roster fills remaining participant positions with AI; Knockout can later reduce that AI population using its eligibility/order state. The fourth network-setting byte `006fd504` also participates in car-selection filtering and is normalized from 3 to 0 only in the session-mode-gated block; its label is unresolved and it is not a demonstrated AI-count setting.

The evidence is static. It does not establish that the Opponents page is reachable on every host setup route, when the reconciliation callback runs relative to each menu event or received setting, whether all online peers complete the next-round exchange, or whether a full supported online Tournament/Knockout works in practice.

## Evidence

- Active binary identity: SHA-256 above; independently reopened with REA's ephemeral Ghidra provider. The owned REA session was closed after inspection.
- `ReconcileRaceSetupMenuConstraints` raw instruction evidence: `ev_54509c7ab105c2cd250ac1c6af7325cd42f3a6266d8a0d03e8610fef818cf8c8`; raw jump at `0044c014` targets the shared series-policy block at `0044c095`. The builder skill stores are at `00474328` and `00473eff`. Direct xrefs for `006fd4d0`: `ev_007ff596b86ec7d6c5ecdddad93b7c13ec0dbc58bf7f35d6499831e262691e04`.
- `006fd504` direct-xref evidence: `ev_2b91e968dbc0384a27b57e8ab2affbac06920c81aba7a442c6cd116ffd3abe27`; includes reconciliation, default initialization, network receive and settings staging references. It contains no direct menu descriptor pointer, so its UI label is not assigned here.
- Installed `opponent.mnu` and text-ID mapping are recorded in [AI difficulty and profile controls](ai-difficulty-gameplay-controls.md) and [ordinary opponent count choices](detailed-analysis-notes.md#regular-race-opponent-count-choices-and-roster-budget). `oppnumber` descriptor references selector `006fd4d0`; ordinary builder semantics and series roster qualifications are also documented in [network capacity and admission audit](network-capacity-admission-audit.md).
- Mode-one/two roster instructions and stable eight-ID-map limitation: the capacity audit's evidence index lists the active-build analyses; its supported conclusion is conditional on the identity map staying stable during the loop.
- Result and next-round host/client boundaries: [network series result ownership](network-series-result-ownership.md), [network next-round state](network-series-next-round-state.md).
