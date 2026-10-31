# Original versus Modern audit: current stopping point

## Acceptance and limits

**The broad reference inventory is complete. The exhaustive code-level investigation is not.** This status separates those deliverables; no percentage of whole-game understanding is justified by chapter, link or byte counts.

| Deliverable | Current result |
|---|---|
| Version-bound original/official/local identities | Recorded with executable hashes and three-way distinctions in the main comparison |
| Documented release-history list | All290 entries across12 releases indexed with stable IDs; vendor claims remain labelled |
| Address navigation | All361 changed saved-function entries listed and linked to chapter address mentions; those mentions are search aids, not semantic completion |
| Detailed code differences | Numerous bounded static chapters, with original/Modern addresses, evidence manifests and unresolved limits |
| Exhaustive explanation of changed code/data/assets/DLLs | Incomplete; the code inventory includes21,926 changed bytes outside saved Modern function ranges |
| Runtime original/Modern compatibility or complete visual equivalence | Not established by this static audit |

Use the [main comparison](original-modern-differences.md), [release-note catalog](modern-patch-change-catalog.md) and [address index](original-modern-function-index.md). Existing host/VM observations must not be relabelled as original-versus-Modern tests.

## Finish this pass

The latest checkpoint adds the [small-entry follow-up](original-modern-small-entry-followup.md), including vehicle-loading progress data and seven previously unreferenced entries, and [quad-set draw arguments](original-modern-viewport-geometry.md#quad-set-draw-arguments-six-changed-constants). All361 changed saved-function entries now have chapter address references. This closes the missing-reference queue, not the semantic investigation. Earlier [partial geometry context tracing](original-modern-geometry-color-admission.md#current-context-trace-and-stopping-point) remains unresolved on its stated terms.

No additional game execution, instruction probes, toolchain work, C reconstruction or Ghidra changes are part of this closeout. Executable bytes and existing reconstruction/raw exports are preserved.

## Acceptance checklist at the latest documentation checkpoint

- [x] Exact supplied-original, official Modern and locally edited target identities are distinguished in the main report.
- [x] All290 documented release-history bullets have stable IDs, full-text reference entries and qualified evidence labels.
- [x] All361 changed saved Modern function entries have address-based chapter references; this remains navigation coverage only.
- [x] All337 outside-body intervals with changed bytes have addresses, hashes, changed runs and byte classes; selected mechanisms are linked to prior reports.
- [x] All11,576 differing initialized-data bytes have a [605-run address/byte map](original-modern-initialized-data-index.md), with PE relocation annotations; semantic object correspondence remains incomplete.
- [x] Detailed static reports include original/Modern counterparts, register/control/data changes and explicit unknowns. Recent additions cover [legacy DDE removal](original-modern-removed-dde.md), [force-feedback menu field writes](original-modern-force-menu-layout.md), [default tables and fog selection](original-modern-resolution-defaults.md#tier-tables-occupy-former-original-code-final-loadstore-mismatch) and [animation register preservation](original-modern-frontend-page.md#animation-function-boundaries-also-change-register-preservation).
- [x] Executables, established Ghidra state, raw reference exports and maintained reconstruction sources are preserved by these documentation/static-audit changes.
- [x] [Relocation differences](original-modern-relocation-index.md) account for added/removed sites, changed shared operands and exact directory-size changes; loader behavior remains untested.
- [x] [Resource payload comparison](original-modern-pe-resources.md) covers all three executable baselines, retained/added icons, media resources and manifests; shell selection and displayed results remain untested.
- [x] [Packaged x87 inventory](original-modern-packaged-x87.md) pins all11 DLL members and distinguishes linear-decoding candidates from the verified DX8 rounding helpers and bounded caller. It is not an original/Modern DLL comparison.
- [x] [Selected local DLL inventory](original-modern-dll-candidates.md) pins legacy-style candidates and official matching wrappers, export names and static imports; retail provenance remains unresolved; bounded Voodoo descriptor/mode-producer comparisons are now documented, while full functional correspondence and rendering remain unverified.
- [x] All12 original entries overlapping the largest removed startup NOP span have an [entry-by-entry research handoff](original-modern-outside-function-index.md#largest-removed-startup-span-entry-by-entry-handoff), with checked report addresses and explicit remaining boundaries. This is classification/navigation, not complete semantic coverage.
- [ ] Every changed instruction/data/asset/DLL mechanism independently explained: still incomplete.
- [ ] Historical introduction claims established from intermediate release pairs: still incomplete.
- [ ] Original/Modern runtime, replay, multiplayer and visual equivalence established: not run by this static audit.

The catalog now links MP161-011 to the verified video-mode refactoring as **partial** support. The final pair cannot date that mechanism to v1.6.1, and both versions already test mode-call failure; neither an introduction date nor newly added failure handling is implied. The documentation handoff is usable now, while the persistent broader investigation remains incomplete. Do not turn the checked inventory items into a whole-game completion claim.

## Latest bounded findings and review

The recent static audits were rerun successfully after the following findings were committed:

| Evidence route | Added finding | Remaining boundary |
|---|---|---|
| [Startup requirements](original-modern-startup-requirements.md) | Removed corruption diagnostic, texture-resource log, DirectDraw capability probe and installation/media admission helpers; exact bodies/tables and caller branches retained. | Pre-exit hook completion, path/API failure behavior, provider results and historical attribution remain incomplete. |
| [Worker/shutdown](original-modern-input-worker.md#complete-shutdown-envelope-around-the-worker-change) | Complete original/Modern shutdown call order, local x87-reset removal, original no-op and hook-cleanup behavior. | All teardown ownership and actual completion/synchronization unverified. |
| [Voodoo candidate pair](original-modern-dll-candidates.md) | Descriptor setup, dynamic sorted mode producer, extra published slot and resolver-backed Glide dependencies. | Legacy provenance, final slot ownership, provider contracts and rendering unverified. |
| [Logo producer](original-modern-frontend-page.md#logo-state-producer-preserves-eax-two-callers-discard-its-working-value) | Additional EAX preservation; both inspected producer callers overwrite the working result before use. | Other callers, memory outputs, flags and x87 equivalence not established. |

Reproduction commands are `python3 analysis/scripts/audit_startup_requirement_difference.py`, `audit_input_worker_difference.py`, `audit_voodoo_about_setup.py` and `audit_model_presence_difference.py` (all scripts under `analysis/scripts/`). Each pins its target identity and retains exact static witnesses. Successful execution means those assertions/captures reproduce; it is not target execution or independent whole-game equivalence. No evidence label is upgraded from runtime-unverified to verified runtime by this review.

## Independent review of the latest numeric contracts

Two Luna6 reviewers independently checked the control-component callback and original calibration/Modern FOV numeric paths against their pinned PE instructions. Neither reported a material inaccuracy within its assigned scope. The [review checkpoint](evidence/validation/recent-static-contract-review.json) binds the reviewed commit, report/script/manifest hashes, named scopes, reviewer qualifications and three successful parent reproduction commands.

The callback review confirms the52-byte delta, shared pointer/gate, finite cancellation and raw return2-to0. The numeric review confirms signed wrapping subtraction, binary32/binary64 spill ordering and negative-product−8 branch in original calibration, plus the conditional unordered107 result in Modern FOV. These findings are static; no reviewer executed a target/probe or changed Ghidra. Signed-zero, nonfinite/exception and caller/state limitations remain explicit.

The original EXE, official Modern EXE, local analysis EXE and saved `db.3146.gbf` hashes were read again and match the recorded baseline. This verifies preservation for those exact artifacts; it is not a new saved-signature readback or runtime acceptance test. The broader investigation remains incomplete.

## Prioritized remaining work

1. **Review substantive gaps, rather than searching for unreferenced entries.** The address-reference queue is now empty. Use each chapter’s limitations to select missing original counterparts or unresolved mechanisms, and check existing research before expanding. A chapter mention can still cover only a caller or partial span; it does not certify a whole function.
2. **Classify the outside-function changed code spans.** The [337-interval address/ranking inventory](original-modern-outside-function-index.md) is now available; its byte classes are complete for the pinned saved-body union, but semantic explanations remain pending. Separate removed instructions, intentional NOP filling, embedded data and missing function boundaries. This addresses a whole-audit gap that additional detail on already-understood menu helpers cannot close.
3. **Reconcile code findings with catalog claims.** Add links only when the mechanism supports the actual claim. Historical versions, bundled claims and undocumented changes may remain separate. Avoid forcing every code change into a release-note bullet.
4. **Complete targeted asset/DLL dependency comparisons where necessary.** Reuse pinned package inventories; establish data formats/lifetimes only for the selected feature. Supplied backups remain unauthenticated retail provenance.
5. **Plan decisive runtime comparisons separately.** Replays/multiplayer require controlled original/Modern inputs and state comparison. Visual or driver success claims require their own observations. Static equality, restored x87 stack balance and modern-to-modern tests do not substitute for these.

For each next investigation, name the question, bounded addresses/artifacts and stopping condition up front. End it with a verified difference or a precise unknown plus required evidence. Commit coherent findings; do not turn every remaining uncertainty into another prerequisite.

This handoff closes a documentation pass, not the persistent objective of explaining all Modern Patch differences. The broader audit remains active and incomplete.

## Subsequent inventory reconciliation

The outside-body triage now routes two further high-ranked intervals to reproduced existing evidence: `0041d6e4..0041d7e4` is the Modern256-byte preset WORD table, while `00472e1d..00472f20` contains54 Modern graphics-default table bytes surrounded by NOPs. The paired preset/default audits were rerun successfully. These are original-code-to-Modern-data transformations, not newly discovered executable functions; whole-code inventory totals are unchanged.

The [InteriorBx follow-up](original-modern-control-component-keys.md) additionally establishes selected-entry return normalization,188-byte template copying, overlapping source-byte destinations, and common-property store ranges. Compass bit9 semantics and InteriorBx+45h consumers remain unresolved. That bounded menu investigation can be resumed from those exact fields; resolving it is not a prerequisite for classifying other outside-body intervals. The next broad task remains semantic classification of the inventory, with existing chapters reused before additional disassembly.

## Menu/audio and interval-classification checkpoint

The [checkpoint manifest](evidence/validation/menu-audio-interval-checkpoint.json) pins the reviewed commit and verifies the original, official Modern, local analysis EXE and saved database against their prior SHA-256 identities. All tracked changes since`a0f4069` are confined to`analysis/`; this observation does not audit ignored filesystem changes or every project/probe file. The two new audio audits each produced identical manifests on two successive runs. That proves repeatability of these static captures, not independent semantic review or runtime equivalence.

New code-level findings in this increment include seven removed truncation calls across five audio sliders, pending-music publication before both setting-change requests, expanded SFX intensity admission mask40h→50h, and verified old copied-mode/new direct-field offset correspondence. InteriorBx selected-entry dispatch normalizes both inspected0020h callback outcomes to0. Its overlapping template copy still leaves Compass bit9 and InteriorBx+45h semantics unresolved.

The outside-body index now additionally partitions graphics, audio/adjacent policy, force-menu, credits, logo, HUD, cascade and idle-controller intervals, and separates the startup jump table from preceding NOP filling. These classifications reuse complete paired research and preserve old/new boundary differences. They do not establish whole-code semantic coverage; all337 intervals and21,926 outside-body changed-byte totals remain inventory counts. Next work should target remaining unclassified mechanisms or substantive chapter limitations, rather than repeat these resolved byte-localization checks. Runtime compatibility, original asset/DLL provenance and historical introduction remain separate open evidence requirements.

## Window-input follow-up checkpoint

The [window-handling chapter](original-modern-window-handling.md) now resolves the hook filters, the original startup's null callback, Modern's two hook decoders and raw-sum installation gate, plus the removed recurring foreground/cursor loop tail and its original predicates. The [cursor chapter](original-modern-mouse-cursor.md#release-note-correspondence-and-remaining-acceptance) connects previously established callback evidence to MP140-069. MP140-068 and MP140-069 now have partial static support rather than vendor-only labels; MP100-040 has a specific removed retry mechanism.

Remaining work for this cluster is focused: identify all producers/lifetimes of the removed tail's input state, qualify any alternate callback/alias writes, and observe the particular focus/system-menu outcomes if runtime validation is later undertaken. Intermediate releases are required for historical rename/introduction claims. No global absence of foreground requests, working Windows NT hook, or cursor display-count balance is established.

## Window, heap and speed-unit validation checkpoint

The [checkpoint manifest](evidence/validation/window-heap-speed-checkpoint.json) binds nine successful static audit reruns to reviewed commit `b693816`, retaining exact commands, script hashes and outputs. It also confirms the saved database's prior SHA-256 identity. This is reproduction of bounded evidence, **not an independent full semantic review**. The refreshed address indexes retain361 changed saved-function entries with chapter references and337 outside-body intervals with21,926 differing bytes.

This increment establishes additional concrete differences: original named-mutex/title recovery versus Modern's process-heap handle producer at the same global address; six Modern heap register adapters; optional renderer-directory export dispatch; and a default HUD selector that takes the digital KPH branch independently of the original locale selector. The analog speed geometry and its constants remain byte-identical, while dial calibration and changed numeric dependencies remain separate questions.

At that pinned checkpoint the catalog had162 vendor-only,39 bounded static,86 partial and3 unresolved labels. These counts describe evidence classification, not a completion percentage. No game/API execution, new instruction probes, exports, compilation or database mutation was used. Historical introduction, original asset/DLL provenance, full state/caller lifetimes and original/Modern runtime compatibility remain open. The next substantive work should target unclassified changed mechanisms or an identified missing data/consumer link, reusing the current reports before new disassembly.

## Parameter-preset static review checkpoint

The [preset report](original-modern-parameter-preset.md) now establishes all original integer-store branches, the exact `wrap32(N*factor)` simplification for its twelve asserted multiply sequences, and concrete differences from Modern's WORD table. It retains64 mathematical input cases,48 differing in fields both apply routines write, and a separate initialization-qualified comparison for untouched original fields. These are static derivations, not instruction-probe results. Retained setter/cycling, three callsite witnesses, reset/append bodies and template initialization narrow the interface/lifecycle boundaries.

Two Luna reviewers independently checked the retained instruction/document consistency and arithmetic/model/manifest consistency, finding no concrete errors in that scope. Neither independently re-extracted binary bytes or ran the audit. The primary agent reran the hash-pinned preset audit and documentation checks successfully. The [review record](evidence/validation/parameter-preset-review.json) pins the exact reviewed revision and file hashes; it is not a claim of whole-repository independent validation.

At that review checkpoint, downstream field meanings remained open. Subsequent evidence now identifies the selector as View Distance and maps all four Modern-written fields to rendering consumers, with Night/two-player branch bindings. Remaining work concerns the pre-existing +20h/+2ch field, complete coordinate/submission meanings, selector/record lifetime invariants, alternate writers and runtime effects. Original's negative-count skip versus Modern's nonzero LOOP remains conditional; reachability is unproven. The review record applies to its pinned revision, not to these later additions. No executable, saved database, maintained reconstruction or raw reference export was changed in this work.

## Current priority queue after View Distance and gear-label follow-ups

The catalog currently labels152 entries vendor-only,39 bounded static,96 partial and3 unresolved. New qualified links include Full view-distance thresholds and mirror record selection, Night/two-player conditions, gear endpoint anchoring/smaller-scale fallback, and the vertical-angle calculation. The HUD base-scale coefficient also changes independently of the dimension-read relocation. These are documented mechanisms, not runtime acceptance or a whole-game completion percentage.

| Priority | Remaining question | Existing evidence / next required action | Evidence boundary |
|---:|---|---|---|
| 1 | MP160-003 horizon/camera shift | [Projection report](original-modern-projection.md) now covers ordinary/weather dispatch and direct centre writers; recover conditional type8 source initialization or qualify its admission, then camera orientation/output | Executable inspection can advance this; visible horizon still needs rendering evidence |
| 2 | MP160-006 remaining output coverage | [Map-marker extent-to-quad chain](original-modern-map-marker-scaling.md) now established; qualify other marker styles, lifecycle and actual rendered size separately | Static source/consumer gap closed; visual scope remains unverified |
| 3 | MP161-001/002 renderer-specific texel alignment/fog | Use [packaged DLL inventory](original-modern-dll-candidates.md) and authenticated matching older DLLs for component comparisons | EXE changes or DLL names alone cannot establish these DLL implementations/history |
| 4 | Historical regressions such as MP153-008 or the specific MP152-001 improvement | Obtain the named intermediate-release pairs; reuse [language fallback](original-modern-language-table.md) and [rear-view mechanisms](original-modern-track-detail.md) as final-state context | Original versus final cannot isolate an intermediate regression/fix |
| 5 | Original/Modern rendered, replay and multiplayer consequences | Compare separately identified inputs/builds within an explicitly stated runtime scope | Existing single-build captures and static derivations are not cross-version equivalence evidence |

Continue with a concrete missing producer/consumer link from this queue. Do not repeat already resolved preset arithmetic, expand into unrelated scratchpad work, or treat historical/runtime requirements as blockers to all remaining static inspection. The bounded reference inventory remains complete; the broader investigation remains active and incomplete.

## Projection and map review checkpoint

The [checkpoint record](evidence/validation/projection-map-review-checkpoint.json) binds nine successful root audit reruns to the reviewed revision and records two Luna consistency reviews. The reviewers checked retained documentation/models and reported no concrete errors; they did not independently re-extract binaries or run the audits. The primary agent performed the fresh hash-pinned static reruns. The saved Ghidra database and local analysis executable still match their prior hashes. The projection introduction now lists the companion audits needed for its expanded sections.

- **Complete within static scope:** original/Modern rectangle examples; temporary weather versus ordinary projection selection; the three changed chooser calls; complete literal-centre writer inventory; retained centre producer/consumer; non-file-backed conditional source classification; map-marker extent-to-quad link; role-profile defaults into map zoom.
- **Still unresolved:** conditional type8 source producer/admission and ordering, computed aliases, camera orientation/final horizon, active map/profile state, all marker styles and actual rendered output. Historical claims need the appropriate intermediate pairs; runtime compatibility remains separate.

The map-point mechanism gap in MP160-006 and field/consumer gap in MP140-073 are closed at the documented static boundary. The whole vendor claims are still partial. MP160-003 remains unresolved. The broader original/Modern investigation is not marked complete, and this checkpoint does not authorize or imply a rebuilt game.

## Logo-claim reconciliation

MP153-013 now links the existing paired presence-policy audit and official atlas identification in the [frontend report](original-modern-frontend-page.md#release-note-correspondence-model-dependent-logos). A fresh audit rerun passed. Modern per-record Ford/HSV model filtering has partial static evidence; the legacy LOGO2-to-logos asset relationship, historical introduction and full runtime behavior remain unverified. The documented rejected-final-record fall-through is retained as a limitation. This reconciles existing evidence rather than claiming a newly discovered code change.

## Texture-query claim reconciliation

A fresh five-envelope texture audit passed. MP161-005 now links [removed queries/cache substitutions](original-modern-texture-loading-followup.md#release-note-correspondence-redundant-about-queries), matching the source bullet's explicit thrash_about wording. This closes a catalog omission using existing paired evidence. Renderer side effects/cache lifetime, actual performance and release-specific introduction remain open; progress-bar changes are not performance measurements.

## Root-path diagnostic claim reconciliation

MP161-007 now has a [branch-to-message mapping](original-modern-startup-paths.md#release-note-correspondence-root-path-diagnostic): the unsigned210-byte prefix gate, exact error text and diagnostic call are asserted against the official executable. Extraction failures share the same branch. The missing-driver subclaim, historical introduction and actual dialogs remain unqualified; no path/API/game execution was performed.

## Missing-driver diagnostic follow-up

The [renderer-loader follow-up](original-modern-renderer-loading.md#missing-driver-diagnostic-correspondence) now maps the second MP161-007 subclaim: configuration constructor failure selects the missing-driver message; low-level load failure uses a distinct cannot-load message. Both named final-build diagnostic mechanisms are mapped, with retained branch captures and exact message assertions. Historical introduction, original-wide absence and runtime dialogs remain unverified; the catalog remains partial.

## View Angle setting linkage

The projection audit now pins both option-list descriptors, the shared selector and official final English labels. [MP140-063 linkage](original-modern-projection.md#view-angle-option-list-and-release-note-correspondence) establishes the75/90/105 choices and final Automatic addition. Ordinal0 changes from fixed90 to cached automatic; intermediate-release lists, persisted-setting migration and rendered behavior remain unverified.

## Audio-mode fallback linkage

MP153-010 now links verified audiomode choice IDs and the [D3D/EAX-to-Stereo normalization](original-modern-config-loading.md#sound-mode-identity-d3deax-falls-back-to-stereo). The complete underlying capability helper is retained between baselines. Actual device transitions/provider behavior, audible output and release-specific introduction remain open.

## Configuration, loading and audio checkpoint

The [checkpoint manifest](evidence/validation/configuration-loading-audio-checkpoint.json) records seven fresh successful static audits, their exact commands/script hashes and outputs, and four preserved identities: original, official Modern, local analysis EXE and saved Ghidra database. This increment has no new independent review; earlier reviews remain scoped to their pinned revisions.

Concrete added findings are indexed in the main report: original save flag versus Modern header refresh; original zero-version prefix and conditional configuration reset; View Angle label/storage/default linkage; Modern loading admission, exact-bit return and two distinct retry levels; and D3D/EAX-to-Stereo fallback using retained driver capability dispatch. The catalog has152 vendor-only,39 bounded static,96 partial and3 unresolved entries; labels are evidence classifications, not completion percentages.

Remaining questions include full original default/save lifecycle, callback result/register contracts, real save migration, timing/audio/rendered outcomes and historical introduction. These findings do not resolve unrelated projection type8 sources, renderer-DLL history or every vendor claim. The broad comparison remains active and incomplete. Continue with another concrete unqualified changed mechanism rather than repeatedly restating this completed static increment.
