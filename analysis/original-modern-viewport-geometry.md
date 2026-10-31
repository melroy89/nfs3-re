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

Original `004be7d4..004be88f` uses the same profile table neighborhood but explicitly calls truncation helper `004dfd56` before its integer stores. Its extent differences include `+1`. Modern's direct FISTP uses the active rounding control and does not add the same inclusive endpoint adjustment. Therefore integer edge placement cannot be assumed bit-identical even where profile floats match. The separate [x87 policy comparison](og-modern-x87-precision.md) also matters; this chapter does not infer the live control word on every caller path.

In the first group of `007cdb48`, original supplies logical height derived from H/4, whereas Modern `004be7ca..004be7e1` derives height from `(physical_width*10)>>4` and centres that height relative to the second group's vertical bounds. For positive fitting dimensions the Modern logical width/height ratio is approximately 8:5, subject to truncation. This is relevant to mirror-proportion release claims, but all consumers and the actual rendered mirror image remain untested; the record address alone is not universal proof of camera behavior.

## 5. Reference width feeds border thickness

After writing the reference rectangle, Modern calls `0047f9a4` at `004be74d`. That helper uses `007a2748`, now traced as **reference width**, to calculate the stored border thickness. See the [border comparison](original-modern-border-geometry.md). For ordinary widescreen modes the reference width derives from `4*H/3`; for taller modes it remains W. Hence “based on vertical resolution” has a specific aspect-dependent implementation, rather than a universal multiplication by H.

## Catalog mapping and remaining work

- **MP100-002:** reference geometry and dynamic aspect-factor writes are concrete EXE mechanisms supporting proportion correction, not proof that all objects/HUD/cameras are correct.
- **MP160-005:** the changed `007cdb48` first/second-group calculations are bounded evidence relevant to mirror proportions; actual imagery and other camera consumers remain pending.
- **MP160-006:** border scaling source is linked to the new reference rectangle; map-point sizing remains a separate trace.

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

This narrows the overlay change to use of a **derived, slightly expanded rectangle** rather than simple address relocation. The source-group producer/profile meaning, intended seam/coverage effect and actual visible result remain unresolved. No release-note bug is assigned from the correction alone. Preserve the literal operation order, overflow and extent semantics during original/Modern C reconstruction until a deliberate policy change is separately validated. No target instructions were executed.

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
