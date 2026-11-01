# Effect rendering: extend renderer-mask admission from 40h to 50h

## Evidence and complete coverage boundary

Eleven same-address original/Modern functions have exactly one changed byte each: the immediate of a byte TEST changes from `40h` to `50h`. All other bytes in their complete envelopes, totaling 17,448 bytes, are identical. The [reproducible audit](scripts/audit_effect_renderer_masks.py) checks both pinned executable hashes, the exact TEST encodings and all 256 possible byte inputs; [its manifest](evidence/audits/effect-renderer-masks.json) retains full-span hashes, disassembly locations and the input set where the predicate changes. No renderer, game or instruction probes were executed.

| Entry / saved Modern label | Envelope end, exclusive | Changed immediate address |
|---|---|---|
| `0041a120` BuildThreePayloadRecordAndAdvanceCursor | `0041a354` | `0041a1c8` |
| `00491190` QueueProjectedBlinkingPointEffectQuads | `00491bb8` | `00491225` |
| `00491bc0` BuildWeatherMaterialProjectedQuadRecord | `00492362` | `00492208` |
| `00492370` BuildAndQueueRotatedProjectedQuad | `00492973` | `004925a2` |
| `00492980` BuildAndQueueProjectedCircularStripSegments | `00493361` | `00492c15` |
| `0049d800` SetGeometryPackedColorsWithRenderFade | `0049d8eb` | `0049d814` |
| `004cb750` AppendViewportOverlayEffectQuadCommands | `004cbc84` | `004cb870` |
| `004cbc90` BuildWorldTransientEffectCommandPair | `004cc539` | `004cbf31` |
| `004ddb40` BuildWeatherOverlayQuadCommands | `004de064` | `004ddd59` |
| `004de070` BuildWeatherParticleQuadCommands | `004de6f9` | `004de0be` |
| `004de700` BuildWeatherParticleHistoryTriangleCommands | `004decd1` | `004de770` |

Labels come from saved analysis, not original source. Complete envelopes include any internal gaps; they must not be substituted for saved-body-union measurements without checking the boundary.

## Exact branch difference

The tested value is byte `007a3a58`, either read directly by TEST or loaded into AH/BL shortly before the test. Each test is followed by a zero branch that skips a block involving float `006fbc38`. Thus:

- Original enters that block when `(renderer_byte & 0x40) != 0`.
- Modern enters when `(renderer_byte & 0x50) != 0`.
- The branch decision changes exactly when bit `0x10` is set and bit `0x40` is clear: 64 of the 256 possible byte values. This count is a truth-table result, not runtime frequency.

| Relevant renderer bits | Original admission | Modern admission |
|---|---|---|
| Neither bit | Skip | Skip |
| `10h` only | Skip | Enter |
| `40h` only | Enter | Enter |
| Both | Enter | Enter |

The [renderer loader comparison](original-modern-renderer-loading.md) already verifies configured type's first-byte mapping: `d`→`40h`, `v`→`10h`, `s`→2, other→1. Under that producer, Modern extends these paths from the `d` type to both `d` and `v`. This is a verified configuration-to-mask relationship; names alone do not prove a particular DLL implementation or visible rendering fix. Other writers or combined masks are not excluded.

The admitted blocks read `006fbc38`, compare it with 1 using x87 and perform retained color/fade work under further conditions. Admission is not an unconditional output change: downstream branches, source colors and state still matter. The full color helper at `0049d800` gives a compact witness: the renderer test precedes the float comparison and otherwise jumps directly to `0049d8d7`. No new floating-point formula appears in any of these eleven bodies.

## Reconstruction implications and limits

Preserve the OR-of-bits meaning: `50h` admits either bit; it does not require both. Preserve downstream float conditions and packed-color arithmetic until their domains are qualified. TEST also writes CPU flags: even where the following zero-branch decision is unchanged, parity can differ when both tested bits are set. The grouped audit establishes branch predicates and byte differences, not full machine-state equivalence or deadness of every flag.

**Work status: done for these eleven bounded static comparisons. Confidence: verified.** Actual renderer output, all producers of the renderer byte, the complete meaning/lifetime of `006fbc38`, asset effects and historical introduction dates remain outside this evidence. Reuse this grouped result rather than treating eleven isolated one-byte edits as eleven independently proven visual features. No executable, Ghidra database or reconstruction sources were changed.

## Retained View Distance scale in the world-effect builder

