# Three-function reference-export results

**PASS for the fixed sample:** two independent runs each produced three `.c` and three `.h` files. All six corresponding C/header files match byte-for-byte; all three serialized options files also match. This establishes repeatability for these reference samples, not compilation, C equivalence or whole-game reconstruction readiness.

## Baseline and retained artifacts

- Saved Git baseline: `add636a2a9b558f86fc066a7fbd42d67485580ed`; Ghidra 12.1.4 PUBLIC, Java 21.0.12.1, language `x86:LE:32:default`, compiler specification `windows`.
- Executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
- Saved `db.3144.gbf` SHA-256: `00b157c74363b3d10efd1138c537d7127f7bbf7cd97dfbf52dc4ccbb86fa2c5a`.
- Configuration digest: `eb696b46be8ff5e41c1ae90a6c882582f9b64ce2348d58214224420ec7793d56`. The manifests pin exporter/source/native-decompiler hashes, runner hashes, effective options hashes, locale and Java version.
- [Run 1 manifest](captures/reference-exports/add636a2a9b558f86fc066a7fbd42d67485580ed/eb696b46be8ff5e41c1ae90a6c882582f9b64ce2348d58214224420ec7793d56/run-1/manifest.json) and [Run 2 manifest](captures/reference-exports/add636a2a9b558f86fc066a7fbd42d67485580ed/eb696b46be8ff5e41c1ae90a6c882582f9b64ce2348d58214224420ec7793d56/run-2/manifest.json) contain baseline, selection, options, per-entry outcomes, output hashes, diagnostics, inline warnings and exclusions.
- [Raw comparison](captures/reference-exports/add636a2a9b558f86fc066a7fbd42d67485580ed/eb696b46be8ff5e41c1ae90a6c882582f9b64ce2348d58214224420ec7793d56/comparison.json); [tracked metadata and comparison evidence](evidence/audits/reference-export-repeatability.json).

Raw export root (relative to the repository):

```text
analysis/captures/reference-exports/add636a2a9b558f86fc066a7fbd42d67485580ed/eb696b46be8ff5e41c1ae90a6c882582f9b64ce2348d58214224420ec7793d56/
  configuration.json
  comparison.json
  run-1/  # 00485c30, 004abd9c, 00518640: .c + .h + options + logs/results; manifest.json
  run-2/  # same six C/header filenames; separate manifest.json
```

The generated files remain in the existing ignored `analysis/captures/` tree. The curated metadata/report and export helpers are tracked; these reference files are not maintained reconstruction sources. Manifests include hashes for every exported C/header, all selected body fingerprints and all warnings. Raw run manifests differ in elapsed times/log identities; those differences are expected and were not treated as source-output equality. Their configurations, selected bodies, per-entry outcomes and inline-warning lists agree.

## Coverage, warnings and failures

| Entry | C bytes per run | Header bytes per run | Run 1 vs run 2 | Inline warnings per run |
|---|---|---|---|---|
| `00485c30` | 7084 | 137 | Identical | 2 |
| `004abd9c` | 9435 | 92 | Identical | 1 |
| `00518640` | 2411 | 93 | Identical | 1 |

Each run: **3 successes, 0 failures, 0 timeouts, 0 cancellations**. Across both runs: six successful attempts covering three unique functions. No `Unable to decompile` placeholder, incomplete preflight result, missing output, process diagnostic or exporter-log error was found. Both run manifests record unchanged isolated database hashes; the working executable and database hashes remained unchanged as well. No Ghidra annotation/byte changes were made.

Exclusions per run: 4,130 other local functions and all 207 external entries. This is not a whole-program export; caller bodies and unrelated dispatcher investigation remain excluded.

Inline warnings are **not** the same as failed exports:

- `00485c30`: “Globals starting with '_' overlap smaller symbols at the same address” and “Unknown calling convention”.
- `004abd9c` and `00518640`: “Unknown calling convention” each.

