# RUSHHOUR traffic configuration contract

Static assembly review of cheat input, roster creation, configuration setter/getters and reactivation. No RUSHHOUR runtime run is claimed.

## Activation and survival

Encoded keyword005594a2 contains bytes5b5e5c5151585e5b, which subtract9 to RUSHHOUR. Dispatch index13 sets006fd4fc bit08 at00452825. Frontend cheat admission permits session0/1 and race0/3. Regular roster00473bf0 preserves override flags only for session0; Hot Pursuit00474640 masks them with0x10 at00474c42, removing RUSHHOUR. Consequently Hot Pursuit is not a valid runtime test of this override even when the menu accepts the keyword.

## Allocation is separate from reactivation

Regular roster reads opponent selection006fd4d0: zero gives0 AI opponents, nonzero signed values below2 give1, and values>=2 fill8 minus human racers. With traffic enabled (006fd4e8==0), traffic allocation is max(0,8-human racers-AI opponents). No RUSHHOUR flag is consulted in this allocation.

For ordinary session0 with one human, opponent selections0/1/2 yield respectively7/6/0 traffic slots when enabled, and0 when disabled. Thus RUSHHOUR cannot produce15 traffic vehicles through this roster. Its cap15 exceeds the maximum ordinary solo allocation7. This is a roster/cap distinction, not proof of actual visible density or valid frontend reachability for every setting.

Installed FEDATA/MENUS/opponent.mnu contains TRAFFIC_BUTTON and TRAFFIC_CASCADE bound to list traffic. Menu visibility/disable dispatch is not proved by file presence alone. The reconciliation writer0044c0b4 forces traffic disabled in modes1/2; regular mode does not receive that particular forced write. A later runtime test must first confirm that a nonzero traffic roster exists.

## Cap and delay

ConfigureTrackAIParameterRecord0040e3c0 sets record+0=15 and+4=0 under bit08. GetConfiguredTrafficVehicleLimit0040ef10 returns the selected record+0 without a weather/night adjustment. GetTrafficReactivationDelayRange0040eed0 adds200 for nonzero006fd4cc and400 for nonzero006fd4c8 after reading base delay. Therefore RUSHHOUR ranges are0/200/400/600, not universally0.

Deactivation00405d40 writes countdown1+((range*u)>>16), with u in0..65535. These four ranges cannot overflow the multiplication. Base-only0 yields1; other ranges bound countdown to1..200/400/600. The override does not remove the tick>=1920 gate in0040c210. At eligible checks, positive countdown decrements; only1->0 evaluates the cap. A failed cap check leaves0; next call writes2 and rejects, followed by2->1 rejection and then1->0 retry. Thus repeated cap checks are separated by three eligible invocations after failure, absent competing writes.

The compared count is signed registered traffic005efd8c minus shared inactive AI0056ebc0, not a direct scan of active traffic. If the registered traffic count is<=7 and the shared inactive count is nonnegative without arithmetic overflow, the cap15 cannot reject. This conditional inequality does not prove counter invariants globally.

## Remaining population contract

Returned direct xrefs show the shared inactive counter is cleared by0040cb20/0040cb50-family helpers, incremented on deactivation and decremented on activation. The activation controller serves traffic, police, opponents and nonlocal humans; police reactivation bypasses the traffic cap. Therefore traffic-only accounting requires mode/state invariants, not just the counter's use in the cap test. Reset+630 writes and aliased state remain relevant.

Closed statically: keyword/flag, mode filtering, ordinary solo roster0/6/7 distinction, cap-versus-allocation separation, delay modifiers and retry cadence. Open: actual RUSHHOUR loaded configuration and traffic activation, menu availability, mixed/network-human accounting, shared-counter consistency, multi-human placement and retry termination. No binary, assets or live memory were changed.
