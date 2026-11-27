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

## Original MMX detection allows an ISMMX override

On the standard CPUID leaf 1 path, both versions first publish EDX bit 23 to `005643b4` (original store `004f1dd4`, including the zero branch at `004f1e76`, and Modern store `004f1db8`). Original then passes the file-backed key `ISMMX` at `0054c9a8` to `0050ead0` at `004f1e06`. If that lookup returns a non-null pointer, `004f1e13` calls the signed decimal parser `004f0430` and overwrites `005643b4` with the full parsed value. A null result branches to the shared epilogue and retains the detected bit. This cell is read by the [line-boundary implementation dispatcher](line-boundary-x87-callers.md).

Final Modern replaces that local lookup and overwrite with its CPU score store, family diagnostic check and jump to the shared epilogue. The old call, result store and alternate epilogue at `004f1e13..004f1e26` are 19 NOPs. Reproduce with `objdump -d --start-address=0x4f1d44 --stop-address=0x4f1e26` on the paired executables and confirm the original key with `objdump -s --start-address=0x54c9a8 --stop-address=0x54c9b0`. This establishes removal of the override from this detection path. Other writers and actual machine-specific dispatch remain outside this check.

The original lookup at `0050ead0..0050eb29` reads the runtime environment vector at `00a0b154`. It compares each entry against the key up to the key length, requires an immediately following equals sign and returns the address after that sign. An existing empty value therefore reaches the decimal parser, which returns zero when no digits are consumed. An absent key leaves the detected flag in place. See the [environment lookup comparison](original-modern-renderer-loading.md) for the shared reader.

