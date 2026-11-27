# Original versus Modern audit: current stopping point

## Core comparison priorities

The primary deliverable is an evidence-backed original/Modern comparison for reconstruction. Historical DLL/menu details support it; completing every historical/runtime unknown is not the next action. The shallow release-note inventory is complete, while exhaustive binary semantics and cross-version compatibility remain unproved.

|Priority |Question / starting evidence |Required result before a broader claim |
|---|---|---|
|1 |[Race arithmetic and x87 scope](og-modern-x87-precision.md): start with race loop004c4e40/render boundary004bc680 and a named simulation callee |One bounded original/official-Modern path with verified CW ownership, arithmetic/storage/conversion boundaries and changed versus retained instructions; do not extrapolate menu arithmetic to physics |
|2 |[Input dispatch](original-modern-input-worker.md), [network endpoints](original-modern-network-endpoints.md) and replay evidence |Map a selected input/state serialization path and its record layout in both baselines; separate protocol, timing, physics and replay presentation. Existing connection tests do not prove OG/Modern equivalence |
|3 |[Reconstruction baselines](original-modern-reconstruction-baselines.md) and [readiness audit](recompilation-readiness.md) |Keep module ABI, shared scratch, data/init dependencies and chosen target version explicit. The tested00485c30 sample and [caller-status review](line-boundary-x87-callers.md) do not qualify whole-game replacement |
|4 |[Remaining release claims](modern-patch-change-catalog.md) |For a consequential unanswered claim, name the exact pair/address and closure evidence; otherwise label missing artifact, static gap, runtime requirement or vague attribution. Do not force a nearby edit into a vendor claim |

A later behavioral comparison would need identical inputs and matched simulation ticks/state against the chosen original/Modern baseline, followed by scoped replay/network exchange. This is a documented evidence gate, not an instruction to run new probes now or a prerequisite to every static finding. The claimed third-party ARM64 implementation has not been supplied for comparison.

**Parked:** further minor menu/renderer history, cosmetic offsets, additional version-resource labels and repeated localization of already mapped spans, unless they resolve a priority above. Preserve all existing chapters/evidence and their original scope; no executable/Ghidra edits or new C/toolchain/probe work are needed for this consolidation.

## Current core arithmetic finding

