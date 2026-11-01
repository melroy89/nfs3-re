# Original versus Modern: track-map marker sizing

## Evidence and changed producer

Run `python3 analysis/scripts/audit_map_marker_scaling_difference.py`. The [manifest](evidence/audits/map-marker-scaling-difference.json) pins both executable identities, complete producer/consumer envelopes, constants and a marker call's arguments. No game, drawing or instruction probe is executed.

The complete931-byte HUD layout envelope `0048d110..0048d4b3` differs only in the absolute operand of FILD at **`0048d40a`**: original reads signed width `007cdac8`, Modern reads signed reference width **`007a2748`**. This reuses the [HUD reference-consumer comparison](original-modern-hud-layout.md#reference-dimension-consumers-in-scale-standings-and-layout-updates), now with the missing map-marker consumer link established.

The retained arithmetic forms four binary32 extent values from that width and the same binary32 approximation to1/640 at `0053b9d0`:

| Store | Real-expression guide, k=that stored constant |
|---|---|
| `007930e4` | width*9*k |
| `007930f8` | width*22*k |
| `00793104` | width*14*k |
| `007930ec` | width*10*k |

The helper also copies these into related fields, including `007930f8` to `007930f0`. Expressions describe dependencies; x87 operation order and binary32 stores remain authoritative. The constants9/22/14/10 and k are identical across versions. These extent values are separate from per-view map-position scale `00792878`; confusing them would conflate marker size with map zoom.

## Confirmed marker geometry consumer

Complete map renderer `0048d4c0..0048e76d` and marker helper `0048cc60..0048cce8` are byte-identical across the two executables. At **`0048e188`**, the renderer passes a transformed point plus width from `007930f8` and height from `007930f0` to the helper. Both extents therefore use22*width*k on this path.

The helper multiplies width/height by retained0.5, constructs coordinates around the supplied centre, supplies texture coordinates and calls `00487620` with the resulting rectangle. This confirms that the changed source width reaches actual marker-quad dimensions. It does not establish final pixel coverage, clipping or backend rasterization. Other marker calls can use different extent fields; the report does not assume every marker is the same square.

## Meaning of vertical-resolution scaling

The [viewport producer](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles) establishes Modern's centred4:3 reference rectangle. Its width normally derives from truncated4*H/3 for widescreen modes and remains W for taller modes. Thus marker extents acquire an **aspect-dependent height relationship**, not an unconditional read/multiply of physical height.

For ordinary1920x1080 initialization, reference width is1440; using a hypothetical original width1920 at the same point would yield a0.75 extent ratio before rounding. This is an input/formula illustration, not observed marker shrinkage: actual source values, profile state, initialization order and later writers remain prerequisites.

This closes the previously unreviewed **map-point mechanism in MP160-006**, alongside the [border mechanism](original-modern-border-geometry.md). The catalog remains partial because actual rendered sizes, all marker styles, every display shape and historical introduction are unverified. Equal consumer bytes do not establish equal floating-point state or final images. Executables and saved Ghidra state remain unchanged.

## Profile scale defaults reach map zoom, independently of marker extents

The extended map audit also retains complete `0048cdb0..0048d105`; it is byte-identical across the executables. It chooses profile variant using vehicle byte+200h bit20h and accesses header+10h at `006fbc50 + variant*1a4h`. The existing [cop/racer variant linkage](original-modern-night-lighting.md#context-producer-optional-mirror-setting-gated-pass) independently associates this bit with the `mirror`/`mirrorcop` profile pair. This supports the role-variant interpretation; the global's role in every object layout is not inferred.

Initializer `0048cdb0` clamps those scale fields to the positive-float encodings of1.0..4.0 using **signed integer comparisons of raw bits**, not x87 comparisons. Do not translate this as a generic floating min/max without checking NaN/sign-bit behavior. The valid initialized values discussed below already lie in range.

In HUD layout setup, `0048d169` loads the selected profile+10h into local EBP-34h. At `0048d24c`, that local multiplies the map's fitted scale before the result is stored in per-view `00792878`. The unchanged map renderer subsequently uses this per-view scale in its screen-coordinate transforms. This establishes a map-zoom consumer for the header field; it is distinct from the marker-size extents documented above.

The [paired default-header audit](original-modern-hud-layout.md#3-header-default-changes-preserve-offsets-not-guessed-widget-names) establishes original header+10h values **4.0,1.0,4.0,1.0,4.0,1.0** across six profiles, versus **3.0 in all six** in Modern. Thus the default cop/racer profile pairs now supply the same map-zoom factor, rather than only having equal unidentified floats. The default change is racer4→3 and cop1→3 under this variant mapping; it is not preservation of one role's old default.

This strengthens **MP140-073** to a confirmed local default-to-consumer mechanism, while the catalog remains partial: saved preferences, later edits, active role/view selection, map fitting/recentering and final images remain unverified. The historical comparison below now establishes the1.3.1→1.4.0 default-equalization boundary. Equal profile multipliers alone do not establish identical visible map coverage for different vehicles or contexts. No map or game code was executed.

## Historical role-specific defaults become equal in140

**Verified historical default stores; no map execution.** The [zoom-default history audit](evidence/audits/map-zoom-default-history.json), reproduced with `python3 analysis/scripts/audit_map_zoom_default_history.py`, pins author-hosted1.1.0,1.3.1 and1.4.0 archives/EXEs and the official final EXE. It reuses the field/role/consumer evidence above; it does not claim every historical map consumer was independently compared.

| Baseline | Header+10h, profiles P0..P5 | Role-pair interpretation from linked consumer evidence |
|---|---|---|
|Supplied original, previously audited |4,1,4,1,4,1 |Racer4 / cop1 |
|Modern1.1.0 |3,1,3,1,3,1 |Racer3 / cop1 |
|Modern1.3.1 |3,1,3,1,3,1 |Racer3 / cop1 |
|Modern1.4.0 |3,3,3,3,3,3 |Both3 |
|Official final1.6.1 |3,3,3,3,3,3 |Both3 |

The complete43-byte store block `00485949..00485974` is identical in1.1.0/1.3.1: load EAX with binary32 bits40400000h (3.0), EBX with3f800000h (1.0), and alternate stores to `006fbc60`, `006fbe04`, `006fbfa8`, `006fc14c`, `006fc2f0`, `006fc494`. The complete1.4.0 replacement `00485943..0048596c`,41 bytes, loads EBX=40400000h and writes all six destinations from EBX. Final retains that block byte-for-byte at `00485932..0048595b`. These ranges end before the next unrelated default assignment, with no calls or branches inside the captured stores.

This dates **MP140-073's equalization mechanism directly to1.3.1→1.4.0** and gives **MP100-032 partial historical support** from an early retained EXE. The old1×/3× bullet describes early Modern, not final Modern;1.0.0 introduction remains unverified. This also distinguishes two edits: racer4→3 between supplied original and early Modern, then cop1→3 between1.3.1 and1.4.0.

The numbers are stored profile multipliers reaching the map-position scale under the linked selected-profile path. They are not physical pixel ratios, actual visible coverage or marker-size factors. Preferences can overwrite defaults; map fitting/recentering, active role/profile, later edits, source lifetime and rendering remain separate. Both catalog claims remain partial rather than runtime-verified. No executable, saved Ghidra database or maintained C changes were made.
