# `usesanti` response semantics audit

## Current label follow-up

The later [UI action crosswalk](controller-action-label-crosswalk.md) establishes Accelerate and Brake for sample+1/+2 and Handbrake for player actionmask04/vehicle+50d. This closes the labelled input-source question, not the physical ABS/wheel-slip feedback question. Earlier unresolved-label wording below is superseded by that crosswalk.

## Scope and result

This is a bounded static audit of the installed PC executable `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. It follows direct accesses to physics-profile byte `+0x1d4` through `CalculateWheelPlanarResponseRecord` (`004aca4f`), its normal limiter (`004ac3af`), the alternate delegate (`004ac094`) and the four-record caller/integrator (`004ad7a3`). No game runtime was observed and no executable or persistent Ghidra project was changed.

**Result:** `usesanti` conditionally enables a per-wheel primary-response cap in the ordinary response path. The capped quantity is a signed scalar already derived from several inputs and scaled by profile field `+0x248`; it is not identified as a direct brake-pressure variable. The cap is skipped for a nonzero vehicle state byte `+0x50d`, which also selects alternate response handling under particular record-selector conditions. The code does not inspect a measured wheel-lock or wheel-slip ratio at the `usesanti` branch. The evidence supports an anti-lock-related generic response limiter, but does not establish complete ABS behavior, which controller action is braking, or whether a particular profile is active at runtime.

## Direct-access census and provenance

A full `objdump -d -Mintel` scan for memory operands matching `PTR [...+0x1d4]` in the installed executable found these relevant decoded sites:

| Address | Access | Role / boundary |
|---|---|---|
| `004acd99` | `cmp BYTE PTR [eax+0x1d4],0` | Runtime consumer in `CalculateWheelPlanarResponseRecord`; exact gate below. |
| `004b0e1d` | byte store | Default physics-profile initialization writes zero. |
| `004b17cd` | byte store | CARP parser stores the low byte of parsed integer field 17. |
| `004b2f6e` | byte load | Unfunctioned profile serialization/formatting path; loads the setting for output, not the response calculation. |
| `004b4c47`, `004b4c4d` | byte comparisons | Unfunctioned profile-record comparison dispatcher case for the byte at `+0x1d4`; not a motion consumer. |

Other textual matches with `+0x1d4` in the disassembly use stack-relative indexed locals and are not accesses through the physics-profile base. The CARP descriptor at `004af460` points to token `usesanti` (`0053e7fc`) and field ID 17. Parser case `0x16` writes the low byte at profile `+0x1d4`; absent fields default to zero. This bounds the consumer census to direct decoded offset uses and does not cover pointer aliases or dynamically computed addresses.

The read-only installed asset inventory covers 47 `.viv` files below `GAMEDATA/CARMODEL`: all 47 parsed profiles contain field 17 with raw value `0` or `1`, 35 are `1` and 12 are `0`. This describes the installed asset set only; it does not identify the selected/loaded profile in any run. The inventory method parses CARP text and does not execute the game parser.

## Response-record roles and exact clamp gate

`CalculateWheelPlanarResponseRecord` accepts EAX = vehicle and EDX = mutable `0x30`-byte response record. Relevant record fields are `R+0` primary signed response `P`, `R+4` capacity input `C0`, `R+0x0c` angle, `R+0x10`/`R+0x18` planar inputs, `R+0x1c`/`+0x20`/`+0x24` outputs, `R+0x28` raw DWORD selector, and `R+0x2c` marker/status. These are operation roles; physical units are not established.

The usesanti clamp capacity C is the unchanged raw R[1] at R+4. A SEPARATE local coefficient L=float(R[1]-scale*R[1]) is computed near entry for later response calculations. Helper004abd9c receives EDX=[V+220]+58 (participant tyre tuning), not R+4. Its returned scale must not be mistaken for a mutation of the clamp capacity. The earlier same-sign gate can reduce `P` toward zero: for positive `P` and positive `R+0x18`, take the smaller when the `V+0x5f0` / gear-byte gate passes; for negative values of both, take the larger under its corresponding gate. Zero or opposite-sign values do not satisfy these paired branches. After that operation, the primary is multiplied by physics-profile float `+0x248`.

For ordinary ordered finite values, the `usesanti` byte is tested only after all these conditions hold:

1. The same-sign reduction gate succeeded (`bVar4` in the recovered flow).
2. `abs(P) > C` using the assembly's ordered floating-point branches.
3. Vehicle byte `V+0x50d` is zero.
4. Profile byte `profile+0x1d4` is nonzero (`cmp` at `004acd99`).

If so, the branch compares `P` to `+C` and `-C`, storing `+C` for an upper excess and `-C` for a lower excess. Thus for a finite nonnegative `C`, the resulting scalar satisfies `-C <= P <= C`. The instruction sequence is at `004acd99..004ace0f`; this interval includes the byte test and clamp stores. The proof does not establish `C >= 0` for every admitted input, nor a policy for NaNs, infinities, negative capacity or x87 exception state. The flag is a one-byte nonzero test; the installed inventory happens to contain only zero and one.

On the capped branch the helper also writes `R+0x2c = 3.0` when signed simulation tick modulo 4 is zero, and zero otherwise. This is a transient marker, not the final normal-path vehicle status: `LimitVehiclePlanarResponseAndAccumulator` (`004ac3af`) imports prior selected status and then clears `R+0x2c` at `004ac572`; the limiter's later value is what the normal path copies back to `V+0x5c0` or `V+0x5c4`. The cap to `P` remains in force despite replacement of that marker.

## Alternate state and independent response limiting

Before the `usesanti` test, `V+0x50d` updates a saturating counter at `V+0x514` (increments by 3, 4, or 1 according to `V+0x160`, bounded above by `0x180`; zero state clears it). When `V+0x50d` is nonzero:

- raw `R+0x28 == 0` routes directly to `004ac094`; or
- a nonzero selector routes there if the same-sign reduction gate succeeded and ordered `abs(P) > R+4`.

Otherwise control continues through the normal path. The alternate helper bypasses the normal call to `004ac3af`, output rotation and final status copyback at `004ad222..004ad24f`. Its calculation uses response magnitudes, capacity and state/history; its entire downstream effect is outside the claims of this audit. The use of raw selector bits is significant: a nonzero bit pattern is not equivalent to floating-point nonzero.

The normal limiter `004ac3af` is a separate mechanism. It forms a weighted magnitude from `max(abs(R+0x1c),abs(R+0x24))` and `min(...)`, compares that against a reciprocal-adjusted capacity, and may update an accumulator/status. It receives the already-produced planar outputs, including the primary scalar copied to `R+0x24` at `004ad1db..004ad1e0`. It should not be conflated with the earlier `usesanti` test: that test caps `P` before this independent vector-response limit. The standard path zeros `R+0x20`, sets `R+0x24=P`, invokes the normal limiter, rotates the output pair by `R+0x0c`, and copies status according to raw selector `R+0x28`.

## What scalar is being limited; why ABS semantics remain incomplete

The caller `IntegrateVehicleFourWheelResponses` (`004ad7a3`) makes four `0x30`-byte records and invokes the response helper for each. It derives the primary response from an engine/drivetrain result split by profile field `+0x1d0`, then combines it with an additional signed, speed-limited term involving `V+0x5ec` and profile field `+0x1d8`. The per-record construction also uses profile field `+0x1dc`; when `V+0x50d` is nonzero, a `0.05` term is included in that distribution. The engine/drivetrain result itself depends on vehicle/profile state and gear/RPM-derived calculations. The caller scales each record's x/z outputs by `V+0x1a0`, combines front/rear pairs in separate half-sums, and adds the resulting vector divided by 32 into vehicle motion `V+0xa4/+0xa8/+0xac`.

Consequently `usesanti` limits a composite wheel planar response scalar that can include engine and normalized controller-derived terms. It is not directly clamping a field identified as brake pressure, nor does the local branch measure wheel angular velocity against vehicle velocity. The vehicle byte V+50d is directly assigned from action-mask04 by UpdatePlayerVehicleControls00431430; other controllers and consumers must be audited separately. Its semantic action name remains unresolved in this pass; it must not be described as exclusively engine/gear/speed-produced. This suggests a drivetrain-state gated response limiter, not a demonstrated wheel-slip feedback controller.

The vehicle floats `V+0x5f0` and `V+0x5ec` are normalized from separate sampled control bytes by the controller update path, but the action assignment of those channels is unresolved. Their consumers support engine-response and wheel-response roles; they do not justify naming either as throttle or brake. Likewise, the legacy string at `0053e1a0` (“Uses Antilock Brake System”) is label evidence only, and no evidence here establishes a user-facing toggle. No PSX parity inference is made.

## Evidence and boundary

- `CalculateWheelPlanarResponseRecord`: retained REA/Ghidra analysis `ev_c4eb6bd084c4393f944735072753237d447a36e1fadf55b484c446fc8eca3d3d`; runtime clamp bytes at `004acd4c` are `ev_a9c0aeb82056c43ff88ab42ef0424a5a838dedea7146433add7f9de5af4660d4`.
- Normal response limiter `004ac3af`: analysis `ev_244c448c57c00ad70cf9e214d6426ecd0ec1a5db09ee7edb1094571c4496714b`; raw bytes from its entry `ev_e90468273dd5d7f7427d0b76906b614a6e374f2325a4e6190d2ebd9646f5a750`.
- Alternate delegate `004ac094`: analysis `ev_90a5d29b72c8efb032338ab946c6250a1775a7dbacab9b133f554bfd7635fb68`.
- Four-wheel caller `004ad7a3`: instruction bytes `ev_e154a899b9c5f6f66c118013471a897a5d027020b337e50564d218c3a036ce8b`; caller calculations and field roles are also recorded under “Four-wheel orchestration frame and selector producers” and “Four-wheel motion integration and damping order” in `analysis/detailed-analysis-notes.md`.
- CARP parsing/defaulting and inventory: `analysis/detailed-analysis-notes.md` (“ABS field provenance and response path”) and `analysis/evidence/inventories/controller-profile-inventory.json`.
- Input channel identities and provenance boundary: `analysis/controller-channel-calibration-audit.md`.

Static question resolved: the field gates a capacity clamp on the primary per-record planar response in a specific ordinary-path state. Remaining: physical units, exact braking-channel identity, all alternate delegate effects, the semantic identity and runtime admission of `V+0x50d`, whether the clamped quantity corresponds to tire-lock prevention in operation, and which installed profile is active in a given session. Those require additional source/runtime evidence; they are not supplied by the field name.

Parent live004aca4f/004abd9c review corrected the raw clamp capacity versus separately adjusted local response coefficient, and verified player action-mask04 as one +50d producer. These corrections are material to interpreting the branch.