The runner's process/decompiler diagnostics were empty. A post-export text inspection added complete inline warning comments to each manifest's `post_export_inspection`; `warning_counts` records four such comments per run. No warning was erased, corrected or waived as ABI/data-layout proof.

## Cleanup required before later reconstruction

| Sample / boundary | Observed reference-output issue | Required follow-up |
|---|---|---|
| All three | Headers omit includes/support definitions and use Ghidra names such as `uint`, `byte`, `undefined*`; prototypes carry unknown-convention warnings | Define explicit ILP32 types and the maintained test ABI; implement an original-register adapter separately. Do not regard these headers as original ABI declarations. Whole-program datatype emission was deliberately off. |
| `00485c30` | Global declarations are `undefined g_fLineBoundaryCandidateComponent0/1`, while float accesses use underscored names; `ABS()` has no definition | Reconcile the two original addresses with one eight-byte binary32 scratch object and preserved aliases. Define bit/float operations from instructions and preserve scratch lifetime, mask writes and rejection behavior. Do not edit the raw exports. |
| `00485c30` floating point | Ordinary-looking float arithmetic/comparisons do not encode every x87 intermediate, spill, unordered predicate or status effect | Follow the existing instruction contract and [comparison plan](recompilation-readiness.md#7-behavioral-comparison-plan); do not replace bit tests or unordered behavior with an assumed standard helper. |
| `004abd9c` | `float10` return, opaque vehicle offsets, inferred globals with no original initializers, and signedness/rounding not fully expressed by convenience types | Retain ST0 physical-return contract and binary32 rounding stages; map actual constants/session flags and signed predicates explicitly if this function is reconstructed later. This remains a reference sample, not module one. |
| `00518640` | Pointer ordering, pointer/int arithmetic and `undefined2/4` loads/stores stand in for machine copy loops; DS/ES and DF effects are only described in comments | Model width, wrapping, alias/alignment and segment/direction behavior; do not mechanically translate to ISO C or declare unrestricted memmove equivalence. This is not module one. |
| Referenced globals | Exporter emits declarations/definitions, not recovered PE initialization, resource contents or a complete data image | Establish required initialization/storage/link symbols from the data evidence before linking any maintained module. |
| Embedded annotations | Large saved plate comments are copied into reference bodies, including historical investigation qualifiers | Preserve them as reference provenance. Curate maintained documentation separately; emitted comments are not execution evidence or proof of semantic equivalence. |

These findings affect **module compilation/linking** and later **runtime validation**. The bounded **reference-export** gate is now passed for this sample. No maintained source cleanup, toolchain installation, C compilation/linking or new instruction probes were attempted.

## Reproduction and next gate

The [Python coordinator](scripts/export_reference_samples.py) and [Ghidra script](scripts/ghidra/ExportReferenceSample.java) select only the three allowlisted addresses, verify their body hashes, use read-only/no-analysis snapshot opens and enforce 30-second decompile / 120-second process deadlines. Both runs use independent copies from the same Git archive and fresh per-entry processes. Effective decompiler options are serialized beside each sample; six C/header hashes and three options hashes were compared without normalization.

```sh
python3 analysis/scripts/export_reference_samples.py \
  --baseline add636a2a9b558f86fc066a7fbd42d67485580ed \
  --ghidra /home/melroy/Documents/ghidra \
  --java-home /usr/lib/jvm/java-21-openjdk-amd64
```

The coordinator refuses to overwrite an existing configuration/run directory. Preserve the completed runs before any future rerun; use a separately retained checkout/output namespace rather than deleting or overwriting evidence. Inline source warnings additionally require text inspection as performed above; the coordinator's initial diagnostics cover process/decompiler/exporter messages.

**Subsequent phase:** the authorized first leaf has now been implemented and functionally tested; see [its separate results and remaining machine-state gates](line-boundary-reconstruction-results.md). These reference-export files and hashes remain the original saved-baseline artifacts.
