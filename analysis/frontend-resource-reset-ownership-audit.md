# Frontend resource reset and async ownership audit

## Scope and conclusion

Static inspection of the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) focused on `ServiceFrontendObjectResourceLoadStateMachine` (`00468860`), reset (`00467ac0`), three archive read submitters, completion recycling, and their direct call sites. The ephemeral REA/Ghidra session was closed without a snapshot. No executable, runtime, or persistent Ghidra state was changed.

The reset path does not locally remove or join queued/in-progress reads before clearing state and releasing buffers. Read submission publishes destination pointers into async worker queue records. The follow-up [worker ordering audit](async-selection-worker-ordering-audit.md) establishes that type-2 file selection does not cancel earlier reads: the single worker consumes queue entries FIFO and finishes its current read before processing a later selection. This leaves the local ownership gap intact, while no inspected path proves reset actually runs with a request pending; no use-after-free is claimed.

The nested loader context itself is not passed as the read callback context: `QueueAsyncReadWithZeroContext` sets `ECX=0`, and the queue producer stores that zero at request-record `+0x24`. Destinations include the inline preheader at nested `+0x174` as well as allocated buffers (`+0x18c/+0x190/+0x194`); the nested context also retains request IDs and phase state.

## Producer to worker-queue edge

REA assembly evidence on `004f15d0` (`ev_638c65fdea58bd7959bd9b17b4031f037c139bb4a70552aded31c3ed6e7cea03`) is a direct adapter: it saves `ECX`, zeros it, calls `004f1500`, restores `ECX`, and returns the result. Assembly for `004f1500` (`ev_24ef7142b2086869b5787050129883f05a76743225ea4d4b5c4219eec0d65d1b`) shows it obtains a request node from the async state's recycle queue, assigns a sequence ID at node `+4`, sets node state `+0x20=3`, stores `EDX` (destination pointer) at node `+8`, stores length in `+0x10`, stores zero context at `+0x24`, appends the node to async state queue `+0x70`, and wakes the worker through `004dfb20`. It returns the node ID, or zero on node-allocation failure.

The installed read submitters publish that returned ID only after the queue call:

| Submitter | Destination allocation | Request ID field | Instruction sequence |
| --- | --- | --- | --- |
| `00467ea0` preheader | inline context `+0x174` (16 bytes) | `+0x160` | Calls `004f15d0` at `00467ed1`, stores EAX at `00467ed6` (`ev_479fa8a255e56214ff91824d53f80cc242b09861474d40d87e8c5dcb64b690d8`) |
| `00468010` primary | context `+0x18c` | `+0x168` | Calls `004f15d0` at `0046814f`, stores EAX at `00468154` |
| `00468170` secondary | context `+0x190` | `+0x16c` | Calls `004f15d0` at `0046829b`, stores EAX at `004682a0` |
| `004682c0` tertiary | context `+0x194` | `+0x170` | Calls `004f15d0` at `004683eb`, stores EAX at `004683f0` |

The primary path (`ev_f4921e40c17410d4eb403ddabd45d6b548bae6f7f18ae5e4e3da5d473c968fe2`) also publishes the requested length at `+0x184` before checking allocation success. Secondary and tertiary assembly (`ev_a8c279b1e8ab1aaa9e0401f906ecd47676843cea8715a82fc4a9ab51329f1ee6`, `ev_d00196d0122df5382b98a00c981f810a85087b370c57350ff22f335289d2e55a`) confirms their corresponding destinations and IDs. Each submission result is a queue-submission indicator; it is not a completion result.

## Reset, free, and completion edges

Reset assembly `00467ac0` (`ev_07b47e4a1d1ef04c56cf067a4248fbd1c81642f8ed831c296af39cb8ae2bf5c6`) performs, in order:

1. Calls `004f1370` with the literal `nul` string (`0053ac80`). The helper creates a type-2 queue record on async state queue `+0x70` and wakes the worker. The [worker ordering audit](async-selection-worker-ordering-audit.md) establishes that this does not cancel or drain prior reads: it is FIFO behind them, and closes/replaces the file only when the worker reaches it.
2. Clears request IDs `+0x160`, `+0x164`, `+0x168`, and `+0x16c`, plus phases `+0x198/+0x19c`. It leaves `+0x170` untouched and zeroes 16 bytes at `+0x174`.
3. Clears the first byte of member names and frees nonnull allocations `+0x188`, `+0x18c`, `+0x190`, and `+0x194` through `004e1890`, then clears those pointer fields.

