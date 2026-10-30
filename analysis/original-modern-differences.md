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

The [configuration comparison](original-modern-configuration.md) traces the Modern caller and INI/environment readers: explicit INI values precede environment defaults, then caller defaults. Original registry imports and the new profile API calls support a migration, but each original setting/key still needs mapping. The configured filename is passed as direct buffer address `007a263c`; its complete initialization history remains unresolved.

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

## 13. Prioritized semantic work remaining

The full JSON inventory gives every current Modern local function name, entry/ranges, original/Modern hashes, changed-byte count, thunk marker and original-entry candidate flag. The following high-change clusters are investigation seeds, not yet completed before/after explanations:

| Current Modern entry / label | Differing same-VA body bytes | Required next evidence |
|---|---:|---|
| `0047f650` BuildNineTexturedRectangleBorderQuads | 800 / 828 | Original function correspondence, layout/geometry calculations and callers |
| `004be5e0` InitializeViewportGeometryForProfile | 608 / 634 | Original projection/FOV arithmetic versus current viewport profile |
| `004cd6c0` InitializeGameWindow | 514 / 918 | Initializer/callback lifecycle traced; actual styles, sizing and hook callback semantics remain |
| `004b5844` LoadThrashDriverSettings | 486 / 504 | Modern INI/driver path traced in renderer report; original selection policy still pending |
| `00494cb0` RenderTiledLoadingArtworkAndInitializeProgressBounds | 480 / 748 | Original scaling/progress boundaries versus tile paths |
| `004e3078` ScreenshotEncodingThread | 451 / 464 | Original synchronous counterpart mapped in screenshot report; GDI+ success, resources and runtime lifetime remain |
| `004b5a58` InitializeThrashRenderer | 407 / 421 | Loader/export checks traced in renderer report; initialization selectors/compatibility consumers still pending |
| `004b5580` LoadGameIniSettings | 374 / 393 | Exact key/default/type/error behavior versus original system settings |
| `0044a2d0` DispatchFrontendMenuKeyToSelectedEntry | 332 / 358 | Exact key/focus actions and behavior removed or added |
| `00485880` InitializeDefaultHudLayoutProfileSettings | 332 / 375 | Original HUD data loading versus synthesized layout |

Continue by matching original functions/control-flow neighborhoods, documenting changed instructions/data and linking the corresponding release-note ID. When a same-VA comparison is not a valid counterpart, explicitly map moved/reused/deleted code instead of interpreting a large byte count as a rewrite of the same routine.

The 290 catalog entries span multiple releases and include driver/assets/configuration changes outside `nfs3.exe`. They cannot all be explained by this executable pair alone. Items still marked vendor-claimed have not been verified simply because their names resemble a current annotated function. Runtime acceptance is separate from static code correspondence.

## Reproduction and completion boundary

`analysis/scripts/ghidra/ExportFunctionInventory.java` exports metadata only. `analysis/scripts/compare_nfs3_executables.py` compares PE sections, imports/resources and selected body bytes without changing an executable or producing C. The JSON records input identities and inventory provenance. Raw downloads, original analysis database, disassemblies and metadata dumps remain under ignored `analysis/captures/modern-differences/`.

Completed so far: exact three-way baseline, initial whole-code/function inventory, precision policy explanation, import/resource deltas, and the existing RaceNet byte witness. **Still pending:** full semantic mapping of changed regions, catalog-to-code coverage and decisive cross-version runtime compatibility tests. This is progress toward the active audit, not a claim that every Modern Patch change is understood.
