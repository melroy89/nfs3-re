# Analysis and evidence

This directory contains reviewed research notes, retained evidence and reproducible analysis helpers.

- [Detailed findings and investigation history](detailed-analysis-notes.md)
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
