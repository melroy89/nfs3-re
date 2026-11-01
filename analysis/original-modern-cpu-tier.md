# Original versus Modern: CPU rating and default-settings tier

## Evidence boundary

Static comparison of the supplied original/backup and official Modern v1.6.1; exact fingerprints and provenance limits are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_cpu_tier_difference.py` (Python pefile, GNU objdump). The [manifest](evidence/audits/original-modern-cpu-tier.json) retains producer/consumer spans and Modern byte tables. No CPUID, benchmark, game or instruction probe was executed.

## Same global, different units

Original routine `004f1ef0` computes a frequency-like estimate through multiple helper calls and x87 comparisons, multiplies the selected integer by **1,000,000**, stores it at **`005652a4`** and returns it (`004f2076..004f208c`). The caller's division by one million and thresholds below support this interpretation. The calibration helpers and accuracy of the estimate are not fully reconstructed here; this is not a measured clock speed for the current PC.

Modern's CPU capability routine `004f1c70` instead stores a small **feature/family score** at the same address (`004f1df5`). Its directly inspected standard-leaf path sums:

| Contribution | Observed test | Increment |
|---|---|---:|
| Basic family field at least 6 | `(CPUID-result EAX >> 8) & 15 >= 6` | 1 |
| Feature EDX bit 23 | byte `[ESP+0x0a] & 0x80` | 1 |
| Feature EDX bit 25 | byte `[ESP+0x0b] & 2` | 1 |
| Feature EDX bit 26 | byte `[ESP+0x0b] & 4` | 1 |
| Feature ECX bit 0 | byte `[ESP+0x0c] & 1` | 1 |

Maximum contribution sum is **5**. Wrapper `0050ea85` writes CPUID results in the nonstandard memory order **EAX, EBX, EDX, ECX**; using the more familiar EAX/EBX/ECX/EDX layout would swap feature interpretations. Leaf 1 is selected through `004f1e68 -> 004f1d49` on the ordinary standard path. Intel identifies these standard feature bits as MMX, SSE, SSE2 and SSE3. [Intel feature table](https://www.intel.com/content/www/us/en/developer/articles/technical/trusted-cpu-feature-detection-library-for-intel-software-guard-extensions-intel-sgx.html)

The routine retains vendor/legacy branches, including a path requesting leaf `80000001`, and only extracts the **basic** family nibble at `004f1d59`; do not infer modern extended-family decoding or apply the standard-leaf feature names universally to extended-leaf output. Missing-CPUID/early-return paths and all initial states require separate treatment. Family below 5 triggers a diagnostic call after the score store; this does not by itself establish the complete minimum-CPU/runtime contract.

Modern startup directly calls `004f1c70` at `004a3e07`. The original rating routine's former address space is reused by other Modern helpers/NOP areas; same-address disassembly is not a corresponding frequency routine.

## Default graphics tier consumer changes with it

Original default initializer calls CPU detection, then the estimate routine, divides its EAX result by 1,000,000, and chooses ECX tiers using signed comparisons (`00472d89..00472de3`):

| Returned quotient | ECX tier |
|---|---:|
| ≤166 | 0 |
| 167..200 | 1 |
| 201..233 | 2 |
| 234..266 | 3 |
| >266 | 4 |

A separate preceding capability condition can leave the initial tier at 4 without the estimate call. This table describes the shown estimate branch, not every original processor.

Modern loads `[005652a4]` directly at `00472d11`, caps it to unsigned **5**, then halves it for renderer mask bits 1/2 before indexing compact byte tables. It therefore consumes the new score, not a raw frequency or MHz quotient. The [resolution-default comparison](original-modern-resolution-defaults.md) follows the resulting tier into fixed/sentinel resolution requests. The exact six-byte tables are retained without inventing names for every target setting.

## A second consumer is also changed

In matched neighborhood `0049616c..004961aa`, original compares `[005652a4]` against **133,000,000** and **200,000,000** to select ECX=1,2,3. Below 133,000,000 it also forces stack field `[EBP+0x7e]=1`.

Modern instead computes signed `score-1`, clamps it to **1..3**, and forces that stack field to 1 when the unclamped result is at most 1. Thus ordinary scores 0..2 select 1, score 3 selects 2, and scores 4..5 select 3. This verifies coordinated producer/consumer changes. The full containing feature's semantics and helper outputs are not reconstructed here, so the field is deliberately not given a guessed gameplay meaning.

## Interpretation and remaining work

Verified: the global's changed units, the directly inspected score arithmetic, default-tier consumption and the second threshold consumer. Inferred: the original million-scaled quantity represents a CPU-frequency estimate, based on its producer and consumer arithmetic. Unresolved: full original calibration, all vendor/legacy feature branches, every alias/indirect consumer and runtime default choices on specific CPUs/VMs.

This score does not prove the game uses SSE instructions for racing physics, measure actual execution speed, change x87 precision policy or establish replay/multiplayer compatibility. Those are separate investigations. No historical release-note entry is marked fully verified merely because this mechanism exists in the final binary.

The [movie admission follow-up](original-modern-idle-movie.md#follow-up-playback-wrapper-relocated-path-and-cpu-tier-input) now identifies the `0049616c` consumer as the wrapper preparing `00495bc0` movie playback. ECX1..3 is passed through frame-buffer setup to display-conversion selector `008ca2cc`; its distinct raster paths are now traced there. Precise filtering and visual-quality acceptance remain unverified.

## Removed calibration-helper span

The [CPU-tier audit](evidence/audits/original-modern-cpu-tier.json) now captures **`004f1ff0..004f22b0`**, a704-byte span entirely NOP-filled in official Modern. It includes the tail of the original frequency-like estimator already discussed above, plus complete original helpers`004f20b0..004f216d`, `004f2170..004f21bd` and`004f21c0..004f22af`. It is not a single original function beginning at`004f1ff0`; disassembling that address alone starts inside an instruction. Complete helper captures start at their inspected entries.

The helper at`004f20b0` conditionally executes RDTSC at`004f20de` and`004f20fc` around calls to`004f06e0`, computes a difference, and repeats sample-selection logic. The helper at`004f2170` counts iterations of a fixed integer DIV workload while polling timestamp`0079c1a4` until a signed elapsed/count comparison ends the loop. The surrounding`004f21c0` invokes that workload repeatedly and combines sample values with CPU-related state. These instructions support classification as **legacy CPU/timing calibration code**, rather than unidentified gameplay code. Exact calibration accuracy, timestamp updates and all exceptional cases remain unresolved.

Modern’s feature-derived CPU tier is documented above. NOP replacement of this old span does not imply removal of CPU identification or all timing facilities, nor that a measured clock speed can be recovered by reading the repurposed tier global. This pass adds byte/role classification to the outside-body index; it does not rerun a benchmark or claim performance effects.

## Original scaled-difference helper has an asymmetric negative branch

The expanded CPU-tier audit captures complete original **`004f1ea0..004f1eea`** (74 bytes), asserts its comparison/branch/multiply instructions and exact binary64 constant **`0054c9b0=-8.0`**, and checks seven direct CALL operands in the already captured estimator. This explains original-only status-reader candidate **`004f1ec4`**. Modern reuses this address region for optional module/export resolution; that is not a corresponding implementation of the old arithmetic helper.

Inputs are EAX and EDX DWORDs plus one binary32 stack scale. It subtracts EDX from EAX modulo2^32, interprets that low DWORD as signed for FILD, and multiplies by the scale using ambient x87 state. The product is first stored to binary32 **without popping**, then stored to binary64 while popping. The local comparison is **0 versus the binary64 copy**, not a comparison against the original extended product or the first binary32 result.

| Non-trapping comparison result | Returned ST0 |
|---|---|
| Ordered product below0 | Reload binary64 copy, multiply by−8, store/reload binary32 |
| Ordered product>=0, including equal zero | Reload the initial binary32 copy |
| Unordered comparison | JA is not taken; reload the initial binary32 copy |

Thus the helper is neither a plain scaled subtraction nor an absolute value: negative products receive an8× magnitude multiplier, while nonnegative products do not. Retaining both spill formats matters for instruction-faithful reconstruction. Do not implement the initial subtraction as unchecked signed C subtraction or discard the binary64/binary32 boundaries because the inputs usually look small.

The verified calls at `004f1fed`, `004f1fff`, `004f2011`, `004f2025`, `004f2037`, `004f2052` and `004f2064` lie in original estimator `004f1ef0`. They pass scale bits for1.0, approximately1.1 and approximately1.2 and feed later sample-selection comparisons. This grounds the helper's calibration context; exact estimator units, rationale for−8, accuracy and real measurements remain unresolved. It is not identified as racing physics, replay arithmetic or a change in Modern's simulation precision.

The helper uses RET4 and returns a binary32-derived value on ST0. EAX contains subtraction/status residue rather than a useful scalar result; EDX and other non-frame general registers are not locally written. EBP is saved/restored, and the temporary x87 stack reaches two additional entries before leaving one result. No local control-word reset establishes all caller modes, exception behavior or arbitrary input safety. The evidence is static only; no calibration helper, CPUID, benchmark or instruction probe was executed.

## Named default choices are now mapped

The [named-option follow-up](original-modern-resolution-defaults.md#named-graphics-defaults-and-the-limits-of-automatic-high-settings) connects the feature-derived tier to exact descriptor labels, verifies ECX preservation across the two intervening mode calls and separates renderer halving from selected-mode overrides. Score5 with mask6 clear selects High/Full table entries; the same score with mask6 nonzero uses tier2 and several lower labels. This partially supports MP100-010 without asserting unconditional best graphics, every startup or actual CPU/display behaviour.
