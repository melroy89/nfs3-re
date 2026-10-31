# Viewport resize wrapper: narrower admission and rectangle refresh

## Complete counterparts and input witnesses

Both executables have a resize wrapper at `004be970`: original ends at `004bea31`, Modern at `004bea36`. The [audit](scripts/audit_frame_resize_difference.py) pins the executable hashes and retains both complete wrappers, complete adjustment helper `004bea40..004beaf7`, and caller witness `004c4fbe..004c4ff2`. [Manifest](evidence/audits/original-modern-frame-resize.json). Ends are exclusive; no target execution.

The caller witness is **byte-identical**: it calls `0048f7b0` for held-action indexes7/8 with EDX=0. Nonzero results call `004be970` with EAX=+1 or−1 respectively. Existing [fixed-action research](detailed-analysis-notes.md#fixed-action-consumers-corrected-against-assembly) maps these to fixed slots31/32. Human key labels and the complete action producer are separate from this machine-level input route.

## All wrapper differences

The prefixes `004be970..004be9a3` and regions `004be9aa..004bea2a` are byte-identical. At `004be9a3`, original compares DWORD `006fbc4c` against zero; Modern tests bit1 of its low byte. A nonzero test skips ordinary resize work unless session value `006fd3b0 == 1`. Thus Modern admits other nonzero values with bit1 clear where original blocks them.

Modern additionally inserts `CALL 004be85c` at `004bea2a`, followed by a shifted byte-identical epilogue. Original returns there without that call. Both the normal update path and the skip branch reach the new helper. It refreshes the [derived overlay rectangle](original-modern-viewport-geometry.md#overlay-rectangle-at-007a2750-separate-derived-extent-correction) even when the ordinary resize is skipped; it is not proof an adjustment succeeded.

This fully identifies the wrapper's local delta. It does not establish complete equivalence of called generic geometry/state helpers merely from unchanged CALL operands.

## Shared resize and bounds machinery

The wrapper chooses horizontal step32 when renderer mask `007a3a58` has bit1 set; otherwise it uses signed physical-width DWORD `007cda68` divided by40 with IDIV. It negates the step when incoming EAX is signed-negative. The **sign**, not the magnitude, is used: input0 takes the ordinary nonnegative direction, rather than requesting zero movement.

It applies the common helper to main record `007cdb88` and two split-view records at `007cda80` / `007cdaa0`, with selected split-record fields saved/restored around the calls. It then calls `004be3d0` and conditionally writes state2 at `007cdba8` when the recorded width comparison indicates reduction. The split-field preservation and main-record mutation are distinct effects; do not replace the sequence with an unconditional resize of every field in every rectangle.

Complete adjustment helper **`004bea40..004beaf7` is byte-identical** across baselines. EAX supplies a rectangle record and EDX the signed horizontal delta. In ordinary nonoverflowing arithmetic it derives vertical delta `trunc(3*horizontalDelta/4)`, rejects zero horizontal delta and rejects a proposed first-group width below half physical width, above physical width, or a proposed first-group height below zero. There is no corresponding local upper-height comparison in the inspected guard.

On an admitted change it updates both four-DWORD groups: shift their origins by half of each delta, truncated toward zero, and add the deltas to their extents. The actual assembly uses wrapped 32-bit operations, signed comparisons and arithmetic-shift/bias sequences; overflow cases must be modelled from those instructions rather than copied into signed-overflow-prone C. The guard uses the first group's proposed dimensions, not independent bounds checks for both groups.

## Relationship to the Frame Size release claim

**MP160-004** reports that Frame Size was extended to restore a camera shift. The paired input, resize gate and derived-rectangle refresh above are concrete relevant mechanisms. The resize witness alone does not establish the visible horizon/camera effect, its complete setting producer or the v1.6.0 introduction date. The later [Frame Size list/selector audit](original-modern-frame-setting.md) closes the UI-label and storage association and establishes two-to-four choices. MP160-004 is now partial on that stronger evidence; the visual camera-shift effect and release date remain unverified.

The [view-offset](original-modern-view-offset.md), [viewport source-group](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles) and [projection](original-modern-projection.md) reports document distinct paths that may contribute to that visual claim. Combining their existence is still not a rendered comparison.

Next: map the complete user-setting/held-key producers, invoke ordinary and boundary resize paths against each version when runtime testing is in scope, and compare viewport/horizon outputs. For reconstruction, preserve direction-only input, the version-specific gate, per-group field preservation, bounds semantics and Modern refresh-on-skip behaviour. No executable bytes, saved Ghidra state, exports or maintained C were changed.
