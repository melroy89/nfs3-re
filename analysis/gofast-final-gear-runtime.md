# GOFAST final-gear lookup

The bounded loading question is closed: a normal menu-entered GOFAST Single Race reaches a final-gear index beyond the 41 torque samples. This is an out-of-table read within the physics profile, not evidence of an unmapped-memory access or a demonstrated driving defect.

## Evidence

The user entered GOFAST before loading the race, selected Diablo SV with automatic transmission and paused at countdown 2. The read-only snapshot at tick404 has session0, race_mode0, override_flags1, model14/DIAB and default tuning `[1,0,1,1,1,1,1]`. See [retained sample](evidence/runtime/gofast-countdown.json).

`ApplyCarTuningToPhysicsParameters` (004a78d6) applies the GOFAST multipliers. Its final-gear calculation uses active count7, ratio[6]=71.94600677490234 and maximum velocity162.84722900390625. Their product is11716.207841189113. Nearest, down, up and toward-zero FISTP rounding all yield integer quotient45 after signed division by256. The live x87 control word was not sampled, but its rounding choice cannot change this index for these inputs.

At004a82ad the unchecked read is `profile+0x114+4*index`. Index45 gives profile+0x1c8, the maximum-velocity field itself; valid torque indices are0..40. Final gear factor is0.00447172112762928; final efficiency1.0099999904632568.

The remaining instructions multiply the fetched value by the gear factor, divide by efficiency and `(1+aero)/3`, divide by `max_velocity^3 * float32(0.3675715923309326)`, then multiply by float32(0.9800000190734863). Reproducing each explicit float32 store yields **6.67679501020757e-07**, exactly matching vehicle+0x58c. Constants were read from0053dc80..8f, and assembly004a8324..004a83a0 independently reviewed.

## Limits

This combines reachable live inputs/output with static instruction semantics; it is not a breakpoint or instruction trace. No executable, asset or live memory was changed. Visible handling/top-speed consequences, intended formula and behavior for other cars/tuning are not closed by this observation. Driving is unnecessary to establish this startup calculation.
