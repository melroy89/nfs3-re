# Network session toggle semantics

## Scope and target

This static audit follows the ordinary Host Game selector into its generated toggle menu, the toggle's target-pointer table and generic Enter handling, and callback `0043f7e0`. Target: active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`; installed English text pack `FEDATA/TEXT/text.eng`, SHA-256 `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`. Static inspection only; no menu was run, no network session was started, and no persistent Ghidra data was edited.

## Visible menu and localized text

The selector-zero callback at `0043f640` calls `InitializeNetworkTransportSelectionMenu` (`0043f320`) at `0043f65f` after explicitly zeroing EAX. The distinct active TCP callback `0043f760` also reaches this initializer at `0043f78e`, after helper `0043fd70` returns nonzero; this is not the explicit EAX-zero callsite. The installed connection flow is summarized in [`multiplayer-discovery-options.md`](multiplayer-discovery-options.md). The initializer stores that selector at `005f3fe8`, sets up the Host Game page, creates a two-item toggle menu through `00445750`, and passes callback pointer `0043f7e0` (`0043f496–0043f4d0`).

The active executable requests these English text IDs in its menu arrays:

| ID | Installed English string |
| --- | --- |
| `0x15` | Host Game |
| `0x1b` | Peer-to-Peer (2 players only) |
| `0x1c` | Client-Server (2-8 players) |
| `0x1d` | Positional Updates |
| `0x1e` | Controller Updates |
| `0x1f` | Optimizes data transfer for two player games |
| `0x20` | Best for games with more than two players |
| `0x21` | Best for slow network connections and Internet |
| `0x22` | Best for fast, local area networks |
| `0xf9` / `0xc6` | Ok / Cancel |

The initializer fills `005556f4` with the sequence `1b, 1c, 0, 1d, 1e`, `00555708` with `1f, 20, 0, 21, 22`, `0055571c` with `15, 0`, and `00555724` with `f9, c6, 0`. These are backing text arrays and descriptions; only the first two row entries fall within this initializer's active row count. The text pack alone does not establish that the later Positional/Controller strings are shown or map an active row to `006fd50c`.

## Target-pointer table and ordinary row writes

At `0043f4bc`, the initializer passes the static target-pointer table beginning at `005556e0` to `00445750`. Original active data bytes decode to:

| Table index | Pointer value |
| ---: | --- |
| 0 | `005f3fe4` |
| 1 | `007a22e4` |
| 2 | null |
| 3 | `006fd50c` |
| 4 | `005f3fe0` |

The generic toggle initializer (`00445750`) stores the table pointer into `00558c6c`, the row-label pointer (`005556f4`) into `00558c68`, and the active item count from EBX into `00558c64`. At this callsite EBX is `2` (`0043f4b2`), so it creates two selectable rows. The generic key handler at `00445520` cycles the current row index `00558c60` within that count on Up/Down (`0044557e–004455a1`, `004455d9–00445602`). On Enter (`AX=0x0d`), code at `00445635–00445659` checks `0 <= rowIndex < activeCount`, fetches `targetPointers[rowIndex]`, and stores DWORD `1` through a nonnull pointer. This path can write only table indices 0 or 1 for this menu instance, to `005f3fe4` or `007a22e4`. The `006fd50c` pointer is at index 3, outside the two active rows. The backing table's extra entries do not make that index selectable through the observed ordinary handler.

This resolves the indirect-write concern for the visible two-row selector: its generic row handler does not use the flag pointer. It does not establish what the two destination fields mean in every network mode, or how other code paths could use the extra table entries.

## Flag initialization and callback behavior

For selector values 0, 1 and 2, `0043f320` explicitly stores zero to `006fd50c` (`0043f43e`, `0043f451`, `0043f45e`). It then derives the auxiliary menu field `005f3fe0` from the flag (`0043f47e–0043f496`): the field is set to one when `006fd50c` is zero and zero otherwise. Thus the visible menu initializer both resets this flag in those selector cases and seeds a separate menu-state value from its inverse; it does not expose the flag as one of the two active pointer-backed rows.

Callback `0043f7e0` handles the menu's accepted selection by reading `005f3fe8`. In the Host Game selector-0 branch, it enters `0049e5f0` with EDX 1; selector 1 enters the same helper with EDX 2. The mode-2 branch calls `004c3f90`. The only callback-local store to `006fd50c` is a zero store at `0043f927` on the corresponding menu-result path. The inspected `0049e5f0` body initializes service/session fields but has no local store to this flag. Separately, `004c3f90` clears the flag in its mode-3 branch. No ordinary toggle-selection path to a nonzero write is established here.

This is distinct from `0049e080`, the shared session initializer that stores one at `0049e0ac`. The parent-reviewed caller refinement records calls `00473239 -> 0049e220 -> 0049e080` and `00473249 -> 0049e2e0 -> 0049e080` under the `RunFrontendSetup` gates. That is a separate setup path; it does not establish that the visible two-row toggle writes the flag. See [`network-motion-feature-flag-owner.md`](network-motion-feature-flag-owner.md) for the flag's other consumers and lifecycle.

## Evidence boundary

- `0043f320` initializer assembly: REA `ev_02ebb9bd5c5fef23088586b9f9a9162a62fa24c217e47cf01b38ecb887ba15a`.
- Generic toggle initializer (`00445750`) assembly: REA `ev_277afdf5e52a7d87e7d07a6819233b1dd3afc00e6b18028648e953c147f5b8aa`.
- The static table pointer has one direct code reference, the pass at `0043f4bc` (REA xref `ev_80c4cbb212e1656117e3942b51d1019a0af5b856f1a0b0bfcf1dbce5c16e504f`); the fourth pointer was confirmed from raw active `.data` bytes at `005556ec`.
- Flag xrefs are from ephemeral REA evidence `ev_bd28197a98dcfee3c917ea0ffb0793c96cb2a2d548994f8739c40597ddbbdd44`; indirect table writes are established from `00445750`, the original data table and Enter handler instructions `00445635–00445659`.
- The installed `text.eng` index resolves the listed IDs to the displayed English strings. The page's exact runtime language, actual user choice and callback execution were not observed.

The ordinary UI row/index chain does not assign a user-facing label to `006fd50c` and does not demonstrate that selecting a visible toggle row can change it. The flag's nonzero session bootstrap is statically present elsewhere; its visible gameplay meaning remains unresolved.
