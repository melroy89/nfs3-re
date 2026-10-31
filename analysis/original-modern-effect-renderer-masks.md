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
