# Original versus Modern Patch: executable differences

For current acceptance, limits and prioritized next work, see the [audit stopping-point report](original-modern-audit-status.md).

For a shallow inventory, see the [complete release-note change list](#complete-release-note-change-list) below. For address-based navigation, use the [361-entry changed-function index](original-modern-function-index.md); chapter mentions are not completion evidence.

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

The [outside-function address map](original-modern-outside-function-index.md) now ranks all337 uncovered intervals containing changed bytes and retains their full changed-run/hash inventory. Its NOP/zero/other classes are byte observations, not semantic completion.

The [initialized-data address index](original-modern-initialized-data-index.md) separately records all11,576 differing `DGROUP`/`.data` bytes in605 contiguous runs, with original/Modern bytes and relocation-operand annotations. It covers file-backed data only; types, object correspondence and initialization lifetimes still require explicit tracing.

The [bounded ASCII string index](original-modern-string-index.md) lists112 Modern-only and186 original-only initialized-data text values with addresses;4027 values are shared. It excludes short/non-ASCII/control-containing text and other sections. Text candidates do not independently prove a feature or loaded dependency.

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

## 27. Race-vehicle render scheduling

The [vehicle-dispatch comparison](original-modern-vehicle-dispatch.md) traces retained participant loops, new admission around an identical selection helper, changed tick/parity bookkeeping and EAX preservation. The downstream randomizer changes from a global snapshot gate to an object tick gate; three render bodies and their dispatch tables remain byte-identical. Its RNG generator, seed routine, fraction wrapper and file-backed initial state also match, but changed gate admission can advance the shared state differently. The admission globals now have exact CPU/renderer-tier default tables and selected initialization/restore producers; complete UI/context meanings remain unresolved. Downstream visual effects and historical release attribution remain pending.

## 28. Localized numeric-scale layout

The [numeric-scale comparison](original-modern-numeric-scale.md) maps original `00489b30` to Modern `00489ab0` using three redirected callers, then traces measured-label spacing, fallback scale and text-helper changes. Invalid inputs, asset lengths and visible output remain unresolved.

## 29. Frontend Race Now entry policy

The [Race Now comparison](original-modern-race-now.md) maps Modern’s complete helper and the related original credits gate. Full original counterparts and entry-flag/global meanings remain unresolved; the same address is not a valid function pairing.

## 30. Parameter preset application

The [preset comparison](original-modern-parameter-preset.md) traces the original scaled-constant path versus Modern’s WORD table, two-record writes and changed conversion-count boundary. Semantic fields, full input invariants and runtime effects remain unresolved.

## 31. Viewport camera selection

The [viewport-pose comparison](original-modern-viewport-pose.md) traces Modern’s new fixed-descriptor branch, retained temporary primary-camera restoration and identical pose finalizer. Extraction/blend/finalizer bodies are identical; snapshot and partial-update producers are mapped. Source initialization, call order and runtime output remain pending.

## 32. Resource-backed frontend page

The [frontend-page comparison](original-modern-frontend-page.md) verifies a one-byte dispatch extension plus an out-of-line resource arm, and page record 75 changing from localized text to `ABOUT.QFS`/`cred`. Payload/render validation remains pending.

## 33. Pending localized overlay

The [overlay comparison](original-modern-pending-overlay.md) traces changed formatting and coordinated producer/consumer coordinate storage. The loading-abort caller and installed ID235 labels are now traced. All flag writers, full producer correspondence and actual rendering remain pending.

## 34. Prioritized semantic work remaining

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

### Current static-audit checkpoint — 2026-10-31

After the registry, vehicle-dispatch, numeric-scale and Race Now follow-ups, all **27** `audit_*_difference.py` scripts exit zero. All **37** existing audit JSON files reproduce without byte changes. This supersedes the earlier 23-script/33-file coverage count, not its historical result. The saved Ghidra database still matches SHA-256 `7d15851180f215eb14609d4a87148b1cb9a33ae105372f172228f2f5f9c2817f`. No target instructions, new runtime probes or game sessions were executed.

| Recent cluster | Evidence now established | Next unresolved evidence |
|---|---|---|
| Registry/renderer selection | Original preferences, fixed flag priority, setup-to-initializer chain, retained registry helpers | Generic key producers, external driver preference mapping, higher callers |
| Vehicle dispatch | Paired loops, changed tick gate/order, retained render/RNG bodies, selected default producers | UI/context meanings, cross-subsystem RNG order and effects, visual behavior |
| Numeric HUD scale | Moved counterpart, three caller setup regions, labels, revalidated 47-profile installed-data bound | Full caller state admission, actual profile/language selection, visual comparison |
| Race Now policy | Modern helper, original setup body, eleven direct caller witnesses, flag consumers, five state writers | Complete original/alternate policy mapping, lifecycle meanings and caller validity, language ABI/text |

This is reproducible static coverage, not a count of fully explained vendor changes or a whole-game completion percentage. Remaining changed-function regions, external components/assets and historical release claims still require the broader comparison described above. At that checkpoint the next targets were `0041d620` and `004228e0`; subsequent [preset](original-modern-parameter-preset.md) and [viewport-pose](original-modern-viewport-pose.md) reports now cover their bounded static comparisons. Their remaining limitations and the follow-ups in this historical table still apply.

## Setup website button follow-up

[MP100-052: website versus Credits](original-modern-setup-website.md) records removal of the website entry in the official menu asset, alongside byte-identical original/Modern callback and conditional binding. The final official asset instead routes that slot to Options, consistent with later entry MP140-017; the historical v1.0.0 Credits implementation remains unresolved. The follow-up also verifies retained button-handler, action-5 dispatch and descriptor-lookup bytes, connecting the asset route to generic engine behaviour within a stated conditional scope.

## Standard menu controls and official asset inventory

[MP140-018 and the menu inventory](original-modern-common-menu-buttons.md) records Options/Exit additions in three official menu files versus local uppercase backups. A reproducible 52-file inventory retains routing fields and hashes, checking each official file directly against its archive member. Runtime visibility and related postgame/Race Now lifecycle claims remain separate.

## Complete menu loader comparison

[The menu graph loader](original-modern-menu-loader.md) differs only in three immediate-operand bytes: original literal directory becomes a Modern initialized path buffer. The full local body comparison narrows the code delta while preserving asset, helper, initialization and filesystem limitations.

## Menu text conversion and callback helpers

[The field-writer comparison](original-modern-menu-text-fields.md) identifies Modern numeric `str_<ID>` lookup and removal of the original literal-text fallback. Ten official assignments connect this delta to six menu assets. The audit also checks five complete retained helpers; registration-table and runtime equivalence remain separate questions.

## Static menu callback registration map

[The complete 57-row callback comparison](original-modern-menu-callback-table.md) identifies every changed field: nine rows, 12 pointers, including eight null registrations and four redirects. Static-table and runtime-descriptor offsets are mapped explicitly. All eight nulled original targets are verified seven-byte return-zero stubs. First counterpart reports now account for all four redirects, including duplicate original Hard Keys/Function Keys bodies replaced by shared Modern initialization. Caller-level null-versus-zero behaviour, transitive dependencies and runtime ordering remain separate.

## Graphics menu transition counterpart

[Original versus Modern graphics transition](original-modern-graphics-menu-transition.md) maps the redirected callback: snapshot/Cancel restore, Modern reselection, extra global outputs and final-row/depth request encoding. The report links existing display-mode evidence and keeps runtime display/persistence validation separate. Its fog-gate follow-up maps both shadow-copy directions, three checked call sites and differing snapshot order; Modern fog-support state is distinguished from the original selector at the reused address.

## Credits panorama callback counterparts

[The panorama comparison](original-modern-credits-panorama.md) maps the two redirected registrations, moved-identical state restore, new Next/Previous controls, direct subtitle lookup and a distant missing-button exit. Official assets partially support MP140-022/024; keyboard dispatch, rendering and historical introduction remain separate.

## Ordinary Credits navigation and initial selection

[The Credits page follow-up](original-modern-frontend-page.md#ordinary-credits-nextprevious-removed-conditional-text-page-skip) verifies removal of the original conditional text-page skip and page0-to-last-page initialization change. The official More button is repositioned while retaining `credits1` routing; visual effect and runtime selection remain untested.

## Car slideshow navigation and deferred refresh

[The slideshow comparison](original-modern-slideshow-navigation.md) maps changed callback returns, a retained Previous core and the Modern shared-counter/periodic-refresh protocol. It supplies the remaining slideshow binding in MP140-022. The original action9 follow-up traces conditional entry cleanup and descriptor reinitialization, contrasting that broader path with Modern periodic refresh; actual input, rendering and historical release attribution remain untested.

## Reproduced static-audit checkpoint after menu follow-ups

Against revision `f26a71d`, all **39** `analysis/scripts/audit_*_difference.py` scripts exited0. SHA-256 comparisons before/after found **no changes to the 49 existing audit JSON files**, and no new audit JSON appeared. The script set, hashes, individual results and scope are retained in the [checkpoint manifest](evidence/validation/original-modern-static-checkpoint.json). Some audit JSON originates from other producers; unchanged files outside these scripts' output sets are preservation evidence, not freshly reproduced analysis.

The main saved Ghidra database still hashes to `7d15851180f215eb14609d4a87148b1cb9a33ae105372f172228f2f5f9c2817f`. No target instructions, runtime sessions, compilation, executable edits or Ghidra writes were used. A file-target check across the 53 `original-modern-*.md` reports plus the detailed catalog found **367 relative file links, zero missing targets**. That check does not verify anchor fragments, external URLs or rendered Markdown.

At that historical checkpoint, the 290-entry catalog distinguished **37 bounded-static**, **35 partial**, **5 unresolved/historical** and **213 vendor-only** entries. Current labels are generated with the complete release-note list below. The 77 entries beyond vendor-only include unresolved findings and bundled claims, so neither77/290 nor any static count is a whole-game completion percentage. Uncatalogued code differences, same-address pairing uncertainty, external DLLs/assets, intermediate-release provenance and original/Modern runtime compatibility remain part of the active investigation.

This supersedes the earlier numerical checkpoint counts while preserving their historical results. Next priorities are the remaining ordinary menu policy claims (including postgame controls), then further high-change regions selected from the retained function-difference inventory. Reuse the completed menu callback/loader evidence rather than repeatedly treating those bounded comparisons as untouched work.

## Options controls in postgame context

[The postgame Options comparison](original-modern-options-postgame.md) connects removal of three asset `mainonly` fields to unchanged template defaults, parser destinations, context producer and suppression consumer. This partially supports MP140-019. The first-screen follow-up also verifies the five-byte setup-state store inserted by Modern and connects it to conditional Options Race suppression (MP140-020). Actual nested-menu admission, later flag writes and runtime visibility remain unresolved.

## Obsolete Download car control

[MP100-053](original-modern-car-download.md) is narrowed to removal of the authored control from the official car-menu asset. The complete car initializer and conditional binding to the retained website/download handler remain byte-identical; service removal, repair or runtime reachability is not inferred.

## Scene-view offset interface and policy

[The view-offset comparison](original-modern-view-offset.md) identifies a new Modern EDX mode, changed fallback offsets and a gated fixed-view update. Its complete function delta is confined to branch policy, while the later x87 transform and two helpers retain identical bytes; numeric/runtime equivalence remains unproven.

## Viewport overlay gate, rectangles and added quads

[The viewport overlay comparison](original-modern-view-overlay.md) maps the narrower bit gate, moved rectangle operands and added fixed-colour shapes. The rectangle producer is now traced to a distinct extent-correction helper and two update calls. Its source initialization distinguishes a width-based covering frame from physical and fitted rectangles, with explicit zero-flag examples. The comparison also retains the complete 143-byte delta envelope: the Modern-range count of138 excludes five bytes belonging to an original CALL operand, so it is not a complete original-instruction diff.

## Viewport resize input and admission

[The paired resize comparison](original-modern-frame-resize.md) traces held-action +1/−1 callers, the narrower Modern bit gate and its added refresh-on-skip path. The complete adjustment helper is retained unchanged. The [Frame Size list/selector follow-up](original-modern-frame-setting.md) now closes the setting association and two-to-four-choice expansion, making MP160-004 partial; its advertised camera-shift effect and introduction date remain unverified.

## Pause-title coordinate adjustment

[The pause-title asset comparison](original-modern-pause-title.md) verifies a five-unit authored upward move with shared X/alignment, while recording omitted legacy fields separately. This partially supports MP100-050; screen pixels, improved alignment and historical introduction remain unverified.

Movie sound parameter initialization is compared in [movie playback level](original-modern-movie-volume.md): the original default127 is replaced with the menu music level masked to seven bits, with forwarding and runtime limits recorded.

The [idle movie controller comparison](original-modern-idle-movie.md) traces NoMovies through the availability mask, application activation through timer reset, and the changed movie-selection order and table type.

The [movie screenshot comparison](original-modern-movie-screenshots.md) separates unchanged movie-stop logic from the changed screenshot consumer and handled Print Screen hook path.

The [official DX7 mode-admission follow-up](original-modern-dx7-mode-admission.md) locates minimum640×480 checks in a packaged driver, with original-driver and exact-size depth-policy limits stated.

The [current comparison-document link audit](evidence/validation/comparison-document-links.json) records file hashes and checks relative file targets and plain ATX heading anchors. Its parser limitations are explicit; external URLs and rendered Markdown are not validated. Reproduce with `python3 analysis/scripts/audit_comparison_document_links.py`.

The [colour-control dispatch comparison](original-modern-colour-control.md) retains complete counterpart bodies and separates removed release-action sound requests from the still-unverified padding claim.

The [cursor-position comparison](original-modern-cursor-position.md) identifies new Boolean return contracts, narrower field reads and adopted sound wrappers in space freed by the HSV handler. Replay-specific attribution remains open.

The [replay-list cursor follow-up](original-modern-replay-list-cursor.md) ties the official replay control to its selection-list callback and documents the60-unit Y correction and shared-tail retargeting.

The [title-delay comparison](original-modern-title-delay.md) maps IntroSplashTime’s0..10-second consumer, zero-skip behavior and changed clock policy, separately from movie admission.

The [startup requirements comparison](original-modern-startup-requirements.md) maps changed memory arithmetic, diagnostics and the added desktop-depth gate, including overflow and fractional-MiB limits.

The [night-lighting comparison](original-modern-night-lighting.md) isolates an expanded context admission gate, unchanged lighting tail and retained scratch-allocation limitation; mirror attribution remains unresolved.

See also [track-chain detail selection](original-modern-track-detail.md): mirror quality policy, classifier interface changes and removed next-block classification.

See also [indexed-texture loading progress](original-modern-texture-progress.md): changed stage progress budget and retained cancellation limits.

See also [input-worker lifecycle](original-modern-input-worker.md): relocated callback, sentinel-controlled exit and changed shutdown synchronization.

See also [window-key translation](original-modern-window-key.md): table-driven mappings, Num Lock gate and keypad-separator handling.

See also [car-list rendering aliases](original-modern-car-alias.md): expanded name matching at two list-renderer call sites.

Recent catalog reconciliation links the mirror admission/track-selector and Num Lock findings to their release-note claims as **Partial**. The car-class display claim and version-specific v1.5.2 rear-view improvement retain vendor-claimed status: related final-pair mechanisms do not prove rendered class text or intermediate-release changes. Input-worker lifecycle, discarded next-block classification, progress budgets and screenshot file policies remain separately documented code findings; they are not forced into unrelated release-note bullets.

The [logo loader and animation investigation](original-modern-frontend-page.md#original-loader-counterpart-one-named-image-becomes-metadata-driven-output) now pairs original `logo.qfs` loading with Modern `logos.qfs`, decodes official tables, and traces model filtering, metadata access, draw fields and index initialization. Its conditional last-record fall-through and reload-state boundaries remain static findings requiring further validation.

See also [renderer state14 setter policy](original-modern-state14.md): changed zero-input handling and conditional disabled-state cleanup.

See also [dialog input dispatch](original-modern-dialog-input.md): Shift/Tab normalization, direct handler table and result3 sound request.

See also [dropdown input shared sound tail](original-modern-dropdown-input.md): selection-route feedback and consolidated close/update ordering.

The [droplist count follow-up](original-modern-common-menu-buttons.md#droplist-effective-count-signed-word-minimum) corrects the overlapping stack-read interpretation: the handler compares the signed low WORD of the actual list count with the authored limit. Within0..32767 this is a minimum, shared by both executable baselines. This handler belongs to droplist; the nine cascade authored increases require separate callback/field tracing. Populated lists, active instance selection and rendered row counts remain unverified.

The [complete expanded-list layout comparison](original-modern-common-menu-buttons.md#complete-layout-helper-difference-coverage) accounts for every changed byte in the379-byte helper: a narrower mode3/name selector, width padding5→15, and count extent5→2. The resulting width contribution can increase or decrease, depending on the list name; no universal wider-menu claim follows.

The [additional track-policy caller comparison](original-modern-car-alias.md#other-consumers-start-from-different-original-policies) distinguishes two further transitions: one original caller already accepts both track-list names and gains a mode gate; another gains a name gate. A common Modern helper therefore replaces different original policies, rather than introducing the same alias change everywhere.

The [measurement-wrapper comparison](original-modern-car-alias.md#width-dependency-removes-an-intermediate-integer-conversion) identifies an additional x87 conversion-boundary change: original integerizes the `004d1000` result inside `004d1430`; Modern returns it directly. Its shared-global policy also changes from forcing1 to increment/decrement. This is a local menu-width dependency, not proof of a whole-game precision policy.

The [numeric-scale anchoring follow-up](original-modern-numeric-scale.md#right-anchor-helper-changes-its-x87-return-contract) verifies an x87 return-ownership change: original anchoring helper discards the draw advance; Modern returns it and the inspected HUD-scale caller explicitly pops it. This is an ABI/stack-effect difference in addition to layout arithmetic.

The [complete list-renderer comparison](original-modern-car-alias.md#complete-renderer-difference-coverage-at-004634d0) now accounts for all36 changed bytes in its2,316-byte body: the track-policy selector and two car-alias CALL retargetings. This closes local byte-difference coverage without claiming identical drawing dependencies or runtime output.

The [widget registration correction](original-modern-common-menu-buttons.md#type-registration-separates-cascade-and-droplist-consumers) identifies the inspected renderer/input/layout callbacks as droplist type1dh. The nine authored cap increases are cascades type11h, requiring separate callback tracing. Their apparent linkage through matching list names was insufficient and has been corrected.

The [cascade-specific follow-up](original-modern-common-menu-buttons.md#cascade-cap-reaches-its-own-effective-count-and-layout-fields) now traces type11h callbacks and the correct cap0x54→effective0x56→layout-extent chain. The nine authored increases have a registered local consumer; list population, active assets and visible row counts remain unverified. This evidence is separate from the droplist chain corrected above.

The [cascade input comparison](original-modern-common-menu-buttons.md#cascade-input-changes-beyond-the-cap-calculation) covers changed bytes across the handler envelope, including reordered opening sound, merged close paths and navigation sound/action-code changes. The higher dispatcher meaning and audible result remain unresolved.

The [menu dispatcher follow-up](original-modern-common-menu-buttons.md#dispatcher-consumes-result2-and-normalizes-it-to0) connects registered input slots directly to construction records and verifies result2 as “skip generic navigation, then return0”. It also identifies Modern’s PUSHAD/POPAD return-slot convention. Other changed branches and upstream admission remain open.

The [complete slideshow refresh comparison](original-modern-slideshow-navigation.md#complete-refresh-envelope-and-persistent-resource-slots) identifies three creator calls routed through persistent WORD slots, alongside the deferred-update protocol. The wrapper and reset are traced; full resource lifetime, index admission and allocation savings remain unverified.

The [complete cascade-renderer comparison](original-modern-car-alias.md#complete-cascade-renderer-and-one-unit-text-argument-change) accounts for its1,556-byte body and identifies an additional one-unit text coordinate argument change on one path, alongside the track-policy selector. Physical-pixel placement and historical attribution remain unverified.

The [geometry-color admission comparison](original-modern-geometry-color-admission.md) identifies an additional context1 gate admitted at Rear View Detail High only, distinct from the High/Medium lighting gate. All envelope differences are confined to admission/prologue/early-return code; context producers and the rendered effect remain unresolved.

The [shape-conversion comparison](original-modern-shape-conversion.md) accounts for the cached renderer descriptor, removed null fallback and unchanged conversion suffix at `004d37a0`.

The [shell-open wrapper comparison](original-modern-shell-open.md) records the removed module-handle query and null owner argument; the [music-selection report](original-modern-music-selection.md#override-wrappers-follow-the-shifted-fixed-choice-index) records both retained override wrappers’ setting-index adjustment.

The [mouse-cursor callback comparison](original-modern-mouse-cursor.md) distinguishes conditional cursor hiding, removed display-count calls and the result-pointer stack-slot anomaly.

The [sound-bank language comparison](original-modern-sound-bank-language.md) accounts for five cached-selector reads and the removed language-indexed path switch across three loading functions.

The [grouped effect-renderer comparison](original-modern-effect-renderer-masks.md) verifies eleven one-byte `40h`→`50h` mask expansions, with complete unchanged surrounding function envelopes.

The [texture-loading follow-up](original-modern-texture-loading-followup.md) verifies cached/removed descriptor queries and four redistributed progress milestones in three complete function envelopes.

The [async-read wait comparison](original-modern-async-wait.md) verifies an added shared flag/event notification before the retained alertable polling loop.

The [car-profile comparison](original-modern-car-profile.md) records the changed base-path source, removed literal directory append and removed file-time rejection branch.

The [music-worker cleanup comparison](original-modern-music-worker-cleanup.md) verifies replacement of forced termination plus close with direct handle closure at one shutdown tail.

The [dead-zone slider comparison](original-modern-deadzone-sliders.md) verifies removed truncation calls, shifted enabled-row numbering, layout/register changes and the removed named-widget flag tail.

The [car-registry comparison](original-modern-car-registry-flags.md) verifies removal of Ferrari/Mercedes flag assignment and a changed copy-source getter; the Hot Pursuit claim has partial static support.

The [environment-grid comparison](original-modern-environment-grid.md) accounts for the revised context/detail admission, expanded renderer mask and changed vector argument.

The [small conversion-helper contracts](original-modern-small-conversion-helpers.md) document ASCII copy pointer/count outputs, the wide-character API wrapper and current-rounding-mode float conversion; original functional counterparts remain unresolved.

The [raster-session comparison](original-modern-raster-session.md) accounts for removed cleanup publication/callbacks and the shortened inactive shutdown branch, including its original remote tail.

The [small-entry follow-up](original-modern-small-entry-followup.md) accounts for a shortened no-op, vehicle-loading progress inputs (including changed referenced data), duplicate-choice helper boundaries, three Modern wrappers and the application-wrapper call retarget. Original counterparts and runtime effects remain explicit unknowns.

The [removed DDE code comparison](original-modern-removed-dde.md) identifies original browser URL-command construction under a large Modern NOP span, while distinguishing retained DDE imports, unrelated Modern address reuse and unresolved original reachability.

The [force-feedback menu comparison](original-modern-force-menu-layout.md) verifies the complete initializer: Modern delegates the local Credits policy and removes six conditional widget-layout blocks while retaining value/callback setup. Device and visible behavior remain untested.

<!-- BEGIN GENERATED MODERN CHANGE LIST -->
## Complete release-note change list

Current catalog labels: **183 Claimed, 37 Static, 67 Partial, 3 Unresolved**. These are evidence labels, not a completion percentage.

This first-reference index includes all **290 release-note entries across 12 releases**, grouped newest first. Descriptions below reproduce the full source bullets, including vendor claims; they are not all independently verified differences between the supplied original and final Modern executables. Historical fixes, reversals, DLLs, assets and configuration changes are included. This is a release-history inventory, not an exhaustive inventory of undocumented binary changes.

Use the stable IDs when choosing original or Modern behaviour for a reconstructed C module. An executable comparison can guide reconstruction of original behaviour; it does not supply the original source code. The [detailed catalog](modern-patch-change-catalog.md) retains source line numbers, categories, evidence links and qualifications. **Static** means bounded static support, **Partial** means only part of the claim is supported, **Unresolved** includes historical claims needing other releases, and **Claimed** means vendor-only. None of these labels establishes runtime equivalence.

Generated from the hash-pinned English README and the catalog by `python3 analysis/scripts/update_change_list_appendix.py`. Refresh after catalog status changes; do not edit this generated section manually.

### Version 1.6.1 (2016-10-28)

| ID | Reported change | Review |
|---|---|---|
| MP161-001 | Fixed the problem with Texel Alignment in the DX6, DX7 and DX8 renderers, so everything looks sharp, like when Glide3x is used. | Claimed |
| MP161-002 | DX8 supports fog effect. Thanks to Verok for investigation. | Claimed |
| MP161-003 | The DX7 graphical glitches like the black polygon near the Old Church were workarounded. | Claimed |
| MP161-004 | DX7 doesn't output 640×480×16 if this mode isn't supported. Also it returns sorted list of resolutions now. | Claimed |
| MP161-005 | A small optimization of texture loading. The thrash_about isn't called when it is not really needed. | Claimed |
| MP161-006 | More strict checking of validity of a thrash driver (a renderer). | Static |
| MP161-007 | New error messages for some problematic situations: too long path to the root directory (it has not to be longer than 210 characters); thrash driver not found. | Claimed |
| MP161-008 | DirectDrawLagFix was renamed to DisableMaxWindowedMode in the thrash.ini files. It is disabled by default now. | Partial |
| MP161-009 | A new DirectDraw compatibility flag NoDwmOffForPrimaryLock was added to the thrash.ini files. | Partial |
| MP161-010 | The game asks a renderer if it supports the fog effect. DX5 and SoftTri always report that they do not support the fog effect. | Partial |
| MP161-011 | Refactoring of the video mode init code. Video mode restore function will not be called twice at exit. | Partial |

### Version 1.6.0 (2016-09-22)

| ID | Reported change | Review |
|---|---|---|
| MP160-001 | Automatic View Angle (FOV H+ mode). | Static |
| MP160-002 | More accurate vertical view angle. | Claimed |
| MP160-003 | Camera doesn't shift down when frame is wide (to match the FOV H+ better), the horizon is always in the middle of the screen. | Unresolved |
| MP160-004 | Frame Size setting was extended to be able to return this camera shift. | Partial |
| MP160-005 | Proportions of the image in the mirror are the same regardless of the aspect ratio of the selected resolution. | Partial |
| MP160-006 | Size of the borders and map points are calculated based on the vertical resolution. | Partial |
| MP160-007 | More accurate positions for the following HUD elements: Rear View Mirror, Cop Detector, Analog Speedometer and Tachometer. | Partial |
| MP160-008 | Cabin image in “In Car” view now rendered 0-3 pixels wider (depending on the resolution) for get rid of chinks on the edges of screen. | Claimed |
| MP160-009 | Ferrari, Lister and Spectre logos were added to the flying logos animation in the menu. | Partial |
| MP160-010 | Ford, HSV, Lister and Spectre logos will not be used in the animation if these addon cars aren't installed. | Partial |
| MP160-011 | When gameplay loading is aborted using Esc key, "Aborted" string will be displayed for 200ms (it was just a frame before). | Claimed |
| MP160-012 | FPU always uses extended precision for all calculations. | Static |
| MP160-013 | The game checks if proper version of language files is used. | Static |
| MP160-014 | dgVoodoo v2.5.3 (Napalm). | Claimed |

### Version 1.5.3 (2016-05-03)

| ID | Reported change | Review |
|---|---|---|
| MP153-001 | Fixed a bug of the original game which was a cause of different volume of the race music each race. | Partial |
| MP153-002 | Fixed a bug of the original game which was a cause of ignoring of the latest Rock track and all Techno tracks when Random race music is choosed. | Partial |
| MP153-003 | Added two additional random race music modes: Random (Rock) and Random (Techno). | Partial |
| MP153-004 | Added two additional random menu music modes: Random (Fast) and Random (Slow). Fast: Romulus 3, Triton, Pi. Slow: Minotaur, Whipped, Whacked. | Static |
| MP153-005 | Random race music actually works as a playlist (each race a new track). It prevents from repeating same music tracks frequently. | Partial |
| MP153-006 | Prevented double music fading in the audio settings when user presses Race button. | Partial |
| MP153-007 | Fixed a regression of the v1.5.2 which was a cause of problems with windowed mode of the nGlide. | Claimed |
| MP153-008 | Fixed a regression of the v1.5.1 in the fallback code for the unupdated language files. | Unresolved |
| MP153-009 | Menu music volume will be used for the movies. | Partial |
| MP153-010 | Proper handling of the case when EAX was presented in the system and choosed by user, but for some reason had become unavailable. | Claimed |
| MP153-011 | Sound Volume and Dead Zone slider values are rounded correctly. | Partial |
| MP153-012 | More accurate time measure function is used (timeGetTime instead of GetTickCount). | Static |
| MP153-013 | HSV and Ford logos from the LOGO2.QFS aren't used in the menu animation if there is no cars from the Australian Edition. | Claimed |
| MP153-014 | Fixed a problem which was a cause of the inability to start the game on some systems. | Claimed |

### Version 1.5.2 (2016-04-10)

| ID | Reported change | Review |
|---|---|---|
| MP152-001 | Better Rear View Detail setting. Light from the car headlights and cop flashers will be rendered even on Medium value of this setting. View Distance and Car Detail in the Rear View Mirror now depends on Rear View Detail also. So, if you have performance problems with High level of the Rear View Detail setting, just use Medium. It have to be much more usable now. | Claimed |
| MP152-002 | Better compatibility with the Thrash API v107 according to fog. So, the DX7 renderer can render fog in the NFS3 now. | Claimed |
| MP152-003 | Fixed a bug which was a cause of config reset after loading of ghost files from the other versions of the NFS3. | Static |
| MP152-004 | Fixed a bug which was a cause of using player name from the loaded ghost file instead of the current player name. | Static |
| MP152-005 | Step size for the Alpha Intensity and sound volume sliders is 5%. | Partial |

### Version 1.5.1 (2016-03-25)

| ID | Reported change | Review |
|---|---|---|
| MP151-001 | “Rear View Camera” setting which allows to lock the rear view camera in the car. It greatly increases visibility and reduces the blind spot when the current main camera is not “In Car”. | Claimed |
| MP151-002 | Fixed a bug which had allowed to save duplicated cameras when the user presses "Race", "Credits", or "Exit game" buttons instead of the "Done" button. | Claimed |
| MP151-003 | Experimental ini setting AllowHugeTextures which enables huge texture (512×512, 1024×1024, and 2048×2048) support for track elements and cars during gameplay. Useful for the game modding. | Static |
| MP151-004 | Fixed a small bug in the DX5, DX6, and SoftTri renderers in the thrash_lockwindow function. | Claimed |
| MP151-005 | Fixed mistakes in new strings in German, Spanish and French languages. Thanks Gonzalo's and Kirill Diduk for hints. | Claimed |

### Version 1.5.0 (2016-03-20)

| ID | Reported change | Review |
|---|---|---|
| MP150-001 | No more non-rotating wheels in the rear view mirror and in the split screen mode (when Car Detail is High). | Claimed |
| MP150-002 | Rear View Mirror can display clouds, lightnings, and light from the headlights of cars and from the flashers of cops. | Partial |
| MP150-003 | Rear View Mirror can use better 3D models of the track, so the problem with the holes in the objects (displayed in the mirror) is solved now. | Partial |
| MP150-004 | “Rear View Mirror” detail setting. Low is equivalent to the original; Medium is for better track 3D model and view distance; High is for the best track 3D model, clouds, lightnings, and light from the car headlights and cop flashers rendering. | Partial |
| MP150-005 | Better proportions of the objects in the rear view mirror. | Claimed |
| MP150-006 | Fixed direction of the camera of the rear view mirror. The horizon is on the middle of the mirror now (for a better view). | Claimed |
| MP150-007 | Fixed a small horizon glitch at the edge of a screen when the wide view angle is enabled. | Claimed |
| MP150-008 | An ability to enable or disable the fog effect directly from the graphics settings menu. | Claimed |
| MP150-009 | An ability to set volume of menu sounds separately from the volume of the ingame special effects. | Static |
| MP150-010 | No more "Render_GetTm() raM out of raN" error for high poly cars. Corresponding buffer is increased from 0.8 MiB to 8 MiB. | Claimed |
| MP150-011 | 512×512, 1024×1024 and 2048×2048 textures support in the voodoo2a.dll. Support of such textures was introduced in the 3dfx Voodoo 4 and 5. | Claimed |
| MP150-012 | The limit of texture size for track elements was expanded from 128×128 to 256×256 pixels in this release. | Partial |
| MP150-013 | Support of the big 512×512 and 1024×1024 textures for cars and track elements still available only in beta versions of the patch. | Claimed |
| MP150-014 | Smooth edges of the cop/player points on the map. | Claimed |
| MP150-015 | Gear numbers are right-aligned now, like the digital speedometer. | Claimed |
| MP150-016 | Gear numbers use smaller font if there is not enough space for them. | Claimed |
| MP150-017 | Opponents List and Speeds List have standard bevel when SoftTri is used (as it was for other renderers). | Claimed |
| MP150-018 | An ability to enter digits from the Num Pad when Num Lock is on. | Partial |
| MP150-019 | Commas are treated as dots when parsing an IP address. | Claimed |
| MP150-020 | HUD preview in the settings now arranged well. | Claimed |
| MP150-021 | Volume and Alpha sliders display own value (in percents). | Partial |
| MP150-022 | Logos from the LOGO2.QFS (if it exists) are used for animation in the menu (together with logos from the LOGO.QFS). Original version of the game have this file, but it is unused. | Claimed |
| MP150-023 | Animated logos of automobile manufacturers are disappearing more smoothly. | Partial |
| MP150-024 | Fixed rendering piority errors for the top dropdown lists in the the “Location” and “Opponents” menus. | Claimed |
| MP150-025 | “Car Showcase” subtitle and “Compare All Cars” subtitle are displayed using the same font as the “Race Results” subtitle. | Claimed |
| MP150-026 | Other insignificant improvements. | Claimed |
| MP150-027 | DX7 renderer is included into this patch. Just for a collection :) | Claimed |
| MP150-028 | Based on the dx7z.dll from the Motor City Online. | Claimed |
| MP150-029 | Dithering is disabled by default. | Claimed |
| MP150-030 | Resolutions under 640×480 are hidden. | Partial |
| MP150-031 | Gameplay loading animation takes into account time of preliminary synchronization of a network game. | Claimed |
| MP150-032 | IntroSplashTime ini setting, which allows you to set duration of the intro splash image. | Partial |
| MP150-033 | Fixed a problem with discolored light from the taillights in the menu when DX6 renderer is used and fog support is enabled. | Claimed |
| MP150-034 | Fixed a bug which cause a crash when using the screenshoter feature on Windows XP. | Claimed |
| MP150-035 | The game doesn't change resolution to 640×480 when “exit to system” is used during the gameplay, so closing the game is faster in this case. | Claimed |
| MP150-036 | Updated version of nGlide with fixes according to the NFS3 is included. | Claimed |
| MP150-037 | dgVoodoo v2.5.1 (Napalm). | Claimed |
| MP150-038 | Fixed a bug in the SoftTri renderer. Now it outputs all available resolutions. | Claimed |
| MP150-039 | DX8 renderer outputs 16-bit resolutions also. However, it still can't play movies at all. | Claimed |
| MP150-040 | nfs3.exe sorts resolutions that it gets from the renderer. Refactoring of the graphics initialization and resolution choosing code. | Static |
| MP150-041 | If ini file with the same name as a executable file name (e.g. nfs3test.ini for nfs3test.exe) is not found, nfs3.ini will be used. | Static |
| MP150-042 | Hide16bitModes ini setting which hides 16 bit resolutions if similar 32 bit resolutions are available. | Static |
| MP150-043 | Use32bitModeInMenu ini setting which enables 32-bit video mode for the menu. However movies can't be played in 32-bit video modes. | Partial |
| MP150-044 | All renderers can use any DLL wrappers from the own subdirectories on the Windows XP SP1+. | Claimed |
| MP150-045 | DDRAW.DLL is removed from imports of the nfs3.exe and voodoo2a.dll. | Claimed |

### Version 1.4.0 (2016-02-16)

| ID | Reported change | Review |
|---|---|---|
| MP140-001 | TCP port 9803 is used by default, because original port 1030 often is occupied by Windows, so a network game can't start. | Static |
| MP140-002 | You can change the port in the “TCP connection” menu. You can choose between 1030 (legacy) и 9803 (modern). Every player have to use the same value! | Static |
| MP140-003 | You can specify a port after “:” symbol when joining IP game. If not specified, a value from the previous dialog will be used. | Static |
| MP140-004 | When you're trying to open TCP multiplayer game menu, “The port is already occupied” error message will be shown if needed port is occupied by other application. | Partial |
| MP140-005 | You can join to other's game even when the same port on your system is occupied. Original game doesn't allow to do this. | Partial |
| MP140-006 | For compatibility with the original NFS3 use 1030, but it is not recommended because this port often is occupied by Windows. | Partial |
| MP140-007 | Don't allows to send empty chat messages. | Static |
| MP140-008 | Tab and Shift+Tab can be used to switch between controls of the menu. | Static |
| MP140-009 | Tab, Shift+Tab, and Esc work even when multiplayer chat is in the focus, so you can switch focus to another control without using your mouse (original game doesn't allow it). | Static |
| MP140-010 | All menu sounds have same volume. | Partial |
| MP140-011 | Consistent sounds for the mini dialogs when using the keyboard. | Partial |
| MP140-012 | Consistent sounds for the top dropdown lists when using the keyboard (the same as for general dropdown lists). | Partial |
| MP140-013 | A car color dropdown list uses consistent (with other controls) sounds and has a normal padding. | Partial |
| MP140-014 | List of replays works correctly using keyboard (fixed an invalid positioning of the mouse cursor). Also it uses consistent sounds (like others). | Partial |
| MP140-015 | Fixed errors of element switching order (when keyboard is used). | Claimed |
| MP140-016 | 3D view of a car interior can be stopped using Space key. Arrow keys change rotating speed more smoothly now. | Claimed |
| MP140-017 | Options button is placed near Exit button on the first menu screen (Game Setup). | Partial |
| MP140-018 | “Connect Players”, “Connect IPX” and “View Car Interior” menu screens also have standard set of buttons (Exit and Options). | Partial |
| MP140-019 | This set of buttons don't disappear in the Options when they are opened directy from the race results screen. | Partial |
| MP140-020 | This set of buttons is smart: when user opens Options from the first screen without choosing game mode, the Race button are hidden. | Partial |
| MP140-021 | Drop down list of cars displays the class of the current car not only for the 1st player, but also for the 2nd player. | Claimed |
| MP140-022 | You can use Left and Right keys to switch slides in the car slideshow and in the credits (inclusive 3D panoramas of the developers). | Partial |
| MP140-023 | Noticeable “More...” button in the credits (opens the 3D panoramas of the developers). | Partial |
| MP140-024 | Credits page with the 3D panoramas of the developers has same controls, as general credits (with Back and Next buttons). | Partial |
| MP140-025 | Increased quantity of visible elements in some long drop down lists (resolution list, car lists). | Partial |
| MP140-026 | Fixed unaligned paddings of the all drop down lists. | Claimed |
| MP140-027 | “Reset To Defaults” button in the Controllers menu was shifted one position down. | Partial |
| MP140-028 | “Predefined Keys”, “View Car Interior”, “Load”, and “IPX connection” are aligned well. | Claimed |
| MP140-029 | NoMovie ini setting also disables demo movies on menu idle. | Partial |
| MP140-030 | Demo movies aren't starting when the game is minimized in the menu mode (useful for the nGlide driver). | Partial |
| MP140-031 | If demo video files are removed, the game doesn't try to play them. | Claimed |
| MP140-032 | Length of a track in the track info is displayed in units, which is choosed in the HUD of the 1st player. | Claimed |
| MP140-033 | “Wide Screen” setting was renamed to “2:1 Field of View”, just to avoid ambiguity. | Claimed |
| MP140-034 | The top dropdown with the player type selection is always displayed in the HUD settings. | Claimed |
| MP140-035 | Fixed bug, when previous text was lost on first key press when entering player name or IP address. | Claimed |
| MP140-036 | A hint about an ability to abort using Esc button in the “Connecting...” window. | Claimed |
| MP140-037 | Refactoring of the Voodoo thrash driver. 32bpp support for 3dfx Voodoo 4 or 5 was added. | Claimed |
| MP140-038 | DX6 thrash driver outputs 16bpp resolutions and sorts them. | Claimed |
| MP140-039 | DX5 thrash driver outputs 16bpp resolutions, limit of resolutions count is expanded from 30 to 100. | Claimed |
| MP140-040 | Refactoring of the thrash driver initialization code. | Partial |
| MP140-041 | No more hardcoded environment variables for the 3dfx Voodoo. | Claimed |
| MP140-042 | Instead of this the game sets environment variables from the [ENV] section of the current thrash.ini file. | Static |
| MP140-043 | The nGlide uses general voodoo2a.dll now, its settings can be changed using the [ENV] section of the thrash.ini. | Claimed |
| MP140-044 | Added separate Glide3x thrash driver for using on the real 3dfx Voodoo hardware. | Claimed |
| MP140-045 | VideoDriver ini setting was renamed to ThrashDriver (original name). Filenames of all thrash drivers also were renamed using original format. | Claimed |
| MP140-046 | Included glide3x.dll from the gGlide v1.05. | Claimed |
| MP140-047 | Included glide3x.dll from the dgVoodoo v2.5.1 (Napalm, WIP16). | Claimed |
| MP140-048 | Uses Print Screen key instead of inconvenient combination Alt+P. | Static |
| MP140-049 | Does one screenshot per second when Print Screen is held for long time instead of hundreds of screnshots without delays. | Static |
| MP140-050 | Saves screenshots in the BMP format (instead of rare TGA). | Partial |
| MP140-051 | Better quality of 16bpp screenshots (original code converts RGB565 to RGB555 because of limitation of the TGA). | Static |
| MP140-052 | Smaller files for 32bpp screenshots because BMP allows to drop alpha channel, so the result is stored as 24bpp. | Static |
| MP140-053 | Ability to save screenshots in the PNG or JPG formats (use ScreenshoterFormat ini setting). | Static |
| MP140-054 | Saves screenshots to the screenshots subdirectory instead of the Desktop directory. | Static |
| MP140-055 | Remembers last screenshot number. If you would like to reset this counter, just empty screenshots directory. | Partial |
| MP140-056 | Makes shutter sound while screenshoting. | Static |
| MP140-057 | Saving a screenshot file was moved to a separate thread, so the game have to freeze for less time while the screenshot is taking. | Static |
| MP140-058 | Ability of making screenshots of the gameplay loading screen. | Claimed |
| MP140-059 | Screenshoting doesn't stop intro movie. | Partial |
| MP140-060 | Super quick gameplay loading on modern systems (thanks Zeus for a hint). | Claimed |
| MP140-061 | LoadingSplashTime ini setting for slowing down gameplay loading, set desired time in seconds or 0 to disable this feature (and get maximum possible speed). | Static |
| MP140-062 | If this “splash” is enabled, it can be skipped just by pressing any key (but Esc aborts loading). | Static |
| MP140-063 | The View Angle setting allows to enable wider view angle, which is useful for the widescreen resolutions. New set of options: Narrow, Normal (former Wide), Wide. | Claimed |
| MP140-064 | It is possible to show rear view mirror when viewing replays (using F7). | Partial |
| MP140-065 | Autimatic creation of empty directories for saving game data. | Static |
| MP140-066 | Working directory is set automatically to the directory of the exe file. | Static |
| MP140-067 | Useless RemoteOnly ini setting was removed. | Claimed |
| MP140-068 | The KeyboardHook ini setting was replaced by the PreventMinimize. Now it works on Windows NT also. | Claimed |
| MP140-069 | Better code for the system cursor hiding, as result the cursor isn't hidden in the standard system menu of the window. | Claimed |
| MP140-070 | Language files with text strings are included, so the patch is compatible with rare prerelease version of the game now. | Claimed |
| MP140-071 | Opponent Name HUD element was moved to the top of screen, just under the rear view mirror. | Claimed |
| MP140-072 | Reset HUD just after installation of this patch over the original version of NFS3. | Partial |
| MP140-073 | Zoom of cop's minimap will be the same as zoom of racer's minimap (by default, can be changed). | Partial |
| MP140-074 | i586 and newer are recommended. The game displays a warning for older systems. | Claimed |
| MP140-075 | nfs3.exe has an application manifest now. | Claimed |

### Version 1.3.1 (2015-07-14)

| ID | Reported change | Review |
|---|---|---|
| MP131-001 | DirectDrawLagFix is readed from a thrash.ini of according driver, not from the nfs3.ini. So, this setting isn't applied for drivers that doesn't require it. This option is useful only for drivers that use DirectX 5/6/7 on Windows 8+. | Claimed |
| MP131-002 | A small optimization in the voodoo2.dll and nglide.dll: grGlideInit and grGlideShutdown functions aren't called when display mode is changing. | Claimed |
| MP131-003 | Windows 98/Me support was returned. | Claimed |
| MP131-004 | If you choose the biggest available resolution, when resolutions list is changed (e.g. when you are using external display with notebook), the biggest resolution will be choosed automatically from the new list. | Claimed |
| MP131-005 | KEY_READ access right is used instead of KEY_ALL_ACCESS for reading path to desktop from the registry for saving a screenshot (Alt+P). | Claimed |

### Version 1.3.0 (2015-06-22)

| ID | Reported change | Review |
|---|---|---|
| MP130-001 | Hangs on multicore systems were completely fixed, so you don't have to use SingleProcAffinity kludge now. The game works much smoother without this kludge (expecially with nGlide and dgVoodoo drivers). | Partial |
| MP130-002 | Unexpected game termination at the end of gameplay loading was fixed. (Thanks Zeus for help with debugging.) | Claimed |
| MP130-003 | Multiplayer game bug were fixed. It had been introduced by the first version of this patch. (Thanks Ivan_83 for testing.) | Claimed |
| MP130-004 | HUD was updated a little. | Claimed |
| MP130-005 | The Wide Screen setting has no any relation to proper widescreen support, so its location next to the Resolution setting is confusing. This is why this setting was moved from the Graphics to the Advanced Graphics settings. Now it's placed near the View Angle setting because it is more logical. The View Distance setting was moved to freed space in the Graphics settings. | Claimed |
| MP130-006 | Menu subitems in the Controller and in the Connect menus aligned vertically like in the other menus. | Claimed |
| MP130-007 | nGlide is updated to version 1.04.3. Now you can safely minimize and restore NFS3. (Thanks Zeus for it.) | Claimed |

### Version 1.2.0 (2015-06-10)

| ID | Reported change | Review |
|---|---|---|
| MP120-001 | If ini file hasn't some setting, program tries to read environment variable with name like SECTION_SETTINGNAME, e.g. for setting NoMovie in the [NFS3] section environment variable name will be NFS3_NOMOVIE. If environment also isn't present default value will be used. | Static |
| MP120-002 | Fixed a bug according to race type autoselection in the race selection dialog (Hot Pursuit and Tournament were mixed up). | Claimed |
| MP120-003 | Mercedes and Ferrari cars aren't locked in the Hot Pursuit mode. It seems that it had been done because of licensing restrictions. Thanks to Manticore for a hint. | Partial |
| MP120-004 | Structure of thrash video drivers was changed. All drivers stored in “drivers” directory. Every driver has own subdirectory with name which is used in VideoDriver ini setting. Inside this subdirectory have to be dll file of the driver and file thrash.ini with information about this driver (File and Type are required fields, type may be null, d3d, voodoo, or software). This change allows to save several different Glide API emulators to neighbour directories and use them when needed. | Claimed |
| MP120-005 | Some thrash driver capabilities could be set in thrash.ini: FogSupport and LightBeams. For example, it allows to override hardcoded values and allow to use fog for d3d thrash driver (if this driver supports it). It allows to use fog in the dx6 thrash driver from NFS4/3DSETUP. | Claimed |
| MP120-006 | Thrash driver is loaded only once. | Claimed |
| MP120-007 | When game can't init thrash driver error message box is displayed. In the original version there was no error reporting. | Claimed |
| MP120-008 | Resolutions count limit was extended up to 100. | Claimed |
| MP120-009 | Fixed a bug of the first release of this patch: returning to the main setup menu instead of a menu of a current game mode. | Claimed |
| MP120-010 | Added an ini setting DirectDrawLagFix which fixes performance problems of DirectX 5/6/7 in Windows 8+ via enabling “DXPrimaryEmulation -DisableMaxWindowedMode” compatibility mode (enabled by default). | Claimed |
| MP120-011 | Added an ini setting KeyboardHook which allows to disable keyboard hook that has been used by the game for blocking Win key and keystrokes like Ctrl+Esc, but this code doesn't work in Windows 7+ so it is better to disable it (disabled by default). | Claimed |
| MP120-012 | Slightly better multilanguage support. When language directory is absent in the ./GameData/Audio/Speech/ directory the game doesn't crash and uses sound files from the English subdirectory. Also Swedish language can use own speech sounds (original game uses English sounds for it) now. The name of the language directory have to be Swedish, and the one-letter code in file names is W. | Claimed |
| MP120-013 | config.dat was moved to its original destination (./FeData/Config/) for preserving settings of original NFS3 when updating. However, graphics settings are reset to their defaults in this case (because format is changed a little). | Claimed |
| MP120-014 | Based on the 3dsetup/d3da.dll from the NFS4, supports fog effect in the NFS3. | Claimed |
| MP120-015 | Fixed a bug according to non-working fog effect on modern systems. (Thanks Dege for debugging this driver and much valuable information about Direct 3D.) | Claimed |
| MP120-016 | Fixed a crash when system supports too many texture formats. (Also thanks Dege.) | Claimed |
| MP120-017 | Resolutions count limit was extended up to 100. | Claimed |
| MP120-018 | The driver hides resolutions with height lower than 480 pixels now. | Claimed |
| MP120-019 | 640×480 always reported as 16-bit because intro movie doesn't works in 32-bit mode. Other resolutions are reported as 32-bit if they are available. | Claimed |
| MP120-020 | Firstly file glide3x.dll is searched in the same directory from where voodoo2.dll is loaded, then it is searched in current directory, and then in system directory. This change allows to save several different Glide API emulators to neighbour directories and use them when needed. | Claimed |
| MP120-021 | Thrash driver voodoo2.dll distributed with two different Glide API emulators: nGlide and dgVoodoo. You have to choose nglide or dgvoodoo instead of voodoo2 in the VideoDriver ini setting. | Claimed |
| MP120-022 | If you would like to play NFS3 on the real 3dfx Voodoo or 3dfx Voodoo 2 hardware, create new subdirectory with name voodoo2 in the drivers directory, copy into this subdirectory thrash.ini and voodoo2.dll from the dgvoodoo subdirectory, set VideoDriver ini setting to voodoo2. | Claimed |
| MP120-023 | glide3x.dll is loaded only once. | Claimed |
| MP120-024 | Resolutions count limit was extended up to 100. | Claimed |
| MP120-025 | It's a slightly changed version of voodoo2.dll with special code for the nGlide wrapper. It's created to prevent unwanted using global settings of nGlide. | Claimed |
| MP120-026 | This is done by setting NGLIDE_* environment variables before glide3x.dll loading. Every setting is gotten from the [NGLIDE] section of according thrash.ini file. Each setting of this section is formatted like NGLIDE_SETTINGNAME and used as name of an environment variable. Names of settings and their formats can be found at the official nGlide forum: http://www.zeus-software.com/forum/viewtopic.php?f=9&t=796 | Claimed |
| MP120-027 | If you would like to use global nGlide settings, just remove [NGLIDE] section in the ./drivers/nglide/thrash.ini file. | Claimed |
| MP120-028 | Bundled with nGlide v1.04.2 (this version also fixes possible problems with projected headlights). | Claimed |

### Version 1.1.0 (2015-05-22)

| ID | Reported change | Review |
|---|---|---|
| MP110-001 | VideoDriver ini setting now accepts a name of a driver file, not one of the predefined values. Thus, you can put several thrash video drivers of the same type in the game's directory and switch between them with a simple changing of the ini setting, without renaming files. It is important to understand that the game uses drivers in different ways depending on the type. The type of driver is determined by the first letter of the name of the driver file (d — d3d; v — voodoo; s — software; the rest — none). | Claimed |
| MP110-002 | VideoDeviceId ini setting became a part of VideoDriver. If it is necessary to specify device number, just put “@” and device number just after the driver name (e.g. dx8@0). | Claimed |
| MP110-003 | -voodoo2, -d3d and -softtri command line arguments are replaced by one universal -driver=. This argument has the same format as VideoDriver ini setting. | Static |
| MP110-004 | Improved validation of thrash video drivers. | Claimed |
| MP110-005 | Original dx5.dll not always works on modern operating systems (e.g. Windows 8.1). That's why dx8.dll was created. | Claimed |
| MP110-006 | Based on the dx8z.dll from the Motor City Online (uses DirectX 8). | Claimed |
| MP110-007 | The driver hides resolutions lower than 640×480 pixels. | Claimed |
| MP110-008 | The driver reports resolutions in a slightly different order. | Claimed |
| MP110-009 | The problem with ugly 16-bit menu was fixed by using 32-bit mode. | Claimed |
| MP110-010 | The problem with non-working video still not solved. It's recommended to disable the intro video by the NoMovie ini setting. | Claimed |
| MP110-011 | Renamed from voodoo2a.dll to voodoo2.dll. | Claimed |
| MP110-012 | Always reports that all resolutios are 16-bit even when nGlide is used. Otherwise making screenshots by pressing Alt+P will not work because in low-level all Glide resolutions are still 16-bit modes from the game's side. | Claimed |
| MP110-013 | Renamed from d3da.dll to dx5.dll similar to dx8.dll, because it uses DirectX 5. | Claimed |
| MP110-014 | Renamed from softtria.dll to softtri.dll. | Claimed |

### Version 1.0.0 (2015-05-17)

| ID | Reported change | Review |
|---|---|---|
| MP100-001 | All resolutions with aspect ratio from 5:4 to 16:9 (inclusive 4:3 and 16:10) are supported. | Partial |
| MP100-002 | All objects will be properly scaled for every aspect ratio and you will see them in correct proportions. | Partial |
| MP100-003 | There is no unreasonable limits for maximum resolution anymore (e.g. for D3D it was 800×600), you can use almost every resolution which is supported by your system (e.g. 1920×1200). | Claimed |
| MP100-004 | Font size is choosed on the basis of screen height, not screen width. It prevents from choosing too big font for widescreen resolutions. | Claimed |
| MP100-005 | HUD will be completely recalculated with the purpose of different aspect ratio support when resolution is changed in settings. Besides the result looks more accurate than original one even on 4:3 resolutions. Files ./GameData/DashHud/*.POS are unnecessary now and can be removed. | Claimed |
| MP100-006 | HUD borders was reduced twice to look better on modern huge resolutions. Without this change they look too fat. | Claimed |
| MP100-007 | Compact cop's speeds table. Now it looks like the standard opponents list. | Claimed |
| MP100-008 | As a whole positions of all HUD elements were adjusted a little to look better on all supported resolutions. | Partial |
| MP100-009 | Resolutions list limit was extended from 20 to 50. | Claimed |
| MP100-010 | The games uses the best possible graphics settings by default when it detects that the game is runned on the modern computer. | Claimed |
| MP100-011 | On first run game tries to choose gameplay resolution nearest to current Windows default resolution. | Partial |
| MP100-012 | New “High” car detail level. New quality of graphics for cars other than 1st player. There is no non-rotating wheels and disappearing side-view mirrors! Also the game uses twice better textures for all cars. Even traffic cars looks twice better. Also it fixes unfairness when 2nd player's car has worse graphics. Old “High” car detail is “Medium” now, old “Medium” is “Low” now, old “Low” was removed. Warning! You have to restart the game when you've changed car detail level to see full effect because the game loads textures only once when loading gameplay. | Claimed |
| MP100-013 | Much better “Full” view distance level. Now it also affects rear view mirror (in “Far” and “Full” levels). | Claimed |
| MP100-014 | View distance in “Full” level renders farther in splitscreen and night driving modes, the same as in singleplayer day driving mode. | Claimed |
| MP100-015 | “Alpha Intensity” setting works for Voodoo2 mode now. Cars look too shining without it. | Claimed |
| MP100-016 | A little better rendering of an image when loading gameplay. An attempt to improve quality of scaling of this image. | Claimed |
| MP100-017 | An attempt to get rid of glitch lines near some sprites (e.g. in exit dialog near NFS logo). | Claimed |
| MP100-018 | Cabin image in “In Car” view now rendered for a pixel bigger in every dimensions for get rid of chinks on the edges of screen. | Claimed |
| MP100-019 | Because of fixed hardware detection bug quality of the starting movie will be much better (in comparison to original version) on modern computers. | Partial |
| MP100-020 | The game reads system settings from ini file now. No more registry! Name of the ini file have to be exactly like the name of game's exe file, but with *.ini extension. For example, for nfs3.exe it have to be nfs3.ini. | Partial |
| MP100-021 | The game automatically binds own process to one core for avoiding hang, so there is no more reasons to install any SDB compatibility files to run this game. This behaviour might be disabled, see SingleProcAffinity setting in ini file. | Unresolved |
| MP100-022 | The game doesn't require file install.win which was created by NFS3 installation utility. All settings which were in this file were moved to ini file (Language and RemoteOnly options). | Claimed |
| MP100-023 | You can choose thrash video driver from ini file, simply set VideoDriver setting to D3D, Voodoo2, or SoftTri. You can set device number in VideoDeviceId setting (but it affects only D3D mode, as in original version of NFS3). | Claimed |
| MP100-024 | You can disable all intro movies by NoMovie setting in ini file. | Claimed |
| MP100-025 | Suppressing of displaying Windows Error Reporting dialog on fatal errors is disabled by default. So if something go wrong you will know about it. But you can enable suppressing of error reporting via NoErrorReporting setting in the ini file. | Static |
| MP100-026 | Internal heap memory limit was extended from 16 to 32 MiB. It have to solve “Out of memory” problem on some rare cases. Also you can control it by OwnHeapLimitMb ini setting (it may be from 16 to 512). | Static |
| MP100-027 | Bugfix for situation when you are cancelled editing audio setting, Engine Volume wasn't restored and set to maximum value, and Sound Effects also sometimes wasn't restored to original value. | Claimed |
| MP100-028 | Fixes for hardware detection function. Original game by mistake tries to simplify intro video graphics for modern computers because internal benchmark thinks that it is 166MHz processor (signed integer, result of benchmark too big and it is treated as negative). This benchmark was replaced to cpuid which sees processor family (i586/i686 or newer), support of MMX/SSE/SSE2, and in result calculates class of processor which is used by game for choosing default settings and deciding which level of video quality user will see. | Claimed |
| MP100-029 | Bugfix for error when game says that on your HDD is less than 1 MiB is free which is not true. | Claimed |
| MP100-030 | Use km/h for speedometers by default. | Claimed |
| MP100-031 | Two camera views: Heli Cam and In Car (you can restore original set in camera settings). | Claimed |
| MP100-032 | Mini map has 1x scaling for cops and 3x for racers by default. | Claimed |
| MP100-033 | Opponent list is displayed by default in splitscreen mode (instead of opponent name which looked a little confusing). | Claimed |
| MP100-034 | “Romulus 3” is used by default for menu soundtrack (but you can change it in audio settings). | Claimed |
| MP100-035 | New icon in variants from 16×16 to 256×256 pixels. Old icon also available and you can set it for your shortcut in properties. | Claimed |
| MP100-036 | Smooth loading indication. Original game does almost nothing between 58% and 100%. | Claimed |
| MP100-037 | Original game makes a copy of music file when loading gameplay, maybe to solve problem with slow CD-ROMs in 90's. Now game plays gameplay music directly from source file. It saves a little time and 10 MiB of resource of your SSD on every gameplay start. | Claimed |
| MP100-038 | Num Lock, Caps Lock и Scroll Lock aren't turned off automatically on every game start. | Claimed |
| MP100-039 | The game doesn't requires CD anymore. | Claimed |
| MP100-040 | The game doesn't try to revert focus every time when it was loosed because it might be a cause of impossibility to kill game process in some situations when the game continuously steals the focus from Task Manager. | Partial |
| MP100-041 | Smart installation checking (it checks existance of some critical game data directories). | Claimed |
| MP100-042 | Some error message boxes were fixed a little. All errors have “error” icon, all warnings have “warning” icon, all fatal errors are displayed with one button “Ok”, not “Ok” and “Cancel” where both buttons do same thing. | Claimed |
| MP100-043 | Information about all unworked debug arguments were hidden in command line help dialog (you can run it with -h argument). | Static |
| MP100-044 | Game's config was moved from ./fedata/config/config.dat to root directory (you can delete ./fedata/config/). | Claimed |
| MP100-045 | The game doesn't removes config.dat, player1.spc, and player2.spc files when exe file is updated. | Claimed |
| MP100-046 | The game doesn't resets video settings when video driver is changed. | Claimed |
| MP100-047 | “About” slide was added to Credits. | Partial |
| MP100-048 | Cone Stats and Tuturial Icon widgets are hidden in HUD editor for cops because these widgets can't be used in this mode. | Claimed |
| MP100-049 | Buggy background animation in graphics settings and opponents choosing screens were fixed. | Claimed |
| MP100-050 | Title in pause menu is more aligned now. In original version of the game it was a little misplaced. | Partial |
| MP100-051 | Flying brands effect added to all slides without large amount of text for consistency. For example, in original version this effect is present on main singleplayer game screen, but it is absent on main splitscreen game screen. | Claimed |
| MP100-052 | On the first menu screen irrelevant link to Need For Speed website was replaced to “Credits...” button. Really, you can't find any mention about NFS3 on this website for 10 years or even more. | Partial |
| MP100-053 | In choose car menu “Download car...” button is hidden because it doesn't work properly anymore. | Partial |
| MP100-054 | Yellow rect which indicates current player in HUD settings screen doesn't overlaps other controls. | Claimed |
| MP100-055 | Standard bottom set of buttons was added to camera settings screen. | Claimed |
| MP100-056 | Based on voodoo2a.dll from the Future Cop L.A.P.D. game. It seems that it is a slightly updated NFS3 driver which uses Glide3x API instead of Glide2x API. So it seems that these drivers are highly compatible and all special effects are present. Original voodoo2a.dll from NFS3 uses Glide 2x API which doesn't have ability do detect supported resolutions. Official update of this file which uses Glide 3x API is based on NFS4 and it seems that it lacks fog effect. So it doesn't fit us. | Claimed |
| MP100-057 | Added support of huge Glide resolutions with ability to use Z-buffer. Now list of supported Glide resolutions are: 640×480, 800×600, 960×720, 1024×768, 1280×1024, 1600×1200. Widescreen resolutions aren't possible with standard Glide API. This list is used when extended Glide API isn't supported. | Claimed |
| MP100-058 | Jointly with the author of nGlide wrapper we are extended Glide API to support all possible resolutions. So if voodoo2a.dll detects that this extended Glide API is supported then it displays all possible resolutions (inclusive widescreen ones). | Claimed |
| MP100-059 | nGlide 1.04.1 with support of extended API is included in this archive. | Claimed |
| MP100-060 | If you would like to use other Glide wrapper with support of all resolutions, please write to author of this wrapper a suggestion to add support of extended resolutions Glide API. This extension is easy to implement and it should not take a long time. | Claimed |
| MP100-061 | Based on the original d3da.dll from NFS3 (works on DirectX 5). Newer versions of this driver not fully compatible with NFS3 and may be a cause of graphical glitches like huge black polygon near Old Church in Hometown. | Claimed |
| MP100-062 | The driver hides resolutions with height lower than 480 pixels now. It frees space in the list for modern resolutions. | Claimed |
| MP100-063 | The driver works in 32-bit mode if it is available in the system. It improves quality of dust or splashes from wheels. | Claimed |
| MP100-064 | 640×480 always reported as 16-bit. Original title movie doesn't works in 32-bit mode. | Claimed |
| MP100-065 | Light beams effect now works in D3D mode. In original version this effect available in Voodoo2 mode only. | Claimed |
| MP100-066 | Based on the original softtria.dll from NFS3. Newer versions of this driver render worse image or crash. | Claimed |
| MP100-067 | The driver reports only 16-bit resolutions now. Original version was reported that 32-bit resolutions are supported, but it isn't true. This driver can't work in 32-bit modes. | Claimed |

<!-- END GENERATED MODERN CHANGE LIST -->