The expanded audit also pins the four binary32 values at **`004ca480`** and the exact26-byte consumer **`004cbdcc..004cbde6`** in `004cbc90`. Both are identical across original and official Modern. The [View Distance binding](original-modern-parameter-preset.md#user-facing-binding-view-distance-and-the-full-preset) identifies selector `006fbc28` as Full/Far/Medium/Close; this separate consumer's factors are respectively **1.0,1.0,0.8500000238418579,0.699999988079071**.

The consumer indexes that table directly with the selector, multiplies its chosen factor by binary32 `[00560bc4 + EDX]` (the preceding code forms EDX as an input index shifted7), then compares the product against binary32 local `[EBP-3ah]`. Ordered greater/equal takes the continuing branch at `004cbdf1`; less or unordered falls into the rejection path at `004cbde6`, subject to x87 exception behavior. No selector bound check occurs in this local sequence. The meanings/units of the viewport-indexed value and local candidate remain qualified.

This is an important boundary on the Full-preset finding: Modern's rewritten track-record threshold table does **not** replace every View Distance consumer. This world-effect scale table and its indexing/comparison remain unchanged; Full and Far both use1.0 here. The only byte changed in the complete2,217-byte builder remains the separately documented renderer mask at `004cbf31`. That does not establish runtime equivalence: source data, allocation/callback dependencies and ambient x87 precision can still differ.

## Alpha Intensity connects menu writeback to packed-colour scaling

**Verified static linkage and arithmetic; visible Voodoo output untested.** The [colour-contract audit](evidence/audits/intensity-color-contract.json), reproduced with `python3 analysis/scripts/audit_intensity_color_contract.py`, pins both complete235-byte helper bodies at`0049d800..0049d8eb`, the65536.0 constant and official `advgrph.mnu` control block. Its sole changed byte is the renderer-mask immediate at`0049d814`,40h→50h, as established above.

The official slider pairs `codelink=SFX_INTENSITY` with text key`kMenuADVGRPHAlphaInt001`. The existing [menu round-trip analysis](original-modern-graphics-menu-transition.md#sfx-setup-helper-and-writeback-contract) proves setup seeds its value from`006fbc38`, installs callback`00448570`, and the admitted callback stores the getter's x87 result back to the same binary32 global. The [type producer](original-modern-renderer-loading.md#5-driver-specific-configuration-before-loading) maps configured `v` to10h. Together these establish a concrete menu-setting→global→newly-admitted colour path, without assuming a successful Voodoo provider or enabled UI in every initial state.

The helper copies incoming EAX/EDX colours to EDI/ESI. On admitted renderer masks it compares1 with the intensity and bypasses scaling for ordered intensity>=1; an unordered comparison also takes bypass if execution continues without an unmasked exception. Otherwise it forms intensity*65536, converts via ambient-rounding FISTP, caps signed results>=65536 at65535, then logically shifts8 and masks255 to obtain integer factor q. For ordinary finite intensity0..1 below the bypass threshold, its packed-lane arithmetic implements `floor(byte*q/256)` for **all four bytes of each input colour**, not only one alpha byte. It repeats the conversion/arithmetic for the second colour, then publishes EDI/ESI to`0055e6dc/0055e6e0`.

| Assumed renderer byte10h; both input coloursffffffffh | Original published colours | Final Modern published colours |
|---|---|---|
|Intensity0 |ffffffffh |00000000h |
|Intensity0.5 |ffffffffh |7f7f7f7fh |
|Intensity1 |ffffffffh |ffffffffh |

These exact ordinary examples are instruction-derived arithmetic, not executed probes. In particular, half intensity uses q=128, so a255 byte becomes127 through division by256. At intensity1 the helper bypasses arithmetic altogether. For other inputs, FISTP rounding/exception state matters; there is no local general lower clamp for negative settings. Do not replace the packed operations with signed-overflowing C or a generic floating colour multiplication and call it machine-equivalent. Global writes are the verified outputs; intermediate EAX does not establish a scalar C return interface.

**MP100-015 advances to partial support:** the menu gate and eleven effect gates admit the v-type bit, and this complete helper shows how the shared intensity changes published colours when its value is below1. Actual car shine, semantic channel ordering, blend state, driver support, every caller/state writer and1.0.0 introduction remain unverified. The result is a local mechanism, not proof that all Voodoo rendering now honors the setting or that the menu always enables it. No game, driver, colour helper, new instruction probe or Ghidra write was executed.
