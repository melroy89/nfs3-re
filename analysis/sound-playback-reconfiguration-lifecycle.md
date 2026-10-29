# Sound playback reconfiguration lifecycle

## Scope and finding

Static review of the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows `004e89f8` through its direct header-parser caller, the periodic stream-state callback that also reaches it, and the relevant start/stop callback publication paths. It does not execute the game, audio backend, or hardware, and makes no persistent Ghidra edits.

`004e89f8` makes one tagged-patch start attempt per invocation. It has no retry loop. Ordinary retry behavior is supplied by its callers: `004e80cc` may make one attempt after a changed stream header, while state-1 invocations of the periodic callback at raw address `004e85a8` can attempt again on later scheduler calls when their local gates still permit it. A separate state-3 path waits for the current voice to expire, releases queued stream nodes, and returns the stream state to 1. These are setup and state transitions; a nonnegative start result is not evidence that playback completed or was audible.

## One attempt in `004e89f8`

The routine first calls `004e8fd0` with `00564690`, the stored voice handle/status. If the check returns zero (the current handle still resolves), `004e89f8` immediately returns `-1` without making a new tagged-patch request. A nonzero result proceeds. The sound-uninitialized result is also nonzero, so that test alone does not suppress the later attempt.

The routine checks patch-ready byte `005646fc`. If it is zero, it emits the `PATCH_NOT_SET` diagnostic and, if the diagnostic returns, continues. It initializes a stack playback-parameter record through `004e9b20`, copies four current setup bytes from `00564702..05`, and calls `00501de8` once with the record and shared patch data at `005646a0`. Its result is stored in `00564690`.

- A negative result increments the persistent WORD at `00564706`. At values above `10000`, it emits the failure diagnostic and returns the saved negative result if the diagnostic returns. At or below that threshold it returns the negative result directly. There is no loop or backoff inside `004e89f8`.
- A nonnegative result is passed to `004ffc9c`; the returned low byte is saved as `00564701` and sign-extended to select a 96-byte voice record whose byte is copied to `005646ff`. The code does not branch on `004ffc9c`'s result before using its low byte. It then writes stream state `2`, clears patch-ready byte `005646fc` and the failure WORD, publishes callback address `004e7e98` through `004ff660`, and returns the stored voice handle.

This establishes a nonnegative tagged-patch setup result and the following voice-record/state writes. It does not establish audible output, completion, or backend callback completion. Also, the `-1` “handle already resolves” result is negative; callers that classify every negative return as a start failure cannot distinguish it from a failed backend attempt on return value alone.

## Callers and retry transitions

### Changed stream header: `004e80cc`

`004e80cc` is the only function-manager direct caller. The normal dispatch path is `004e7f30`: it enters the sound critical section, recognizes the `SCHl` tag (`0x6c484353`), calls `004e80cc`, and leaves the section afterward. Therefore the header-triggered start and surrounding header/state writes occur within that dispatch critical-section interval.

The parser compares the current eight-byte header with the saved header when its change flag is set. On a difference, it calls `004e89f8` only when stream state `005646fd` is neither `2` nor `3`. A negative return causes the `COULDN'T START` diagnostic; if it returns, the parser sets state `3` and the header-change flag. A nonnegative return also flows to the common state-`3` store. Thus the caller overwrites the success-path state `2` with state `3` as it completes this reconfiguration path. It then copies the header, signals `005021ac(-1)`, marks patch-ready, calls `004e68a0`, and returns `1` on its ordinary return path. That return value does not report the playback-attempt result.

The header caller does not immediately retry when the changed-header attempt fails: it leaves state `3`, which suppresses another changed-header start attempt. Re-entry into state `1` is handled by the periodic state machine below.

### Periodic service and state-3 wait: raw callback `004e85a8`

`004e8944` initializes the stream queue state and, when registration byte `00564708` is zero, registers raw callback address `004e85a8` through `004e7520` with `EDX=0` and `EBX=1`. The scheduler records the callback and an interval/deadline value derived from its current clock plus `1`; the time unit is not established here. The callback address is not a separately recognized function entry in the ephemeral provider database, so its state dispatch below is supported by exact-executable disassembly.

The callback first applies a service-availability gate, then enters the same sound critical section and dispatches on `005646fd`. In its state-1 path, two conditional branches call `004e89f8` (call sites `004e869d` and `004e86f5`). Each returns from the callback after the attempt; there is no local retry loop around either call. If state 1 and the relevant chunk/header conditions persist, another scheduler invocation can make another attempt. The interval value is 1, but this static trace does not assign real-time units or prove scheduler cadence.

In state 3, the callback checks the stream's remaining-count helper. While that value is positive, it returns and preserves state 3. Once the value is not positive, it requests voice cleanup through `004e9670` and polls `004e8fd0` with the current handle. A zero result returns to the scheduler for another poll. A nonzero result proceeds to `004e7ff8` to clear/release the queued chain, calls `004e8944` to reset stream initialization state, and sets state `1` before returning. There is no state-3 deadline or bounded wait in this callback path; progress depends on queued-count and voice-handle observations changing.

This asynchronous state-3 transition is distinct from the synchronous purge routine `004e7b28`, whose separate wait loop has a service-clock deadline and diagnostics documented in the detailed notes. The purge result does not supply a timeout to the periodic state-3 branch.

