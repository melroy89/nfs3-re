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
