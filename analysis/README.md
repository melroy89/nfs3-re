# Analysis and evidence

This directory contains reviewed research notes, retained evidence and reproducible analysis helpers.

- [Original versus Modern Patch: baseline, measured differences and remaining work](original-modern-differences.md)
- [Original versus Modern HUD preset source and default records](original-modern-hud-layout.md)
- [Original versus Modern loading artwork tiling and progress setup](original-modern-loading-artwork.md)
- [Original versus Modern menu navigation and multiplayer chat input](original-modern-menu-input.md)
- [Original versus Modern viewport reference geometry and aspect factors](original-modern-viewport-geometry.md)
- [Original versus Modern border geometry](original-modern-border-geometry.md)
- [Original versus Modern display-mode admission and sorted menu list](original-modern-display-modes.md)
- [Original versus Modern texture extent limits](original-modern-texture-limits.md)
- [Original versus Modern startup error mode, affinity and option defaults](original-modern-startup-policy.md)
- [Original versus Modern RAM pool size](original-modern-heap-initialization.md)
- [Original versus Modern endpoint defaults and colon-port parsing](original-modern-network-endpoints.md)
- [Original versus Modern network port menu and retry](original-modern-network-port-menu.md)
- [Original versus Modern screenshot input, format and worker paths](original-modern-screenshots.md)
- [Original versus Modern window initialization and callbacks](original-modern-window-handling.md)
- [Original versus Modern configuration lookup and defaults](original-modern-configuration.md)
- [Original versus Modern renderer loading and validation](original-modern-renderer-loading.md)
- [Modern Patch release-note traceability catalog](modern-patch-change-catalog.md)
- [Original versus Modern Patch x87 precision comparison](og-modern-x87-precision.md)
- [Line-boundary x87 caller-dependence audit](line-boundary-x87-callers.md)
- [First line-boundary C module and differential results](line-boundary-reconstruction-results.md)
- [Three-function reference-export results](reference-export-results.md)
- [Incremental C reconstruction readiness and staged blockers](recompilation-readiness.md)
- [Detailed findings and investigation history](detailed-analysis-notes.md)
- [Network roster admission and count contract](network-roster-admission.md)
- [Installed CARP physics profile inventory](evidence/inventories/controller-profile-inventory.json)
- [Installed car selector categories](evidence/inventories/installed-car-selector-categories.json)
- [Evidence categories and provenance](evidence/README.md)
- [Helper scripts, dependencies and rerun commands](scripts/README.md)
- [Temporary-artifact review](temporary-artifact-review.md)

Markdown findings remain here; JSON evidence is grouped under `evidence/`, scripts under `scripts/`, and new raw captures under ignored `captures/`. Evidence includes runtime observations, isolated instruction probes, installed-asset inventories, static calculations and historical audits. Each has different limitations; naming coverage does not imply complete behavioral validation. Historical findings retain their original confidence and limitations.

For each finding, record:

- Target filename and SHA-256 (see [target provenance](../docs/TARGET.md)).
- Ghidra version, address space, address, and relevant function or symbol.
- Observed facts and the evidence supporting them.
- Interpretation, confidence, and unanswered questions.
- Checks performed, including whether runtime behavior was actually tested.

Use Markdown for small, reviewable findings. Follow [the sharing workflow](../docs/SHARING.md) before including exported annotations. A note on one executable version does not automatically apply to another.