## Callback and lock ownership

There are two callback mechanisms in this path; their addresses and lifetimes should not be conflated.

- `004e85a8` is the periodic stream-state callback registered through `004e7520` by `004e8944`. Stream stop/purge paths remove it through `004e75e0` when registration byte `00564708` is set, then clear that byte.
- `004e7e98` is published in global slot `009f6a50` after a nonnegative playback-start result. The setter `004ff660` is only `MOV [009f6a50],EAX; RET`: it neither validates nor locks nor waits for prior invocations. The consumer `004ff670` checks the slot and calls it indirectly; on its active path it uses a separate library critical section at `00564480` conditionally. The callback body at `004e7e98` updates the sound-stream notification/deadline fields and may invoke another optional callback at `0056480c` before calling the threshold checker.

The stream packet dispatcher and periodic state callback each hold the sound critical section (`00a09b04`) while executing their state path. Helpers such as `004e8fd0` and `00501de8` also enter and leave that section internally. The publication setter itself has no synchronization; the top-up consumer uses section `00564480`, not `00a09b04`. Consequently the inspected code shows pointer publication/clearing and several protected call paths, but no single lock or in-flight-call barrier that proves callback replacement is quiescent.

The successful purge path clears `009f6a50` with an explicit zero in `004e7b28` after the voice-expiration wait and under the sound section. Shutdown callback `004e784c` also clears the slot at entry, before its availability/callback checks, and then invokes purge when its gates pass. Clearing the slot prevents later consumer lookups from selecting that pointer; it does not itself wait for a callback invocation already in progress.

## Limits and remaining uncertainty

- The validated reachability and lifetime of voice-record indices and the 96-byte table extent are not established by this lifecycle trace.
- The `00501de8` return establishes the start helper's status/handle convention only. The callback writes and state changes do not prove audible playback or completion.
- State-1 retry cadence and eventual success depend on ordinary stream arrivals and scheduler progress. State-3 cleanup can continue polling indefinitely if its remaining-count or voice check never advances; no runtime timing claim is made.
- The callback setter and consumer do not establish race-free replacement or callback quiescence. The static path contains no explicit callback reference count or join at `009f6a50`.
- Diagnostic handlers may affect whether the returning branches described above continue; this report distinguishes code that follows when they return.

## Evidence and reproduction

Artifact identity: SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

- `004e89f8` start attempt: `ev_6257d93f281851f462eb11aeb5fcc2d89004ee03fde5bcec7213e35631a6e350`.
- Header parser `004e80cc`: `ev_107765ed9524a252799d340362c5831779a2a3e8bba9c58f4ad54a75d1db6c87`.
- Packet dispatch and critical-section envelope `004e7f30`: `ev_c64f9395071beb04e76b70abc168d221df7d925585e49c18dbfb01356bf91e08`.
- Stream initializer/periodic-callback registration `004e8944`: `ev_9b203afd299f0167a501af97701693192a512eb762291646d771a49c605cba4f`; scheduler `004e7520`: `ev_844da111f89c6183a58f3e41211111d5492087289c1b54fcae76a78baf36340e`.
- Handle check `004e8fd0`: `ev_77a71e50d9829cc2caf970c809e57c45618ea169e52d44d28dacb25491e9e031`; voice-slot lookup `004ffc9c`: `ev_7e2b60657178042289423e2e430a975a9b863a1ca51d9259b8d33de82d56f4bd`.
- Tagged-patch start helper `00501de8`: `ev_03e3b0896c514ef5e07b1d12725374c9a84c4d43d6eb95effc943d1c67c8cc72`.
- Queue cleanup `004e7ff8`: `ev_a5dd6056095fc55cb61fd5a6158977e6496585ad1efb3e74c25cdf21c4a0b96f`; purge/wait `004e7b28`: `ev_29faf6c53409bed42cb76e419e81be2be67ea7ab1938d581297a9536246abebf`; shutdown `004e784c`: `ev_841505e009432f479ce2364d0a7f78a4e6f0f589f8ff6c21384f4eac3f1152cb`.
- Callback setter `004ff660`: `ev_14810379f1c6e6da172c2d61ff83600ea6b85a42b8afb247c30bf52ecd947655`; consumer `004ff670`: `ev_57323fe0884ef483a23a10593d22a74095d6e89e45054e1d42d53e4019c74470`.

For the callback ranges not exposed as function entries, the exact executable can be inspected with:

```sh
objdump -d -M intel --start-address=0x004e85a8 --stop-address=0x004e8944 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004e7e98 --stop-address=0x004e7f2d '<selected nfs3.exe>'
```

No game/audio execution, hardware test, executable/configuration write, or persistent Ghidra annotation was performed.

Parent reviewed the start/header/voice-expiry and callback publication/consumer bodies, plus full original-byte periodic callback004e85a8..004e8940. Parent retained the existing shared-project function ServiceQueuedSoundStreamPlayback004e85a8 and saved its state/retry/wait comment; the callback is now a recognized function in the shared project (its absence above describes the worker's ephemeral database). The separate consumer lock is identified by address00564480, without assigning exclusive display ownership. No audio playback or wait duration was observed.
