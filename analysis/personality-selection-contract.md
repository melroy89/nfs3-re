# Personality and palette selection status

This report separates saved bounded findings from the remaining Astra work.
Original context is preserved in[backlog context](astra-backlog-context.md).

## Nearest palette numeric boundary

FindNearestFcePaletteIndex0049d240 scans while its index is signed below
both FCE counts+7fc and+900. It converts requested and candidate colours,
then compares three-channel Euclidean distance; fourth channel is excluded.
No local16-entry clamp is present. Ordinary ordered equal distances keep
the earlier entry. Full assembly reveals an additional numeric boundary:
FCOMP/FNSTSW/SAHF/JNC at0049d2f3..f9 accepts unordered comparisons
under masked invalid, too. The candidate is stored to binary32 without pop
before comparison, so comparison uses extended ST0 against binary32 best.
Ghidra comment refined and saved. Exceptional reachability is unproved.

## Established historical bounds

Saved context establishes ordinary opponent selectors0..6 and police7..14,
per-build usage-row resets, conditional first7/8 uniqueness, and bounded
byte-counter scans. Low19-bit LCG exhaustive enumeration gives18/20-draw
colour-selection bounds only with normally evolving seed and fixed exclusion.
These historical conditional findings do not establish global seed ownership.

## Remaining Astra validation

Alternate-pool model/palette compatibility and activation, seed ownership,
alias writes, unusually large within-build counter wrap, profile producers
and extent, caller resource validity and exceptional numeric equivalence
remain open. No runtime behaviour or reachable fault is claimed.


## Verified selector wrapper domains

Full assembly readback confirms00473550 passes row2/count7 to
SelectLeastUsedSetupOption00473360;00473570 passes row3/count8 then
adds7 to its result. These select profile variety, not participant population.
The start helper00474c60 returns a zero-extended byte, so the selector's
signed remainder by positive7/8 starts in the corresponding nonnegative
domain. The helper raises its threshold after each complete cyclic scan;
usage is a zero-extended byte, so threshold255 necessarily accepts a slot
with valid stable storage. Conservative probe bounds are7*255+1=1786
and8*255+1=2041. Selected-byte increment wraps255 to0 but does not expand
the returned index domain. Counter-row addresses are00678e00..06 and
00678f00..07.

This does not validate the start helper's own table address: it uses signed
remainder of wrapping session+offset by256 before the byte read. Lookup
offset admission, storage ownership, reset timing and eventual profile use
remain separate. No new global bound is inferred.
