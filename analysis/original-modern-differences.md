# Original versus Modern Patch: executable differences

**Audit in progress.** This document explains verified differences and indexes the remaining code-level investigation. It does not equate vendor release-note entries, differing bytes or Ghidra functions with independently explained gameplay changes. The original supplied executable, official Modern Patch release and local edited analysis target are kept distinct.

## Evidence and scope

- [x87 precision comparison](og-modern-x87-precision.md): verified original single-precision switches removed by Modern Patch; frontend/render scopes and runtime limits explained.
- [Original/Modern/local function-range and PE inventory](evidence/audits/original-modern-function-diff.json): all 4,133 local functions in the saved Modern database, plus imports, resources and section-level byte counts.
- [Official download and local-edit provenance](evidence/audits/modern-official-provenance.json).
- [290-entry release-note catalog](modern-patch-change-catalog.md): a traceability backlog, not 290 verified code changes.
- [RaceNet callback comparison](connect-menu-dispatch-crosswalk.md): earlier explicit original-versus-active-binary evidence.
- [Renderer loader](original-modern-renderer-loading.md), [configuration precedence](original-modern-configuration.md), [window callbacks](original-modern-window-handling.md) and [screenshots](original-modern-screenshots.md): instruction-level comparisons and bounded unknowns.
- [Network endpoints](original-modern-network-endpoints.md) and [menu toggle/retry](original-modern-network-port-menu.md): default/selected ports and revised adapter behavior.
- [Startup policy/defaults](original-modern-startup-policy.md) and [RAM pool](original-modern-heap-initialization.md): optional OS requests, configurable size and retained allocator instructions.

Read-only PE parsing, disassembly and Ghidra metadata inspection were used. The original was separately imported/analyzed under ignored `analysis/captures/modern-differences/ghidra-original/`; the established Modern Ghidra project, executable and maintained C were not modified. No new game, multiplayer, replay or instruction-probe execution was performed for this audit.

## 1. Three-way provenance

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Supplied `nfs3_org.exe` | 1,589,248 | `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` |
| Official v1.6.1 executable downloaded from VEG | 1,698,304 | `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6` |
| Local v1.6.2 preparation / saved Modern analysis target | 1,699,840 | `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb` |

