# Original versus Modern: viewport reference geometry and aspect factors

## Scope and evidence

**Static comparison; no rendered-image acceptance.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_viewport_geometry_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-viewport-geometry.json) records exact function-span/input hashes and file-backed float bits, with raw assembly under ignored `analysis/captures/modern-differences/viewport-geometry/`. No executable/Ghidra changes or instruction probes. This chapter explains selected differences in matched initializer `004be5e0`, not every field or render path in that rewritten routine.

## 1. Width/height outputs and internal setter interfaces

Both initializers call dimension helper `004be570`, which stores the mode's width through ECX and height through its stack output argument; EDX/EBX point to origin outputs initialized zero. The initializer's locals are therefore **W at `[EBP-0x20]`, H at `[EBP-0x1c]`**, not the reverse. Modern uses the descriptor cached by its renderer loader; the helper's unknown-index fallback is 640×480.

Original setters `004beb00` / `004beb40` take destination EAX, first two coordinates in EDX/EBX, third in ECX and fourth on the stack, then `RET 4`. Modern's new `004be89c` / `004be8a8` take destination EDI and all four values in EAX/EBX/ECX/EDX, writing the first or second four-DWORD group and returning with plain RET. The register/stack interface changed even where the destination records remain at the same addresses.

## 2. New centred 4:3 reference rectangle

Modern at `004be60a..004be61d` computes synthetic height `S=(3*W)>>2` and offset `D=(H-S)>>1` with arithmetic shifts. It then writes reference rectangle `007a2740..007a274f` at `004be700..004be743`:

| Condition | Stored `{x, y, width, height}` for normal positive dimensions |
|---|---|
| D > 0 | `{0, D, W, S}` |
| D = 0 | `{0, 0, W, H}` |
| D < 0 | `R=trunc(4*H/3)`, then `{(W-R)>>1, 0, R, H}` |

Examples derived from integer arithmetic, not game execution:

| Display | Reference rectangle |
|---|---|
| 640×480 | `{0, 0, 640, 480}` |
| 1920×1080 | `{240, 0, 1440, 1080}` |
| 1280×1024 | `{0, 32, 1280, 960}` |

Thus a reference rectangle can differ from the full physical display. Other records receive profile-dependent first/second groups; the meaning of every flag bit and every consumer is not established here. The original matched initializer builds its viewport records through the older setter pair, without this new reference-record construction. The original's separate profile/special-mode branches must not be collapsed into the Modern formulas.

Machine caveat: integer products/shifts are 32-bit; the formulas assume positive, nonoverflowing dimensions. Odd sizes use the shown shifts/truncation, not exact fractional centring. No malformed display descriptor was supplied.

## 3. Three fixed float values acquire startup writes

At file load, **both binaries** contain the same binary32 values:

| Address | Initial bytes | Initial value |
|---|---|---:|
| `00538ad8` | `00 00 fe 42` | 127 |
| `0053a9d4` | `00 00 20 c1` | -10 |
| `0053a9e0` | `00 00 20 41` | 10 |

Original direct instruction witnesses at `00443a27`, `00460bd5` and `00460ca0` add these values. Modern retains those read sites but adds writes in the initializer at `004be81d`, `004be82f` and `004be841`.

Modern first computes W/H in x87, then reverse-divides the binary32 literal `0x3faaaaab` by that ratio. Let `C` denote that stored binary32 approximation to 4/3; then the intermediate factor is `C/(W/H)`. It multiplies 127, -10 and 10 by this factor, storing each result to binary32 at the addresses above. For 1920×1080 the idealized factor is approximately 0.75; the literal approximation and x87 rounding mean this is not an exact-real identity.

This is a concrete difference between **file-backed initial values** and **later initialization writes**. Equal initial data bytes do not establish equal runtime constants. The direct original instruction search did not locate these new writes; arbitrary alias writes or every consumer are not excluded by that bounded search. Their full visual roles are not assigned solely from the numbers or current names.

## 4. Profile rectangle conversion and rounding change

