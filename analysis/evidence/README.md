# Retained analysis evidence

These are historical evidence artifacts, not current completion reports. Organization does not revalidate their conclusions or close open questions.

| Category | Establishes | Limits |
| --- | --- | --- |
| `runtime/` | Observed scenario-specific memory states and capture-derived reconstructions | Non-atomic reads; reconstructed geometry is not an instruction trace or full x87 emulation |
| `probes/` | Tested behavior of isolated extracted instructions | Input coverage and harness stubs apply; does not establish game caller reachability |
| `inventories/` | Properties of the inspected build and installed assets | Other builds/installations may differ |
| `static/` | Analytical witnesses/calculations under stated assumptions | Runtime admission is not implied |
| `audits/` | Historical backlog and evidence-link review | Link existence is not semantic validation; old statuses are not current conclusions |

All 60 original JSON artifacts were moved without changing their bytes. [Migration manifest](migration-manifest.json) records old paths, destinations and SHA-256 hashes. Source paths and links embedded inside historical JSON are intentionally unchanged: use this mapping to locate moved counterparts. Older absolute paths identify the original workspace, not a portable API.

Keep reviewed evidence tracked, including large retained sample sets. New raw captures belong in ignored `analysis/captures/`; generated reruns should go there until reviewed. No evidence was pruned or compressed, and Git history was not rewritten.

See [helper commands and capture dependencies](../scripts/README.md), [temporary-artifact decisions](../temporary-artifact-review.md), and the [detailed analysis notes](../detailed-analysis-notes.md).
