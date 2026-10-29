# Async file-selection and read-worker ordering audit

## Scope and result

Static inspection of the installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, follows type-2 file selection from `004f1370`, ordinary type-3 reads from `004f1500`, the worker entry at `004f1820`, completion routing, and global async-I/O shutdown. Ghidra's ephemeral FunctionManager does not define `004f1820` as a function; its bytes were read with REA and disassembled at the exact address. The REA session was closed without a snapshot. No executable or persistent Ghidra metadata was changed.

**Finding:** The `nul` selection request does not cancel, flush, or overtake prior read jobs. Queue insertion is at the head and the worker removes the tail, preserving FIFO order. The singleton worker handles one job at a time. Its ordinary read path remains inside the read helper before returning to dequeue another job. A type-2 selection then closes the current file handle and selects/opens the new path. Therefore, if a reset enqueues `nul` while an older read is queued or executing, that read is processed first; the selection operation is not the mechanism that makes its destination safe.

The frontend reset remains a separate lifetime issue: it can clear/free a destination without joining the worker. The scoped static audit did **not** establish a live call path where a nonzero request is known to remain pending at reset time, so a freed-destination race is not claimed as an observed/reachable defect.

## Queue construction, synchronization, and order

`InitializeAsyncResourceIO` (`004f0da0`, assembly Evidence `ev_af60dcd64528a875f2b15c0c53ee915c154179bb4b1ef4797edb18e08e6cd2f9`) initializes the queues at state offsets `+0x1c`, `+0x38`, `+0x54`, and `+0x70`, then starts a thread with entry pointer `004f1820`. The worker waits on the state event when its input queue is empty; producers signal that event after enqueuing.

The common queue helpers prove FIFO mechanics:

- `0050de50` enters the critical section at queue `+0x18`, writes the inserted node's next link to the former head, makes the new node the head, initializes the tail for an empty queue, increments count, and leaves the lock (`ev_9590bee50a66dc3e74865fc2e15fdc97a45eb5b02696f73e728ff51c5d55364e`).
- `0050dff0` enters the same lock, removes the tail, walks from the head to unlink its predecessor when needed, decrements count, and leaves the lock (`ev_27bea5e7c28df93fe373e43ee6da4c932e5aa67c800ad9d111f2eab540496f22`).

Thus insertion-at-head plus removal-at-tail is FIFO. The critical section protects each list mutation only. Worker dispatch and I/O happen after the pop helper has returned, so producers can enqueue while a read is executing; such a new node waits behind older nodes in list order.

## Exact type-2 selection and type-3 read paths

`004f1370` creates a queue record with node `+0x20=2`, clears the read-related fields and callback `+0x24`, copies the requested path into node `+0x1c`, inserts it into state queue `+0x70`, and signals the worker (`ev_f678a77434efad6a4c89d5bb5c82a6096e98039d9baef0a94d14a84119149475`). Reset supplies the literal path `nul` (`0053ac80`). The worker dispatch table at `004f1810` subtracts 1 from node `+0x20`; type 2 reaches block `004f1a97` in the worker code (byte evidence for the switch and worker: `ev_9dd84da14f28bf68eeadb2e69d53fb9e020e2d0d538574e9f28098e908159414`). That handler:

1. Closes the current file handle if state `+8` is nonnull (`004e2da0`), clearing state `+8`.
2. If node `+0x1c` contains a path, opens/selects it through `004e28d0` and stores the resulting handle at state `+8`.
3. Routes the completed node according to `+0x24`; zero context goes to completion queue `+0x38`, nonzero callback/context goes to callback queue `+0x54`.

The type-2 handler does not walk or remove earlier nodes from queue `+0x70`, nor does it inspect/modify their destination fields. It closes the active file only when the type-2 node reaches the worker.

Ordinary reads are created by `004f1500` with node `+0x20=3`, destination at `+8`, file offset at `+0x0c`, length at `+0x10`, and callback at `+0x24` (`ev_24ef7142b2086869b5787050129883f05a76743225ea4d4b5c4219eec0d65d1b`). Frontend's `004f15d0` adapter forces that callback field to zero (`ev_638c65fdea58bd7959bd9b17b4031f037c139bb4a70552aded31c3ed6e7cea03`). Type 3 reaches worker block `004f1b28` and uses the currently selected file handle. It enters the associated file-handle critical section, seeks to the requested offset, reads into the caller-supplied destination, and leaves that critical section only after the read helper returns.

