# Track-profile controller integer quotient

Target: `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
Function: `004a83d3`, currently `UpdateVehicleControlsFromTrackProfile`.
Evidence: saved Ghidra instructions and read-only extraction of installed resources. No new runtime execution or instruction trace supports this report.

## Result and scope

The quotient is a genuine signed integer division before conversion to float. Its downstream clamp makes it a coarse three-regime controller under the assumptions below. Developer intent, whether integer division was deliberate, and the visible driving effect are unresolved.

The installed-resource denominator question can close: all 47 inventoried profiles have positive `redline - idle`, between 4050 and 7480. This excludes divisor zero and signed IDIV overflow for those successfully loaded endpoints. It does not establish a global valid gear index, safety of modified profiles, or admission of this function in every race mode.

## Exact computation and branches

Let `v` be the vehicle, `p = DWORD[v+528]`, and `gear = unsigned BYTE[v+50b]`. Offsets below are hexadecimal. All integer arithmetic follows the binary's signed comparisons and 32-bit wrapping; `FISTP` uses the current x87 rounding mode.

1. Fetch track speed at segment+7, or segment-7 on a reverse track; wrap once. `GetAISpeedTableSample0040e080` returns an unsigned byte as a float (0..255), or fallback64.
2. Multiply by the heading-dependent modifier, using default1 or `p+2b0/2b4/2b8`; spill to float32. Subtract float speed `v+4f4` and spill to float32. Call the result `residual` (`004a8703–004a8723`).
3. For ordinary finite `residual > 1`, increment the control accumulator by `min(FISTP(residual*0.5)+4,16)`. For ordered negative residual, decrement by `max(FISTP(residual*0.67)-8,-24)`. Separate pre-gates return an accumulator on the wrong side of 256 to 256.
4. For ordinary finite `0 <= residual <= 1`, calculate:

```text
derivedRPM = FISTP(speed * FLOAT[p + 94 + 4*gear])
idle = signed DWORD[p+1c0]
redline = signed DWORD[p+1c4]
if signed DWORD[v+590] > idle:
    q = trunc_toward_zero((derivedRPM - idle) / (redline - idle))
else:
    q = 0
v.control520 = 256 + FISTP(float32(q) * 256.0)
```

The gear-indexed read and conversion occur at `004a8899–004a88c3`, **before** the RPM admission comparison at `004a88d2–004a88de`. Division is `IDIV ECX` at **`004a8919`**, followed by `FILD` at `004a891e` and float32 storage at `004a8921`. Multiplication by256 and final conversion occur at `004a892d–004a8948`.

The gate uses current RPM `v+590`; the numerator uses speed-derived RPM. These are separate values and must not be substituted for each other.

The implementation tests the residual's signed integer bit pattern against `3f800000` as well as making an x87 comparison with zero. The simplified three-way residual description applies only to finite values. NaN, infinity, x87 invalid-conversion handling and 32-bit tick/state corruption are outside this closure.

## Effect of the quotient

Requested target is `256 + unsigned BYTE[v+504] - unsigned BYTE[v+505]`, in1..511 (`004a8433–004a8454`). The target state at `v+218` starts at256 (`0042be7c`) and moves toward the request by at most32 per call (`004a8726–004a87a6`). The only identified direct literal-offset writes are this initialization and smoother; aliased writes are not exhaustively excluded.

Let `T` be that smoothed target. With `T` in1..511, finite moderate `q`, and no conversion/addition overflow, the quotient branch is clamped at `004a894e–004a89a9` to:

| Quotient | Final control520 | Output consequence |
|---|---:|---|
| `q <= -1` | 0 | Gas byte508=0, brake byte509=255 |
| `q = 0` | `min(256,T)` | Coasting when T>=255; requested braking when T<255 |
| `q >= 1` | T | Smoothed requested input |

Output conversion is at `004a89af–004a8a22`. Both255 and256 produce zero gas and zero brake. In particular, with nonnegative derived RPM below redline and the installed endpoint ranges, the quotient is zero. Derived RPM at or above redline gives a positive quotient only if the separate current-RPM gate admits division. This is not a fractional throttle calculation.

## Installed resource evidence

[controller-profile-inventory.json](controller-profile-inventory.json) records all 47 extracted profiles, per-archive and per-member SHA-256, member offset/size, classification, gear counts, idle/redline, both eight-entry velocity-to-RPM tables, and three corner speed modifiers. [inventory_car_physics.py](inventory_car_physics.py) reproduces it using only the Python standard library:

```sh
python3 analysis/inventory_car_physics.py \
  '/home/melroy/.local/share/winegui/prefixes/NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III' \
  --output analysis/controller-profile-inventory.json
