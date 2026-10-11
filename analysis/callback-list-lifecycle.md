# Race callback-list lifecycle

Static assembly and complete returned direct-reference inventories from the saved nfs3.exe project. No runtime callback mutation or instruction trace was captured.

## Closed bounded ownership findings

All resolved direct calls to insertion004be250 belong to the race initialization chain: initializer004c45f0, vehicle registration0042c830, force-feedback registration004711e0 and final pair registration004bc910. Each of the latter three has only one returned direct caller, in004c45f0. The two final callbacks are00426680 and004cb2c0, contextNULL, priority100, on list007d368c.

All11 resolved direct removal calls belong to cleanup: one at004c487d and ten in0042cab0. The vehicle cleanup has only caller004c4882. Release004c4830 is called only from shutdown004a35d0, whose two direct callers are in RunRaceSession004a3690. The abort branch004a371c shuts down after initialization fails, before the race loop. Normal shutdown004a383b occurs after RunRaceLoop004c4e40 returns and the restart loop exits. Thus these explicit removal paths are not ordinary per-tick self-removal. This is a direct-call graph result, not proof excluding indirect reentry or concurrent access.

Dispatcher004be3a0 has two returned direct callers:004c4a7f on even ticks for007d3690, and004c4a97 every tick for007d368c. Both run before tick increment. It uses live list count and index; the callback must preserve its register-based dispatch state. If a callback indirectly mutates the active list, current/earlier removal can skip the shifted next entry, and earlier insertion can repeat an entry. No such execution was established here.

## Ordinary initialization capacity bound

Both lists allocate capacity0x90=144 at004c4651/004c4665. CreateCallbackList004be1f0 requests16*capacity+24 bytes and stores capacity at+0/count0 at+4; insertion does not check it. Records have16-byte stride with priority/function/context at list+8/+c/+10.

For N valid configured vehicles, registration adds six callbacks per vehicle to the even-tick list, plus one when categorybit04 is clear. The even-tick list also receives global0042ce70 and at most one force-feedback callback: at most7*N+2 entries. The every-tick list receives +610 for every vehicle, +604 if bit08 or04, and +614 if bit04; plus the final pair: at most3*N+2. For N<=16 these maxima are114 and50, below144. This proves capacity sufficiency for one ordinary initialization under the stated roster bound, not a universal N<=16 invariant, safe re-registration or allocation success.

## Membership and teardown qualifications

The +604 registration condition is category bit08 OR04, but removal uses bit01. These predicates are not universally equivalent. For explicit hexadecimal bit patterns,0x05/0x0b satisfy both predicates;0x04 registers without removal;0x22/0x12 satisfy neither. These are predicate examples, not a fresh runtime category inventory. An entry admitted only by the registration predicate can remain until whole-list destruction; that alone does not establish an absent-pair removal or a gameplay defect. Changing categories/counts/callback fields between phases remains a separate contract.

Force-feedback registration requires selected device!=-1 and playback0, then inserts even if resolved targetNULL. Removal additionally requires nonNULL matching vehicle, current device/playback conditions and device-record readiness00471dc0. A surviving entry is subsequently freed with the whole list. Predicate stability and unusual teardown/reentry remain open.

RemoveCallbackFromList004be2f0 returns forNULL/empty lists, otherwise searches exact function/context and shifts after first match. Absent pairs still reach004be379 and decrement count, logically dropping the last entry. Cleanup frees both lists at004c48aa/004c48b4 without clearing the globals there. Earlier preparation resets globals; abnormal ordering and indirect mutation cannot be dismissed from these local facts.

## Remaining investigation

Global/aliased/indirect mutation, asynchronous ownership, abort/reentry resource lifetime, configuration changes across registration and teardown, and registered/configured count equality are still unresolved. No reachable missed or duplicated gameplay callback is asserted. The bounded direct lifecycle and single-initialization capacity questions are closed; overall callback ownership remains partial.
