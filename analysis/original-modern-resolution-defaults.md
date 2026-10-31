# Original versus Modern: requested resolution defaults

## Evidence and scope

Static comparison using the supplied original/backup and official Modern v1.6.1 fingerprints in the [baseline](original-modern-differences.md). The [display-mode manifest](evidence/audits/original-modern-display-modes.json) retains the original/Modern default initializer `00472d10`, original menu selector `004483a0`, Modern selector `00448394`, and Modern desktop-metrics helper. Reproduce with `python3 analysis/scripts/audit_display_mode_difference.py`. No game/API/probe execution or executable/database mutation.

This follows the requested-mode producer missing from the [mode-selection report](original-modern-mode-selection.md). It is a bounded default-initialization path, not proof that it runs on every first launch or ignores every saved configuration.

## Original default path

Original `00472d10..00472f18` initializes multiple settings from local tables and a calculated tier. Near its end, renderer mask `[007a3a58] & 6` selects **320** or **640** in EAX (`00472eaa..00472ec8`). It calls `004bee80`, then selector `004483a0` at `00472ed2`.

Original `004483a0` takes an identifier in EAX, initializes/enumerates the list through `004482c0`, then scans the collected menu records at `00661220` with stride 0x114, and stores the matching row index at `006fbc14` and that row's DWORD `+4` at `006fbc18`. If no matching ID is found, it selects row zero. This differs from Modern's packed width/height request and nearest-area search; the same global addresses must not be assigned unchanged field semantics across versions.

The complete original tier computation and `004bee80` contract remain outside this chapter. The shown path establishes literal 320/640 selection, not an original desktop-resolution query.

## Modern default path

Modern `00472d10..00472e1c` loads `[005652a4]` into ECX, caps it to unsigned 5, and halves it when `[007a3a58] & 6` is nonzero. This ECX value indexes byte tables for several graphics settings. The [CPU tier comparison](original-modern-cpu-tier.md) now traces its feature/family score producer, distinct from original’s million-scaled estimate. Vendor/legacy branches and runtime interpretation remain bounded.

The requested size is then chosen as follows (`00472dbb..00472dce`):

| Condition | Stored DWORD at `006fbc18` | Width/height WORDs |
|---|---|---|
| Renderer mask has bit 1 or 2 set | `01e00280` | 640 × 480 |
| Neither bit set, adjusted tier < 4 | `01e00280` | 640 × 480 |
| Neither bit set, adjusted tier ≥ 4 | `7fff7fff` | 32767 × 32767 |

It stores `006fbc14=1` and calls `00448394` (`00472dde`). The default initializer itself contains no desktop API read.

The large request must not be described unconditionally as “highest resolution.” It feeds the same machine-width nearest-area calculation documented in the mode-selection chapter, with approximate eligibility and depth handling. For ordinary fitting candidate areas below the requested area it favours larger area; arbitrary driver dimensions or arithmetic wrap need not follow that intuitive model.

## Modern request-to-menu linkage

`00448394` first initializes/enumerates the menu list through `00448320`. It chooses requested depth **32** by default. If `Hide16bitModes` is zero and bit 0 of `006fbc14` is clear, it instead requests **16**. Thus the default initializer's explicit bit value requests 32 on this path.

It zero-extends height WORD `006fbc1a` and width WORD `006fbc18`, pushes depth/height/width, then invokes `004bedcc` at `004483c4`. It searches the menu list for the returned driver index; if absent, it uses row zero. It stores the menu-row index at `00a1825c` and invokes `00448400` on that row. The latter copies dimensions/depth into `006fd1e4..006fd1ec` and reacts to changed dimensions.

This connects default requests to actual selection code. It does not prove a nonempty list, a valid row-zero fallback, driver availability or rendered output. The sorted menu's deduplication and `Hide16bitModes` rules are documented in the [admission/menu report](original-modern-display-modes.md).

## Desktop helper and release-note claim

Modern also contains helper `004f9140..004f915d`: EAX points to two output DWORDs, populated by imported GetSystemMetrics with arguments 0 and 1. That is a concrete metric-read mechanism, not proof of its use by default initialization. The inspected `00472d10 -> 00448394 -> 004bedcc` route does not call it. A bounded search of the retained linear Modern disassembly found no direct `CALL 004f9140`; indirect calls and data-held function pointers are not excluded.

**MP100-011** says the first run tries a gameplay resolution nearest the Windows default. The final binary contains a nearest-area helper, but the directly traced default path supplies fixed/large sentinel requests instead of values from the metric helper. The historical claim therefore remains **unresolved/partial**, not confirmed and not universally disproven. Establishing the precise first-run path requires tracing the caller's saved-setting validity branch and all relevant indirect/configuration producers; dating behavior additionally needs the earlier release binary.

Modern caller neighborhood `00472aac..00472aea` checks header/version-like fields before choosing between another path and default setup (`00472ad7 -> 00472d10`). The fields' complete serialization/validity contract is not reconstructed here, so this branch is not relabeled simply “first run.”