The [bounded race/physics comparison](og-modern-x87-precision.md#bounded-race-scheduling-and-four-wheel-arithmetic-comparison)
now verifies five byte-identical scheduling, registration, dispatch and four-wheel-integration
ranges in original/official Modern. The actual velocity stores remain binary32. The selected
straight-line window has no CW change; inherited CW across dynamically registered callbacks
and delegated helpers remains unresolved. The [follow-up](og-modern-x87-precision.md#callback-producer-and-immediate-helper-follow-up)
verifies the callback initializer and18 immediate helpers, including ten retained integer
conversion sites and explicit AI/network overrides. Next trace further callees and preceding
callbacks for transitive CW ownership; do not claim identical physics or inevitable desynchronization.
Static evidence only; no new instruction probes or game execution.

The [deeper dependency inventory](og-modern-x87-precision.md#deeper-dependency-inventory-retained-local-extended-state-math)
now identifies retained FNSAVE/reset/FRSTOR and explicit extended-mode angle math on a physics
call path in **both** baselines. It also compares the changed drivetrain truncation helper's
complete bodies. Of 176 saved entries per file, 174 ranges match. The sole
nonentry direct target is a verified shared epilogue. The
[indirect-edge review](og-modern-x87-precision.md#deeper-dependency-inventory-retained-local-extended-state-math)
identifies 27 named import sites, 79 other indirect call sites and five indexed
jumps per executable. The [angle follow-up](og-modern-x87-precision.md#the-retained-angle-dispatch-restores-the-saved-word-on-all-eight-table-routes)
resolves one indexed jump for all eight entries and another for the two
calls using selector 15. The 17-entry lookup data and the scoped divide
operations match. Transitive control-word ownership through the remaining
callbacks and other selectors remains open.

For an eventual numeric comparison, use both signs of each operand with
magnitude pairs on either side of the exchange boundary and at equality.
Include ratios immediately below, at and above the half-step lookup
thresholds `(2k + 1)/32` for k = 0 through 15, and use the same binary
inputs in both implementations. Compare the selected index, reduced
angle, quadrant result and final binary32 store. Separately exercise
signed zero, subnormals and infinities through the fallback branch.
Record the incoming and outgoing control word and status around the
wrapper. This is a proposed comparison set. Game trajectories and
multiplayer compatibility require additional tick-matched evidence.

## Outside-function documentation coverage

The [outside-function index](original-modern-outside-function-index.md) inventories
337 changed intervals and 21,926 differing bytes. Matching exact interval boundaries
in its linked explanation rows to the JSON inventory identifies 112 intervals
containing 19,597 differing bytes. The other 225 intervals contain 2,329 differing
bytes. These counts measure direct navigation from the index. Some remaining
intervals already have partial notes or links for subranges, and a linked row
can still have open semantic questions.

Ranking the intervals without an exact linked row by changed Modern bytes other
than NOP or zero places the remaining intervals in the machine-readable inventory for follow-up.
These are candidates for matching against existing research before assigning
new meaning to the changes.

## Latest bounded reproducibility checkpoint

The [five-audit checkpoint](evidence/validation/early-hud-package-worker-checkpoint.json) reviews `6e5e9dc`: **10/10 static runs** reproduce five committed outputs (early HUD, wrapper packages, race-entry guard/registrar, input-worker/creator and block relocation). **12 protected artifacts and12 raw exports** retain prior hashes. Reproduce with `python3 analysis/scripts/check_early_hud_package_worker.py`. This closes repeatability/preservation for those follow-ups, not semantic independence, live Ghidra readback, runtime behavior or the full comparison.


## Current texture, clock, speech and loader checkpoint — 2026-11-21

The [eight-audit checkpoint](evidence/validation/texture-clock-speech-loader-checkpoint.json) reviews `b1b26ab`: **16/16 static reruns** reproduce eight committed evidence outputs; **12 protected artifacts and12 retained raw exports** match prior hashes. Reproduce with `python3 analysis/scripts/check_texture_clock_speech_loader.py`. This covers all eight investigation scripts added/changed since the preceding renderer/loading/menu checkpoint; selected shared dependencies and exact output hashes are recorded. It is primary-agent repeatability/preservation, not independent semantic review, runtime acceptance or whole-repository qualification.

|Investigation |Verified static result |Still unknown |
|---|---|---|
|[Texture extent](original-modern-texture-limits.md#historical-track-extent-and-experimental-setting-are-separate-changes) |140→150 track argument128→256;151 adds configurable wrapper overriding retained128 |Beta-only claim, all producers and actual uploads |
|[Clock source](original-modern-clock-source.md#historical-clock-boundary-is152-to153) |152→153 switches16 known calls; timer ranges otherwise retained after operand normalization |Accuracy, pacing, rollover and separate generic startup-fix cause |
|[DX6 format count](original-modern-texture-limits.md#dx6-format-count-bound-is-separate-from-texture-dimensions) |120 callback guards unsigned count100 before156-byte record writes |Missing prepatch NFS4 driver and reproduced crash repair |
|[Early DX6 modes](original-modern-display-modes.md#early120-dx6-mode-policies-and-the640-by480-caveat) |120/131 driver identity; capacity/height policy; conditional32-bit overwrite of640×480 seed |Actual mode selection and movie behavior; not universally forced16-bit |
|[OS admission](original-modern-startup-requirements.md#historical130-to131-lowers-the-directx-probe-os-gate) |130→131 probe changes one byte: major minimum5→4 |Windows98/Me loader, driver and game success |
|[Speech fallback](original-modern-sound-bank-language.md#cached-selector-producer-checks-a-directory-and-requests-english-fallback) |Directory-false English request; helpers preserve selector; two Swedish E→W tables |English/files not rechecked; playback and full lifetimes |
|[Speech history](original-modern-sound-bank-language.md#historical110-to120-dates-the-selected-fallback-and-swedish-code) |110→120 dates those selected changes; historical/final cache and helper contracts distinguished |All consumers and crash avoidance |
|[Renderer load sites](original-modern-renderer-loading.md#historical110-to120-consolidates-direct-renderer-load-sites) |Six switch-wrapper sites become one direct loader site at120; snapshot bodies still retained |Runtime invocation/refcount counts; one site is not one process load |

The subsequent [120→130 HUD preset audit](original-modern-hud-layout.md#earlier120-to130-updates55-preset-records) compares the complete1152-byte table:55/144 records and118 WORDs change, while selected copy/converter/scaler bodies remain identical. MP130-004 gains partial support; whole release scope and rendered results remain unverified. This new audit is outside these16 checkpoint runs.

The expanded [early Glide package audit](original-modern-renderer-loading.md#early120-package-contains-two-configured-glide-provider-pairs) verifies120's two configured provider/adapter choices and110's nGlide1.04.1 label. MP120-021 gains bounded package support; MP120-028/MP100-059 gain partial label support, with headlight/extended-API/runtime and exact100 inclusion unverified. This extension is outside these16 checkpoint runs.

The subsequent [120→130 race-entry audit](original-modern-loading-timing.md#historical130-removes-a-nonpositive-counter-termination-at-race-entry) verifies removal of an explicit nonpositive-counter termination guard, with the selected progress spans retained. MP130-002 gains partial candidate support; counter-state provenance, causal attribution and runtime success remain unverified. This new audit is outside these16 checkpoint runs.

The [race-entry registrar follow-up](original-modern-loading-timing.md#callback-registrar-preserves-the-zero-reset-value) resolves EDX preservation and proves the first-registration branch resets the tested counter to zero. Subsequent callback timing and actual entry state remain unobserved; MP130-002 stays a partial candidate. This expanded audit is outside these16 checkpoint runs.

The subsequent [120→130 input-worker audit](original-modern-input-worker.md#historical-cooperative-worker-change-is120-to130) dates cooperative sentinel/event exit and changed shutdown routing, with collector/table/wrappers retained. MP130-003 gains partial candidate support; the vague multiplayer-fix attribution and runtime synchronization remain unverified. This new audit is outside these16 checkpoint runs.

The [historical worker-creator follow-up](original-modern-input-worker.md#historical-creator-publishes-descriptor-before-explicit-resume) proves retained suspended creation and descriptor-before-resume order120/130, while distinguishing event readiness and the callback-to-ThreadProc shim. It does not establish a new130 handshake or runtime synchronization. This expanded audit is outside these16 checkpoint runs.

The subsequent [worker-space relocation audit](original-modern-input-worker.md#historical-worker-placement-relocates-a-pre-existing-block) proves120's150-byte block0041d7c8 relocates to0040fed0 in130 with11 unchanged control-transfer targets, freeing space for the worker. Final music/worker labels must not be transferred backward. This new audit is outside these16 checkpoint runs; catalogue counts are unchanged.

The expanded [early HUD aspect audit](original-modern-hud-layout.md#earlier130-also-changes-the-x87-aspect-adjustment-block) assigns329 changed byte positions to120→130 aspect construction/helpers, with new dimension operands, near-half coefficient and six-value x87 cleanup. Earlier copy-prefix equality does not imply whole-initializer equality; dimension provenance and visual behavior remain unverified. This extension is outside these16 checkpoint runs; labels are unchanged.

The [early HUD publisher follow-up](original-modern-hud-layout.md#historical-dimension-publisher-moves-with-the-hud-operands) proves the operand-address change follows the same selected-record publication, with retained composite-key rebuild gating. MP100-005 gains partial support from this linkage and existing original/final initialization evidence; universal rebuilding, all POS consumers and visual accuracy remain unverified. This expanded audit is outside these16 checkpoint runs.

At this checkpoint the catalogue had **40 vendor-only, 57 bounded-static, 193 partial and 0 unresolved-category entries** across290 release-note bullets. Labels are evidence classifications, not distinct EXE changes or a completion percentage. The shallow list covers every source bullet; it does not cover every undocumented binary difference. Zero unresolved-category entries does not mean zero unknowns.

The requested Markdown comparison and reproducible, address-based findings exist, but exhaustive original/Modern semantic coverage is **not complete**. The table above distinguishes new mechanisms from pending behavior instead of making each runtime unknown a prerequisite for other inspection. Next prioritize a remaining concrete mechanism with an available baseline; preserve named component/version boundaries, reuse previous findings and avoid attributing vague fixes from neighboring release notes.


## Current renderer, loading and menu checkpoint — 2026-11-21

The [eleven-audit checkpoint](evidence/validation/renderer-loading-menu-checkpoint.json) reviews `ea2fc48`: **22/22 static runs** reproduce11 committed evidence outputs; **12 protected artifacts and12 raw exports** retain prior hashes. Reproduce with `python3 analysis/scripts/check_renderer_loading_menu.py`. It covers all nine newly added/changed investigation scripts since the preceding checkpoint, plus the canonical SoftTri and Glide reference-pair audits reused by the follow-ups. The manifest records exact script/output hashes and selected shared dependencies. It does not qualify the entire repository, independently review semantics or execute target code.

|Area |Established in this checkpoint |Remaining boundary |
|---|---|---|
|[Wrapper packages](original-modern-renderer-loading.md#historical-nglide-labels-and-the150-same-version-binary-change) |nGlide120→130 label update and130/131 equality;140/150 same-version build differences; dgVoodoo2.51 metadata |Upstream authentication, WIP identity, wrapper code and minimize/restore behavior |
|[SoftTri](original-modern-software-reference-pair.md) |Canonical44-byte code map; historical mode-bound policy, allocation linkage and bounded debug parsing |Complete callback ABI, storage lifetimes and actual rendering |
|[Voodoo/Glide](original-modern-glide-reference-identity.md#complete-code-section-cluster-routing) |Existing18-envelope code map reused; historical131/140 fallback/register contracts and363-byte data localization added |Full data/alias/lifetime model, historical attribution and provider behavior |
|[Reference debug records](original-modern-original-reference-bundle.md#dx5-and-voodoo-debug-records-have-independent-export-anchors) |Three carriers,542 units/2,872 records and102 matched export anchors |Full types, nonexport mapping and final ABI |
|[DX6 modes](original-modern-display-modes.md#historical-dx6-depth-keys-and-sorting-change-at140) |131→140 sorted depth-aware keys and seed policy |Actual catalogue, activation and visible order |
|[Loading screenshots](original-modern-screenshots.md#loading-progress-screenshot-service-is-added-at140) |131→140 service addition, local gates and request clearing |Captured frame, input delivery and file success |
|[Controller/Connect](original-modern-common-menu-buttons.md#controller-and-connect-tab-layout-changes-at130) |120→130 authored positions/order;131→140 Reset6→7 |Parser defaults, loaded assets and rendered alignment |

Later texture/clock/DX6/OS/speech/loader findings are consolidated in the [newer checkpoint](#current-texture-clock-speech-and-loader-checkpoint--2026-11-21), rather than covered by these22 earlier runs. The catalog snapshot at the end of that follow-up sequence is47 vendor-only/56 bounded-static/187 partial; the full comparison remains incomplete.

## Current HUD, Glide, projection and affinity checkpoint — 2026-11-21

The [six-audit checkpoint](evidence/validation/hud-glide-projection-affinity-checkpoint.json) reviews `8706616`: **12/12 static runs** reproduce six committed evidence outputs; **12 protected artifacts and12 raw exports** match the prior checkpoint hashes. Reproduce with `python3 analysis/scripts/check_hud_glide_projection_affinity.py`. The Frame Size dependency is reproduced before the projection audit that records its hash. This is primary-agent repeatability and preservation, not independent semantic review, target execution or complete comparison acceptance.

|Area |Established |Remaining boundary |
|---|---|---|
|[HUD presets](original-modern-hud-layout.md#complete131-to140-preset-table-difference-inventory) |144 records compared;14 change; all four changed slots have identity evidence with stated qualifications |Actual active profiles, later writes and rendered placement |
|[Glide environment](original-modern-renderer-loading.md#historical131-to140-hardcoded-glide-environment-requests) |13 explicit131 requests/API adapter pinned; names absent140 |Computed/inherited/provider settings and exhaustive writer coverage |
|[nGlide/Glide3x packages](original-modern-renderer-loading.md#historical-nglide-special-driver-becomes-shared-voodoo-configuration) |Six settings migrate to ENV; shared140 driver copies and separate provider-free Glide3x directory |Installation/loading, provider resolution and real hardware acceptance |
|[Frame Size](original-modern-frame-setting.md#historical-constructor-changes-boolean-policy-to-two-independent-bits) |153→160 Boolean-to-bit constructor, two-to-four labels and config reset route |All lifecycle/override paths and live upgrade behaviour |
|[Projection](original-modern-projection.md#historical-fulldefault-origin-change-reaches-projection-centre) |Bounded camera-region partition and default origin-to-centre linkage; odd-dimension limit explicit |Capture lifetime, other contexts/orientation and actual horizon |
|[Affinity](original-modern-startup-policy.md#early110-affinity-policy-defaults-enabled) |110 configured/reader default1 and conditional mask1 request; final default0 |Exact100 introduction, API success and multicore reliability |

Earlier catalogue snapshot: **54 vendor-only,56 bounded-static,180 partial,0 unresolved-category entries**, across290 release-note bullets. These are labels, not distinct EXE changes or completion percentages. Zero in the last category does **not** mean no unknowns: vendor-only claims, partial mechanisms, provenance, projection capture, preset−5 meaning and runtime compatibility remain open. The full original/Modern comparison is incomplete.

The subsequent [140/150 dgVoodoo metadata audit](original-modern-renderer-loading.md#historical140-and150-dgvoodoo-wrappers-share-versions-but-differ-in-bytes) adds bounded support for MP150-037 and partial support for MP140-047; WIP16 identity remains unverified. It is outside these12 checkpoint runs.

The newer [nGlide label/build audit](original-modern-renderer-loading.md#historical-nglide-labels-and-the150-same-version-binary-change) adds partial support for MP140-046/MP150-036, preserving the source gGlide/nGlide naming discrepancy and unresolved fix semantics. It is also outside the checkpoint.

The newer [SoftTri mode-bound audit](original-modern-software-reference-pair.md#historical-softtri-fix-initializes-a-mode-bound-input) assigns all19 changed code-section bytes140→150 and adds partial support for MP150-038. Its [original-reference follow-up](original-modern-software-reference-pair.md#original-reference-softtri-already-has-the-local-system-info-query) adds partial support for MP100-066 and assigns all36 later150→final code-byte differences to state-result and lock/page-flip callback changes; callback ABI/lifetime and runtime effects remain open. It is outside the checkpoint; runtime symptom/capacity acceptance remain unverified.

The [SoftTri reference-debug audit](original-modern-software-reference-pair.md#reference-debug-records-recover-names-with34-export-anchors) extracts1,034 bounded records/173 units and corroborates all34 export addresses. Stock readelf fails on the unterminated abbreviation table; the custom parser preserves exact bytes and does not establish complete source/types or final ABI. This new audit is outside the checkpoint.

The new [DX5/Voodoo debug audit](original-modern-original-reference-bundle.md#dx5-and-voodoo-debug-records-have-independent-export-anchors) adds1,838 bounded records and68 independently matched exports, reusing the SoftTri parser without changing its existing output. Complete types, nonexport address mapping and final ABI remain unverified. It is outside the checkpoint.

The [new Voodoo2 reference pair](original-modern-voodoo-reference-pair.md) distinguishes the author reference from the earlier local candidate, matches34 exports and inventories3,307 changed code bytes. Its [historical about follow-up](original-modern-voodoo-reference-pair.md#historical131-to140-about-calls-retarget-without-changing-its-publications) adds partial support for MP140-037 with five changed call-operand bytes131→140; the existing [Glide analysis](original-modern-glide-reference-identity.md#complete-code-section-cluster-routing) already routes all3,307 changed code bytes into18 envelopes and documents selected local mechanisms. The historical follow-up adds fallback/register differences, not a new unassigned-code inventory. Full data/lifetime, historical attribution and runtime behavior remain pending. This new audit is outside the checkpoint.

The expanded [nGlide package audit](original-modern-renderer-loading.md#historical-nglide-labels-and-the150-same-version-binary-change) now verifies120→130 self-label1.04.2→1.04.3, with130/131 wrappers byte-identical. MP130-007 gains partial support for the package update; safe minimize/restore remains unverified. This extension is outside the checkpoint.

The [131→140 DX6 admission audit](original-modern-display-modes.md#historical-dx6-depth-keys-and-sorting-change-at140) adds partial support for MP140-038: dimension-only depth selection becomes sorted width/height/depth insertion; the prior16-bit seed prevents claiming wholly new16-bit support. Actual catalogue/activation and rendered behavior remain unverified. This new audit is outside the checkpoint.

The [loading screenshot follow-up](original-modern-screenshots.md#loading-progress-screenshot-service-is-added-at140) dates the queued service call to131→140, advancing MP140-058 to partial. Complete selected progress bodies and local gates are captured; current-frame identity and actual file output remain unverified. This new audit is outside the checkpoint.

The [Controller/Connect layout follow-up](original-modern-common-menu-buttons.md#controller-and-connect-tab-layout-changes-at130) adds partial support for MP130-006 from120/130 authored positions/order, and dates MP140-027's reset6→7 move131→140. Parser defaults, actual menu selection and rendered alignment remain unverified. This new asset audit is outside the checkpoint.

Next prioritize unassigned original/final changed mechanisms and remaining vendor claims with usable baselines. Reuse the completed HUD table inventory and bounded camera-region partition; their retained bodies need not be rechecked absent new evidence. Resolve runtime questions only within their stated test scope, without treating static reruns or package inclusion as game compatibility evidence.

## Earlier historical DX5, configuration, language and HUD checkpoint — 2026-11-21

The [four-audit checkpoint](evidence/validation/historical-dx5-config-language-hud-checkpoint.json) reviews `c15d718`: **8/8 static runs** reproduce four committed outputs; **12 protected artifacts and12 raw exports** match prior hashes. Reproduce with `python3 analysis/scripts/check_historical_dx5_config_language_hud.py`. This is primary-agent repeatability and preservation, not independent semantic review or runtime acceptance.

|Investigation |Established |Remaining boundary |
|---|---|---|
|[DX5 modes](original-modern-dx5-reference-pair.md#historical131-to140-mode-count-and-depth-key-changes) |131→140 guard30→100, exact raw-depth matching and clear1200→4000; callback retained final |Visible catalog, complete capacity ownership and display activation |
|[RemoteOnly](original-modern-language-table.md#remoteonly-reader-removal-is-dated131-to140) |131→140 shipped key/reader removed; caller supplies literal0 |Complete destination writers, shared overrides and vendor “useless” characterization |
|[Language package](original-modern-language-table.md#six-language-tables-enter-the140-package) |140 adds six fully partitioned1,933-entry tables absent from131 archive |Installed asset provenance, translation quality and runtime loading |
|[HUD presets/Name](original-modern-hud-layout.md#complete131-to140-preset-table-difference-inventory) |All144 table records compared:14 change; Name slot12 source/scaler/local loop/draw consumer linked |Slots3/6/15 identities at checkpoint time, later writes, mirror-relative placement and rendered output |

The subsequent [slot15 follow-up](original-modern-hud-layout.md#slot15-supplies-the-wrong-way-text-branch) links that slot to the140 English WRONG WAY entry and retained drawing branch. The [slot6 follow-up](original-modern-hud-layout.md#slot6-connects-to-the-tutorial-icon-quad-path) reuses the POS/editor evidence to connect its changed bounds to Tutorial Icon geometry. The [slot3 follow-up](original-modern-hud-layout.md#slot3-has-a-qualified-analog-tachometer-identity) adds a qualified Analog Tachometer association from reference ordinal names and historical border geometry. All four changed slots now have explicit identity evidence and limits. The [Glide environment follow-up](original-modern-renderer-loading.md#historical131-to140-hardcoded-glide-environment-requests) adds partial support for MP140-041. The [nGlide configuration migration](original-modern-renderer-loading.md#historical-nglide-special-driver-becomes-shared-voodoo-configuration) adds partial support for MP140-043 and its [separate Glide3x configuration](original-modern-renderer-loading.md#separate140-glide3x-configuration-omits-a-bundled-provider) for MP140-044. These expanded/new audit findings are newer than, and outside, these8 checkpoint runs.

The newer [153→160 projection restore audit](original-modern-projection.md#historical153-to160-restore-removes-integer-stores-not-float-centre-mapping) dates four removed legacy stores while retaining the float mapping/builder/consumer and the fixed-descriptor camera dispatch/handler already present in153. Its complete28,672-byte camera-region partition assigns all91 changed bytes to the restore and one removed empty stub/alignment block. Its [default-origin linkage](original-modern-projection.md#historical-fulldefault-origin-change-reaches-projection-centre) now gives MP160-003 partial static support: the scoped153 centre450 becomes160 midpoint540 at1920×1080. These additions remain outside the checkpoint; cache lifetime and universal rendered horizon remain unresolved.

Catalogue after the later follow-ups: **65 vendor-only,55 bounded-static,170 partial,0 unresolved** across290 release-note entries. These are evidence labels, not distinct EXE change counts or a completion percentage. The [early affinity audit](original-modern-startup-policy.md#early110-affinity-policy-defaults-enabled) advances the last historical-caveat entry to partial and is outside the checkpoint. Zero entries in the unresolved category does **not** mean zero unknowns:65 vendor-only claims and the limitations of170 partial entries remain. The full comparison is still incomplete. Reference inventories and address navigation locate differences; they do not establish all changed semantics. Projection capture lifetime, preset−5 meaning and runtime compatibility remain unresolved. Next prioritize new changed mechanisms and projection capture/orientation provenance, rather than repeating retained Name/scaler bodies or treating preset values as final pixels.

## Earlier DX8 admission and activation checkpoint — 2026-11-21

The [two-audit checkpoint](evidence/validation/dx8-admission-activation-checkpoint.json) reviews `033f062`: **4/4 static runs** reproduce two committed evidence outputs; **12 protected artifacts and12 raw exports** match the prior checkpoint hashes. Reproduce with `python3 analysis/scripts/check_dx8_admission_activation.py`. This is primary-agent repeatability and preservation, not independent semantic review or runtime acceptance.

| Investigation |Established |Remaining boundary |
|---|---|---|
|[DX8 catalog history](original-modern-display-modes.md#dx8-early-size-filter-and-later16-bit-admission) |110/140 builder identity;140→150 removes32-only admission; ordinary append/dedup and special-slot rules mapped |API output validity, complete consumers, historical ordering comparison and actual offered modes |
|[DX8 activation and adjustment](original-modern-display-modes.md#dx8-ancillary-helper-selects-depthstencil-with-a-success-without-write-edge) |Retained140/150 activation, depth override/fallback and depth/stencil search; conditional success-without-write edge recorded |Selector/flag lifetime, slot/index validity, complete errors/synchronization and rendered results |

At this DX8 checkpoint the catalogue had72 vendor-only/54 bounded-static/162 partial/2 unresolved entries. The four later historical investigations are covered by the current checkpoint above. Unchanged helper code is not another patch change; full selector/device lifetime and rendered outcomes remain outside these static checks.

## Earlier menu policy and keyboard checkpoint — 2026-11-21

The [five-audit checkpoint](evidence/validation/menu-policy-keyboard-checkpoint.json) reviews `92708c8`: **10/10 static runs** reproduce five committed outputs, with **12 protected artifacts and12 raw exports unchanged** against prior hashes. Reproduce with `python3 analysis/scripts/check_menu_policy_keyboard.py`. This is primary-agent repeatability and preservation, not independent semantic review or runtime acceptance.

| Investigation |Established |Remaining boundary |
|---|---|---|
|[HUD selector](original-modern-hud-settings-policy.md#hud-selector-policy-simplifies-at131-to140) |131→140 removes all-three-suppressed branch, always selects a local list and removes a legacy control |Prior/later flags, actual loading and visible availability |
|[Shared bounds](original-modern-common-menu-buttons.md#shared-list-bounds-change-padding-and-special-width-admission-in140) |All76 changed bytes in two envelopes assigned to padding and special-width predicate |All-list reachability, metrics and pixels |
|[Four-dialog layout](original-modern-common-menu-buttons.md#four-named-dialogs-have-authored-layout-edits-in140) |Nine matched controls change coordinates; Load maxvis8→10 |Final placement, language/font effects and input |
|[Key routing](original-modern-menu-input.md#tab-and-chat-bypass-routing-appears-at131-to140) |Tab/chat/arrow mechanisms dated; modifier flags contract retained |Callbacks, complete ABI and live focus/timing |
|[Entry eligibility/order](original-modern-menu-input.md#complete-registered-class-flag-census-finds-three-changes) |32-class census: three flags change; Load/IPX section reorders feed retained indexed code |Later eligibility, actual traversal and every-menu correctness |

At this checkpoint the subsequent DX8 investigations bring catalog counts to: **72 vendor-only,54 bounded-static,162 partial,2 unresolved** across290 release-note entries, following the [DX8 mode-admission audit](original-modern-display-modes.md#dx8-early-size-filter-and-later16-bit-admission). The DX8 audits are covered by the newer checkpoint above, not these10 menu runs. These are evidence classifications, not distinct EXE changes or completion percentages. The comparison remains incomplete: unresolved changed-region semantics, data/interface provenance, projection capture lifetime, preset−5 meaning and runtime compatibility still require work. The next investigations should address remaining mechanisms and dependencies rather than recheck the retained selector bodies or treat authored coordinates as final pixels. Existing executable, database, maintained C and raw export preservation is qualified by the checkpoint's exact file list.

## Earlier DX7, hint and shape checkpoint — 2026-11-21

The [five-audit checkpoint](evidence/validation/dx7-hint-shape-checkpoint.json) reviews `666a0c8`: **10/10 static runs** reproduce five committed evidence outputs, with **12 protected artifacts and12 raw exports unchanged** against the prior checkpoint. Reproduce with `python3 analysis/scripts/check_dx7_hint_shape.py`. This verifies primary-agent repeatability and preservation, not independent semantic review, runtime acceptance or the whole executable comparison.

| Investigation | Established | Remaining boundary |
|---|---|---|
|[DX7 inclusion](original-modern-renderer-loading.md#dx7-provider-is-added-to-the150-package) |150 adds a configured i386 provider under a directory absent from140 |Installed selection, source ancestry and device success |
|[Dithering](original-modern-renderer-loading.md#selector5-normalizes-its-payload-against-a-verified-zero) |Mode-export call chain; normal initializer path requests off; selector5 zero/nonzero requests off/on |Full branch admission, EXE overrides, state lifetime and pixels |
|[Connecting Esc hint](original-modern-network-port-menu.md#connecting-notice-gains-an-explicit-esc-hint-in140) |131→140 caller substitution adds two-line notice; helper retained final |Actual visibility and cancellation across network phases |
|[Field-of-View label](original-modern-frame-setting.md#140-field-of-view-wording-retains-the-earlier-setting-interface) |140 label binds the retained131 setting/storage/Off-On IDs |Old text baseline, exact rename and full camera consumers |
|[Map-marker shape](original-modern-hud-layout.md#game-side-pixel-format-corroborates-the-alpha-interpretation) |Retained draw chain; pinned backup/150 shape pixel difference; alpha interpretation corroborated |Backup provenance, loaded texture conversion/blend path and visible smoothing |

At that reviewed revision, the catalog had78 vendor-only/54 bounded-static/156 partial/2 unresolved entries. The checkpoint covers only its five named audits. The later menu investigations and current counts are listed above. The projection capture writer, preset−5 meaning, complete changed-region semantics and runtime compatibility remain unresolved; bounded checks do not establish whole-game equivalence.


## Earlier seven-audit checkpoint — 2026-11-21

The [seven-audit checkpoint](evidence/validation/renderer-menu-counter-followup-checkpoint.json) reviews `794ddde`: **14/14 static runs**, seven committed evidence outputs reproduced, **12 protected artifacts and12 raw exports unchanged** against prior hashes. Reproduce with `python3 analysis/scripts/check_renderer_menu_counter_followup.py`. This is primary-agent repeatability and preservation evidence, not independent semantic review, target execution or complete comparison acceptance.

| Follow-up | Established | Still open |
|---|---|---|
|[DX6 count consumers](original-modern-display-modes.md#dx6-extra-count-slot-reaches-inclusive-scans-but-can-fail-admission) |Inclusive scans; extra zero row rejected under N<100 insertion-only premises |N100, alias writes, direct/same-current switching and visible modes |
|[Vehicle effect bodies](original-modern-state14.md#selected-vehicle-effect-bodies-remain-unchanged) |Eight ranges,5,567 bytes identical across four EXEs |Changed inputs/state/callees and actual menu-light submission |
|[DX6 selector](original-modern-state14.md#dx6-provider-distinguishes-the-menu-gate-payloads) |Payload4 versus0 makes different raw-state requests in unchanged provider code |Device acceptance and taillight colour result |
|[DX6 quad flag](original-modern-state14.md#dx6-quad-attribute-copying-is-not-switched-by-payload4-versus0) |Both payloads clear flag; same vertex attribute copy under unchanged-flag premise |Other primitives, intervening writes and actual input values |
|[Setup history](original-modern-setup-website.md#early-credits-route-and140-options-replacement-are-present-in-assets) |110/131 Credits route;131→140 Options replacement, retained final |Exact100 introduction, historical activation and pixels |
|[Counter serialization](original-modern-screenshot-feedback.md#counter-belongs-to-the-saved-configuration-block) |Counter at config+16A0h inside20F0h copy extent; cleared1860h distinct |I/O success, save timing, concurrent snapshots and later resets |
|[Counter history](original-modern-screenshot-feedback.md#saved-counter-mechanism-appears-at131-to140-boundary) |131→140 counter relocation, atomic increment and filename-format change |Successful cross-launch preservation |

At this seven-audit checkpoint the catalog had83 vendor-only/53 bounded-static/152 partial/2 unresolved entries. Later findings and current counts are listed above. The taillight claim remains vendor-only; its remaining static question is the actual menu primitive/state lifetime, beyond the resolved selected code-identity and flag checks.


## Earlier snapshot — 2026-11-01

The [latest renderer/screenshot checkpoint](evidence/validation/renderer-screenshot-history-checkpoint.json) reviews`d57e760`:16/16 static reruns reproduce eight committed outputs, with12 protected artifacts and12 raw exports matching prior hashes. The [compact findings table](original-modern-differences.md#recent-renderer-and-screenshot-findings) records each mechanism and its limits. No independent semantic or runtime acceptance is implied.

The [latest HUD/menu/import checkpoint](evidence/validation/hud-menu-import-checkpoint.json) reviews`be46b2b`:16/16 static runs reproduce eight committed evidence files;12 protected artifacts and12 raw exports match prior hashes. See the [compact current findings table](original-modern-differences.md#recent-hud-menu-and-import-findings). This verifies repeatability/preservation, not independent semantics, runtime compatibility or all remaining differences.

The two recent HUD investigations now have concrete mechanisms. These bounded checks are complete at the stated static/package scope; runtime acceptance and the broader executable comparison remain open.

| Item | Established mechanism | Historical boundary | Remaining |
|---|---|---|---|
|[MP150-017 software list bevel](original-modern-hud-layout.md#historical-list-bevel-fix-retargets-the-software-branch) |Two-byte JNE retarget admits eight border quads while skipping the separate background |Verified1.4.0→1.5.0; retained final |Visible bevel, Speeds List identity and provider behaviour |
|[MP100-048 police editor widgets](original-modern-hud-settings-policy.md#police-only-widget-omission-is-authored-in-the-role-specific-menus) |Role-specific menu files omit police Tutorial Icon/Cone Stats items; racer items retained |Already present in retained1.1.0 package; exact1.0.0 introduction unverified |Authenticated retail asset comparison, installed loading and visible editor acceptance |

The earlier “unresolved” HUD checkpoint sections below preserve investigation history; they are superseded by these linked findings. The EXE bytes, saved Ghidra database, raw exports and maintained C were not changed by these investigations. No game or new instruction probe was run.

At this earlier snapshot, the [catalog](modern-patch-change-catalog.md) had **83 vendor-only,53 bounded-static,152 partial and2 unresolved** entries. These count release-note bullets, including assets/DLLs/history; they are not counts of distinct EXE changes or a completion percentage.

- **Complete:** the bounded reference inventories, address navigation and the individually qualified static investigations.
- **Recent verified increments:** historical renderer alignment/fog/mode mechanisms, language regression, rear-view presets, config path reversal and x87 release boundary, plus original/final update/reset/toggle paths. See the [compact findings table](original-modern-differences.md#recent-findings-at-a-glance) and [11-script static checkpoint](evidence/validation/historical-startup-checkpoint.json).
- **Startup increments consolidated:** [four later findings](original-modern-differences.md#startup-findings-added-after-the14-audit-checkpoint) cover version-header production, optional exception unmasking, demo overrides and the low-address/filter path. The [contiguous974-byte partition](original-modern-startup-policy.md#contiguous-accounting-of-the974-byte-nop-region) explicitly separates byte accounting from unresolved startup semantics. The [five-audit checkpoint](evidence/validation/startup-static-checkpoint.json) now reproduces these selected audits twice each and confirms all four preserved artifacts match the prior checkpoint; it is not runtime or independent review.
- **Historical mechanism checkpoint:** [lock-failure synchronization, localization/consumer remapping and Frame Size expansion/reset](original-modern-differences.md#recent-historical-mechanisms-at-a-glance) now have a [three-audit checkpoint](evidence/validation/historical-mechanisms-checkpoint.json): six successful runs with repeatable outputs and all four preserved artifacts matching the prior checkpoint. This is selected static evidence, not runtime or whole-goal completion.
- **Projection narrowed but unresolved:** type8 descriptor availability/conditional publication, local prepare/render/finalize order, retained399-byte handler and excluded33-byte viewport-flag helper. See the [projection report](original-modern-projection.md).
- **Still open:** the projection-source writer/capture lifetime and visible horizon outcome. The preset−5 field retains a verified layout/value with opaque physical meaning; a candidate offset match was a different record family. See the [preset report](original-modern-parameter-preset.md#shared-field-offset-is-not-a-consumer-identity).
- **Preset consumer search boundary:** the [paired pointer inventory](original-modern-parameter-preset.md#selected-pointer-reference-inventory-and-stopping-boundary) accounts for15 decoded literal references per EXE (14 loads/one store). It does not identify a direct−5 consumer; aliases, copied values and computed record addresses remain the required follow-up rather than another literal search.
- **Adjacent-table false lead resolved:** the [relocation follow-up](original-modern-parameter-preset.md#relocated-record-addresses-and-an-adjacent-unaligned-read) records37 original/seven Modern operands into the four-record region. Retained contact code reads a DWORD three bytes before an effect entry and keeps only its signed high byte; it does not establish a−5 consumer. C result reproduction and original access-footprint equivalence are explicitly separated.
- **Glide activation compared:** the [paired worker audit](original-modern-glide-reference-identity.md#selected-mode-activation-and-optional-extended-open) verifies retained export/callback bodies but changed mode resolution/extra-selector consumption, optional extended open, dimension fallback and depth-dependent state publication. This connects constructed mode records to activation; provider success, complete state effects and visible32-bit rendering remain unverified. Catalog labels unchanged.
- **Glide special-mode gate producer resolved:** the [hardware-name table comparison](original-modern-glide-reference-identity.md#hardware-name-classification-explains-the-special-resolution-gate) explains the changed gate and unmatched class0→4. Under ordinary initialized state, final admits Rush/Banshee/unmatched names where reference tests Rush class1; shared gating, byte-store/DWORD-read widths and state-lifetime limits remain explicit. No physical GPU/provider success or runtime behavior is inferred.
- **Glide depth has transfer consumers:** the [paired pixel-access audit](original-modern-glide-reference-identity.md#selected-depth-also-changes-lock-and-rectangle-transfer-contracts) verifies depth-dependent read/write stride, conditional write format and returned lock format; unlock is byte-identical. Complete bodies/bindings are retained. Pixel results, buffer validity, provider success and release attribution remain unverified; catalog labels unchanged.
- **Glide depth-clear chain resolved locally:** the [complete setstate comparison](original-modern-glide-reference-identity.md#depth-clear-value-survives-the-changed-state-setting-routes) accounts for all61 changed bytes in that function. Selector4 payload1/2 stop resetting the mode-selected depth-clear value toffffh; the clear caller forwards it as the provider's depth argument. Register, global-lifetime, provider and rendered-depth limits remain explicit; catalog labels unchanged.
- **Glide texture-table expansion compared:** [paired allocation/upload bodies](original-modern-glide-reference-identity.md#texture-tables-expand-from256-through2048) have only table-address differences; the referenced exponent, square-size and side-length tables extend from exponent8 to11. MP150-011 now has partial support for512/1024/2048; actual provider acceptance/rendering and historical introduction remain unverified.
- **Glide close/restore callers compared:** the [complete lifecycle caller comparison](original-modern-glide-reference-identity.md#context-close-no-longer-shuts-down-the-provider-directly) verifies removal of direct provider shutdown from context close and replacement of restore's direct shutdown/handle release with the latch helper. All13 restore differing bytes are locally accounted for. Early-return admission, unchecked provider results and transitive cleanup limits remain explicit; catalog labels unchanged.
- **Glide DirectDraw dependency qualified:** the [paired creation-helper comparison](original-modern-glide-reference-identity.md#directdraw-creation-moves-from-a-static-import-to-conditional-lookup) resolves its sole changed call operand and all three new lookup helpers. Final borrows/loads DDRAW.DLL, resolves DirectDrawCreate and rejects lookup failure through the retained caller. Missing static import does not mean no conditional dependency; provider identity, reference lifetime and actual creation remain unverified.
- **Glide suitability query compared:** the [complete is-export audit](original-modern-glide-reference-identity.md#suitability-query-retains-lexical-scoring-but-changes-provider-ordering) verifies retained lexical3.00 score computation/override helpers and changed capability-query initialization/cleanup ordering. Derived scores are not runtime observations; override/negative query returns, provider state and environment lifetime retain separate limits. Catalog labels unchanged.
- **Glide code-byte routing complete for the named pair:** the [18-cluster map](original-modern-glide-reference-identity.md#complete-code-section-cluster-routing) assigns all3307 differing code-section bytes once, including reused thunk/copy-helper space and padding. This is address accounting with documented local mechanisms, not complete data/import/lifetime semantics or runtime equivalence. Further EXE work need not wait for unrelated driver unknowns.
- **Original EXE mode-budget producer linked:** the [focused budget audit](original-modern-display-modes.md#original-budget-is-a-renderer-selection-constant) connects five fixed2/4/8 MiB stores to the removed eligibility gate and reconciles the border chapter's repurposed address. Ordinary gate examples are derived, not advertised modes or hardware-memory measurements. Alternate writers, callee preservation and actual allocations remain qualified; catalog labels unchanged.
- **Original border dimension linked:** the [publication audit](original-modern-border-geometry.md#original-dimension-source-is-mode-width-on-the-publication-path) traces mode width through the rectangle setter/eight-DWORD copy to007cdac8, contrasting Modern's reference-width input. Derived unrounded ratios are qualified by x87 rounding and later geometry; no universal visible-size ratio is claimed. Full writer/lifetime and quad/UV coverage remain open.
- **Material border-extent correction:** the [paired destination audit](original-modern-border-geometry.md#corrected-output-extent-eight-quads-not-nine) proves eight quads/400h bytes in both EXEs, not the previously claimed nine/480h. Derived slice-overlap claims are withdrawn throughout the detailed notes. Local/official Modern body bytes match. Saved Ghidra labels/comments remain stale and require a later saved/read-back correction; no database mutation here.
- **Border UV correspondence completed:** the [UV comparison](original-modern-border-geometry.md#all-eight-quads-retain-their-uv-bits) resolves all64 paired UV DWORDs and verifies identical bits through different MOV/x87 copy schedules. Eight Modern rectangle/UV regions are tabulated. Original coordinate arithmetic, atlas identity, filtering, machine-state and rendered equivalence remain separate; no probes executed.
- **Border operation schedule compared:** the [x87 schedule audit](original-modern-border-geometry.md#thickness-calculation-moves-out-of-the-builder) verifies178 versus44 builder x87 instructions and the separate four-instruction updater. Original calculates thickness12 times; Modern caches one updater result. This documents computation timing/FP-state dependencies, not measured speedup or coordinate/machine-state equivalence.
- **Recent bounded checkpoint reproduced:** the [four-audit checkpoint](evidence/validation/glide-border-static-checkpoint.json) pins reviewed revisionb272693, completed commands, script/output hashes and unchanged original/official/local EXE plus saved-database hashes. Primary reproduction passed; independent semantic review, runtime, whole-repository audit and Ghidra readback were not run. The main overview now surfaces both the verified mechanisms and the withdrawn border-overlap claim.
- **EXE mode-count cache/storage narrowed:** the [count/storage audit](original-modern-display-modes.md#count-caching-and-the-declared-storage-boundary) finds seven exact count-address operands and only a direct increment, distinguishing zero-count retries from populated-cache reuse. A conditional101st unique append clears a record ending20 bytes past the BSS size-field extent into the next declared section. Provider admission, aliases and actual mapping/write/fault behavior are not established; no runtime defect is claimed.
- **Original mode-accessor counterparts mapped:** the [paired race-init handoff](original-modern-display-modes.md#original-accessor-counterparts-and-the-race-init-handoff) establishes original004482f0 versus Modern00448374 through the same stored mode field/application consumers. Original eagerly rebuilds before its signed check; Modern uses unsigned cached selection. The existing field10 copy/direct-load mapping is reused. Both local counterpart gaps are closed; all-record/runtime equivalence remains unverified.
- **Mode sentinel ordering distinction documented:** the [static reselection example](original-modern-mode-selection.md#final-menu-row-and-sentinel-reselection-use-different-orderings) connects final-row sentinel storage to the existing area-distance search. Lexicographic final row1920×1080 can differ from selected larger-area1800×1440 under explicit hypothetical eligibility premises. This rules out an unconditional last-row shortcut, not an observed provider/UI mismatch or compatibility result.
- **Mode Z-buffer indication and label change linked:** the [field10 audit](original-modern-display-modes.md#field10-retains-the-z-buffer-indication-while-the-label-suffix-disappears) verifies the same signed driver+18h>=2 Boolean reaches named Z_BUFFER controls in both versions. Modern removes original's conditional `(z)` label append, retaining the indication; deduplication uses the retained candidate's value rather than an aggregate. Provider semantics, UI results and actual depth rendering remain unverified.
- **Glide texture release boundary verified:** the [historical pair](original-modern-glide-reference-identity.md#historical-texture-table-boundary140-to150) pins author-hosted1.4.0/1.5.0 archives and the same Glide member. Tables expand9→12 and both complete allocation/upload functions change only their table-address operands. MP150-011 retains partial status because runtime/provider support is untested; this specific release-boundary gap is now closed without claiming every beta/variant history.
- **Both historical Glide initialization pairs compared:** the [1.3.0→1.3.1 audit](original-modern-glide-reference-identity.md#historical-initialization-boundary130-to131) pins voodoo2.dll/nglide.dll and verifies direct call sites4 init/6 shutdown→1/1 behind a latch. Old module-handle caching already exists; mode-worker/context-close direct calls are removed. MP131-002 gains partial support; all transitive/runtime counts, arbitrary nesting and measured optimization remain unverified.
- **Historical biggest-mode persistence mechanism compared:** the [1.3.0→1.3.1 EXE audit](original-modern-mode-selection.md#historical131-uses-a-different-scalar-sentinel) verifies scalar width*height+depth maximum tracking,7fffffff request storage and preservation through separate active-mode publication. The nearest-score selector is retained. MP131-004 gains partial support; actual hotplug/persistence and general arithmetic domains remain unverified. This historical scalar is distinct from final packed dimensions.
- **Historical Desktop access-mask claim verified:** the [complete1.3.0→1.3.1 helper comparison](original-modern-registry.md#historical130-to131-access-mask-comparison) finds exactly two changed bytes in the requested access mask,KEY_ALL_ACCESS→KEY_READ. MP131-005 gains bounded static support. Query success, permission outcomes and screenshots remain untested; final1.6.1 removal stays distinct from this earlier change.
- **Historical DirectDrawLagFix source verified:** the [1.3.0→1.3.1 configuration audit](original-modern-renderer-loading.md#historical-directdrawlagfix-configuration-relocation-130-to-131) traces the executable-derived sibling INI to selected-driver `thrash.ini`, section NFS3→THRASH and caller default1→literal0. The57-byte optional compatibility tail is identical. MP131-001 gains bounded static support; overrides, API effects and performance remain untested.
- **Final compatibility rename qualified:** the [1.6.0→1.6.1 audit](original-modern-renderer-loading.md#historical-compatibility-rename-and-section-change-160-to-161) verifies `[THRASH] DirectDrawLagFix`→`[DDRAW] DisableMaxWindowedMode`, both default0, retaining request12 but changing raw assignment/Boolean dispatch into accumulated bit12/bit1 dispatch. MP161-008 remains partial for OS effects; the historical rename gap is closed.
- **Historical LightBeams reader established:** the [capability audit](original-modern-renderer-loading.md#historical-lightbeams-reader-and-capability-defaults) pins1.2.0 reader/INIs and a local consumer gate, and distinguishes type-derived defaults from1.3.1 literal0 fallbacks. Historical FogSupport normalizes to0/4, unlike final0/1. MP120-005 remains partial for rendered effects; exact later key removal and full consumers remain open.
- **Historical LightBeams consumer qualified:** the [three-version setter comparison](original-modern-state14.md#historical-lightbeams-key-controls-this-setters-admission) proves original/1.2.0 complete78-byte state14 setters differ only in the seven-byte gate. The old named key controls that gate; final retains a changed setter with different admission, scaling and reset policy. This does not establish beam-render identity or feature removal.
- **Another outside-body interval classified:** the [removed inline default block](original-modern-config-loading.md#removed-inline-defaults-at-00472566-replacement-initialization-matters) accounts for197 NOP-replaced bytes and the preceding call→jump. Original profile/audio defaults move into grouped Modern helpers, with stored values100→95,127→108 and selector2→0; capability-selected audio mode remains3/0. This is local static classification, not complete initializer or audible validation.
- **Removed default-time call identified:** original [language mapper00472250](original-modern-language-table.md#removed-defaults-time-language-mapper-00472250) maps six exact names into active language006fbb4c, leaving it unchanged on no match. Modern removes that call and publishes its INI-validated selector instead; this closes the preceding-call gap in the197-byte default-block classification.
- **Audio-default identities resolved:** [paired slider bindings](original-modern-config-loading.md#changed-audio-defaults-have-named-slider-bindings) identify menu/race music, sound effects and engine defaults100→95, speech127→108, with retained approximate1/127 initialization scale. These establish slider-input fractions, not acoustic loudness; live-value branches and callback rounding remain qualified.
- **Legacy DirectDraw adapter removal classified:** [the paired wrapper/adapter audit](original-modern-renderer-loading.md#removed-legacy-directdraw-enumeration-wrapper-and-register-adapter) accounts for all64 changed bytes in004ed904..004edbc0 plus the separate16-byte wrapper. Original adapts enumeration stack arguments to register callbacks and substitutes temporary zero-GUID storage; Modern NOP-fills these bodies. Original reachability remains unresolved, so no visible enumeration change is claimed.
- **Removed render lifecycle wrappers mapped:** the [three-wrapper audit](original-modern-heap-initialization.md#removed-wrappers-relocate-arena-lifetime-and-shorten-race-shutdown) accounts for79 changed outside-body bytes. Modern directly initializes/frees the arena in subsystem setup/teardown, and retains three old shutdown targets inline. Full lifetime ordering and effects of the other omitted calls remain separate; no arena-removal claim is made.
- **Omitted shutdown calls resolved:** [complete original targets](original-modern-heap-initialization.md#omitted-race-shutdown-targets-are-original-no-op-paths) prove all four calls omitted from the local seven-call wrapper are no-op paths, one nested. Three substantive calls retain their order. Original004dbbe0 is a stub, whereas Modern reuses that address for a real loader; full shutdown/machine-state equivalence is not claimed.
- **Replay description layout compared:** [complete callback/binding](original-modern-replay-description.md) explains90 outside-body changed bytes: removed localized heading, rowY+25→+20, retained ten-record loop and narrower signed-coordinate reads. This is menu layout, not replay-format/trajectory evidence; actual rendering and record lifetime remain unverified.
- **Help-builder removal classified:** [paired presentation strings and helper](original-modern-command-line.md#help-banner-error-text-and-dialog-title-change) explain72 outside-body NOP bytes, the embedded Modern banner, changed newline construction and fixed About title. Initial copy count1024 does not establish bounds for later formatted appends; runtime dialogs remain untested.
- **Complete race-frame byte partition established:** [official-final comparison](og-modern-x87-precision.md#complete-race-frame-partition-against-the-official-final-executable) confines changes in the414-byte original frame body to three regions: x87 entry, same-target wrapper bypass and x87 exit/epilogue. Two removed call targets are no-op stubs;76 outside-body NOP bytes include an operand fragment and separate stub/alignment. Full-frame/runtime equivalence remains unverified.
- **Mouse registration tail explained:** [ten retained message/handler pairs](original-modern-window-handling.md#mouse-registrations-move-callback-bodies-stay-identical) move earlier; both complete87/84-byte handlers are identical. The61 changed outside-body bytes do not remove mouse support. Forwarded coordinates retain unsigned16-bit extraction; downstream/runtime mouse behaviour remains unverified.
- **Viewport tail contains new adapters:** [two complete helpers](original-modern-viewport-geometry.md#new-record-to-setup-adapters-occupy-the-original-initializer-tail) explain42 outside-body changed bytes and call234-byte-identical shared setup. Their record/register contract differs from the publishing setter; outer-wrapper reachability and full state/render effects remain unresolved.
- **Race-loading music wrapper removal classified:** [complete original wrapper/caller](original-modern-music-selection.md#removed-race-loading-music-wrapper-and-adjacent-shutdown-no-op) explains64 outside-body changed bytes, including a separate shutdown no-op. Original006fbb54-gated loading/poll wrapper is replaced locally by direct Modern selection/poll placement; full gate semantics and audible results remain unresolved.
- **Media/audio gate producer identified:** [config-tail evidence](original-modern-config-loading.md#mediaaudio-gate-snapshots-the-original-remote-prefix-classification) connects original006fbb54 to the six-byte remote-prefix classifier and shows Modern explicitly writes0. This is a classification snapshot, not a proven multiplayer/audio-disable mode or immutable field; source ownership and later writes remain unresolved.
- **Original gate source writer resolved:** the [install.win record loop](original-modern-language-table.md#original-installation-reader-also-produces-the-remote-prefix-source) places the second nonempty processed string at007a26b4, connecting file records→remote-prefix classifier→006fbb54. The cleared40-slot extent is not an enforced record bound; actual contents, read failures, long lines and other writers remain unverified.
- **Recent14-audit checkpoint passed:** [recorded commands, script/output hashes and preserved artifact hashes](evidence/validation/recent-static-increments-checkpoint.json) reproduce the latest bounded findings. The [main overview](original-modern-differences.md#further-code-level-findings-and-reproducibility-checkpoint) now summarizes them. This is primary static reproducibility, not independent review, runtime/CI or whole-audit acceptance.
- **Race-loop screenshot latch connected:** [exact signed gates and key-byte getter](original-modern-screenshots.md#race-loop-key-latch-becomes-render-then-queued-capture) explain51 outside-body changed bytes. Original latch selects synchronous capture instead of the local render arm; Modern renders then checks queued capture. The loop increment/back-edge move earlier; runtime pixel/timing/output results remain unverified.
- **Four existing investigations connected to the outside index:** [machine-checked routes](original-modern-outside-function-index.md#mechanism-triage-from-existing-comparisons) now cover the34-pair renderer export table, original camera-dispatch tail, old ordered defaults tail and window-thread restoration tail. Exact intervals, changed counts and report hashes are retained. This closes navigation/byte-partition gaps without claiming new independent semantic or runtime verification.
- **DX5 mode-field/fog-default link qualified:** [callback quotient to EXE signed threshold](original-modern-resolution-defaults.md#dx5-producer-qualifies-the-selected-mode-fog-default) proves selector1 iffQ>=3 for a valid selected record from that callback. Separate DX5 fog rejection still governs support. The same audit classifies99 removed original table bytes, not code; other drivers, records and visuals remain unverified.
- **DX5 quotient budget producer identified:** [paired unchanged query/dataflow](original-modern-dx5-reference-pair.md#mode-budget-producer-retained-query-and-2-mib-fallback) proves60010eb4 receives2 MiB on query failure or total-output plus pitch×height on success. IID/vtable match IDirectDraw2; surface-field validity and runtime memory/allocation remain unverified. This is a retained heuristic, not a Modern-only query.
- **Complete HSV-wheel keyboard comparison added:** [831-byte callback and binding](original-modern-colour-control.md#complete-wheel-keyboard-callback-endpoint-writes-and-feedback-change) explain369 differences plus11 adjacent old mouse-tail/alignment bytes. Modern skips endpoint stores, adds adjustment feedback and changes action sound ordering; ordinary0..255 values agree while out-of-range results differ. Actual UI/audio and component invariants remain unverified.
- **Separate broader backlog:** remaining vendor claims, historical driver/release comparisons and original/Modern runtime compatibility. There are more than two questions in the complete backlog.

The [five-mechanism checkpoint](evidence/validation/five-static-mechanisms-checkpoint.json) reproduces DX7 viewport, comma parser, vehicle detail, mode capacity and LOGO2 audits twice each (10/10 pass). All five output hashes match pre-run evidence;12 protected files remain unchanged and12 raw exports match retained manifests. The [compact table](original-modern-differences.md#five-further-mechanisms-and-verification-checkpoint) keeps those mechanisms and remaining qualifications together. This is selected primary-agent static verification, not independent review, runtime testing, Ghidra reopening or whole-goal completion.

The checkpoint narratives below describe their pinned increments. Their older counts and “latest” wording are historical, not competing current totals. The broad objective remains incomplete; no new game execution or reconstruction is implied by this snapshot.

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

## Historical reference-routing pass

That reference-routing checkpoint added the [small-entry follow-up](original-modern-small-entry-followup.md), including vehicle-loading progress data and seven previously unreferenced entries, and [quad-set draw arguments](original-modern-viewport-geometry.md#quad-set-draw-arguments-six-changed-constants). All361 changed saved-function entries now have chapter address references. This closes the missing-reference queue, not the semantic investigation. Earlier [partial geometry context tracing](original-modern-geometry-color-admission.md#current-context-trace-and-stopping-point) remains unresolved on its stated terms.

No additional game execution, instruction probes, toolchain work, C reconstruction or Ghidra changes are part of this closeout. Executable bytes and existing reconstruction/raw exports are preserved.

## Acceptance checklist at the reference-inventory checkpoint

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

The catalog currently labels136 entries vendor-only,45 bounded static,107 partial and2 unresolved. New qualified links include Full view-distance thresholds and mirror record selection, Night/two-player conditions, gear endpoint anchoring/smaller-scale fallback, and the vertical-angle calculation. The HUD base-scale coefficient also changes independently of the dimension-read relocation. These are documented mechanisms, not runtime acceptance or a whole-game completion percentage.

| Priority | Remaining question | Existing evidence / next required action | Evidence boundary |
|---:|---|---|---|
| 1 | MP160-003 horizon/camera shift | [Projection report](original-modern-projection.md) now establishes conditional CCM-to-type8 publication, preparation/render/finalizer ordering and bounded non-producer searches; recover computed/bulk source writes or capture lifetime, then qualify camera orientation/output | Executable inspection can advance this; visible horizon still needs rendering evidence |
| 2 | MP160-006 remaining output coverage | [Map-marker extent-to-quad chain](original-modern-map-marker-scaling.md) now established; qualify other marker styles, lifecycle and actual rendered size separately | Static source/consumer gap closed; visual scope remains unverified |
| 3 | MP161-002 DX8 fog; MP161-001 visual acceptance | [Historical DX6/DX7/DX8 coordinate corrections](original-modern-renderer-texel-alignment.md#dx7-and-dx8-historical-instruction-traces) are now traced; reuse the traced specular-alpha/state contracts and retained table expansion; reuse selected exported fog routes; reuse the traced capability guard and notifier; qualify remaining reset/callback lifecycle and other submission paths | Alignment mechanisms are verified statically; fog semantics and rendered outcomes require separate evidence |
| 4 | Historical rear-view consequences and remaining release claims | [Historical preset comparison](original-modern-track-detail.md#historical-v152-improvement-second-record-source-selection) now isolates the Medium-detail value change; qualify visual/performance effects separately, and select other claims from the catalog | MP153-008 structural fix verified; MP152-001 mechanism partially supported, not rendered acceptance |
| 5 | Original/Modern rendered, replay and multiplayer consequences | Compare separately identified inputs/builds within an explicitly stated runtime scope | Existing single-build captures and static derivations are not cross-version equivalence evidence |

Continue with a concrete missing producer/consumer link from this queue. Do not repeat already resolved preset arithmetic, expand into unrelated scratchpad work, or treat historical/runtime requirements as blockers to all remaining static inspection. The bounded reference inventory remains complete; the broader investigation remains active and incomplete.

## Projection and map review checkpoint

The [checkpoint record](evidence/validation/projection-map-review-checkpoint.json) binds nine successful root audit reruns to the reviewed revision and records two Luna consistency reviews. The reviewers checked retained documentation/models and reported no concrete errors; they did not independently re-extract binaries or run the audits. The primary agent performed the fresh hash-pinned static reruns. The saved Ghidra database and local analysis executable still match their prior hashes. The projection introduction now lists the companion audits needed for its expanded sections.

- **Complete within static scope:** original/Modern rectangle examples; temporary weather versus ordinary projection selection; the three changed chooser calls; complete literal-centre writer inventory; retained centre producer/consumer; non-file-backed conditional source classification; map-marker extent-to-quad link; role-profile defaults into map zoom.
- **Still unresolved:** conditional type8 source producer/admission and ordering, computed aliases, camera orientation/final horizon, active map/profile state, all marker styles and actual rendered output. Historical claims need the appropriate intermediate pairs; runtime compatibility remains separate.

The map-point mechanism gap in MP160-006 and field/consumer gap in MP140-073 are closed at the documented static boundary. The whole vendor claims are still partial. MP160-003 was unresolved at this earlier checkpoint; the current historical origin linkage above advances it to partial. The broader original/Modern investigation is not marked complete, and this checkpoint does not authorize or imply a rebuilt game.

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

Concrete added findings are indexed in the main report: original save flag versus Modern header refresh; original zero-version prefix and conditional configuration reset; View Angle label/storage/default linkage; Modern loading admission, exact-bit return and two distinct retry levels; and D3D/EAX-to-Stereo fallback using retained driver capability dispatch. At that checkpoint the catalog had152 vendor-only,39 bounded static,96 partial and3 unresolved entries; labels are evidence classifications, not completion percentages.

Remaining questions include full original default/save lifecycle, callback result/register contracts, real save migration, timing/audio/rendered outcomes and historical introduction. These findings do not resolve unrelated projection type8 sources, renderer-DLL history or every vendor claim. The broad comparison remains active and incomplete. Continue with another concrete unqualified changed mechanism rather than repeatedly restating this completed static increment.

## Dashboard versus gear overlay linkage

The [overlay follow-up](original-modern-view-overlay.md#primary-tile-binding-supports-a-bounded-cabin-widening-association) separates gear-labelled optional records from dash.qfs primary tiles and links the latter to the expanded rectangle. MP160-008 now has partial static support. The correction gives0..3 extent units at standard widths640..2560, not a universal cap; actual pixel coverage/seams and historical introduction remain unresolved.

## Renderer lifetime and dashboard checkpoint

The [checkpoint record](evidence/validation/renderer-dashboard-checkpoint.json) records five fresh successful static audits, exact script hashes/commands and unchanged original, official Modern, local EXE and saved-database identities. It is primary-agent reproduction, not a new independent review. The main comparison now summarizes callback registration, cleanup/cache boundaries, official DX7 descriptor ownership/environment effects, gear-versus-dashboard resource bindings and retained tile construction.

The bounded increment establishes those mechanisms and leaves actual cleanup failure/reachability, driver callback conformance, post-unload consumer admission, rasterized coverage and seam removal unverified. Final DX7 component inspection is not an authenticated older-DLL comparison. At that checkpoint the catalog had151 vendor-only,39 bounded static,97 partial and3 unresolved labels; the whole audit remains incomplete. Historical release pairs and runtime behavior retain their separate evidence requirements.

## DX7 sorted-list claim linkage

MP161-004 now has partial evidence for its bundled sorted-list subclaim: unsigned width/height/depth binary insertion, full duplicate-record replacement and new-key capacity99. The [driver report](original-modern-dx7-mode-admission.md#sorted-list-subclaim-in-mp161-004) distinguishes this from the still-unverified unsupported640×480×16 policy and release-specific history. Labels at that checkpoint:150 vendor-only,39 bounded static,98 partial,3 unresolved.

## Resumed projection boundary review

The complete399-byte type8 handler `00425060..004251ef` is now asserted identical across the pinned EXEs. This narrows local change attribution to the already documented finalizer and surrounding dependencies; unchanged handler instructions do not prove identical context, x87 state or callees. The priority queue has been corrected to reuse the conditional selection and local stage-order evidence rather than investigate those again. Projection source capture/lifetime remains unresolved; no runtime, export, compilation or Ghidra changes were made.

## Historical renderer acquisition gap removed for v1.6.0/1.6.1

A fresh official-directory lookup located the author-hosted versioned archives. The [baseline audit](evidence/audits/official-160-161-baseline.json) verified v1.6.0/v1.6.1 internal banners and pinned both EXEs plus DX6/DX7/DX8 members; all four member pairs differ. This removes the missing-artifact prerequisite for that release pair, not the remaining function-level comparison. No DLL or EXE was executed; current analysis targets and saved database were preserved. Other historical pairs remain separate acquisition/qualification work.

## Historical DX7 mode-policy mechanisms verified

The [paired audit](evidence/audits/dx7-160-161-mode-policy.json) now verifies the old fixed640×480×16 seed and arrival-order callback versus1.6.1 removal and sorted insertion. MP161-004 moves from partial to bounded-static support. This closes the two local code mechanisms, not actual display support or every later override. Current catalog labels are150 vendor-only,40 bounded static,97 partial and3 unresolved. The broad original/Modern goal remains incomplete.

## DX6 texel-alignment mechanism identified

The [historical DX6 audit](original-modern-renderer-texel-alignment.md) verifies eight PUSH1c4h-to-CALL patches and a complete55-byte adapter subtracting0.5 from vertex X/Y in place before restoring the original pushed-argument shape. MP161-001 now has partial support for DX6; DX7/DX8 and physical raster outcomes remain unverified. Current labels:149 vendor-only,40 bounded static,98 partial,3 unresolved. No driver execution or target modification.

## Three-driver alignment mechanism closed at static scope

[Historical DX7/DX8 traces](original-modern-renderer-texel-alignment.md#dx7-and-dx8-historical-instruction-traces) now supplement DX6: separate half-unit X/Y adjustment helpers and3/15 direct-call boundaries are pinned. MP161-001 moves to bounded-static support across all three named drivers. Rendered sharpness/all drawing routes remain untested; DX8 fog remains a separate claim. Current labels:149 vendor-only,41 bounded static,97 partial,3 unresolved.

## DX8 fog representation checkpoint

The [paired helper inspection](original-modern-renderer-texel-alignment.md#dx8-fog-related-vertex-policy-partial-historical-evidence) establishes the newer mode0x10 table-derived DWORD store at vertex+0x14, default inverse-byte table and local state writers. The older helper already has depth/table/colour-blending logic; absence of fog in v1.6.0 is not claimed. MP161-002 now has partial support, with API format/state contracts and visible fog explicitly outstanding. Current labels:148 vendor-only,41 bounded static,98 partial,3 unresolved.

## DX8 API contract checkpoint

The [API follow-up](original-modern-renderer-texel-alignment.md#dx8-api-and-vertex-format-follow-up) traces the imported factory, device-output slot, render-state wrapper and two FVF layouts to the new specular-alpha store. Header snapshots and instruction spans are pinned in the audit. The table setter is a transformation, not a direct copy. Full dispatch/table semantics and visible fog remain unverified; MP161-002 stays partial. No target execution or executable/database edits.

## Retained DX8 table expansion checkpoint

The [complete208-byte table routine](original-modern-renderer-texel-alignment.md#retained-table-expansion-and-changed-selection) and coefficients are verified identical across1.6.0/1.6.1. Its64-to256 dataflow and imported _ftol boundary are documented; local callers change selection from the old colour-blending route to the new fog-channel route. Complete dispatch/default-state admission, exceptional CRT behavior and actual rendering remain outside this finding. MP161-002 remains partial; catalog counts unchanged.

## DX8 exported fog-state routing checkpoint

The [selected dispatch audit](original-modern-renderer-texel-alignment.md#exported-state-dispatch-selected-fog-routes) resolves the public setstate selectors, aliases and changed parameter conversions in both historical DLLs. New mode/table paths have a checked guard; former0x4b/0x4c routes now return0. Accepted cases discard device-state results, so local success is not runtime acceptance. Guard/default-state lifecycle, notification effects, other drawing routes and visible fog remain open. MP161-002 remains partial; counts unchanged.

## DX8 local investigation stopping point

The [guard/default/notifier follow-up](original-modern-renderer-texel-alignment.md#guard-provenance-initial-storage-and-stopping-point) establishes capability-derived gating, device-quirk zero overrides, file-backed mode2 versus virtual-tail enable storage, and retained notification/cache logic. The new rejection polarity is preserved as observed. Local producer questions are now answered; remaining reset/callback lifecycle, other submission routes, CRT edge cases and rendered acceptance are explicit broader requirements. Continue to another substantive difference rather than repeating this chain.

## Historical language regression resolved statically

The [four-release audit](original-modern-language-table.md#historical-fallback-regression-v150-through-v153) pins author-hosted1.5.0/1.5.1/1.5.2/1.5.3 EXEs and fallback data. The admitted range exceeds the embedded offset table by four entries in1.5.1/1.5.2; predecessor and successor fit their ranges. The newer table supplies the missing camera/rear-view labels. MP153-008 moves from unresolved to bounded static; actual consumer failures and localized rendering remain untested. Current counts:148 vendor-only,42 bounded static,98 partial,2 unresolved.

## Historical Rear View Detail mechanism

The [1.5.1/1.5.2 audit](original-modern-track-detail.md#historical-v152-improvement-second-record-source-selection) verifies an unchanged classifier/builder/table and a changed second-record preset policy. Four of48 finite derived cases differ, all Medium detail with Full/Far view-distance and mode!=1; this is not a runtime percentage. MP152-001 moves from vendor-only to partial. Current counts:147 vendor-only,42 bounded static,99 partial,2 unresolved. Rendered improvement/performance and release-wide coverage remain untested.

## Player-specification timestamp deletion bypass

The [expanded config audit](original-modern-config-loading.md#executable-update-deletion-config-and-both-player-specifications) now binds player1/player2 path selection to the removed timestamp/DeleteFileA route, complementing the established config gate. The player filename builder independently switches prefixes and skips carspecs; its root provenance remains unqualified. MP100-045 moves to bounded static support; config relocation and driver-change reset claims remain separate. Current counts:146 vendor-only,43 bounded static,99 partial,2 unresolved. No settings files or target instructions were executed.

## Config path reversal now version-bound

The [1.1.0/1.2.0 prefix comparison](original-modern-startup-paths.md#config-path-history-root-relative-then-restored) confirms root-relative config defaults becoming FeData/Config with the same formatting consumers. It also ties the final player-spec prefix to the final22-slot layout, distinct from the early24-slot meanings. MP120-013 gains bounded static support; MP100-044 gains partial historical support, without asserting1.0.0 introduction or observed migration. Current counts:144 vendor-only,44 bounded static,100 partial,2 unresolved.

## Historical x87 release attribution

The [1.5.3/1.6.0 pair](og-modern-x87-precision.md#historical-release-boundary-v153-to-v160) verifies centralized single/saved-CW helpers in1.5.3, their removal and selected FINIT boundaries in1.6.0. The application loop is at4a3b4a in1.6.0, distinct from final1.6.1. MP160-012 gains historical support within its existing bounded static label; all-thread/DLL precision and runtime compatibility remain unverified. Catalog counts unchanged.

## Renderer-type reset route narrowed

The [loader-to-startup comparison](original-modern-config-loading.md#renderer-type-mismatch-no-longer-requests-the-original-startup-reset) connects original saved/current type mismatch to a conditional graphics-default call and verifies Modern bypasses that route. The comparison is type-mask based, not all DLL/device identity changes; the original flag address is repurposed for WindowedMode in Modern. MP100-046 gains partial support. Current counts:143 vendor-only,44 bounded static,101 partial,2 unresolved; actual settings survival remains untested.

## Keyboard-toggle startup operation identified

The [window helper follow-up](original-modern-window-geometry.md#removed-startup-reset-of-keyboard-toggles) binds original creation indices0/1/2 to Caps/Num/Scroll Lock and a conditional keybd_event pair, then verifies the matched Modern creator omits the calls. Retained imports/thunk do not establish startup reachability. MP100-038 gains bounded static support; OS/Wine/device effects and alternate callers remain untested. Current counts:142 vendor-only,45 bounded static,101 partial,2 unresolved.

## Historical/startup reproducibility checkpoint

At reviewed head7c36f96,11 selected static audit scripts passed, and original/official/local EXE plus saved Ghidra database hashes matched their recorded identities. [The checkpoint](evidence/validation/historical-startup-checkpoint.json) records commands, outputs, identities and limits. Stale overview text about untraced DX7/DX8 alignment and vendor-only historical rear-view work was corrected. This self-check does not independently validate every semantic interpretation or qualify runtime behaviour. The full difference investigation remains active and incomplete.

## Historical abort-presentation routing

The [1.5.3/1.6.0 comparison](original-modern-pending-overlay.md#historical-v160-change-defer-presentation-until-loading-exit) verifies overlay drawing moves from the input poller to the terminal abort branch, alongside the explicit200ms alertable wait. Overlay and wait adapter bodies are retained. MP160-011 stays partial: neither the older500ms claim nor exact visible duration is established. Counts unchanged; no target/API/timing execution.

## Two local evidence boundaries tightened

The historical abort audit now verifies the supplied-original poll helper matches1.5.3 and contains no direct fixed wait; the claimed prior500ms duration remains a transitive/runtime question, with the required evidence recorded. Separately, complete original helper472fc0 saves/restores EDX, closing the register dependency for the conditional reset-flag clear. No broad runtime or whole-game completion claim follows; catalog labels/counts unchanged.

## Camera dispatch wrapper follow-up

The [paired wrapper audit](original-modern-projection.md#camera-dispatch-wrapper-changes-around-the-retained-type8-handler) resolves24 routes:22 preserve handler targets, while15/22 use a RET stub instead of direct return. Modern changes register preservation/EDX input and adds a conditional post-handler call on fixed descriptor661220. Type8 body equality therefore does not establish wrapper equivalence. Missing projection capture/lifetime and rendered horizon remain unresolved; MP160-003 status and counts unchanged.

## Fixed-descriptor handler resolved locally

The [complete handler/callee comparison](original-modern-projection.md#fixed-descriptor-handler-changed-control-input-and-bounded-write-set) establishes a new EDX control input, exact descriptor position/orientation destinations and retained vector/orientation helpers. For the fixed661220 call, the write set is disjoint from the projection restore-source cells; this specific branch is excluded as their capture writer. Generic aliases, other handlers, actual capture lifetime and rendered horizon remain unresolved. No catalog status/count change or target execution.

## Name/IP edit-state claim now bound to constructors

The [dialog follow-up](original-modern-dialog-input.md#replace-first-policy-bound-to-ip-and-player-name-dialogs) verifies unchanged IP/Player One/Two constructor prefixes, their localized labels and initial-text pointers, then links them through shared prefill and replace-first state to insertion. MP140-035 gains partial support; actual typing, all filters/bounds and release introduction remain unverified. Current counts:141 vendor-only,45 bounded static,102 partial,2 unresolved. No target/input execution.

## Edit prefill and filter boundary narrowed

The [filter/copy audit](original-modern-dialog-input.md#retained-filter1-and-bounded-prefill-contract) verifies retained helper bodies and all six file-backed language rows for filter1. It establishes byte20h..ffh admission, full-string validation before truncation, bounded-copy padding behaviour and termination from prior zero-fill/max255. Full-buffer behaviour differs through the existing replace flag, not a new append routine. MP140-035 remains partial; active-language/callback lifetimes, malformed input and live typing remain unverified. Counts unchanged.

## Car-class output identity established

The [class-text chain](original-modern-car-alias.md#alias-expansion-reaches-localized-car-class-text) resolves the expanded car2/carShowcase renderer branch through model+388h, localized IDs190..192 and text submission. Ordinary class0..2 gives Class A/B/C in the pinned English asset. Registry pointer/index validity and actual UI output remain unverified. MP140-021 gains partial support. Current counts:140 vendor-only,45 bounded static,103 partial,2 unresolved.

## Original-reference bundle acquired with explicit variant boundary

The [98-file inventory](original-modern-original-reference-bundle.md) pins an author-hosted reference bundle:80 menus, six HUD-position files, six PE files and six others. Its EXE differs from the established supplied original by exactly one byte at4b639b; it was not substituted. Candidate original-side renderers are now available for explicit pairing, while pristine-retail provenance remains unverified. No semantic catalog claim is promoted from artifact identity alone; counts unchanged.

## DX5 reference/final correspondence and byte map

The [DX5 comparison](original-modern-dx5-reference-pair.md) verifies34 identical export entries,710 differing code-section bytes in25 intervals, equal file-backed import/data sections, and the two-byte immediate change publishing descriptor+40h. The complete284-byte selection span is retained. BSS extent grows1000h under the nonzero raw-size-field interpretation; file-backed zeros and runtime mapping are not inferred. Table initialization/consumers and other intervals remain next actions; no catalog claim/count changes or target execution.

## DX5 callback policy recovered at a bounded static scope

The [callback comparison](original-modern-dx5-reference-pair.md#mode-callback-and-selected-initialization-paths) verifies the added unsigned640/480 dimension filter, larger table requests, changed fixed seeds, raw-key linear scan and quotient cap. Recognized32-bit inputs remain conditionally admissible, including at640×480; the fixed16-bit seed does not establish the release note’s absolute always claim. MP100-062/063/064 gain partial evidence; actual mode selection/rendering and historical introduction remain unverified. Catalog totals:137 vendor-only,45 bounded static,106 partial,2 unresolved. No DLL or target execution.

## DX5 numeric state15h removal

The [state-handler comparison](original-modern-dx5-reference-pair.md#removed-numeric-state-selector15h-route) checks the complete2425-byte export body: only two changed intervals remove selector15h table/control handling and replace it with EAX=0 rejection. Generator, expander and numeric-device-state adapter remain byte-identical. Reference success did not forward device acceptance. API naming, caller use and visual effects remain unverified; no blanket fog-removal or release-note completion claim. Catalog counts unchanged.

## DX5 lock callback and complete changed-code localization

The [lock comparison](original-modern-dx5-reference-pair.md#lock-failure-now-notifies-the-callback) verifies a new callback0 notification on nonzero surface-call status, while the success suffix and unlock body remain identical. The [accounting table](original-modern-dx5-reference-pair.md#changed-code-accounting-and-stopping-boundary) assigns all710 differing code-section bytes to six reviewed clusters with no omissions/overlap. This is bounded code localization, not complete DLL consequences or full EXE coverage. Non-code PE differences, callback targets and runtime acceptance remain open; catalog counts unchanged.

## Reference menu/HUD inventory and coordinate comparison

The [asset index](original-modern-reference-assets-index.md) accounts for86 reference and52 final menu/POS members:52 paired menus differ beyond line endings;28 menus and six POS files are reference-only in this archive scope. Each POS parses into138 matching-name/order records; comparing23 rectangles per profile against Modern embedded data finds91–95 changed rectangles per variant. This is numerical/packaging evidence, not pristine-retail authentication, file-deletion proof, target parser execution or rendered layout. Full paired hashes, line counts and changed HUD names are retained. Catalog counts unchanged.

## Menu property inventory and prior-evidence reuse

The [asset follow-up](original-modern-reference-assets-index.md#property-changes-and-reference-identity) verifies all80 local backup menu hashes match the author-reference bundle, and crosschecks52 paired identities in the existing visible-count manifest without rerunning its binary audit. All52 menu pairs still differ after blank/comment/whitespace normalization; repeated property occurrences are retained in per-file multiset deltas. Frequent omissions include998 each of postonly/mainonly and993 each of the demo keys. Omitted defaults, control identity/moves and actual effects are not inferred. Existing count/control research is linked rather than duplicated; pristine-retail authenticity remains open. Catalog counts unchanged.

## Postgame Options admission/return linkage

The [expanded Options audit](original-modern-options-postgame.md#postgame-to-options-transition-and-return-witnesses) verifies both author-reference/final Postgame button records and the retained action5 transition, complete descriptor initializer and history push/restore bodies. The initializer calls runtime descriptor+08h before the generic mainonly filter; nested selection returns to the descriptor loop without directly restarting the outer context-name prefix. This closes the authored-target/local-linkage gap, not callback-wide flag preservation, arbitrary history depth, all return inputs or runtime visibility. Existing MP140-019/020 remain partial; counts unchanged.

## DX5 rejection linked to EXE fog-support admission

The [cross-component audit](original-modern-dx5-reference-pair.md#exe-fog-trial-connects-to-the-rejected-dx5-selector) pins the final DX5 INI and EXE reader/trial/recompute spans. Decimal21 equals rejected selector15h: on the common trial route, final DX5 returns0 and clears a nonzero support flag; zero support forces zero admission in the captured recomputation. The bundled INI has no opt-in key. Actual INI/DLL selection, skipped initialization routes, later writes and visual output remain unverified. Catalog counts unchanged; no target execution.

## Software-renderer raw-depth admission

The [paired software audit](original-modern-software-reference-pair.md) verifies34 matching exports,44 shared-code differing bytes in nine intervals and equal import/data sections. Complete callback comparison resolves the new raw-depth16 filter; retained RGB555 handling may still publish depth15. Selected seeds/registration are unchanged. MP100-067 gains partial support; historical introduction, other code intervals, overlay/resource meaning and actual rendering remain unverified. Current catalog labels:136 vendor-only,45 bounded static,107 partial,2 unresolved.

## Software-renderer changed-code accounting completed

The [software follow-up](original-modern-software-reference-pair.md#complete-shared-code-difference-accounting) assigns all44 shared-code differing bytes to four reviewed clusters: raw-depth filter8, state21 rejection6, lock failure notification18 and page-flip tail/order12. Unlock is unchanged. The page-flip diagnostic import is OutputDebugStringA, and its new failure route avoids success-only POPs before callback0. These are local control-flow/return-contract findings, not all runtime consequences, callback ABI proof or non-code PE interpretation. Catalog counts unchanged; no target execution.

## Renderer/assets integration checkpoint

The [checkpoint manifest](evidence/validation/reference-renderer-assets-checkpoint.json) pins reviewed revision `fcd71a4`, all five executed static commands, script/output hashes and the unchanged hashes of the supplied original, official Modern, local analysis EXE and saved Ghidra database. All five commands passed. This is primary-agent reproduction and bounded consistency review, not independent semantic review, a rerun of all repository audits or runtime acceptance.

The main report now summarizes the reference branch variant, DX5/software code clusters, full suffix-scoped menu/HUD comparison and Postgame Options linkage in its existing table. The function-navigation index is regenerated from current chapter addresses; address mentions remain navigation rather than semantic coverage. Catalog labels remain136 vendor-only,45 bounded static,107 partial and2 unresolved.

The full objective remains incomplete. Priority returns to a concrete EXE producer/consumer gap from the queue above, particularly the unresolved projection capture source/lifetime; reuse the existing negative searches before new inspection. Runtime consequences, historical attribution and authenticated retail provenance retain separate gates. Repeating renderer byte localization or counting catalog labels does not close those gaps.

## Projection type1 bulk-initialization boundary

The [new bulk-boundary audit](original-modern-projection.md#type1-initializer-bulk-copies-stop-before-the-projection-sources) verifies the highest-address pair is mode1 and resolves its retained initializer branch/table. Explicit30-DWORD and9-DWORD copies,25-byte clear and scalar/extension stores end no later than005e1010 for slot1, excluding source cells005e1020/2c/30/38 on that ordinary path. This eliminates a computed/bulk candidate without asserting a global absence of writers. Actual producer/lifetime and MP160-003 remain unresolved; catalog counts unchanged.

## Projection indexed marker/counter contracts

The [indexed-state audit](original-modern-projection.md#indexed-camera-markercounter-writers-retain-their-slot-index) accounts for11 exact-base references per EXE and compares retained selectors/preparer/track-test envelopes. Eight writers manipulate a marker/counter pair; the subordinate track test restores EDX in all five normal epilogues. Ordinary slot0/1 destinations exclude projection sources, while wrapped alias indices outside that domain are explicitly retained. This resolves an index-clobber hypothesis without recovering the actual capture writer or proving all caller domains; MP160-003/counts unchanged.

## CCM positive-count admission qualification

The [CCM gate audit](ccm-camera-contract.md#positive-file-counts-do-not-exclude-the-type8-fallback) revalidates all eight current loose CCM identities and eight retained selector/helper envelopes. Positive counts do not exclude distance/orientation rejection. The latter gate is now traced to a binary32 dot output and signed raw-bit threshold, with exceptional-bit branch derivations clearly separated from instruction probes. The type8 path cannot be dismissed from nonempty file counts alone; actual selection, source capture/lifetime and MP160-003 remain unresolved. Catalog counts unchanged.

## Sound DLL whole-file localization

The [distinct sound-pair comparison](original-modern-sound-reference-pair.md) verifies every one of41,472 shared post-header bytes matches, including all existing code/data/import/export/relocation sections and16 exports. All file differences are confined to headers and an appended1536-byte version-resource section. ProductVersion1.5.3 is component metadata, not the containing final package version. This rules out changed implementation bytes for this named pair without claiming runtime/FPU equivalence or retail authentication. Catalog counts unchanged; no DLL or target instructions executed.

## Glide author-reference baseline distinguished

The [three-way Glide audit](original-modern-glide-reference-identity.md) verifies hosted/final export-entry equality and all34 local/reference RVA differences. Hosted reference already has three static Glide3x imports absent from the local candidate; final has neither DDRAW nor Glide3x static descriptors. Earlier local-candidate findings cannot be transferred without rechecking. The new paired code map records3307 differing bytes/141 intervals, plus import/data maps. This is baseline/localization progress, not completed semantic coverage or authenticated retail lineage. Catalog counts unchanged.

## Hosted Glide reference mode construction compared

The [paired about follow-up](original-modern-glide-reference-identity.md#hosted-referencefinal-about-and-mode-construction-comparison) captures both complete413-byte entries and their different helpers. Hosted reference initializes16 fixed mode records and already calls a statically bound query helper; final changes count/table pointer and uses the previously traced insertion-based builder. All six about differing-byte intervals are locally accounted for, including removed guards/calls and changed cleanup target. Query-API presence is not a Modern-only change; query-result use differs. Provider/failure/cleanup semantics, remaining functions and rendered support remain unverified; catalog counts unchanged.

## Glide loader/shutdown lifecycle compared

The [complete helper comparison](original-modern-glide-reference-identity.md#loader-and-cleanup-lifecycle-differ) resolves the changed cleanup target: hosted reference releases/clears its module handle, whereas final centralizes init/required binding and uses a shutdown/latch helper that retains the handle locally. Nonzero-state acquisition does not increment the latch; it is not a general refcount. All four exact init-cell literals are in the captured loader/shutdown helpers. Partial-bind consumers, detach/unload and runtime effects remain unverified; no leak/dangling-pointer claim is made. Catalog counts unchanged.

## Glide module-instance producer and direct detach boundary

The [entry audit](original-modern-glide-reference-identity.md#entry-callback-supplies-the-module-directory-handle) pins equal PE entry/CRT-wrapper/reason-table bytes and the changed user callback. Final captures its first entry argument into600127cc, which is passed to verified GetModuleFileNameA; reference callback only returns1. Direct callback cleanup is absent even on notification0, but optional/registered CRT finalizers and other unload paths remain unqualified. This resolves the directory-handle producer without claiming universal detach behaviour. Catalog counts unchanged; no DLL/API execution.

## Glide internal-failure descriptor consumer

The [cross-component failure trace](original-modern-glide-reference-identity.md#internal-provider-failure-is-not-a-null-about-result) captures final cold-about setup/return, EXE descriptor validation and complete mode enumeration. Internal provider return0 can yield a nonnull+8=68h descriptor with count0; it passes that local validation but enumerates no modes. Subsequent about calls take the descriptor cache guard absent intervening writes. Later init/recovery and actual provider failure remain untested, so no whole-load success/failure or irreversible-cache claim is made. Catalog counts unchanged.

## Glide exported-init retry and outward failure linkage

The [init comparison](original-modern-glide-reference-identity.md#thrash-init-retries-provider-setup-and-has-a-separate-failure-channel) captures complete paired init bodies and EXE callers. Retained init admission can retry provider setup independently of the about marker; loader0 returns init0. Slot009ef978 feeds a platform cleanup branch, then a stored-status return; outward0 skips later display/mode setup and reaches the startup diagnostic. Cleanup callback state, successful retry and runtime failure/termination remain unverified. The earlier accepted-empty-descriptor result is not whole-startup acceptance or proof of irreversible failure. Catalog counts unchanged.

## Paired DLL control-site correspondence

The [four-pair audit](original-modern-paired-dll-x87.md) verifies both archives/eight members,102 primary x87 control candidates and six FSAVE/FRSTOR candidates. VAs, instruction encodings/operands and32-byte before/after contexts match in all four pairs. These remain linear-decoding candidates, not execution/numerical equivalence or all-component precision policy. This narrows older-DLL correspondence while preserving changed EXE/ambient-state and other-provider limits. Catalog counts unchanged; no target execution.


## Original startup version-template producer

The [resource/header comparison](original-modern-config-loading.md#original-startup-populates-the-header-template-from-a-version-resource) now identifies the original startup writer into `0055e8b8/+2`, removing the assumption that file-backed zeros describe ordinary startup. The retained resource is `27, 2.0`; Modern removes this read/scan callsite and has a static version6 header. Exact scanner widths/overlap effects, runtime filename resolution and later writes remain pending. Catalog counts unchanged; no target execution or Ghidra changes.


## Original scanner width and version2 consequence

The [scanner follow-up](original-modern-config-loading.md#scanner-width-and-conditional-version2-header) resolves plain `%d` to a DWORD store at `0050d500`. Successful parsing of the inspected `27, 2.0` resource leaves low header version2 despite destinations two bytes apart. Conditional on that header surviving initialization and saving, Modern rejects version2 and resets grouped defaults. Runtime file selection, partial parsing and later writes remain pending; this is not a real-file migration test. Catalog counts unchanged.


## Version-reader failure/copy and static dependency closure

The [follow-up](original-modern-config-loading.md#version-reader-failure-gates-and-string-copy-boundary) qualifies original reader failure/cleanup paths, copy count/padding and conditional termination, plus the caller's zero-only scanner gate. Final Modern lacks the original three version-query imports and `VERSION.dll` descriptor. This closes the inspected copy and static-dependency questions, not runtime resource provenance, all malformed scanner inputs or header lifetime. Catalog counts unchanged; no target execution.


## Removed optional fpuerrors startup sequence

The [x87 follow-up](og-modern-x87-precision.md#removed-optional-startup-exception-unmasking) verifies original slot25/bit25, all five zero-value mask updates, final69-byte NOP replacement and the byte-identical76-byte runtime helper. It distinguishes exception unmasking from precision selection and leaves guard lifetime, other callers and actual exception delivery open. Catalog counts unchanged; no target execution.


## Removed demo startup override bodies

The [ordered-branch audit](original-modern-command-line.md#removed-demo-startup-writes-and-precedence) records the raw common writes, two differing WORD stores and e3demo-after-msdemo precedence in original `004a3b3d..004a3d05`, versus456 Modern NOPs. Field meanings and visible demo effects remain pending. This extends the existing switch-table and save-gate findings without claiming all demo consumers are removed. Catalog counts unchanged; no target execution.


## Removed low-address startup read and filter path

The [startup comparison](original-modern-startup-policy.md#removed-low-address-read-and-exception-filter-handler) identifies original absolute byte read`0x190`, the metadata-associated UnhandledExceptionFilter path and conditional `0055e8c0` publication within Modern's100-byte NOP replacement. It records the nonordinary stack contract of runtime entry`004f7b7d` and changed metadata target. Intended OS/debugger policy, full dispatch and global consumers remain unresolved. Catalog counts unchanged; no fault or target execution.


## Later demo application-flow branches

The [extended comparison](original-modern-command-line.md#later-demo-branches-also-change-application-flow) completes the local original fragment beyond the startup partition: bit21 adds raw WORD writes, language/default calls and pointer publication; bit20 adds other writes, EAX0 race preparation and a cleanup jump. Final's complete application body lacks those exact direct gate encodings. This is not a whole-process absence proof; field meanings, callback contract and runtime outcomes remain pending. Catalog counts unchanged.


## Replacement startup flags have retained diagnostic consumers

The [producer/consumer follow-up](original-modern-startup-policy.md#replacement-startup-values-control-retained-diagnostic-output-and-break) resolves direct uses of `005643fc`/`0055e8c0`: a byte-identical consumer gates OutputDebugStringA and then DebugBreak. Modern explicitly initializes them1/0, replacing the original filter-dependent break flag. Both retain an exception-report-side clear of the outer flag. Other writers and full handler/runtime behaviour remain open; catalog counts unchanged.


## Complete diagnostic body: two flag bytes, no changed call target

The [handler comparison](original-modern-startup-policy.md#diagnostic-dialog-flags-are-the-only-local-handler-body-change) now accounts for all differences in the520-byte `00401010` body: two immediate bytes change MessageBoxA flags from11031h to51011h, requesting an error icon and explicit topmost flag. Both already specify SYSTEMMODAL; no new visible stacking fix is inferred. Unchanged code is not a transitive/runtime equivalence claim. Catalog counts unchanged; no target execution.


## Historical lockwindow failure callback change

The [three-driver comparison](original-modern-lockwindow-history.md) verifies retained1.5.0→1.5.1 DX5/DX6/SoftTri failure paths adding callback0 after a preceding callback1 request. DX5/DX6 gain null-guarded register-to-stack adapters; SoftTri adds a direct tail call. Callback meaning, full state lifetime and runtime bug effects remain unresolved. MP151-004 advances vendor-only→partial; current counts are130/47/111/2. This is historical DLL evidence, not retail-original EXE correspondence; no target execution.


## Historical failure callback identity: critical-section enter/leave

The [EXE/table follow-up](original-modern-lockwindow-history.md#exe-callback-table-identifies-critical-section-enter-and-leave) verifies same-archive EXEs, eight-pointer callback blocks, the+14h target and complete59-byte RET4 callback. Nonzero calls EnterCriticalSection, zero LeaveCriticalSection, then publishes the raw argument. Under installed-block/valid-stable-pointer assumptions, the added driver failure callback0 supplies the missing release request. Full registration/lifetime and runtime failure effects remain pending; MP151-004 remains partial and counts unchanged.


## Historical lock callback setup and failure prerequisite

The [setup follow-up](original-modern-lockwindow-history.md#critical-section-setup-narrows-the-pointer-lifetime-prerequisite) verifies three paired-identical EXE spans: pool-node InitializeCriticalSection producer, general publisher and raster null-check/create/publish route. Producer failure can return0, and the captured raster route does not retest after publication. Setup is therefore evidenced without assuming universal validity; replenishment, destruction, other publishers and concurrency remain pending. MP151-004 remains partial; counts unchanged.


## Original/final EXE side of the historical lock fix corresponds

The [four-EXE correspondence check](original-modern-lockwindow-history.md#correspondence-with-supplied-original-and-official-final-exes) verifies identical callback table,59-byte callback,83-byte producer,89-byte publisher and35-byte registration witness across supplied original, official final and both historical EXEs, with matching API bindings. The driver failure-path change uses retained EXE synchronization code. This is scoped byte/interface correspondence, not full startup/driver equivalence or retail provenance for all DLLs. Counts unchanged; no target execution.


## DX6/SoftTri callback registration dispatch resolved locally

The [selector13h follow-up](original-modern-lockwindow-history.md#dx6-and-softtri-selector13h-registration-routes) verifies1.5.1 DX6's jump-table entry19→nonnull eight-DWORD copy and SoftTri's ordered selector comparisons→copy without a local payload-null guard. This closes those selected dispatch edges, while preserving pointer/DF prerequisites and unresolved replacement/lifetime/runtime questions. MP151-004 remains partial; counts unchanged.


## Historical1.5.1 localized text changes

The [complete twelve-asset comparison](original-modern-localization-151.md) partitions every offset/string byte in six languages across1.5.0/1.5.1. Shared entries differ only at1932 in all languages and1283 in French; five entries are appended. French wording is verified, but a separate German/Spanish correction among other shared strings is not found. MP151-005 advances vendor-only→partial with that limitation; current counts129/47/112/2. No target execution.


## Historical km remapping has a matched EXE consumer

The [consumer follow-up](original-modern-localization-151.md#track-length-consumer-follows-the-moved-km-entry) verifies the only byte change in the170-byte historical track-length helper:1932→1936, preserving `km` in all six matched asset tables. The lookup maximum also grows1935→1940. This resolves one code/asset remapping without claiming all IDs/consumers or mixed-version compatibility. Catalog counts unchanged; no target execution.


## Historical rear-camera and mirror-detail label bindings

The [two-menu audit](original-modern-localization-151.md#historical-menu-assets-bind-two-new-labels) verifies the1.5.1 camera-menu15-line insertion and graphics-menu's sole lang1537→lang1937 label replacement. This binds new language entries1938/1937 to authored controls and dates the selected rear-camera asset addition. Full/new1932 consumer and parser/runtime state remain unresolved. Counts unchanged; no target execution.


## Historical Full entry has a Frame Size descriptor consumer

The [WORD-table follow-up](original-modern-localization-151.md#frame-size-first-choice-label-switches-to-the-new-full-entry) verifies identical widescreen descriptor/selection storage but first label184→1932, preserving second1933. Matching assets change French/Spanish first-choice wording; German remainsVoll. This explains a semantic retargeting beyond changed shared strings, while keeping the claimed German correction and runtime rendering unresolved. MP151-005 remains partial; counts unchanged.


## Frame Size expansion directly dated1.5.3 to1.6.0

The [historical descriptor/English-asset audit](original-modern-frame-setting.md#direct153-to160-expansion-boundary) verifies immediate retained release hashes, two→four choices and retained selector storage. This resolves the table-expansion introduction gap for MP160-004, while full historical geometry consumers, saved-ordinal migration and visible shifts remain unverified. The catalog entry stays partial; counts unchanged. No target execution.


## Historical Frame Size constructor bit policy

The [constructor follow-up](original-modern-frame-setting.md#historical-constructor-changes-boolean-policy-to-two-independent-bits) captures complete624/634-byte1.5.3/1.6.0 constructors and verifies1.6.0/final body equality.1.5.3 normalizes the selector;1.6.0 uses bit1 for2:1 and bit0 for covering-frame shift, matching the expanded labels locally. Other consumers, saved ordinals and visible outcome remain pending. MP160-004 remains partial; counts unchanged.


## Historical Frame Size version-reset gate

The [config follow-up](original-modern-frame-setting.md#historical-config-version5-to6-selects-reset-rather-than-ordinal-conversion) verifies1.5.3/1.6.0 templates5→6, the sole threshold-byte change in the decision range, and Frame Size0 default. An admitted version5 header takes grouped reset in1.6.0, rather than unconditionally reinterpreting old ordinal1. Real files, writers/overrides and rendered behaviour remain pending; counts unchanged.


## Historical nGlide regression: package/header boundary

The [component audit](original-modern-nglide-window-history.md) verifies1.5.2/1.5.3 nGlide provider/INI equality and exactly seven adapter-file changes, confined to checksum/import-directory size/IAT-directory headers. File-backed sections/layout are identical; BSS is not read as file-offset0 payload. Cause/fix remains unresolved, with EXE paths and metadata loader behaviour separate candidates. MP153-007 advances to partial package evidence; current counts128/47/113/2. No target execution.


## Historical nGlide EXE-side mode-publication candidate

The [historical follow-up](original-modern-nglide-window-history.md#exe-mode-publication-changes-to-selected-dimension-centring) captures complete239/223-byte mode bodies and verifies three identical sizing helpers.1.5.3 removes the flag-gated desktop-size call and uses selected-dimension centring at the publication point. This supplies a concrete candidate mechanism without proving nGlide/windowed admission, sole causality or runtime recovery. MP153-007 remains partial; counts unchanged.


## Historical sizing flag has retained producer and toggle

The [flag/order follow-up](original-modern-nglide-window-history.md#sizing-flag-producer-later-toggle-and-mode-request-order) verifies the retained inverse-WindowedMode producer, complete42-byte bit0 toggle and mode request/publication order. The1.5.3 local difference affects flag1; flag0 already centred requested dimensions. This narrows interpretation of the nGlide claim without inventing a provider-specific branch or fixed lifetime. Counts unchanged; no target execution.


## nGlide candidate now has a three-release boundary

The [predecessor comparison](original-modern-nglide-window-history.md#predecessor151-separates-refactor-introduction-from-a-simple-revert) captures1.5.1's different447-byte mode body with no direct calls to the two sizing helpers, versus1.5.2's new desktop-size branch and1.5.3's selected-size route. The1.5.1 adapter equals1.5.2 exactly, so1.5.3 metadata is not a rollback to a distinct151 layout. Full causal/runtime evidence remains pending; counts unchanged.


## Historical dgVoodoo2.53 package identity

The [five-component package audit](original-modern-dgvoodoo-version-history.md) verifies1.5.3/1.6.0 archive hashes, wrapper/setup ProductVersion2.51→2.53, identical adapter/INI and changed binary config. Wrapper FileVersion remains3.10 and must not be used as product version. MP160-014 advances to bounded static package-identity support; provider code/runtime and upstream authentication remain unverified. Current counts127/48/113/2. No target execution.


## DX7 display-env wrapper has a hidden-register/default change

The [wrapper/consumer follow-up](original-modern-dx7-mode-admission.md#missing-display-environment-stops-forwarding-saved-ecx) verifies old missing THRASH_DISPLAY→entryECX versus new→0, an omitted local flag store and a byte-identical295-byte selection consumer. This is a concrete independent display-selection difference; black-polygon attribution, caller ECX initialization and runtime effects remain unresolved. No visual catalog claim is promoted; counts unchanged.


## DX7 display wrapper caller qualification

The [caller follow-up](original-modern-dx7-mode-admission.md#caller-qualification-narrows-the-old-saved-ecx-consequence) identifies two direct wrapper calls per driver and old about's staged ECX word73617233h. For an unchanged source and adapter count<=that value, the old missing-env path falls back0, narrowing the earlier possible-different-index example. The second init caller and count/source lifetime remain open. Counts unchanged; no target execution.


## DX7 display count: callback cap is not a global invariant

The [count-path follow-up](original-modern-dx7-mode-admission.md#adapter-count-callback-cap-is-followed-by-an-environment-override) verifies four retained paired-identical spans. A16-entry callback admission cap precedes unclamped DX7_displays/THRASH_displays overrides, then filtered-count publication. This prevents promoting the local cap into a universal global bound and preserves the conditional about-path conclusion. No new visual claim or runtime result; counts unchanged.


## DX7 clip-record depth candidate for the visual workaround

The [complete150-byte clip comparison](original-modern-dx7-viewport-depth.md) verifies exactly two changed immediate bytes,1−1/65536→1.0 in a six-DWORD record sent through vtable+34h. SDK layout/slot matches D3DVIEWPORT7/SetViewport; complete object provenance, device acceptance and Old Church black-polygon attribution remain unverified. MP161-003 advances to partial candidate evidence, not confirmed workaround. Current counts126/48/114/2; no target execution.

## DX7 viewport device producer follow-up

The [viewport-depth audit](original-modern-dx7-viewport-depth.md#device-producer-identifies-the-receiving-interface) now pins identical paired QueryInterface and CreateDevice witnesses. The exact IID identifies IDirect3D7; its factory output identifies IDirect3DDevice7 in`60058d9c` on a successful selected path, supporting SetViewport at+34h. Object lifetime, other writers, call admission and Old Church symptom attribution remain unverified. MP161-003 remains partial; catalog counts unchanged. No target execution or database changes.

## Historical network comma parser boundary

The [endpoint follow-up](original-modern-network-endpoints.md#historical-comma-normalization-and-exact-suffix-grammar) verifies1.4.0→1.5.0 adds the ten-byte comma-to-period branch and that final retains the complete61-byte body. Identical shared converters/classification tables resolve whitespace, prefix parsing and wrapping port acceptance; examples remain static derivations. MP150-019 advances vendor-only→bounded-static, giving125/49/114/2 catalog labels. Provider/UI acceptance and cross-version race compatibility remain untested; no target execution or database writes.

## Car Detail and historical wheel-related policy

The [vehicle-detail follow-up](original-modern-vehicle-dispatch.md#car-detail-binding-and-historical-high-budget-bypass) binds Car Detail0/1/2 to High/Medium/Low, compares original/Modern threshold rows and dates the High-budget bypass plus two per-object wheel-tick reads to1.4.0→1.5.0. Final retains a mirror-detail exception to that bypass. Complete classifier, budget and selected render bodies remain equal across the four pinned EXEs. MP100-012 and MP150-001 advance vendor-only→partial; counts123/49/116/2. Actual wheel motion, texture quality and sole-cause attribution remain unverified; no target execution or database mutation.

## Historical EXE mode-menu capacity and label consumers

The [capacity history](original-modern-display-modes.md#historical-exe-capacity-expands-from51-to101-local-entries) verifies original20, early1.1.0 local51 and direct1.2.0 expansion to101, alongside matching cleared label banks, inclusive dynamic-label ranges, descriptor pointers and record-label accessors. Headlines50/100 are not exact local limits. MP100-009 advances vendor-only→partial; MP120-008’s historical mechanism boundary is now verified. Counts122/49/117/2;1.0.0 introduction, provider ceilings, complete storage/UI lifetime and actual displays remain unverified. No target execution or database changes.

## Historical optional LOGO2 producer and draw consumer

The [two-image follow-up](original-modern-frontend-page.md#historical-logo2-loading-and-two-image-draw-selection) verifies1.4.0→1.5.0 adds an optional logo2.qfs attempt after primary success, publishes0/6/8, and selects the second uploaded identifier through the retained records’ fourth DWORD. Primary failure prevents the second attempt. Count/identifier address roles change; final uses the separately audited logos.qfs metadata path. MP150-022 advances vendor-only→bounded-static; counts121/50/117/2. Historical image contents, actual uploads/animation and later consolidation remain unverified; no target execution or database mutation.

## Named default graphics policy

The [default-policy follow-up](original-modern-resolution-defaults.md#named-graphics-defaults-and-the-limits-of-automatic-high-settings) binds eight tier-table destinations through descriptor labels, verifies effective-tier ECX preservation across mode calls and records score5’s renderer-dependent choices. Maximum-score High/Full defaults remain conditional on renderer bits and selected-mode overrides; fog receives record EAX rather than the ninth table. MP100-010 advances vendor-only→partial; counts120/50/118/2. Actual settings, full initialization lifetime, visual quality and1.0.0 introduction remain unverified; no target execution or database mutation.

## Audio Cancel volume-source correction

The [paired Cancel follow-up](original-modern-frontend-sound.md#audio-cancel-restores-the-block-without-the-original-cache-overwrite) verifies identical64-byte snapshot instructions and matching audio callbacks, then isolates original’s conditional overwrite from separately saved caches after block restoration. Final retains the configured Engine Volume/Sound Effects block values locally. MP100-027 advances vendor-only→partial; counts119/50/119/2. Actual flag/cache values, audible maximum-volume behavior, later application and1.0.0 introduction remain unverified; no target execution or database mutation.

## Historical movie-disable key and switch spelling

The [movie-option history](original-modern-idle-movie.md#historical-movie-option-spelling-and-the-early-title-gate) traces early NoMovie INI reads to the retained title-disable bit and verifies1.5.1→1.5.2 renames both INI key and switch to NoMovies/-nomovies with identical setting-branch/mask-builder code. Final’s environment name is plural; the README’s singular example is historical, not a proven alias. MP100-024 advances vendor-only→partial; counts118/50/120/2. All intro paths,1.0.0 introduction, actual configuration and playback remain unverified; no target execution or database mutation.

## CPU-rating overflow and low-class consequence

The [signed-wrap follow-up](original-modern-cpu-tier.md#original-signed-wrapping-can-select-the-lowest-class) links original’s low32 million-scale IMUL to signed default/movie thresholds and records twelve hypothetical arithmetic cases. Negative stored results select the lowest default class/movie selector1 on the admitted paths; repeated wrapping is not monotonic. “166MHz” denotes a class, not a literal reassignment. MP100-028 advances vendor-only→partial; counts117/50/121/2. Actual calibration inputs, CPU/video outcomes, bypass paths and1.0.0 introduction remain qualified; no benchmark or target execution.

## Free-space warning arithmetic and retained failures

The [directory/error follow-up](original-modern-startup-requirements.md#directory-and-error-paths-qualify-the-false-free-space-warning-fix) verifies four retained helper bodies, used-buffer length/copy conditions and normal geometry-error return. It connects the previously verified unsigned overflow-aware arithmetic to MP100-029 without claiming the check was removed. Directory return remains unchecked by the caller; actual API outcomes and warnings remain unverified. Catalog advances that row vendor-only→partial, counts116/50/122/2. No disk, dialog or target execution.

## Fitted reference dimensions reach text scaling

The [text-scale follow-up](original-modern-hud-layout.md#fitted-reference-scales-reach-a-conditional-text-path) connects the changed width/coefficient producer to retained85-byte adapter00451530 and bitmap setter. Wide-branch fitted width is height-derived; backend/font flags and unchanged width-based bitmap paths prevent a universal all-font claim. MP100-004 advances vendor-only→partial; counts115/50/123/2. Actual glyph sizes, other font routes, reference lifetime and1.0.0 introduction remain unverified; no font rendering or target execution.

## Police HUD widget claim remains unverified

The [bounded HUD-editor review](original-modern-hud-settings-policy.md#police-cone-stats-and-tutorial-icon-claim-remains-unresolved) binds Tutorial Icon/Cone Stats to preset slots6/7, records nonzero reference/final defaults, and verifies retained pshud initializer/HudItem rectangle-loader/template bytes. These checked routes do not identify the advertised police-only hiding mechanism. MP100-048 stays vendor-only; counts unchanged. Next is active item-list construction and slot/role draw/input admission, with archive omission kept separate from installed deletion. No menu or target execution.

## Historical nGlide settings before provider loading

The [paired adapter audit](original-modern-renderer-loading.md#historical-nglide-configuration-precedes-provider-loading) verifies1.2.0’s complete NGLIDE-specific helper, packaged six settings and pre-LoadLibrary order. Removing the section skips writes but leaves inherited/previous values untouched; global-settings outcome remains conditional and untested. MP120-025/027 advance to partial, MP120-026 to bounded static; counts112/51/125/2. Final EXE generic ENV remains a separate mechanism. No target execution or database changes.

## Menu music default changes across Modern history

The [three-baseline default audit](original-modern-music-selection.md#historical-romulus-default-is-not-the-final-modern-default) verifies original selector0, early1.1.0 selector2/Romulus 3 and final selector0/Random (All), with six changed bytes in the complete early audio-default block. This qualifies the old release-note claim rather than presenting it as final behavior. MP100-034 advances to partial historical support; counts111/51/126/2. Exact change dates, user-setting admission and playback remain unverified; no target execution or database changes.

## Historical cabin extent correction dated

The [three-release helper comparison](original-modern-view-overlay.md#historical-fixed-expansion-becomes-resolution-dependent-in160) verifies identical36-byte+1/+1 helpers in1.1.0/1.5.3, replaced by the63-byte resolution-dependent helper in1.6.0 and retained in final. Coordinate units, general-register preservation and physical pixel/seam claims remain distinct. MP100-018 advances to partial; MP160-008 gains its direct release boundary. Counts110/51/127/2; no target execution or database changes.

## Camera slot defaults and retained choices

The [paired default audit](original-modern-viewport-pose.md#default-camera-slots-change-without-removing-the-choice-table) binds four descriptors and unchanged choice/mode tables to original In Car/Roof Cam/Heli Cam/None versus final Heli Cam/In Car/None/None. The complete85-byte converter is retained; original GetTickCount wrapper preservation and the ordinary Windows ABI assumption are explicit. MP100-031 advances to partial, counts109/51/128/2. Runtime cycling, UI restoration and saved-user settings remain unverified; no target execution or database writes.

## Historical minimap role-default transition

The [three-release store comparison](original-modern-map-marker-scaling.md#historical-role-specific-defaults-become-equal-in140) verifies early1.1.0/1.3.1 racer3/cop1, then1.4.0 all3, with the latter block retained at a relocated final address. Existing field/role/zoom-consumer evidence remains separate from fresh historical store evidence. MP100-032 advances to partial; MP140-073 gains direct release-boundary support. Counts108/51/129/2; saved preferences and rendered map coverage remain unverified. No target execution or database changes.

## Named opponent HUD default swap

The [descriptor/default/consumer audit](original-modern-hud-layout.md#opponent-name-and-list-have-distinct-profile-defaults) resolves header+04/+08 as Opponent Name/List. Racer suffix1/2 defaults change1/0→0/1; cop suffix profiles remain0/0. Two retained conditional branch spans establish List admission without guaranteeing visibility or full session/view mapping. MP100-033 advances to partial, counts107/51/130/2. Saved preferences, runtime display and1.0.0 introduction remain unverified; no target execution or database changes.

## Police-list compact-spacing mechanism

The [data/consumer audit](original-modern-hud-layout.md#police-list-row-and-panel-spacing-use-smaller-data-coefficients) verifies paired binary64 coefficients20→12.414 in row advance and panel-layout metrics, retained1/13 multipliers and unchanged font-metric bodies. Equal-metric unrounded ratio0.6207 is not a rendered-size measurement or proof of resemblance to standard standings. MP100-007 advances to partial, counts106/51/131/2. Font state, caller admission, visual layout and1.0.0 introduction remain unverified; no target execution or database changes.

## Alpha Intensity colour-publication mechanism

The [complete colour-helper audit](original-modern-effect-renderer-masks.md#alpha-intensity-connects-menu-writeback-to-packed-colour-scaling) links the official control and existing writeback/type audits to a235-byte helper with only the mask40h→50h change. Below1 it quantizes intensity and scales all four bytes of two published colours; at1 it bypasses scaling. Ordinary examples are derived, not probes. MP100-015 advances to partial, counts105/51/132/2; driver output, car shine, full lifecycle and1.0.0 introduction remain unverified. No target execution or database changes.

## Recent eight-mechanism reproducibility checkpoint

The [checkpoint](evidence/validation/recent-static-mechanisms-checkpoint.json) pins reviewed revision`f92b1e7` and16/16 successful runs across nGlide configuration, menu music defaults, cabin extents, camera defaults, map zoom defaults, opponent HUD defaults, police-list spacing and intensity colour publication. All eight outputs match their pre-run evidence;12 protected files match the earlier checkpoint before/after, and12 raw exports match prior recorded hashes. The [compact findings table](original-modern-differences.md#recent-configuration-and-hud-mechanisms) lists mechanisms and separate remaining qualifications. This is primary-agent static reproducibility, not independent review, runtime, new exports, compilation or Ghidra reopening. Catalog classifications remain105 vendor-only/51 bounded-static/132 partial/2 unresolved; no whole-goal completion claim.

## Original temporary music-copy route removed

The [copy/start comparison](original-modern-music-selection.md#original-temporary-music-copy-is-removed-from-the-inspected-loading-route) verifies original761-byte copy routine replaced by NOPs and final source-suffix replacement instead of temporary-name construction. Original requests512KiB chunks; no fixed10MiB saving, motive, measured speedup or successful I/O is inferred. MP100-037 advances to partial, counts104/51/133/2. Actual playback, complete failure handling/caller coverage and1.0.0 introduction remain unverified; no target execution or database changes.

## Loading estimator branch contract qualified

The [complete143-byte estimator audit](original-modern-loading-timing.md#smoothing-is-branch-specific-not-a-monotonic-five-point-invariant) verifies that the time-percentage branch bypasses prior+5, exact100 bits bypass the unsigned50ms gate, and accepted branches publish progress/time. Five exact ordinary derived examples distinguish local behavior from reachable lifecycle states and visible smoothness. MP100-036 advances to partial, counts103/51/134/2. Actual animation, state provenance and1.0.0 introduction remain unverified; no target execution or database changes.

## Early loading-artwork grid distinguished from sprite-edge claim

The [early/final comparison](original-modern-loading-artwork.md#early-modern-already-has-the-six-tile-loading-artwork-path) verifies1.1.0 already has256 extent/3x2 grid; only nine bytes differ in the748-byte final comparison envelope, classified as scale-read/store-address and call-target changes. Existing original/final evidence supplies300→6 iterations. MP100-016 advances to partial; MP100-017 remains vendor-only because this does not establish a sprite-edge mechanism. Counts102/51/135/2. Visual quality, sampling/atlas behavior and1.0.0 introduction remain unverified; no target execution or database changes.

## Race-dialog Tournament/Hot Pursuit preselection remap

The [four-baseline audit](original-modern-race-dialog.md) verifies1.1.0 raw stored-mode passing becomes a19-byte AL1↔3 remap in1.2.0, retained at a different final address. Unrestricted dialog rows and stored race-choice order differ at those two positions; only four bytes differ in the complete original/final354-byte builder. Wider inputs retain upper24 bits. MP120-002 advances to partial, counts101/51/136/2. Restricted states, live focus/input and full state lifetime remain unverified; no target execution or database changes.

## Early border coefficient change separated from160 source rewrite

The [five-baseline comparison](original-modern-border-geometry.md#historical-coefficient-halving-precedes-the-fitted-width-cache-rewrite) verifies original/1.1.0/1.5.3 identical1420-byte builders with data coefficient4→2, then1.6.0’s fitted-width cached-thickness builder/updater retained in final. MP100-006 advances to partial; MP160-006 gains the border-specific direct release boundary. Counts100/51/137/2. Integer/visible ratios, refresh lifecycle, marker introduction and1.0.0 introduction remain qualified; no target execution or database changes.

## Race-dialog caller and initial-selection storage follow-up

The [expanded caller audit](original-modern-race-dialog.md#checked-direct-callers-exclude-the-compacted-array-premise) verifies both decoded direct callers passEAX1 and explicitly clear the restriction flag before the builder, without intervening calls. The retained dialog helper stores/clamps the passed candidate into00558b3c. Compacted C1 rows remain a separate local case with no demonstrated direct-caller admission here; no runtime bug or universal fix is inferred. MP120-002 stays partial and catalog counts unchanged. Callback/live interaction and indirect callers remain unverified; no target execution or database changes.

## Installer-record settings versus early/final INI behavior

The [three-baseline history](original-modern-language-table.md#installer-settings-move-to-early-ini-but-remoteonly-is-not-retained-in-final) verifies early1.1.0 Language/RemoteOnly profile-API wrappers and normalized RemoteOnly publication, contrasting original install-record sources and final literal-zero gate. Early retains INSTALL.WIN only in the checked diagnostic literal census; string presence is not a file-read proof. MP100-022 advances to partial, counts99/51/138/2. Exact removal date, full file-access coverage, actual startup and1.0.0 introduction remain unverified; no target execution or database changes.

## Early installation directory checker and final creation contract

The [history/helper audit](original-modern-startup-paths.md#early-four-directory-installation-check-versus-final-preparation-tables) verifies1.1.0’s four direct-string directory checks versus final13 required/four preparation slots. Both reject API attribute failure/non-directory results; final creation returns API failure without retry/requery or recursive parent creation. MP100-041 advances to partial, counts98/51/139/2. Complete installation/assets, permissions, actual startup and introduction/expansion dates remain unverified; no target execution or filesystem/database mutation.

## Early EXE resolution budget removal and depth-policy distinction

The [three-baseline predicate audit](original-modern-display-modes.md#early-modern-already-bypasses-the-budget-gate-and-has-a-broader-depth-test) verifies early1.1.0 skips the original size/budget block while retaining indirect about lookup and using signeddepth>=16, unlike final16/32 equality. Four ordinary derived cases qualify larger local admission and retained restrictions. MP100-003 advances to partial, counts97/51/140/2. Provider support, actual menus/rendering,1.0.0 introduction and later depth-change date remain unverified; no target execution or database changes.

## Mode depth narrowing and cache-source dates resolved separately

The [release-boundary audit](original-modern-display-modes.md#depth-narrowing-and-descriptor-caching-occur-in-different-releases) verifies1.4.0→1.5.0 introduces the16/32 shared eligibility helper, retained through final.1.5.0/1.6.0 selected bodies match;1.6.0→1.6.1 replaces enumerator/search about calls with cached reads and repacks surrounding instructions. Prior1.1.0 bytes match fresh1.4.0 enumeration. Catalog counts unchanged. Source lifetime/provider effects, mode rendering and machine-state equivalence remain unverified; no target execution or database changes.

## Early abort-diagnostic presentation change

The [three-baseline handler comparison](original-modern-startup-policy.md#early-release-already-contains-the-diagnostic-dialog-flag-change) verifies early1.1.0/final520-byte equality, original’s two flag-byte differences and retained caption/MessageBox binding. Warning→error icon and explicit topmost requests do not establish a repaired stacking problem; original SYSTEMMODAL remains qualified. MP100-042 advances to partial, counts96/51/141/2. Actual dialogs, all error paths and1.0.0 introduction remain unverified; no target execution or database changes.

## Early driver filename/device parsing and live key rename

The [three-release audit](original-modern-renderer-loading.md#early-filename-and-device-suffix-interface-then-driver-key-rename) verifies early151-byte filename/.dll/@device parser and1.3.1→1.4.0 VideoDriver→ThrashDriver read-key change. It distinguishes early path/type/device globals from final reused addresses. MP110-001/002 advance to partial, MP140-045 to bounded static; counts93/52/143/2.1.0.0 alias/separate-key predecessor, scan edge cases, provider/device success and rendering remain unverified; no target execution or database changes.

## Eleven later investigations reproduced against committed evidence

The [checkpoint](evidence/validation/later-static-mechanisms-checkpoint.json) records reviewed revision`1a5b591`,22/22 passing static runs and eleven outputs matching the committed pre-run evidence.12 protected artifacts and12 raw exports retain their prior hashes. The [compact table](original-modern-differences.md#later-startup-loading-and-mode-findings) consolidates the mechanisms and their remaining limits. The primary agent performed these checks; independent semantic review, game/API/instruction execution, new exports, compilation and Ghidra reopening were not performed. Catalog remains93 vendor-only/52 bounded-static/143 partial/2 unresolved; these are release-note classifications, not a game-completion percentage. The goal remains incomplete.

## SoftTri list-bevel attribution remains unresolved after paired gate check

The [four-baseline boundary audit](original-modern-hud-layout.md#softtri-list-bevel-claim-checked-renderer-gates-are-retained) verifies identical91/53-byte bit2/JNE spans, including140→150. These are not established as the complete claimed frame route; nearby dimensions/defaults/spacing changes cannot substitute for that linkage. MP150-017 remains vendor-only and counts unchanged. Required follow-up is frame-resource/submission/provider linkage, not repeating the same local-gate search. No target execution or database changes.

## Top dropdown ordering in the150 package boundary

The [priority comparison](original-modern-common-menu-buttons.md#location-and-opponents-dropdown-priority-changes-in150) adds partial support for MP150-024: two top lists move to priority0 and Location lower controls shift upward, matched to selected descending-group consumers. The1.4.0→1.5.0 asset boundary is verified. Visible compositing, actual loading and full-loop equivalence remain untested; the changed intervening state preparation is explicitly excluded.

## Subtitle style replacement in the150 package boundary

The [Showcase/Compare subtitle audit](original-modern-common-menu-buttons.md#showcase-and-compare-subtitles-adopt-the-race-results-text-style) adds partial support for MP150-025: new text records match nine existing Race Results style fields, while old cascades change notitle0→1. Five named descriptor bindings match across supplied original/final EXEs. Actual font-bank selection, complete title consumers and rendered acceptance remain untested.

## Two-member DDRAW import history

The [paired historical PE inventories](original-modern-glide-reference-identity.md#ddraw-import-removal-is-verified-across140-to150-for-both-named-binaries) directly support MP150-045 at1.4.0→1.5.0 for nfs3.exe and drivers/glide3x/voodoo2a.dll. Conditional dynamic use remains proven separately. Catalog counts88/53/147/2; no game, API or instruction execution.

## Callback selection preparation fully compared

The [four-build code audit](original-modern-common-menu-buttons.md#callback-selection-gains-a-none-check-and-narrower-sum-in140) resolves the previously excluded37-byte block in the complete363-byte callback loop, including five NOP bytes outside saved ranges.1.3.1→1.4.0 adds selection100 suppression and16-bit wrapped summation. The query retains32-bit arithmetic; scalar examples are derived, not executed. Catalogue labels remain unchanged because no release-note identity is asserted. Runtime producers/consumers and reachability remain open.

## Eight recent investigations reproduced against committed evidence

Run `python3 analysis/scripts/check_hud_menu_import_mechanisms.py` to reproduce the [checkpoint](evidence/validation/hud-menu-import-checkpoint.json). It pins each selected script/output to reviewed HEAD, records selected shared dependency hashes and verifies protected files before/after. Historical negative-gate/draw findings remain bounded; later positive branch/asset evidence supersedes their former vendor-only status. No target/API execution, new exports, compilation or Ghidra reopening was performed. Next static targets are MP150-020 HUD-preview arrangement and MP150-035 exit resolution, with existing evidence reused; the full audit remains incomplete.

## HUD preview authored arrangement measured

The [four-snapshot asset audit](original-modern-hud-settings-policy.md#hud-preview-authored-coordinates-change-in150) identifies13 coordinate-pair changes in140→150, retained final, with unchanged moved-image aliases and paired x/y descriptor bindings. MP150-020 is partial. Active geometry/asset loading and visible alignment remain unverified. The next code-level priority is MP150-035 gameplay-exit resolution handling, reusing window lifecycle evidence.

## Gameplay-exit mode request suppressed at150

The [four-build shutdown audit](original-modern-renderer-lifecycle.md#gameplay-exit-skips-frontend-mode-setup-from150) supplies partial support for MP150-035:140→150 adds zero-input suppression of frontend mode/viewport setup, with retained selected action/state/input linkage and cleanup admission. Literal640×480 is a viewport request, not proof of the OS mode. Runtime display, network mediation and full cleanup remain unverified.

## Loading setup time included in150 budget

The [three-build timing audit](original-modern-loading-timing.md#preliminary-setup-elapsed-time-enters-the-budget-in150) supplies partial support for MP150-031: earlier baseline/elapsed subtraction replaces the full post-setup budget. Clamp ordering changes, and historical clocks are GetTickCount while final uses timeGetTime. A retained wrapper links admitted network setup inside the elapsed interval; actual protocol duration and animation remain unverified.

## DX7 fog support defaults enabled in152

The [historical DX7 review](original-modern-renderer-loading.md#dx7-fog-opt-in-changes-in152-while-its-driver-bytes-remain-identical) verifies package FogSupport0→1, identical driver bytes and paired read/normalization semantics. Selected dispatcher/environment bodies remain unchanged. MP152-002 has partial configuration support, with full API107 glue/version contract and actual fog rendering still unresolved; no runtime evidence was added.

## Selected API fog request mechanism now linked

The [mode/enable follow-up](original-modern-renderer-loading.md#fog-formula-setup-separates-from-ordinary-enable-state-in152) supersedes the preceding configuration-only boundary:151→152 changes effective mask normalization and adds separate supported-only mode4 setup. Retained scene restore and cached setter connect it to distinct unchanged DX7 provider branches. MP152-002 remains partial, with no count change; complete API specification, provider success and rendering remain open.

## Menu fog context verified without over-attributing taillight repair

The [historical context audit](original-modern-state14.md#menu-fog-admission-becomes-contextual-at150) verifies140→150 support/effective separation and selected writer/consumer linkage. DX6 has an independent eight-byte code-section edit; its counter meaning remains unresolved. MP150-033 stays vendor-only pending direct lighting/colour evidence. Catalog counts unchanged; no runtime or database changes.

## DX6 counter structural purpose resolved

The [mode-catalog audit](original-modern-display-modes.md#dx6-public-mode-count-gains-its-leading-slot-in150) resolves the previously opaque6003bd3c cell as descriptor+3c public mode count.150 adds one for the leading public-table slot before the insertion arena. Retained callback/insertion/about bodies and loader-zero-fill boundaries are verified. Leading-slot state, all consumer bounds/device outcomes and visible modes remain untested; no taillight attribution or catalog label change.

## Screenshot partial-depth-local correction identified

The [three-build worker audit](original-modern-screenshot-pixels.md#historical150-correction-initializes-the-full-depth-local) verifies140→150 removes a WORD-write/DWORD-read mismatch in source-stride calculation.150/final core bytes match. MP150-034 is partial: scalar effects are derived, with no screenshot crash or XP-specific runtime result. Existing lifecycle/encoding limitations remain.

## Eight renderer/screenshot investigations reproduced

The [checkpoint](evidence/validation/renderer-screenshot-history-checkpoint.json) verifies eight selected script/output identities against reviewed HEAD, repeats each twice and checks protected artifacts before/after. It includes HUD preview, exit setup, loading budget, DX7 opt-in, fog mode/enable, menu context, DX6 count and screenshot depth-local evidence. Existing unresolved runtime/provider/bounds qualifications remain; the full comparison is incomplete. Follow the actual DX6 count consumers and direct lighting chain rather than redoing the resolved structural mapping.

## Selected DX6 count consumers qualified

The [consumer audit](original-modern-display-modes.md#dx6-extra-count-slot-reaches-inclusive-scans-but-can-fail-admission) verifies inclusive scans and150 eligibility ordering. The extra visited row is rejected under the documented N<100 zero-arena/insertion-only premises; N100, external writes and direct/same-current switching retain separate limits. Nearest fallback1 is not proof of an eligible record. This advances the count follow-up without a target run or catalog classification change.


## DX6 contextual gate reaches distinct provider requests

The [selected driver linkage](original-modern-state14.md#dx6-provider-distinguishes-the-menu-gate-payloads) verifies both140/150 selector15h dispatch and retained0/4 branches through the raw-state wrapper. The main-menu effective-payload change can select different raw requests; actual cache forwarding, menu-light submission and rendered repair remain qualified. MP150-033 remains vendor-only. The [vehicle-effect comparison](original-modern-state14.md#selected-vehicle-effect-bodies-remain-unchanged) separately establishes eight selected bodies unchanged across four EXEs; it does not establish state/input equivalence.