There is no direct call from this reset body to the completion consumer or to a named cancellation routine. The `nul` operation is queued separately; the worker's no-cancel FIFO behavior is documented in the [worker ordering audit](async-selection-worker-ordering-audit.md). The tertiary ID remaining in `+0x170` also means reset does not erase all request bookkeeping.

`GetAndRecycleAsyncReadCompletionStatus` (`004f1790`, `ev_834119554bc6b2eeeb35e7e29b85cc92aca865f837dff4eb4deaaa126ecdb3f5`) searches completion queue `+0x38` by request ID, removes a match, recycles it to queue `+0x1c`, and returns 1 or -1 based on completion-node `+0x20`; it returns zero for no match. The loader tests only zero, so either nonzero value advances its state. This is a completion-consumption path, not a cancellation path.

## Callers and ownership boundaries

REA's resolved direct-caller inventory for `00467ac0` is `00467c40` and `00468860`. The two loader direct-call xrefs are not assigned function records by Ghidra. Raw installed-binary instructions were inspected at those addresses and at the teardown block:

- At `00466d8e`, caller code invokes `00468860`, then checks outer `+0x3c` and proceeds through presentation/resource work if nonzero. This call site has no local loop waiting for the loader's terminal phase before continuing.
- At `0046785e`, setup code invokes the loader after allocating/initializing nested state. It loops back to call the loader while outer byte `+0xb1` is set, the loader result is nonzero, and nested completion phase `+0x19c` is not 8. This is a synchronous polling loop, but it is not a worker join primitive. It is bypassed when the active flag clears or the phase reaches 8.
- At teardown block `00467968..0046797a`, code calls reset at `0046796a`, then frees the nested object at outer `+0xb8` and clears that field. It does not poll the loader phase or wait for worker shutdown first.

These direct instructions establish one caller that polls state to a terminal condition and another that can call the loader and continue on the same invocation, plus a teardown path that resets and releases the nested context. A path that polls until phase 8 or inactive is not a worker join in itself; the loader's completion polls do consume matching completion records before advancing. The read-submission failure branches call reset only after the current submission returns zero, and the normal request phases advance through preceding completion polls. I found no call path in the inspected instructions that proves a nonzero pending request ID is still active at the instant of reset. The teardown caller's nested phase/request-ID state is not established. They also do not establish that teardown can run concurrently with the setup loop, nor that all callers share the same scheduling/serialization rules.

There is a distinct buffer-transfer edge: `TransferLoadedResourcePayloadsAndUpdateShapeTexture` (`00468410`, `ev_bcc7e83649649cad878b18b63c608394e3caf0325dc683857afb4561b41a56e3`) checks nested buffers `+0x18c/+0x190`, releases prior outer resources, copies those pointers to outer `+0xa8/+0xac`, then clears the nested pointer fields. This is an explicit ownership handoff for that pair once reached. The helper itself does not poll request IDs or establish async completion; the caller's state ordering is a separate precondition. Tertiary buffer `+0x194` is not transferred by this pair path.

At application async-I/O shutdown, `ShutdownAsyncResourceIO` (`004f0f40`, `ev_12c88d0fb9b014e19733737d7192d8dd014f7605a2b602e2f8b5e7cb2217b31d`) signals/clears active work, waits for state DWORD `+0` to become zero, then drains pending queues and releases their allocations. This is the explicit worker-lifetime boundary found in the scoped call chain; it is global shutdown and is not invoked by frontend reset or its direct callers. The wait depends on worker progress and is not evidence for reset safety.

## Assessment and residual assumptions

**Supported:** async read records retain destination addresses in queue `+0x70`; reset does not locally unlink those records and releases its buffers without an in-body completion wait; one teardown block frees the nested object immediately after reset; one setup caller polls phase state, while the normal frontend service caller does not locally join; a later helper transfers a subset of buffers by clearing nested pointers.

**Not established:** any particular queued request remains outstanding at reset; that the worker uses a destination after its buffer is released; whether the type-2 `nul` selection causes backend cancellation or drain; whether teardown can race the synchronous setup loop; whether provider/worker serialization or an external lock prevents lifetime overlap; whether any indirect callback re-enters the loader; or whether phase 8 follows completion of every write relevant to every freed/transferred buffer. The async queue's scheduling, file-selection handling, and callback contracts remain unresolved.

The remaining discriminator is frontend lifecycle timing: whether a reset can run while the worker is inside or queued for a read. A controlled trace should record each request ID, destination address, worker dequeue/completion, reset/free events, and teardown ordering for the same nested context. A completion must be correlated to its request ID and destination; reset or queue selection alone does not prove that no destination is still in use.
