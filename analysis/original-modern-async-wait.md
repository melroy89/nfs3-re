# Async-read wait: add a shared event notification

## Evidence boundary

The complete same-address function `004f0cd0..004f0d1c` (76 bytes, exclusive end), saved as `ClearActiveAsyncReadStatusAndWaitForChange`, differs in ten bytes, all inside `004f0cf0..004f0cfc`. The [reproducible audit](scripts/audit_async_wait_difference.py) checks the pinned executable hashes, complete caller and three supporting wrappers, and resolves the relevant PE imports. [The manifest](evidence/audits/async-wait-difference.json) records span hashes and retained disassembly. No game, thread, event or instruction execution was performed.

## Retained entry and polling behavior

Both versions preserve incoming ECX/EDX and load the state pointer from `009f0be0`. If null, they return. Otherwise ECX receives the pointer at state `+18`; when nonnull, DWORD `[ECX+20]` is cleared. They then reload the state pointer to obtain its first DWORD as an event handle.

After notification, both set EDX=0 and repeatedly reload `009f0be0`. The loop exits if the state's first DWORD becomes zero, the captured ECX pointer is null, or state `+18` no longer equals that captured pointer. Otherwise it calls `004df8e0` with EAX=0 and retries. The complete sleep wrapper `004df8e0..004df8ef` is byte-identical and invokes imported `SleepEx` at `00534604` with arguments `(0, 1)`, preserving ECX/EDX. This is an alertable zero-duration polling call, not a blocking wait on the state event.

The initial null check does not protect every subsequent state reload: the loop dereferences the reloaded pointer without a new null check. This is retained behavior, not a newly introduced Modern defect. State lifetime, concurrent writers and callback/APC effects must be qualified before translating this into safe concurrent C. No crash or hang is claimed.

## Changed notification sequence

| Original | Official Modern |
|---|---|
| Load event handle into EDX | Load event handle into EAX |
| Put address `009f0be4` into EAX | Call `004dfb30` directly |
| Call `004dfb20` | Then call `004ff780` |

Original `004dfb20` moves EDX to EAX and falls through padding into `004dfb30`. That wrapper preserves ECX/EDX, pushes EAX and calls imported `SetEvent` at `005345e8`. Thus original's apparent EAX state-address argument is overwritten before the API call; it is not an additional pointer passed to SetEvent. Modern's direct call retains the first event notification without that overwritten argument.

The additional Modern call reaches existing helper `004ff780..004ff7a3`, also byte-identical between versions. It loads DWORD `00567864`; if zero, it returns. Otherwise it saves ECX, writes DWORD 1 to `0056785c`, and signals the loaded handle via `004dfb20`, then restores ECX/EDX. The change adds a conditional **flag publication plus second event notification before polling**. The helper was already present in original; Modern adds this caller edge rather than introducing its implementation.

The first SetEvent result is not checked before polling in either version. Modern likewise does not test the added helper's outcome here. The local caller's additional notification does not establish delivery, receiver wakeup, completed I/O or improved scheduling.

## Reconstruction and follow-up

**Bounded comparison status: done; evidence confidence: verified static bytes and import binding.** Preserve both Modern notifications and their order, ECX's captured-pointer role, the status clear and exact polling conditions. Original compatibility needs only the original notification at this callsite. Do not replace the loop with an assumed equivalent blocking event wait without separately qualifying APC handling and shared state.

**Pending:** event creation/reset/close ownership, the consumer of flag `0056785c`, all producers of state `009f0be0`, cancellation and shutdown ordering, and actual race/load behavior. These affect linking/interface reconstruction and runtime validation. Trace those producers/consumers before assigning a specific deadlock fix or release-note claim. The executable, Ghidra database and reconstruction sources remain unchanged.