The read helper `004e3ae0` (`ev_6d184203dfaaf19d7061410a7d70eb0fb5ef11a8eb1cba09b7c65c6a4279d48a`) calls the imported `ReadFile` entry with a NULL `OVERLAPPED` argument (the mapped-view pointer tested at `004e3bcb/004e3bd0` is zero and `EDX=0` is pushed at `004e3c5a`). On `ERROR_IO_PENDING` (`997`), the helper calls `SleepEx(1, TRUE)` and jumps back to retry `ReadFile` at `004e3ba9`; it does not poll with `GetOverlappedResult`. The worker does not dequeue another queue node until this helper returns. This establishes worker-side serialization, but does not by itself prove OS I/O completion on unusual pending/abort/error paths. The destination is sourced from node `+8` while the helper uses it.

Worker bytes `004f1820..004f1c2b` are not a Ghidra-defined procedure; REA returned the complete requested byte range `ev_9dd84da14f28bf68eeadb2e69d53fb9e020e2d0d538574e9f28098e908159414`, and the switch/flow was checked against the installed executable's disassembly. Queue and helper bodies have separate REA assembly records cited above and below.

## Completion and callback ownership

After type-2 or type-3 processing, node `+0x24` selects its completion route:

- `+0x24 == 0`: worker appends the node to state queue `+0x38`. `GetAndRecycleAsyncReadCompletionStatus` (`004f1790`, `ev_834119554bc6b2eeeb35e7e29b85cc92aca865f837dff4eb4deaaa126ecdb3f5`) removes a matching node by ID and recycles it to `+0x1c`.
- `+0x24 != 0`: worker appends to callback queue `+0x54`. Registered callback `004f0d20` drains this queue; it invokes the stored callback after recycling when the node's thread affinity permits, and routes a node to `+0x38` when it does not. Byte evidence is `ev_789b54fa5683cf4d4592b8abf8b63ab251c1926f4b07e3e6d0512e63a1c2d0d3`.

Both frontend read submissions and the reset's NUL selection use zero callback/context. Their worker completions therefore go to `+0x38`, not the callback queue. `004f1370` does not retain a request ID in the frontend object or start a matching completion poll, so its selection completion is not synchronously consumed by reset; global shutdown is the reviewed cleanup path for queued completions. This is independent of whether the worker has already processed the selection.

## Shutdown and wait boundary

`ShutdownAsyncResourceIO` (`004f0f40`, `ev_12c88d0fb9b014e19733737d7192d8dd014f7605a2b602e2f8b5e7cb2217b31d`) sets the state stop flag, asks `004f0cd0` to clear/signal the active node/event, and waits until the worker clears its state event/handle field at `+0`. Worker stop handling occurs at the loop top: once the current dispatch returns, it closes any open file handle and exits instead of popping another node. Shutdown's wait for `+0` to clear is the actual join-like boundary in this subsystem; it then drains pending queues `+0x70/+0x38/+0x54`, recycles/frees queue-owned payloads, unregisters callback `004f0d20`, and destroys the queue heads.

This shutdown is not called by frontend reset. Reset's queued `nul` operation is not a substitute: it is ordered as ordinary queue work and does not wait for completion. Also, shutdown's active-node status clear is not shown to abort the in-progress type-3 read; the worker stop path is observed only after that read helper returns. The shutdown wait therefore protects teardown of the async subsystem by waiting for worker exit, while the frontend reset does not acquire that guarantee.

## Sequential assumptions and remaining limits

The evidence supports FIFO ordering within the single worker's queue, per-node queue locks, and the worker remaining within the current read helper before dispatching the next node; helper retry behavior is not equivalent to a proven completion wait on every error path. This means a selection queued behind an earlier read closes/replaces the file only after that read's worker operation has ended. It does **not** prove that another reset cannot free that read's buffer while the worker is using it, and does not prove a particular frontend reset occurs during a pending operation.

No worker-side cancellation/removal of prior reads is observed for type 2. The remaining reset-safety question is whether frontend lifecycle serialization guarantees reset only at a no-pending point, or whether a reset can overlap the worker's blocking read interval. The ownership audit did not establish such serialization or a nonzero pending ID at reset. A controlled runtime trace would need correlate the exact request ID and destination to read begin/end, reset/free, and worker queue events; no runtime test was performed here.