Modern **1.1.0** stores the detected MMX value at `004f1dbd` and jumps back to the common epilogue at `004f1dfe` after publishing its CPU score. The original override tail is all NOPs in that build and every later retained release. The [recovered 1.0.0 comparison below](#modern-100-already-uses-the-feature-score) dates the observed removal to the first retained release.

| 1.1.0 input | SHA-256 |
|---|---|
| `nfs3_modern_patch_v1.1.0.7z` | `31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac` |
| `nfs3.exe` extracted with `7z x -so <archive> nfs3.exe` | `59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72` |

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

## Original signed wrapping can select the lowest class

**Confidence: verified producer/consumer instructions; examples derived arithmetically. Work status: done for this local mechanism, partial for MP100-028’s full hardware-detection claim.** The expanded [CPU audit](scripts/audit_cpu_tier_difference.py) asserts the original multiply/store, signed-division sequence and movie signed thresholds. Its [manifest](evidence/audits/original-modern-cpu-tier.json) records the derivation and twelve hypothetical inputs. No benchmark, CPUID, movie or original instructions were run.

At`004f2076`, the estimator multiplies EDI by **1,000,000 using32-bit IMUL**. It moves the low DWORD to EAX and global`005652a4`; the captured return tail does not test multiplication overflow. Let **N** be the integer reaching this instruction, not a measured host frequency. The stored bits are `(N*1000000) mod2^32`.

On the admitted default-rating path, caller`00472dab..00472db7` sign-extends returned EAX with`MOV EDX,EAX; SAR EDX,31`, then executes **signed IDIV1,000,000**. Its signed threshold ladder selects the tiers already listed above. Movie wrapper`00496175` separately compares the stored global **signed** against133,000,000 and200,000,000.

| Hypothetical N before multiply | Stored signed DWORD | Default quotient, truncating toward zero | Default tier before renderer reduction | Movie conversion selector |
|---:|---:|---:|---:|---:|
|2147 |2,147,000,000 |2147 |4 |3 |
|2148 |−2,146,967,296 |−2146 |0 |1 |
|2200 |−2,094,967,296 |−2094 |0 |1 |
|3000 |−1,294,967,296 |−1294 |0 |1 |
|4000 |−294,967,296 |−294 |0 |1 |
|4294 |−967,296 |0 |0 |1 |
|4295 |32,704 |0 |0 |1 |
|5000 |705,032,704 |705 |4 |3 |

For nonnegative integer N,2148 is the first value at which this multiplication crosses the signed32-bit positive boundary. The table supports the vendor’s **signed overflow→low class** mechanism, conditional on calibration producing such an input and the consumer taking this path. It is not a verified2.148GHz hardware threshold: the full estimator’s calibration, timing, input formation and units remain incompletely reconstructed. The separate original capability branch can bypass estimation and retain initial tier4.

“Thinks it is a166MHz processor” is therefore shorthand for **selecting the lowest `quotient<=166` default class**, not an instruction that replaces the stored global with166 or166,000,000. Movie selector1 is also chosen for negative stored values, and the wrapper forces local field+7eh to1 below the signed133-million threshold. Downstream conversion paths are traced in the [movie chapter](original-modern-idle-movie.md#follow-up-cpu-tier-reaches-display-conversion-with-unchanged-consumers); exact perceived video quality remains untested.

The5000 example matters: repeated modulo2^32 wrapping means **not every larger N selects the lowest tier**. A saturating arithmetic explanation, or an unqualified statement that every fast CPU is misdetected identically, would contradict the inspected instructions.

Modern replaces the shared quantity with the feature/family score and changes both consumers, avoiding this specific frequency-like multiply/divide contract on the reviewed paths. That is coordinated static evidence, not proof of accurate speed measurement, every legacy CPU branch or all hardware-detection fixes. Precise1.0.0 introduction and actual behavior on a particular machine remain unverified.

For an original-faithful C reconstruction, use explicit32-bit wrapping, signed reinterpretation and truncation-toward-zero division under a validated domain. Signed C multiplication overflow cannot model this contract safely; silently widening/saturating it would change the original’s results. Modern’s small score must remain a distinct version-specific field meaning rather than being fed into original frequency thresholds.

## Older CPU warning in 1.4.0

Retained 1.4.0 tests DWORD `005643ac` at `004f1dfb` after computing the score. The standard detection path sets that cell at `004f1d91` for a basic CPUID family of at least 5. If the cell is zero at the test, the code passes the string “Your CPU is too old. i586 and newer are recommended to operate properly.” at `0053ca37` to `004b573c`. That helper calls `MessageBoxA` with flags `0x51031`, then calls the termination thunk only when EAX is 2 (Cancel). The corresponding 1.3.1 tail has no warning call. This establishes static support for MP140-074 on the inspected path. Other vendor and no-CPUID paths, actual dialog behavior and operation on older hardware remain unverified.

The same dialog behavior persists in every retained release from 1.4.0 through 1.6.1. The call at `004f1e09` moves among helper entries `004b573c`, `004b56e0`, `004b5704`, `004b5714` and `004b5728` as surrounding code shifts. Each 30-byte helper has the same instructions apart from the relative call displacement to termination thunk `004f2a7d`. The import slot still resolves to `MessageBoxA`. It calls the thunk only for return value 2. Other values proceed to the helper's RET. This verifies the local Cancel policy across these releases without requiring the dialog to be exercised.

The family flag itself predates the warning. Original and final Modern both zero `005643ac` at `004f1cb8` on entry, then set it to 1 on the inspected CPUID path for family 5 or higher. Original continues through its feature tests and optional `ISMMX` lookup without the Modern warning on that path. Both executables branch at `004f1ccb` to the same no-CPUID fallback when `0050ea68` returns zero. The fallback calls `0050eaa7`, stores EAX to `005643c8`, restores registers and returns without reaching the new dialog. Thus the warning is an added consumer of the existing family flag on the path that reaches the score tail. Other startup checks remain outside this comparison.

### Modern 1.0.0 already uses the feature score

Extract the root EXE from the [pinned 1.0.0 archive](original-modern-dll-candidates.md#recovered-100-package-separates-code-changes-from-renames)
and compare PE RVA `f1c70` for `200h` bytes with 1.1.0. The entire
span matches (SHA-256
`e51b0598373a517cfddb360e69ef3a38476e715a1fc76b1c206e54e476800910`),
including the MMX and score publications and the 19 NOPs at
`004f1e13..004f1e26` that replace the original `ISMMX` override tail.
The defaults prefix at `00472d10` also matches for `36h` bytes,
including the direct score read, cap and renderer-dependent adjustment.
This dates both the selected scoring mechanism and the local override
removal to 1.0.0. Other writers and the actual hardware-selected tier
remain outside the comparison.
