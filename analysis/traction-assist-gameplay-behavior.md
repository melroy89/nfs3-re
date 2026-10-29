# Traction assistance: menu to physics consumers

## Established control

The installed level menu binds Traction to `listname=traction`, descriptor `0055662c`, selection DWORD `006fd488`, with ordinal0 Off and1 On. The regular-race builder copies that setting to runtime DWORD `006fd4a4` at `00473c72`; Hot Pursuit clears the runtime DWORD at `004746cd`. See [gameplay-assist-menu-crosswalk.md](gameplay-assist-menu-crosswalk.md) for exact descriptor, token and localization evidence. This establishes a mode-specific setting, not a live configuration capture.

## Concrete effects

`UpdateVehicleWheelAndProfileCoefficients` (`004aab41`) checks runtime `006fd4a4` at three sites:

- At `004aacfa..004aad21`, each of four material-derived coefficient fields (`vehicle+5d8`, `+5dc`, `+5e0`, `+5e4`) is multiplied by float1.41 when the runtime assist is nonzero **or** override bit01 at `006fd4fc` is set. The override is a separate producer of this effect.
- At `004aad7d..004aad8f`, on the signed-raw-magnitude branch for vehicle field+4f4 greater than10.0, assistance multiplies profile coefficient+24c by1.41 before the signed original+4f4 coefficient calculations for fields+5c8/+5cc. The other pair+5d0/+5d4 instead uses the original profile coefficient times1.5, without that assist multiplier.
- At `004aae13..004aae76`, the lower/equal branch assigns the four fields from profile coefficient+24c times1.41 plus1 when assistance is on; off uses the unscaled profile coefficient plus1.

The three float constants at `0053dcf8`, `0053dcfc`, `0053dd04` all have raw DWORD `3fb47ae1`, approximately1.4099999666. A coefficient multiplier is not proof of a universal41-percent grip increase: subsequent calculations, branch selection, materials and profile values remain relevant.

`LimitVehiclePlanarResponseAndAccumulator` (`004ac3af`) has two further assist gates. In its main limiter, assistance plus response-record+28 zero and signed-raw vehicle+5b0 greater than0.15 selects a specialized response/accumulator path. Otherwise it uses the ordinary branch. At the later conditional response scaling (`004ac8d8..004ac8fe`), assistance multiplies response-record+24 by the computed ratio; off multiplies it by half that ratio. These paths have additional magnitude, vehicle and profile gates; they are not unconditional per-frame adjustments. Existing function comments retain the exact arithmetic and raw-bit/x87 distinctions.

## Full-physics path qualification

The coefficient routine's reviewed direct caller is `IntegrateVehicleFourWheelResponses` (`004ad7a3`). The default physics dispatcher `004ae4c1` reaches that integrator only with vehicle category bit02 clear, byte+8a zero, and signed raw DWORD+10c at least `0x3f666666`. Its category-bit02 branch instead calls `ProcessAIVehicleDynamics` (`004088f0`). Thus these coefficient effects are tied to the qualified full-physics path; the global setting is not proof that the AI dynamics path receives identical assistance. The planar limiter is called by `CalculateWheelPlanarResponseRecord` (`004aca4f`). Actual callback selection remains a runtime question.

## Evidence and completion boundary

Parent Ghidra decompilation and instruction review covered all five direct physics reads of runtime006fd4a4: `004aacfa`, `004aad7d`, `004aae13`, `004ac588`, `004ac8d8`. Other direct references are the regular-race write, Hot Pursuit clear and stored-record assist metadata read. Independent PE section-aware constant reads confirmed all three1.41 encodings; original-byte objdump confirmed the branch sequences. Executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. No executable/configuration changes or runtime-memory writes were made.

**DONE:** connecting the existing Traction menu choice to mode-specific runtime storage and its direct coefficient/limiter effects.

**OPEN:** physical units/meaning of the underlying fields, actual selected settings, player-perceived difference, complete indirect consumers and PSX handling comparison. This is distinct from Braking assistance and CARP `usesanti`; no ABS or universal grip conclusion follows from this audit.
