# Original versus Modern: renderer callback and video-mode lifecycle

## Evidence boundary

Static analysis of the supplied original/backup and official Modern v1.6.1. Exact executable hashes and provenance limitations are in the [loader report](original-modern-renderer-loading.md). The [selection/lifecycle manifest](evidence/audits/original-modern-renderer-selection.json) retains hash-pinned spans and asserts a shared tail is byte-identical. Reproduce with `python3 analysis/scripts/audit_renderer_selection_difference.py`. No game, driver or instruction probe was executed; no executable/database changed.

## Original indirection versus Modern direct entry

Original selector branches call `004f8830` and `004f8930` after loading, as mapped in the [initialization report](original-modern-renderer-initialization.md). `004f8830` tests about-export slot `009ef980`. When present, it installs five internal callbacks at `00567dc4`, `00567dcc`, `00567dd0`, `00567dd4` and **`00567dc8`**, the last pointing to **`00517610`** (`004f8844..004f887a`). Missing about export follows a diagnostic path, rather than installing those callbacks on the inspected branch.

`004f8930` first calls `004df740` with EAX=0 and allocates the backing pool through `004f92d0` if `005644fc` is null. When `00564364` is zero, it applies environment settings and calls `005089d0` with values from `00564384/88/8c`. That dispatcher loads callback slot `00567dc8` and, if nonzero, calls through it (`005089d8..00508a15`). Thus **original `00517610`**, not same-address `00517620`, is the relevant video-initialization counterpart.

Modern initializer instead calls **`00517620` directly at `004b5aa3`** and tests its return. This establishes removal of that particular indirection from the inspected startup path; it does not prove every old callback slot is unused throughout Modern.

## Parameters and mode selection change

Original `00517610` takes width in EAX, height in EDX and depth in EBX, copies width/height into ECX/ESI, checks the backing pool, and normalizes defaults. Width/height zero become 640/480; either -1 becomes 1024/768 respectively. Depth zero, -1 or 15 becomes 16. Those behaviors follow explicit branches, not a guessed C prototype.

It calls `005247c0` with the selected values, initializes the platform path if needed, and chooses hard-coded video-mode IDs through width/height comparisons before `_THRASH_setvideomode@12` at `005176a4`. The full ID-to-resolution table is not inferred here.

Modern `00517620` no longer reads those three input registers as requested dimensions. After its platform setup, it:

1. Calls `_THRASH_selectdisplay@4` (`009ef944`) with `[007a3a70]` at `00517665`.
2. Calls about-refresh helper `004f853c`, which stores a newly returned descriptor at `007a3a5c`.
3. Pushes `[0056438c]`, `[00564388]`, `[00564384]` and calls mode lookup `004bedcc`, storing its result at `0055fec0`.
4. Calls `_THRASH_setvideomode@12` (`009ef958`) with that mode result and literal arguments 2 and 1, then tests EAX at `0051769c`. Zero returns through the failure epilogue **before** the common tail.

The export identities are verified by the retained 34-name binding map. Original falls through after its corresponding setvideomode call without testing EAX there. Modern's mode lookup replaces the original local hard-coded selection branches, but mode enumeration/provider behavior and complete failure recovery remain outside this chapter.

## A retained tail with different entry conditions

Bytes **`005176aa..0051776b`** are exactly identical in the two executables; the manifest asserts this, rather than relying on visual similarity. This tail conditionally releases four stored objects through `00509b10`, clears their slots, handles `005643e0`, sets `00564364` to 1, calls `005179d0` for one or two records, then writes current width/height from `00565030/34`.

The common bytes do not imply identical lifecycle behavior: Modern can skip them on a failed setvideomode return, and its preceding display/mode selection differs. At the end, original calls imported ADVAPI32.RegFlushKey at `00534468` after pushing `0x80000000`; Modern instead calls `004beeb0` with `[0055fec0]`. The import identifies the original API, but its intended role/error handling and the complete effects of Modern’s descriptor-based mode helper remain unresolved here. Both success paths return EAX=1.

## Original hard-coded environment setup

Before its callback dispatch, original `004f8930` invokes environment helper `004f8b50` with:

| Names | Value | Replacement flag |
|---|---|---:|
| `SST_VIDEO_24BPP`, `FX_GLIDE_SHAMELESS_PLUG` | Empty string | 0 |
| `FX_GLIDE_NO_SPLASH`, `SST_DUALHEAD`, `SSTV2_DUALHEAD` | `1` | 1 |
| `SST_RGAMMA`, `SST_GGAMMA`, `SST_BGAMMA`, `SST_GAMMA` and four `SSTV2_` gamma names | `1.0` | 1 |

These values are read from the original PE and their call operands. Empty strings have special handling in the helper; do not equate the first row with unconditionally replacing an existing value. The earlier Voodoo selector also performs environment writes, documented separately; order matters.

