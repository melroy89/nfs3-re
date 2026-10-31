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