Both versions read four floats at `006fbd04/08/0c/10 + profile_index*0x1a4`. Modern multiplies W by fields +08/+10 and H by +04/+0c, converts with direct FISTP, adds/subtracts the border thickness from `0055fed0`, and forms differences at `004be752..004be7b6`. These writes fill the second group of record `007cdb48`.

The profile index is an input to `004be5e0`: its entry saves EAX at `[EBP-4]` and the mirror builder multiplies that value by `0x1a4` at `004be752`. The selected callers at `0044d28c` and `0044d4b2` pass 1 if bit `0x20` of the selected object's byte `+0x200` is set, otherwise 0. The startup caller at `004a3428` passes the boolean value of bit `0x08` at `006fd544`. These caller instructions and the entry save match in retained 1.6.0 and final 1.6.1. This verifies how these paths select the two profile records. Other callers and actual flag values remain outside this trace.

The mirror rectangle is slot 9 because `006fbd04 - 006fbc50 = 0x24 + 9 * 0x10`. In both profiles 0 and 1, the 1.5.3 archive member stores the same four WORDs in source order, `(350, 0, 650, 133)`, corresponding to normalized bounds `(0.350, 0, 0.650, 0.133)` before rounding. In the 1.6.0 archive member both profiles store binary32 approximations of `(0.346875, 0, 0.653125, 0.14375)`. These reads use tables `00540500` and `0053eb20` and the strides in the [HUD preset comparison](original-modern-hud-layout.md). For these profiles, 1.6.0 widens the authored horizontal span from 0.300 to 0.30625 and increases the lower-edge coordinate before runtime layout arithmetic. The change in stored bounds is separate from the inset and projection-height formulas. Actual clip extents still depend on the active HUD state and rounding.

Across all nine retained packages from 1.1.0 through 1.5.3, slot 9 has the same four WORDs for profiles 0 and 1, and all four coordinates are zero in profiles 2–5. The 1.6.0 table changes only profiles 0 and 1 in that slot. Profiles 2–5 contain four positive-zero binary32 values, and 1.6.1 retains the 1.6.0 table. This also establishes that the 1.5.0 mirror centering change did not coincide with a change to the authored mirror bounds. Whether a zero preset suppresses rendering on every path remains unverified.