Modern's smaller initializer does not contain this block. It instead has the configuration-driven `ENV` section path traced in the loader chapter. This supports a local hard-coded-to-configurable mechanism change, not proof that all environment manipulation disappeared or that each driver's shipped INI reproduces every original value.

## Further evidence required

The [mode-selection comparison](original-modern-mode-selection.md) now traces the original ID decision tree, Modern search rules and final record publication. Pending: complete resize/helper semantics, callback/storage users outside startup, platform helpers and actual driver acceptance/failure behavior. The original `004f8930` post-initialization path and Modern `004f8548` share several calls but differ in timer/input/callback setup; their full equivalence is not claimed. Historical release attribution and runtime compatibility remain separate questions.

## Final Glide init failure now connected to platform callers

The [paired driver follow-up](original-modern-glide-reference-identity.md#thrash-init-retries-provider-setup-and-has-a-separate-failure-channel) connects the final Glide init export to EXE slot009ef978 at0052473a. Its admitted path retries internal provider setup independently of the about cache; provider failure returns0. The EXE branches to cleanup, whose wrapper then returns current platform byte0056aff0. If that returns0,00517620 skips later display/mode work and startup reaches its existing init diagnostic. This is conditional static propagation, not observed recovery/termination or proof that every cleanup callback preserves zero.

## Gameplay exit skips frontend mode setup from150

**Verified shutdown admission change and selected action/state chain; OS display result untested.** The [exit-mode audit](evidence/audits/gameplay-exit-mode-history.json), reproduced with `python3 analysis/scripts/audit_gameplay_exit_mode_history.py`, pins original, author-hosted1.4.0/1.5.0 and official final EXEs. It captures complete shutdown bodies and retained route spans.

| Stage | Original/1.4.0 |1.5.0 |Final |
|---|---|---|---|
|Shutdown entry`004a35d0` |Always enters setup, saves incoming EAX in ESI |PUSHAD; TEST EAX,EAX; JE`004a365b` |Same zero-input gate, JE`004a3657` |
|Zero input |Performs frontend mode/viewport setup; skips later conditional`00495600` call |Skips setup and`00495600`, reaches cleanup |Same admission policy with changed cleanup |
|Nonzero input |Performs setup and conditional call |Performs setup and now-unconditional-on-that-path call |Same admission policy; mode/FOV/cleanup details differ |

Historical1.4.0/1.5.0 setup bytes`004a35d9..004a3652` are identical. The block loads configured frontend mode index`0055fec8` and calls original-role mode application`004bef50`; final uses`004beeb0`, as the [existing mode report](original-modern-mode-selection.md) qualifies. At`004a361d/004a3622`, retained instructions load ECX480 and EBX640 before calling viewport helper`004352d0`. Thus the skipped work contains both a frontend mode-application request and explicit640×480 viewport arguments. **The constants are not proof that the requested OS mode is always640×480:** mode application uses the configured index and driver descriptor, can fail, and has changed internals. Final also uses a different FOV argument representation and cleanup sequence; this is not whole-shutdown equivalence.

### Checked exit state reaches the zero-input branch

The audit retains the following chain, identical in all four builds within its explicit spans:

1. The confirmation callback`0044b0f0..0044b164` can publish byte`00559251=1` and return action10 for its accepted branch. Other selection/cancel paths remain distinct.
2. The in-race action mapping at`0044bcf6..0044bd3b` converts action10 to return5. The caller at`004c4c07` invokes in-race menu processing, then mediates the result through`004c5720`; **network mediation can change the result**, so the next step is conditional on accepted action5.
3. The accepted action5 arm`004c4d35..004c4d6f` performs cleanup, explicitly sets ECX1 and ultimately stores ECX into terminal state`007d36b4`. Its intervening finalizer`004ce750..004ce7ff` saves/restores ECX and is byte-identical in all four builds, supporting that published1 rather than assuming a register survives a call.
4. At`004a3829..004a3840`, the retained postrace caller maps terminal state1 to EAX0, other states to EAX1, then calls shutdown`004a35d0`.

The new zero-input gate therefore suppresses the inspected frontend mode/viewport transition on this accepted terminal-state1 route while retaining cleanup. The original's zero input only controlled the later conditional call, after setup had already happened. The complete captured shutdown envelopes end at`004a3684` (original/140), `004a3680` (150) and`004a3681` (final); the raw body identities and disassembly are retained separately.

**MP150-035 advances to partial static support:** the advertised140→150 boundary contains a concrete mechanism for avoiding the unnecessary frontend display transition on the checked gameplay-exit route. Actual desktop resolution, all exit paths, provider behaviour, callback admission, mediator outcomes and transitive cleanup remain unverified. Retained local code does not establish complete network or lifecycle equivalence. Reconstruction must preserve the conditional setup/cleanup split and register contract, rather than removing shutdown wholesale. No game, mode API, driver, new instruction probe, compiler or Ghidra write was used.
