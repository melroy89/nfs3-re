# AI gear selection: conditional fallback contract

Target: the documented `nfs3.exe` SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Static assembly evidence; no malformed-state runtime test was performed.

## Closed bounded questions

The forward scan in `004061b0` does not have an intentional previous-gear fallback. Its direct caller chain supplies EBX equal to the vehicle address plus `0xe4`: `00408a22` sets it, subsequent dot-product helper `004e01f0` preserves it, and `00408600` reaches gear calls `0040865d`/`00408678` without assigning it. The intervening `00407380` saves/restores EBX; `00408870` and `0040ed40` do not change it.

The forward path starts candidate index2 and best error100000.0 at `004062f6`–`00406300`. Only an accepted candidate assigns EBX and local target RPM (`00406351`/`00406358`). If no candidate is accepted, the later comparison uses the incoming pointer and the store `00406392` writes its low byte to vehicle gear `+0x50b`; local target RPM remains uninitialized. This is a conditional bad fallback, not proof that ordinary gameplay reaches it. Reverse selection explicitly assigns gear0, and the positive shift-delay branch bypasses this gear write.

The comparison is also resolved: `FCOMP`, `FNSTSW`, `SAHF`, `JNC` at `00406343`–`00406349` rejects ordered error greater than or equal to the current best, but accepts unordered comparison when x87 invalid is masked. The old inline comment incorrectly required an ordered strict winner. NaN therefore cannot generally be cited as a no-winner example. Equal finite candidates retain the earlier index.

## Remaining questions

- Prove a winning candidate for the reachable speed domain and correctly parsed installed profiles, or capture a normal no-winner case. Count at most2 or all ordered errors at least100000 are sufficient abstract conditions, not established normal inputs.
- Establish requested gear `+0x506` and all other writer invariants before asserting a global gear bound. Other paths can copy that byte or select constants independently of this scan.
- Preserve exceptional arithmetic and x87 policy distinctions; a corrected comment does not make malformed input safe.

The parser stores the declared gear count separately from the fixed eight-ratio array; those contracts must not be conflated. Further inventory and producer proofs are tracked in the Astra backlog. No executable or live memory was changed.

## Closed conditional producer and numerical bounds

Assembly0048f6e0 preserves a valid incoming manual gear: up increments only below count-1, down decrements only above0, otherwise unchanged. Assembly0048f710 selects automatic0/1/2 with up0->1->2 and down2-or-higher->1->0. Up input takes precedence in both helpers. With a valid incoming gear and installed counts5..8, these local producers preserve bounds; they do not sanitize a pre-existing invalid gear. Other writers and aliased/network/replay state still prevent a global invariant claim.

All47 installed profiles, manual and automatic (94 cases), have positive finite active forward ratios. Choosing the minimum active forward ratio bounds absolute target error below100000 for any finite speed magnitude0..600, under untuned inventory ratios. The three targets are float32(redline*0.5), float32(redline*0.8), and redline-200, verified against assembly/constants. Absolute affine error is convex and bounded by interval endpoints. The worst endpoint is approximately93657, TRAFFIC/0000, ratio160.2616729736328, target2500, speed600. The6343 margin comfortably covers intermediate floating rounding, including the FST at0040631b that leaves the extended value on the x87 stack. Therefore a candidate exists throughout this specified numerical domain.

The inventory is [controller-profile-inventory.json](controller-profile-inventory.json). This is not a universal reachable-speed proof:0042cf25 obtains an absolute velocity projection via0042cdd0 without a clamp. Nondefault gearing multipliers and indirect writes remain unresolved. No claim is made that the no-winner path is a normal gameplay defect.