```

The script reads the active `GAMEDATA/CARMODEL` tree and excludes the backup `gamedata_org`. It checks BIGF declared size, member extents, duplicate numeric fields, eight-entry ratio widths, and finite numerical values. Decimal floats are converted to IEEE float32 using Python nearest-even conversion; this is a resource inventory, not execution or emulation of the game's text parser. Archive hashes make later resource drift reviewable.

| Property | Installed range |
|---|---:|
| Minimum/idle RPM, CARP12 | 0..1350 |
| Redline RPM, CARP13 | 4800..8500 |
| Redline minus idle | 4050..7480 |
| Velocity-to-RPM entries, CARP7/76 | approximately -839.466..763.151 |
| Corner speed modifiers, CARP52/53/54 | approximately 0.399991..0.999880 |

Parser descriptor entries at `004af438/004af440` associate CARP12/13 with slots17/18. Stores at `004b170a/004b1731` write profile `+1c0/+1c4`. Common tuning `004a78d6` reads these endpoints but does not modify them. Defaults can write them at `004b0dc3/004b0dd5`; incomplete or malformed profile/default semantics are outside the installed successful-parse contract.

With finite installed untuned modifiers, valid speed-table access, and finite residual0..1, vehicle speed is approximately -1..255. A valid index into the installed untuned ratio arrays therefore gives speed-derived RPM magnitude below215000, well inside signed32 conversion range. The positive denominator and this bound also keep the quotient/moderate conversion path safe. The bound does not claim that every combination is reachable in a race, nor that tuning or a bad gear index preserves it.

## Caller admission and later validation

The sole resolved direct caller is `004a9bc4`. It calls this function at `004a9d1d` only if `006fd490 != 0` or `006fd494 != 0`, after excluding racer-category state3. Earlier low-motion handling does not clamp current gear+50b.

Regular race setup copies menu globals `006fd474/006fd478` into `006fd490/006fd494`. Descriptor `005565f0` binds name `braking` to474; descriptor `00556618` binds `steering` to478. Installed `FEDATA/MENUS/level.mnu` exposes braking assistance. Hot Pursuit explicitly zeroes both effective flags at `004746a5/004746ab`, so an ordinary Hot Pursuit run does not exercise this quotient.

A useful runtime case is a regular race with braking assistance enabled. Capture the effective assist flags, current gear, profile pointer and RPM endpoints/ratio, vehicle speed, heading-derived modifier and track-speed sample, current RPM, and control states508/509/218/520. Near the adjusted track target, distinguish derived RPM below and above redline. Asynchronous memory samples alone cannot prove an individual branch executed; an instruction trace or sufficiently bounded observation is needed for that claim.

## Closed and still open

- **Closed statically:** integer rather than floating division; exact quotient/clamp behavior under stated finite-state assumptions; positive installed denominators; bounded untuned conversion with valid array index; ordinary Hot Pursuit admission exclusion.
- **Open:** global gear-byte validity and exceptional gear writers; nonfinite/malformed/defaulted profiles; tuning multiplier bounds; unreviewed aliased profile/state writes; current FPU policy at execution; actual branch frequency, visible oscillation and original design intent.

Parent review independently verified the quotient/clamp assembly and added the bounded result to the saved Ghidra function comment. No executable, resources or live memory were changed.
