# Music-worker cleanup: remove forced thread termination at shutdown tail

## Evidence boundary

The complete same-address shutdown function `004e4a30..004e4b41` (273 bytes, exclusive end), saved as `StopHeadMusicStreamWorkerAndReleaseHandles`, differs in exactly eight bytes inside `004e4b28..004e4b35`. [The audit](scripts/audit_music_worker_cleanup.py) checks pinned executable hashes, full caller, supporting wrapper bytes and PE import bindings. [Its manifest](evidence/audits/music-worker-cleanup.json) records hashes and disassembly locations. No music, thread or instruction execution was performed.

This extends the [music-start comparison](original-modern-music-start.md). It is a distinct callsite from the [race-input worker shutdown](original-modern-input-worker.md); similar removal of forced termination does not establish a shared worker or identical lifecycle.

## Changed cleanup operation

| Original at `004e4b28` | Modern at `004e4b28` |
|---|---|
| `LEA EAX,[ECX+8c]` | `MOV EAX,[ECX+8c]` |
| Zero ESI | Call `004dfc00` |
| Call `004df870` | Zero ESI |

The original passes the address of an embedded record to `004df870`. Its normal nonnull/non-minus-one path reads the record's first DWORD into EBX, calls imported `TerminateThread(handle, 0)` at `004df881`, then imported `CloseHandle(handle)` at `004df889`. This 36-byte normal-path witness is byte-identical in Modern. Its separate invalid-pointer diagnostic branches are outside the retained normal-path span.

Modern instead passes that first DWORD directly to `004dfc00`, whose complete 13-byte wrapper simply calls the same imported `CloseHandle` and preserves ECX/EDX. The wrapper is also byte-identical between versions. Thus the modified caller removes **forced termination**, retaining handle closure at this point. It does not replace the normal helper with a changed implementation, and it does not add a wait before this handle closure.

Neither old normal-path helper nor Modern close wrapper clears the embedded handle field. Both caller tails clear global `005645b8` after the operation. API results are not checked by this tail. Whether the handle identifies an already-exited worker depends on the earlier protocol; closing it alone does not prove that.

## Retained shutdown protocol and limitations

The entire prefix before `004e4b28` is byte-identical. Both require the supplied pointer to match the active object at `005645b8`, with an existing diagnostic route when that global is zero. They write request value 8 to object `+24`, test/poll object `+28` against 1, and retain a signed tick/deadline diagnostic using `0079c1a4 + 10000`. A zero return from the diagnostic call is not assumed; its exceptional continuation is not a successful-shutdown guarantee.

The retained later prefix writes request 8 again, signals the event at active object `+a8` through `004dfb20`, calls `004dfb70` on object `+a4`, closes that `+a4` handle through `004dfc00`, releases `+ac` through `004eb360`, and clears `+ac`. The SetEvent wrapper/import binding is directly checked by this audit. The complete semantics of `004dfb70`, worker-side request handling and the relationship between the `+a4` and `+8c` handles are **not established here**; the presence of an earlier wait-related helper must not be promoted to proof that the removed TerminateThread was redundant or that the same thread has finished.

One retained detail matters for faithful reconstruction: after the initial polling-state check, EBP can be reused for diagnostic metadata while ECX remains the object pointer for subsequent polls. Treating EBP as a conventional frame pointer throughout would misrepresent these register contracts. Shared globals and fields must likewise retain ordering until synchronization is qualified.

## Readiness and follow-up

**Bounded comparison status: done; confidence: verified static caller/API difference.** Preserve the selected version's address-versus-handle argument, retained request/event operations and final global clear. Do not add forced termination back to Modern or silently add a join while claiming instruction-level compatibility.

**Pending:** worker startup/exit protocol, handle identities and ownership, the full prior wait helper, concurrent shutdown/reentry, and audible/runtime behavior. These affect ABI/data reconstruction and runtime validation. Trace those relationships before claiming a deadlock fix, leak fix or universally safe teardown. Executable bytes, Ghidra state and maintained reconstruction sources are unchanged.
