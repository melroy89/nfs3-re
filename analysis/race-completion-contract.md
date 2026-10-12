# Race completion and shared exit state

## Established local publication

CheckRaceCompletion004ceae0 returns early for nonzero007d369c. A successful
mode predicate publishes1 at004ceb24 before FinalizeRaceVehicleStates
004ceb2a (EAX3). Ordinary synchronous reentry through this same dispatcher
is suppressed while that value remains set. Unsupported unsigned race-mode
values>3 do not locally finalize. This is not a concurrency guarantee.

## Shared flag and reset boundary

The existing global name is g_nRaceLoopExitRequested. It is not exclusive
to successful finish: pause-action stores at004c4c7e/004c4cbf/004c4d0e/
004c4d57 also publish1. Callback initialization004c460f clears it. Full
reset004c4740 uses XOR EBX,EBX at004c476c then clears it at004c479e,
before seed/subsystem initialization calls beginning004c47b3. No intervening
call modifies EBX on that clear path. RunRaceLoop has additional writes at
004c5434/004c54e5 requiring their own branch/register analysis.

## Existing predicate distinctions

Saved comments/pseudocode retain mode2 bit80 exclusions versus modes0/1
all-player counting, status3 and signed wrapping(startTick+448)<tick gates,
and session4 nonzero network-state alternatives. Three-group mode3 logic
also accepts status4 in its first two groups and may assign status3 to
unfinished third-group entries. Names do not prove all enum/role meanings.

## Remaining Astra work

Full reset/exit/restart ordering, concurrent/aliased flag writes, participant
count/index lifetime, signed tick-wrap admission, network ownership, mode
semantics, finalization/result persistence and actual runtime transitions
remain open. A nonzero exit flag alone must not be counted as a finish.
No binary or runtime state was changed during this pass.


## Alternate finalization order

RunRaceLoop branch004c54ae requires nonzero WORD007a22dc. It loads
EAX1/ESI1 at004c54d6/db, calls finalizer004ce750 at004c54e0, then
publishes ESI to the exit flag at004c54e5. Full finalizer assembly saves
ESI at004ce753 and restores it at004ce7fa, establishing the stored1 on
normal return. This route publishes after finalization, unlike
CheckRaceCompletion. Therefore the earlier before-call protection is
strictly local to the completion dispatcher. Event identity, full branch
reachability, reentry and network ownership remain unresolved.


## Conditional loop clear remains ABI-dependent

Luna bounded review identifies ESI zero initialization004c52f6 before
store004c5434. Parent verified the store and its local gates:0055eb2e bit20,
pause flag007d36a0 zero, exit flag nonzero, and007d36b4 zero. Intervening
004d5cc0/00418610 calls have unresolved transitive register-preservation
contracts, so do not upgrade intended zero to a proven end-to-end clear.
Astra should verify those callbacks/ABI or capture the actual transition
before closing loop-reset lifetime. Existing direct initialization clears
remain independently established.
