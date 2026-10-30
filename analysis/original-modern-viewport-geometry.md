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