The [six matching local and reference `.POS` inputs](original-modern-hud-layout.md#1-file-sourced-presets-become-embedded-data) show a locale-dependent difference in the original's authored data. Reading the tenth row of each 23-row profile group gives the following `RearView` inventory, with coordinates in `(left, top, right, bottom)` order:

| Original preset files | Racer | Cop | Split-screen profiles |
|---|---|---|---|
| `EDEF`, `FDEF`, `SDEF`, `WDEF` | `(0.350, 0.010, 0.650, 0.143)` | `(0.346875, 0.0125, 0.646875, 0.145833)` | All four zero |
| `GDEF` | Same Racer bounds | Same as Racer | Both Player 1 profiles repeat Racer. Both Player 2 profiles add 0.5 to the vertical bounds. |
| `IDEF` | Same Racer bounds | Same as `EDEF` Cop | Racer profiles zero. Player 1 Cop repeats Cop. Player 2 Cop adds 0.5 to its vertical bounds. |

The early Modern table uses the Racer horizontal bounds for both standalone profiles and shifts both Racer vertical bounds up by 0.010. Its zero split-screen presets eliminate the authored German and Italian exceptions when the embedded initializer runs. These are input differences. Profile eligibility and visible split-screen mirror output remain unverified.

Original `004be7d4..004be88f` uses the same profile table neighborhood but explicitly calls truncation helper `004dfd56` before its integer stores. Its extent differences include `+1`. Modern's direct FISTP uses the active rounding control and does not add the same inclusive endpoint adjustment. Therefore integer edge placement cannot be assumed bit-identical even where profile floats match. The separate [x87 policy comparison](og-modern-x87-precision.md) also matters; this chapter does not infer the live control word on every caller path.

In the retained 1.3.1 → 1.4.0 pair, the five-byte shift of
the conversion sequence comes from the initializer's prologue
at `004be5e0`: six individual register pushes become one
PUSHAD. From the frame setup through the first mirror conversion,
the decoded instructions match after shifting addresses and
accounting for branch and call targets. In particular, the two
rectangle setters move from `004be898` and `004be8a4` to
`004be88c` and `004be898`, respectively. Their register-to-field
stores match in both archives.

The ordinary return also changes. In 1.3.1, the six individual
pops leave EAX holding the DWORD read from `007cdb88` by the final
helper at `004be874`. The helper's copy to `007a2750` preserves
that EAX value. In 1.4.0, the relocated helper at `004be868`
performs the same copy, but POPAD at `004be866` restores the
initializer's incoming EAX before RET. The other six saved
registers are restored in both versions. Caller dependence on
the old EAX value and runtime inputs remain unverified.

Across the 11 retained archives, the ordinary epilogue switches
from individual pops to POPAD in 1.4.0 and retains POPAD through
1.6.1. The supplied original also uses individual pops. The
ordinary return locations identify the specific bodies checked:

| Executable | Initial save | RET |
|---|---|---|
| Supplied original | Individual pushes | `004be8d1` |
| 1.1.0–1.3.1 | Individual pushes | `004be871` |
| 1.4.0 | PUSHAD | `004be867` |
| 1.5.0–1.5.3 | PUSHAD | `004be84f` |
| 1.6.0–1.6.1 | PUSHAD | `004be859` |

The individual saves do not by themselves establish the EAX value
on every earlier return path. The explicit EAX dataflow above is
verified for 1.3.1.

Linear disassembly finds the same five direct initializer calls
in 1.3.1 and 1.4.0. Both builds overwrite EAX before its next use
at every inspected site. At `0044d28c`, `0044d4b2`, `004a3439`
and `004b611a`, the overwrite is in the caller. At `00485626`,
the next instruction calls `0047fd80`, which loads EAX from
`007cdac8` at `0047fd8b` before reading it. The earlier EAX value
therefore has no observed consumer on these direct paths.
A follow-up found no decoded direct jump to the same entry and
no literal `004be5e0` DWORD anywhere in the file-backed PE sections
of either archive. The HIGHLOW relocation sites also have no
matching operand (46,140 checked in 1.3.1 and 45,987 in 1.4.0).
This rules out a stored absolute pointer to the exact entry in
these bytes. Computed pointers and alternate entries remain
outside the scan.

Across all 11 retained releases the linear scan still finds five
direct calls per executable. Three stay at `0044d28c`, `0044d4b2`
and `00485626`. The call at `004a3439` moves to `004a3428` in
1.6.0 and retains the following local-address setup that overwrites
EAX. The fifth call moves within renderer startup: `004b611a`
through 1.4.0, `004b5bb1` in 1.5.0, `004b5bfc` in 1.5.1,
`004b5c12` in 1.5.2–1.5.3, `004b5c03` in 1.6.0 and `004b5c91`
in 1.6.1. Each startup sequence loads EAX with `007cdb68`
before its next call, with only EDX/EBX setup preceding that load
in the later variants. The retained direct continuations provide
no evidence of EAX-result dependence.

The 1.5.0–1.5.3 mirror-edge span `004be6f4..004be74b` is byte-identical in all four retained builds. It calls `004dfd56` before each of four FISTP stores and computes both extents as upper edge minus lower edge plus one. In 1.6.0, the corresponding `004be752..004be7a5` uses direct FISTP and insets each converted edge by `0055fed0` before taking the difference. For the same four converted edges and an inset of `B`, each 1.6.0 extent is smaller by `2*B + 1`, assuming ordinary fitting integer arithmetic. The comparison holds the converted edges fixed. Actual edge rounding and the inset value depend on runtime state.

The four intermediate-only calls in the
[x87 census](og-modern-x87-precision.md#changed-drivetrain-truncation-helper)
map directly to the four 1.6.0 stores. Each pair uses the same
profile-table operand and stack destination.

| Profile DWORD operand | Stack destination | 1.5.3 truncation call / FISTP | 1.6.0 direct FISTP |
|---|---|---|---|
| `[EDX+006fbd08]` | `[EBP-18h]` | `004be706` / `004be70b` | `004be76a` |
| `[EDX+006fbd10]` | `[EBP-10h]` | `004be714` / `004be719` | `004be776` |
| `[EDX+006fbd04]` | `[EBP-14h]` | `004be72e` / `004be733` | `004be78d` |
| `[EDX+006fbd0c]` | `[EBP-0ch]` | `004be73c` / `004be741` | `004be799` |

For a fixed finite in-range product of 10.75, the old sequence
stores 10, while the direct store gives 11 if the active rounding
mode is nearest. This isolates the conversion difference. The
example does not represent an observed viewport coordinate.

The 1.6.0 path calls the [border updater](original-modern-border-geometry.md#modern-wrapper-and-call-site-mapping) at `004be74d`, before reading the freshly written value at `004be759`. The updater computes the inset from the fitted 4:3 reference width, twice the stored binary32 approximation of `1/640`, and the active x87 rounding mode. For a 1280×720 mode with fitted width 960 and nearest rounding, the product is approximately 3 and FISTP stores 3. Holding converted edges fixed, the new physical extent would then be seven units smaller in each dimension. This is a conditional arithmetic example. It excludes any separate changes to the profile coordinates, edge rounding and presentation.

In the first group of `007cdb48`, original supplies logical height derived from H/4, whereas Modern `004be7ca..004be7e1` derives height from `(physical_width*10)>>4` and centres that height relative to the second group's vertical bounds. For positive fitting dimensions the Modern logical width/height ratio is approximately 8:5, subject to truncation. This is relevant to mirror-proportion release claims, but all consumers and the actual rendered mirror image remain untested; the record address alone is not universal proof of camera behavior.

The exact release boundary is 1.5.3→1.6.0. The 73-byte mirror producer span `004be74b..004be794` matches in all four archived 1.5.x builds. It averages a height-derived term and a width-derived term, as traced in the [mirror-centre comparison](original-modern-viewport-pose.md#earlier-mirror-direction-claim). The 1.6.0 path still executes the division by 533 at `004be7c8`, but then overwrites EDX with the width term and reloads EAX from the physical X before calling the logical-rectangle setter. The quotient no longer contributes to the stored height. The vertical centering rule remains. This verifies the release-note mechanism at the logical-rectangle level. Actual rendered proportions remain untested.

The archive-matched 1.6.0 and final 1.6.1 executables share all 148 bytes at `004be752..004be7e6`, including the profile rounding, both setter calls and the width-derived logical height. Both setter bodies at `004be89c..004be8b5` match as well. The first group feeds projection through `004bed20` on the mirror path, while the second group retains the physical bounds. The matching code establishes continuity through 1.6.1 for this calculation. Actual profile inputs and the rendered result remain unverified.

The physical bounds have a separate consumer. In both archived 1.5.3 and 1.6.0, the identical adapter span `004bed39..004bed4a` loads the four DWORDs at record `+0x10..+0x1c` into EAX/EDX/EBX/ECX and calls `004bebe0`. Its complete 234-byte body also matches across the pair. The setup clamps the physical origin and compares the requested extents against the space remaining within the published viewport dimensions. Thus the 1.6.0 physical inset reaches the retained clipping path, where clamping can affect the final extents. The logical rectangle goes through the projection wrapper separately. Actual clipping and presentation remain untested.

## 5. Reference width feeds border thickness

After writing the reference rectangle, Modern calls `0047f9a4` at `004be74d`. That helper uses `007a2748`, now traced as **reference width**, to calculate the stored border thickness. See the [border comparison](original-modern-border-geometry.md). For ordinary widescreen modes the reference width derives from `4*H/3`; for taller modes it remains W. Hence “based on vertical resolution” has a specific aspect-dependent implementation, rather than a universal multiplication by H.

## Catalog mapping and remaining work

- **MP100-002:** reference geometry and dynamic aspect-factor writes are concrete EXE mechanisms supporting proportion correction, not proof that all objects/HUD/cameras are correct.
- **MP160-005:** the changed `007cdb48` first/second-group calculations are bounded evidence relevant to mirror proportions; actual imagery and other camera consumers remain pending.
- **MP160-006:** border scaling source is linked to the new reference rectangle; the [map-marker producer-to-quad trace](original-modern-map-marker-scaling.md) separately establishes marker extents. Other styles, lifecycle and rendered output remain unverified.

Next: follow the three aspect-factor consumers, map all profile flags/viewport group consumers, compare remaining camera and map-point calculations, and use controlled image comparisons if visual correctness must be established. Do not silently normalize rounding, inclusive extents or suspected original behavior during reconstruction.

## Overlay rectangle at 007a2750: separate derived extent correction

The [overlay consumer comparison](original-modern-view-overlay.md) found its rectangle sources move from `007cdb98..007cdba4` to **`007a2750..007a275c`**. The expanded geometry audit now retains the complete Modern producer **`004be85c..004be89b`** and its two checked direct calls at `004be851` and `004bea2a`.

This output starts16 bytes after the centred 4:3 rectangle at `007a2740`. They are separate four-DWORD groups. Applying the earlier centred-rectangle formula to `007a2750` without inspecting its producer would be incorrect.

The producer saves general registers with PUSHAD and reads:

| Register / source symbol used below | Source DWORD |
|---|---|
| EAX / X | `007cdb88` |
| EBX / Y | `007cdb8c` |
| ECX / W | `007cdb90` |
| EDX / H | `007cdb94` |

It forms `ESI=wrap32(W-X)`, clears EDI, and repeatedly subtracts640 from ESI. After each subtraction, signed `JLE` ends the loop; otherwise it increments EDI and repeats. The branch uses the subtraction flags, including overflow, rather than a separately recomputed sign test. Let N denote that increment count. It then adds N to ECX, computes `logical_shift_right(wrap32(3*N),2)` and adds that value to EDX. Setter `004be89c` writes the resulting tuple to `007a2750`, preserving X/Y and changing the extents.

For ordinary nonoverflowing positive `D=W-X`, the count is `N=floor((D-1)/640)`. For ordinary `D<=0` the first subtraction exits with N=0, provided it does not overflow. Thus the normal tuple is `{X,Y,W+N,H+floor(3*N/4)}`; the actual implementation uses wrapped 32-bit arithmetic, signed branch flags and a logical shift. Do not replace it with an unrestricted real-number formula or silently alter its use of `W-X`.

Examples derived from those instructions, **not game execution**, with X=Y=0:

| Source W×H | N | Output extent |
|---|---:|---|
| 640×480 | 0 | 640×480 |
| 1280×720 | 1 | 1281×720 |
| 1920×1080 | 2 | 1922×1081 |

The main viewport initializer calls it at `004be851` after `004be3d0`. Another viewport-update path calls it at `004bea2a`, after its own `004be3d0` call and conditional state write. The captured latter region is a caller witness, not a complete analysis of that enclosing function. These two producers do not prove freshness at every overlay call; further writes/aliases and lifecycle ordering remain dependencies.

This narrows the overlay change to use of a **derived, slightly expanded rectangle** rather than simple address relocation. The following section resolves the ordinary initializer's source-group identity and flag-dependent tuples. Full profile/lifecycle admission, intended seam/coverage effect and actual visible result remain unresolved. No release-note bug is assigned from the correction alone. Preserve the literal operation order, overflow and extent semantics during original/Modern C reconstruction until a deliberate policy change is separately validated. No target instructions were executed.

## Source groups: covering frame versus physical/fitted rectangles

The complete Modern initializer already retained at `004be5e0..004be85a` resolves the source group's ordinary initialization. Its first call pair targets the two groups of record **`007cdb88`** through different setters:

- `004be652` calls `004be8a8`, which writes **record+10h..1ch**, therefore `007cdb98..007cdba4`. With ESI bit1 clear, this is `{0,0,W,H}` from the physical display dimensions. With bit1 set, it uses `{0, (H-(W>>1))>>1, W, W>>1}` in ordinary arithmetic.
- `004be683` calls `004be89c`, which writes **record+0..0ch**, therefore `007cdb88..007cdb94`. It stores X=0, width W and synthetic height `S=(wrap32(3*W)) arithmetic_shift_right 2`. Its base Y is `D=(wrap32(H-S)) arithmetic_shift_right 1`.

These are different groups in one record. Original overlay code reads the +10h group; Modern overlay reads a corrected derivative of the +0 group. Merely saying “both use viewport width/height” would conceal that distinction.

ESI is zero when session value `006fd3b0 == 1`; otherwise it is read from `006fbc4c`. For the first group, if ESI bit0 is set the initializer changes Y to `wrap32(D + (D arithmetic_shift_right 1))`. If both bits0/1 are set, it additionally subtracts the twice-arithmetic-shifted value `wrap32(H - (W arithmetic_shift_right 1))`. These flag branches must not be erased while generalizing the ordinary zero-flag example. The overlay's own revised bit1 gate can independently reject drawing.

For ordinary positive, nonoverflowing dimensions with these flags zero, the first group is a **width-based 4:3 covering frame**. It may extend vertically beyond the display, unlike the separately established fitted rectangle at `007a2740`. Derived examples, not runtime observations:

| Physical display | Source group at `007cdb88` | Corrected overlay group at `007a2750` | Fitted group at `007a2740` |
|---|---|---|---|
| 640×480 | `{0,0,640,480}` | `{0,0,640,480}` | `{0,0,640,480}` |
| 1920×1080 | `{0,-180,1920,1440}` | `{0,-180,1922,1441}` | `{240,0,1440,1080}` |
| 1280×1024 | `{0,32,1280,960}` | `{0,32,1281,960}` | `{0,32,1280,960}` |

Thus the prior extent-correction examples using source `{0,0,W,H}` were conditional examples of that helper, not necessarily the source produced by physical-mode initialization. In particular, a 1920×1080 display does not imply source height1080 in this zero-flag path.

The expanded audit also retains complete Modern resize/update code `004be970..004bea36` and rectangle-adjustment helper `004bea40..004beaf7`. The former applies the helper to the record and eventually refreshes `007a2750`; this is why initial tuples alone are not lifetime invariants. The adjustment helper can update both groups' origins/extents after bounds tests. Its full caller/UI binding, arithmetic admission and original counterpart remain pending; this report does not attribute it to the Frame Size release-note change solely from nearby code.

For reconstruction, give the physical +10h group, covering +0 group, corrected overlay group and fitted reference group distinct identities. Their storage adjacency does not make them aliases or equivalent rectangles. The intervening complete `004be3d0..004be570` helper is now retained too: it reads rectangle state to construct separate float geometry, with no calls or stores back to these source groups in its inspected body. This narrows the ordinary producer-to-correction linkage without proving all later writers absent. Runtime profile/flag admission, resize ordering, clipping and final visual acceptance remain outstanding. No original executable behaviour is inferred from the new Modern producer names alone.

## Quad-set draw arguments: six changed constants

The saved Modern entry `004a75e0` is labelled `DrawViewportQuadSet`. The [focused audit](scripts/audit_viewport_quad_constants.py) verifies both complete same-address function envelopes, `004a75e0..004a78b6` (726 bytes including RET), against the hash-pinned supplied original and official Modern executables. The [manifest](evidence/audits/viewport-quad-constants.json) records binary and span hashes and retained disassembly paths.

Only six PUSH-immediate arguments differ:

| PUSH instruction addresses | Original bits / binary32 value | Modern bits / binary32 value |
|---|---|---|
| `004a77bf`, `004a77cd` | `3f440000` / 0.765625 | `3f447ae1` / 0.7674999833106995 |
| `004a781d`, `004a782d` | `3f440000` / 0.765625 | `3f447ae1` / 0.7674999833106995 |
| `004a787e`, `004a788c` | `3f440000` / 0.765625 | `3f447ae1` / 0.7674999833106995 |

The pairs feed the retained calls to `004a7310` at `004a77f5`, `004a7850` and `004a78a8`, respectively. Every other byte in the function is identical, including the viewport-query call `004beb80`, integer layout arithmetic and five earlier calls to `004a7080`. Each changed value increases by approximately 0.001875. The audit masks only these six immediate operands before comparing the complete bodies; there are 12 differing bytes in total.

**Bounded work status: done; confidence: verified static arguments and complete function delta.** The binary32 interpretation describes the bit patterns; exact parameter roles require the callee contract. Texture coordinates, depth and visible effects are not established by these pushes alone. Retained callees may themselves differ between versions. No runtime validation, executable modification or Ghidra write was performed.

## New record-to-setup adapters occupy the original initializer tail

The expanded [viewport audit](scripts/audit_viewport_geometry_difference.py)
retains complete Modern adapters, the shared setup and bounded reference
searches in [the manifest](evidence/audits/original-modern-viewport-geometry.json).
This classifies all42 changed bytes in outside-body interval
`004be8b5..004be8e0`, which contains **new instructions**, not just NOPs.
The original interval begins inside MOV ECX at `004be8b1` and continues
through initializer code/epilogue/alignment; it was not a standalone function.

| Modern subrange | Role |
|---|---|
| `004be8b5..004be8b8` |3 alignment NOPs |
| `004be8b8..004be8cf` |23-byte record-to-setup adapter |
| `004be8cf..004be8d0` |1 alignment NOP |
| `004be8d0..004be8dd` |13-byte fixed-record wrapper |
| `004be8dd..004be8e0` |3 alignment NOPs |

Inner adapter input is **ESI=record**. It saves EBX/ECX/EDX, loads record
DWORDs+0/+4/+8/+0ch into EAX/EDX/EBX/ECX, calls `004bebe0`, restores those
three saved registers and returns. The outer wrapper saves ESI, selects
record `007cda60`, calls the inner adapter and restores ESI. Neither body
assigns a normalized return value; do not infer a Boolean interface from
whatever the shared setup leaves in EAX.

Complete shared setup `004bebe0..004becca` is234 byte-identical bytes in
original and final. The separately retained setter `004bebb0` writes the four
incoming registers into `007cda60..007cda6f` before calling that setup. The
new inner adapter instead reads a record and directly calls setup, without
those four publication stores. This distinguishes its register/data contract
from the setter; it does not prove equivalent global state for arbitrary
record pointers, aliases or setup side effects.

**Reachability remains unresolved.** The final executable code-section scan
finds only relative-E8 candidate `004be8d6` targeting the inner adapter and
none targeting the outer wrapper. Whole-file searches find no literal pointer
to either entry. These bounded encoding searches do not exclude computed or
indirect calls. The ordinary setter remains separately mapped; no replacement
of every viewport publication route is asserted.

**Status:** done, verified static for both complete adapters, unchanged shared
setup,42-byte classification and bounded caller census. Caller registration,
source-record lifetime, full shared-state effects and rendered results remain
unverified. No viewport helper, renderer or instruction probe was executed;
executable, database and maintained C bytes were preserved.

### Historical mode-dimension input

A linear `objdump -d -Mintel` scan finds one decoded direct call
to `004be570` in the hosted original and each of the 12 retained
Modern EXEs. All calls immediately follow an EAX load from
`0055fec4`, so the viewport initializer still passes the same
mode-index cell after the helper switches to the
[cached descriptor](original-modern-renderer-lifecycle.md#eight-final-exe-sites-read-the-cached-descriptor)
in 1.6.1.

| EXE | Call to dimension helper |
|---|---|
| Hosted original | `004be5ff` |
| 1.0.0–1.3.1 | `004be5fe` |
| 1.4.0 | `004be5f9` |
| 1.5.0–1.6.1 | `004be5fb` |

The immediate load and call establish the argument source.
They do not establish that the index identifies the same mode
across builds or that every invocation is direct.