Official source: [VEG's v1.6.1 page](https://veg.by/en/projects/nfs3/), [package](https://veg.by/files/nfs3/nfs3_modern_patch.7z), fetched 2026-10-31. The archive is 1,663,896 bytes, SHA-256 `c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3`. Its English readme matches the installed one exactly (`02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d`). No publisher signature or independent original-retail provenance was established; these are exact downloaded/supplied artifact identities.

**Local edits are not silently attributed to VEG.** Official versus local `.code` has exactly three changed bytes at `004a534f..004a5351`, changing `004a534e MOV ESI,immediate32` from About-string pointer `0053d698` to `00a52bf2`. The relocated string contains the local v1.6.2 date and VEG/Melroy attribution. The corresponding `.data` span differs at 131 bytes; `.idata` and `.reloc` are identical. Resource/header/version changes account for the other measured local differences and file growth. The original-versus-Modern function inventory uses the **official executable**, with names/ranges from the local saved analysis; the one code operand difference is recorded explicitly.

The precision blocks studied in the first chapter are the same between official and local Modern builds. Thus that precision finding is not an accidental consequence of our local attribution edit.

## 2. Whole-section and function-range inventory

Original and official Modern share a 1,257,472-byte code span at VA `00401000`, raw offset `400`. Within that span **41,441 bytes differ**. Section renaming from `AUTO` to `.code`, and `DGROUP` to `.data`, is not itself an algorithm change.

| Original / Modern region | Comparison |
|---|---|
| `AUTO` / `.code` | Same VA/raw size; 41,441 differing bytes |
| `.idata` | Same VA/raw size; 3,517 differing bytes, including reorganized descriptors/names |
| `DGROUP` / `.data` | Same VA/raw size; 11,576 differing bytes |
| `.bss` | Uninitialized-data attributes and raw offset 0; declared extent grows by 27,648 bytes. Not treated as on-disk initialized bytes. |
| `.reloc` | Moves from VA `00a19000` to `00a1f000`; raw size 96,256 → 94,720 |
| `.rsrc` | Moves from VA `00a31000` to `00a37000`; raw size 2,048 → 112,640 |

The saved Modern Ghidra inventory has **4,133 local entries**, including thunks:

- **3,772** have identical bytes at all corresponding original VAs in their current Modern body ranges.
- **361** have differing bytes at those same VAs.
- Every selected range could be read from file-backed sections in both binaries.

These are **same-address body comparisons**, not proved semantic function matches. Of the 361 differing entries, 202 also have an automatically identified original entry at the same address; 159 do not. Even the former need boundary/control-flow confirmation. The separate original autoanalysis identified 3,619 functions; that count difference is not proof that the patch added exactly 514 functions, because analysis coverage and manually recovered boundaries differ.

Of the 41,441 differing code bytes, 19,515 lie inside the currently identified Modern bodies and 21,926 lie outside them. The outside-body changed bytes include 18,098 NOP bytes (`90`) and 605 zeros; the rest still need classification as removed/dead code, data, new unrecognized code or boundary problems. The audit does not silently call those bytes “padding” or claim full code coverage.

A function with unchanged bytes can still change behavior because a caller changes the FPU control word, globals, imports or input domain. Conversely, a changed operand does not necessarily represent a new feature.

## 3. Confirmed numerical difference

The [precision chapter](og-modern-x87-precision.md) records six original FINIT/save/AND/FLDCW sequences selecting CW `007f` (24-bit significand), their removal, and Modern FINIT/extended boundaries. It also shows conditional extended precision around original race-frame rendering, so “only menus/HUD use extended precision” is too narrow.

The following representative Modern-named body ranges are byte-identical in the original and official Modern executable:

| Entry | Current analysis label | Bytes |
|---|---|---:|
| `00485c30` | Line-boundary candidate helper | 747 |
| `004a78d6` | Apply car tuning to physics parameters | 2,777 |
| `004aca4f` | Calculate wheel planar response record | 2,049 |
| `004ad7a3` | Integrate four-wheel responses | 3,358 |
| `004ae4c1` | Vehicle physics dispatch | 257 |
| `004bd000` | Record participant replay input tick | 135 |
| `004bd090` | Apply participant replay input tick | 335 |
| `004bcee0` | Decode replay four-channel input block | 285 |

This supports a specific mechanism: important unchanged physics/input-replay instructions can run under different surrounding precision settings. It is **not** proof that the full simulation is otherwise unchanged, that the replay format is wholly identical, or that cross-version multiplayer/replays do or do not desynchronize. Their dependencies, headers/timing and runtime behavior need separate comparison.

## 4. Import and resource changes

Both executables have 207 import entries, but the symbol sets differ. Counts alone would conceal the changes.

| Static import additions in Modern | Static imports removed from the executable table |
|---|---|
| `GetPrivateProfileIntA`, `GetPrivateProfileStringA`, `GetPrivateProfileSectionA` | `CompareFileTime`, `GetFileTime`, `GetDriveTypeA`, `GetLogicalDriveStringsA`, `GetLogicalDrives`, `GetVolumeInformationA`, `GetVersionExA` |
| `GetProcessHeap`, `HeapAlloc`, `HeapFree`, `HeapReAlloc`, `HeapSize` | `_lopen`, `_lclose` |
| `FindResourceA`, `LoadResource`, `LockResource`, `SizeofResource` | `GetFileVersionInfoA`, `GetFileVersionInfoSizeA`, `VerQueryValueA` |
| `PlaySoundA`, `timeGetTime` | `DirectDrawCreate`, `DirectDrawEnumerateA` |

These are verified dependency-table changes, not yet complete proofs of behavior at every use. Removed static DirectDraw imports do not prove DirectDraw support was removed: dynamic loading and renderer interfaces must be traced. Added INI/heap/resource imports provide concrete anchors for the corresponding code chapters rather than establishing all of their semantics on their own.

Original PE resources contain icon `3/1/0`, group `14/32512/0`, version `16/1/0`. Official Modern includes icon payloads `3/100..105/0` and `3/200/0`, groups `14/MAIN.ICO/0` and `14/ORIG.ICO/0`, RCDATA `10/ABOUT.QFS/0` and `10/SNAP.WAV/0`, version `16/1/0`, and manifest `24/1/0`. The exact RVAs, sizes and payload hashes are retained in the JSON inventory. Resource presence is not a call-path proof; screenshot/About integration still needs use-site tracing. The local variant changes the version resource and adds the redirected About text.

## 5. Confirmed menu-routing difference

The existing [connect menu crosswalk](connect-menu-dispatch-crosswalk.md) directly compared the two local binaries. Original `nfs3_org.exe` stores a RaceNet callback at `004406d7`; active Modern jumps from `004406c7` to `004406de`, with the original assignment region replaced by NOPs. The unchanged TCP route is registered separately at `004406ee`. This is a specific removed registration, not evidence that all RaceNet/network transport functionality was removed or that a provider works at runtime.

The official/local code comparison establishes that this region is the same in the downloaded Modern release. The earlier mistake of treating original registration as active Modern evidence must not recur in broader cross-version analysis.

## 6. Renderer loading: verified semantic comparison

The [renderer-loading comparison](original-modern-renderer-loading.md) establishes the original `004f8390` / Modern `004f84a8` correspondence: all 34 export names retain their pointer slots, while Modern adds mandatory export/null-descriptor checks, table-driven cleanup and changes local fallback/return behavior. It also traces driver-specific INI/ENV configuration. Original selection precedence, renderer DLL implementation changes and runtime acceptance remain separate work.

## 7. Game configuration lookup

The [configuration comparison](original-modern-configuration.md) traces the Modern caller and INI/environment readers: explicit INI values precede environment defaults, then caller defaults. Original registry imports and the new profile API calls support a migration. The [registry follow-up](original-modern-registry.md) maps original renderer values and retained online/memory queries; generic key producers and complete migration coverage remain pending. The configured filename is passed as direct buffer address `007a263c`; its executable-basename selection and fallback are now traced in the startup-path chapter; later writes remain outside that bounded audit.

The [renderer lifecycle comparison](original-modern-renderer-lifecycle.md) maps original callback installation and `00517610` to Modern’s direct `00517620`, including mode-call return checking, a byte-identical setup tail and original hard-coded environment values. This is static control-flow evidence; driver success/failure recovery remains untested.

## 8. Window initialization and callback lifecycle

The [window comparison](original-modern-window-handling.md) records all 26/27 initializer registrations, the shift from focus callbacks to application activation, hook install/teardown changes, and an ABI/result anomaly in the added power handler. The 120-byte window dispatcher is unchanged. Actual window style/size and every focus-restoration path remain to be compared; no suspend behavior was tested.

## 9. Screenshot input and encoding

The [screenshot comparison](original-modern-screenshots.md) traces original Alt+P to synchronous Desktop TGA writing, versus Modern Print Screen to a pending request and encoding worker under `.\screenshots\`. Modern format selection, PNG default and BMP fallback are documented with ownership/runtime limits. No screenshot was taken.

## 10. Network ports, endpoint conversion and menu

The [endpoint comparison](original-modern-network-endpoints.md) traces original literal 1030 versus Modern configured/default 9803, comma normalization and colon-port handling. The [menu comparison](original-modern-network-port-menu.md) identifies the two-value toggle and conditional alternate-port retry. Local notice suppression/reinitialization changes are traced; actual occupied-port joining and original/Modern race synchronization remain untested.

## 11. Startup policy and RAM pool

The [startup comparison](original-modern-startup-policy.md) traces optional error-mode suppression, dynamically resolved affinity mask 1, and the final binary’s settings defaults/clamps. The [RAM pool comparison](original-modern-heap-initialization.md) confirms original fixed 16 MiB versus configurable default 32 MiB, the original null-backing-pointer guard and unchanged allocator instructions. Effective OS policy, allocator callback state and historical multicore fixes remain separate, untested claims.

## 12. Display modes and texture extents

The [display-mode comparison](original-modern-display-modes.md) traces exact-4:3/15-or-16-bit original admission versus Modern approximate aspect/16-or-32-bit admission, internal callback ABI changes, sorting and `Hide16bitModes` grouping. It records the inclusive count boundary separately from the advertised 100-mode limit. The [texture comparison](original-modern-texture-limits.md) follows configured extents, renderer reductions and fixed/bypass branches; the original helper is not universally capped at 256. Driver DLL behavior, all list storage/reachability and actual rendering remain untested.

## 13. Viewport, aspect factors and border geometry

The [viewport comparison](original-modern-viewport-geometry.md) derives the centred 4:3 reference rectangle, changed internal setter ABI, dynamic aspect-factor writes and profile rectangle rounding differences. The [border comparison](original-modern-border-geometry.md) traces the cached thickness source and changed wrapper call, while keeping the original same-address global’s meaning separate. Complete HUD/camera/map consumers and visual correctness remain pending.

## 14. Menu and multiplayer text input

The [input comparison](original-modern-menu-input.md) traces Tab/Shift+Tab routing, explicit Tab/Escape bypass of the lobby handler, generalized named-arrow actions and the new empty-text send guard. The lobby handler, previous/next routines and send routine are byte-identical; the relevant changes are in their callers. Active entry callbacks can still consume keys, and actual original/Modern UI behavior remains untested.

## 15. HUD presets and loading artwork

The [HUD initializer comparison](original-modern-hud-layout.md) traces original locale-selected `*def.pos` parsing versus Modern embedded coordinate data and x87 aspect adjustment, plus exact six-profile header defaults. The [loading-artwork comparison](original-modern-loading-artwork.md) traces 300 small-tile iterations versus six larger/overlapping tiles, reference-rectangle placement and changed progress calculations. Both retain the original floor/ceil helper bodies; this is not a new floor/ceil algorithm. Original asset-to-preset correspondence, full progress meaning and rendered output remain pending.

## 16. Startup paths, INI basename selection and directories

The [startup-path comparison](original-modern-startup-paths.md) traces Modern’s explicit executable-directory attempt, its ignored API result/210-character gate, executable-basename INI preference and fallback, 22 initialized path slots and 13-required/four-create directory tables. Original already has directory setters and a frontend switch/restore path; the change is not a newly imported API. Ordinary INI producer-to-reader linkage and conditional screenshot-directory anchoring are now explained. Complete original installation discovery and later CWD/path writes remain separate.

## 17. Clock source and loading timing

The [clock comparison](original-modern-clock-source.md) verifies 16 direct GetTickCount-to-timeGetTime replacements, while three timer functions retain every other body instruction. This supports the API-change claim, not measured accuracy or frame pacing. The [loading-timing comparison](original-modern-loading-timing.md) traces seconds-to-milliseconds conversion, low-32-bit arithmetic, signed 0–10,000 ms clamp, progress throttling and input cancellation. Exact visible duration, all synchronization consumers and cross-version behavior remain untested.

## 18. CPU rating and defaults tier

The [CPU comparison](original-modern-cpu-tier.md) traces original’s million-scaled estimate versus Modern’s family/feature score at the same global, with coordinated changes in two consumer neighborhoods. This is not a measured CPU benchmark or evidence of SIMD racing physics. Full calibration/vendor paths and runtime default choices remain pending.

## 19. Frontend sound requests and separate volume

The [frontend sound comparison](original-modern-frontend-sound.md) traces the removed caller volume multiplier, separate menu-volume field and slider, new ID bounds and per-ID timing gates. The normal record initializer is byte-identical. Counter units, sample/backend behavior, all callers and audible equality remain pending.

The [music comparison](original-modern-music-selection.md) traces menu subset cycles, race-state progression and contextual restart/continuation gates. Asset labels, other progression producers, once-per-race cadence and volume/fade claims remain separate.

## 20. Command-line table and driver override

The [command-line comparison](original-modern-command-line.md) traces 33 retained slots reduced to two nonempty names, universal driver-prefix handling, INI bypass linkage and empty-row help suppression. It also records ASCII-copy and machine-shift contracts, and traces duplicate driver arguments: name and numeric suffix can come from different options, while an empty driver option can still bypass INI selection. Full legacy option semantics, argument edge cases and runtime acceptance remain pending.

## 21. Ghost loading and preserved current settings

The [ghost comparison](original-modern-ghost-loading.md) traces the changed snapshot/save order, refreshed header restoration and three additional identity-field copies. The reader/model-resolver bodies are byte-identical. These support settings/name preservation mechanisms; full file/version validation and trajectory compatibility remain separate.

## 22. Config-file acceptance and reset routing

The [config-load comparison](original-modern-config-loading.md) traces removal of the old file-time gate, retained exact file-size check, Modern size/version-byte reset decisions and header template. The version-only reset is not necessarily a full reset. Complete serialization, failure paths and cross-release file compatibility remain pending.

## 23. Automatic FOV and projection angles

The [projection comparison](original-modern-projection.md) traces dimension-derived automatic FOV clamped to 90–107 degrees, fixed alternatives, moved-wrapper correspondence and the integer-to-float angle interface. The complete projection builder remains identical. All camera/horizon consumers and rendered output remain pending.

## 24. Language-table compatibility and fallback

The [language comparison](original-modern-language-table.md) traces the v1.6.0 marker test, compatibility flag, table-coverage tests, 27 embedded fallback entries and changed dynamic display-label range. This is selected-string fallback rather than complete format validation; external localized assets and historical regression claims remain pending.

## 25. Replay mirror/variant admission

The [replay presentation comparison](original-modern-replay-mirror.md) traces coordinated toggle, eligibility and refresh gates around state 2 and an enable global. The default F7 binding-to-action-11 chain is now traced through the unchanged mask builder and edge reader. Full mirror consumers, reset paths and rendered behavior remain pending; replay trajectory compatibility is separate.

## 26. Retained and replaced registry paths

The [registry comparison](original-modern-registry.md) inventories 15 original versus 6 Modern direct open/query call sites, traces renderer preferences into the original selector, and verifies unchanged online-DLL and memory-query bodies. Modern retains registry use; a one-for-one migration of every INI option is not established.

## 27. Prioritized semantic work remaining

The full JSON inventory gives every current Modern local function name, entry/ranges, original/Modern hashes, changed-byte count, thunk marker and original-entry candidate flag. The following ten high-change clusters now have initial instruction-level comparisons linked above. Remaining column entries identify what is still needed for complete semantic/behavioral coverage; they are not ten untouched investigations:

| Current Modern entry / label | Differing same-VA body bytes | Required next evidence |
|---|---:|---|
| `0047f650` BuildNineTexturedRectangleBorderQuads | 800 / 828 | Matched builder/inset and six callers traced; full quad/UV rewrite and visual output remain |
| `004be5e0` InitializeViewportGeometryForProfile | 608 / 634 | Reference/aspect/profile-rectangle deltas traced; all projection consumers and visual comparison remain |
| `004cd6c0` InitializeGameWindow | 514 / 918 | Initializer/callback lifecycle traced; creation style/size instructions and helpers compared; context producers and remaining hook semantics remain |
| `004b5844` LoadThrashDriverSettings | 486 / 504 | Modern INI/driver path traced in renderer report; original environment/name wrapper and selector branch targets traced; direct original selector/override/setup chain traced; higher-level callers, alternate writes and external driver behavior remain |
| `00494cb0` RenderTiledLoadingArtworkAndInitializeProgressBounds | 480 / 748 | Tile/reference/rounding deltas traced; full progress/UI contract and output remain |
| `004e3078` ScreenshotEncodingThread | 451 / 464 | Original synchronous counterpart mapped in screenshot report; GDI+ success, resources and runtime lifetime remain |
| `004b5a58` InitializeThrashRenderer | 407 / 421 | Loader/export checks traced in renderer report; numeric/type dispatch, callback-to-direct mode initialization and compatibility calls traced; selector producers and DLL semantics remain |
| `004b5580` LoadGameIniSettings | 374 / 393 | Modern defaults/API effects traced; original renderer registry preferences now mapped; generic key producers and other option counterparts remain unresolved |
| `0044a2d0` DispatchFrontendMenuKeyToSelectedEntry | 332 / 358 | Dispatcher/named keys/chat guard traced; all assets, entry callbacks and sound paths remain |
| `00485880` InitializeDefaultHudLayoutProfileSettings | 332 / 375 | File versus embedded preset source and header stores traced; asset/consumer/reset mapping remains |

Continue by matching original functions/control-flow neighborhoods, documenting changed instructions/data and linking the corresponding release-note ID. When a same-VA comparison is not a valid counterpart, explicitly map moved/reused/deleted code instead of interpreting a large byte count as a rewrite of the same routine.

The 290 catalog entries span multiple releases and include driver/assets/configuration changes outside `nfs3.exe`. They cannot all be explained by this executable pair alone. Items still marked vendor-claimed have not been verified simply because their names resemble a current annotated function. Runtime acceptance is separate from static code correspondence.

## Reproduction and completion boundary

`analysis/scripts/ghidra/ExportFunctionInventory.java` exports metadata only. `analysis/scripts/compare_nfs3_executables.py` compares PE sections, imports/resources and selected body bytes without changing an executable or producing C. The JSON records input identities and inventory provenance. Raw downloads, original analysis database, disassemblies and metadata dumps remain under ignored `analysis/captures/modern-differences/`.

Completed static chapters are linked above: exact three-way baseline and whole-code inventory; precision, loader/configuration, windows/screenshots, network ports/input, startup/heap, display/texture, viewport/border, HUD presets/loading artwork, startup paths and clock/loading timing; renderer selection/initialization/lifecycle; display defaults and mode selection; CPU tier, frontend sound and music selection/start; command-line, ghost/config loading, projection, language fallback and replay mirror admission; plus import/resource deltas and the existing RaceNet byte witness. Each chapter states its own bounded coverage and unresolved behavior. **Still pending:** full semantic mapping of changed regions, catalog-to-code coverage and decisive cross-version runtime compatibility tests. This is progress toward the active audit, not a claim that every Modern Patch change is understood.

### Integrated static-evidence check — 2026-10-31

All 23 `analysis/scripts/audit_*_difference.py` scripts were rerun with Python 3, pefile and GNU objdump; each exited 0. SHA-256 comparisons of all 33 existing `analysis/evidence/audits/*.json` files before and after the run found no changed or newly created JSON files. This checks reproducibility against the retained inputs and current tools, not independent correctness of every interpretation. The scripts hash-check their executable baselines and do not execute target instructions.

The saved main Ghidra database remained SHA-256 `7d15851180f215eb14609d4a87148b1cb9a33ae105372f172228f2f5f9c2817f`. No Ghidra edits, executable edits, reconstruction edits or runtime probes were made for this checkpoint.

Next priority is the original setting-by-setting registry correspondence for `004b5580` and its Modern INI counterpart, reusing the existing settings audit. External driver behavior and runtime comparisons remain separate follow-ups. This bounded next step does not require resolving the unrelated dispatcher investigation.

The subsequent [registry audit](original-modern-registry.md) completes the bounded renderer preference mapping and narrows the remaining work to generic key producers, selector overrides/callers and driver-specific preference handling.
