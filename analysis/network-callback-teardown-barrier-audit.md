# Network callback teardown barrier audit

> **Deferred draft:** preserved with the final session checkpoint. Not reviewed or qualified as completed in the current research pass.

## Scope and target

This pass follows the normal status-selected cleanup in `004a65e0` through packet-layer queue draining, endpoint cleanup, provider calls, and global reset. The target is the installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Analysis was static in an ephemeral REA/Ghidra session; no executable, runtime, or persistent Ghidra project was changed.

Question: does this path unregister/disable the type-5 receive callback and wait for any callback already executing before the setup accumulator is reused?

## Normal cleanup sequence

`004a65e0` first optionally sends packet type4 if WORD `007a22da` is nonzero, then calls `004f5280`, services a callback pump (`004e7630`), runs network-state cleanup (`0049eed0`), two other cleanup routines, and finishes with `004a6390`. This is the status-selected path described in the [setup and abort lifecycle audit](multiplayer-setup-abort-lifecycle-audit.md).

`004f5280` is a queue/list drain. Its instructions repeatedly obtain nodes from lists rooted at `009f2628` and `009f260c`, call `004f5330` on each, and, for the latter list, remove/report entries that remain. It does not stop a worker, acquire a callback-exclusion lock around the drain, clear the dispatcher slot, or wait for an active-callback counter. The two list roots remain globally referenced. The per-node `004f5330` invokes a descriptor method at `[node+4]+0x10` when node+0x10 is nonzero, conditionally decrements `00566df8`, and frees/clears the node's connection+0x30 collection through `005126c0`. The observed critical section in `004f29b0` protects removal from a separate eight-entry registry table; it is released before the subsequent empty-list check and possible cleanup call. Neither the queue traversal nor this registry lock is an established in-flight callback barrier.

The reset routine `004a6390` uses the fill helper `004e070c` to zero exactly these ranges: `[007a2294,007a22ba)` (0x26 bytes), `[007a22ba,007a22ca)` (0x10), and `[007a22ca,007a22da)` (0x10). It then sets `007a22da=1`, `007a22dc=0`, and `007a22e0=0`, and conditionally clears `007a22de`. The seven endpoint records start at `007a22e8` and are 0x6c apart in the indexed cleanup loop; these reset fills do not reach them. In particular, the callback fields written by `004a6410` at endpoint-record offsets +0x14, +0x18, and +0x20 are not cleared by the reset routine.

That last fact matters because `004a6440`, installed at endpoint-record+0x20 by `004a6410`, dispatches packet types through the callback table when WORD `007a22dc==0). Type5 selects `004c6080`. The teardown reset sets `007a22dc` back to zero; the dispatcher has no check of `007a22e0` or the loading-abort latch. Static code therefore does not provide a post-reset callback-disable gate at this dispatcher. This describes the local gate if a callback reaches it; it does not establish that a provider will deliver one after teardown.

## Endpoint/provider cleanup is a separate, unresolved boundary

`0049eed0` performs endpoint/provider cleanup only when dword `007a22e0==3` and `007a22e4!=2`. If local role WORD `007a22da` is nonzero, it walks seven endpoint records and calls `0049ecb0` for each record whose +0x10 field is nonzero. `0049ecb0` calls `004f5330`, then `004f4ff0` with endpoint+0x34, decrements `007a01e0`, and sets `007a2296=1`. The routine also conditionally calls provider methods through `004f4f50` and `004f4f90`, then clears `0055e860`. These are indirect vtable calls at provider-object offsets +0x34, +0x24, and +0x2c. Their implementation and whether any method unregisters, blocks, cancels, or joins a callback are not resolved by this executable-side wrapper.

Thus `0049eed0` is evidence of provider cleanup requests on one exact state/role branch, not proof of callback unregistration or quiescence. When its status gate is false, the endpoint/provider operations above do not run at all. Even when true, no local wait or in-flight count is visible in the traced callers and callees.

The socket-provider close route is distinct. The type-1 socket path previously traced through `004f71a0` removes an entry from the active list, shuts down and closes its socket, marks its socket/status fields closed, and recycles the provider record. The reviewed close path shows no worker-snapshot retirement wait. It is not called directly by `004a65e0`'s visible sequence, and a socket close cannot be substituted for the unresolved NPS/provider vtable behavior. Likewise, packet-layer queue draining is not evidence that a socket reader or NPS callback has stopped.

## Conclusion

For the status-selected normal cleanup path, static evidence establishes queue-node draining, conditional endpoint/provider close requests, and reset of network state globals. It does **not** establish an unregister-and-wait barrier for callbacks already in flight. The endpoint dispatcher slots are not cleared by `004a6390`; after that reset its local `007a22dc==0` gate again permits type dispatch, including type5, if delivery reaches it. A late append after reset is therefore not ruled out by the packet dispatcher itself.

That is a conditional exposure, not an observed late delivery or demonstrated cross-session corruption. Whether a late callback can occur depends on the unresolved provider/scheduler lifecycle: callback-thread ownership, callback serialization, the semantics of the indirect provider methods, and the lifetime of endpoint records. The precise remaining gap is provider/runtime evidence showing that cleanup prevents or drains all callback invocations before `004c5e80` resets the shared type-5 cursor for the next transfer.

## Evidence and bounds

REA evidence from the exact binary:

- `004a65e0` sequence: `ev_17c5cddc65f76ddf43512a72f98d908a317b8e9375a82b69e059456b70cfcfc4`.
- `004f5280` drain and queue traversal: `ev_7a45925ef0d7746214925ea37ba2e5161d88a2721b815b141ec13593c781deb1`.
- `004f5330` per-node callback, counter decrement, collection free: `ev_abe8529026af4c9ad66e379d2700156a82686ce906eef92fd9796d8f69d83462`.
- `004f29b0` registry-table critical-section scope: `ev_1631ac7908454026ad303abb2a4e1d8f09dfcc212bd343fd7d16faa81a96edbc`.
- `004a6390` reset ranges and scalar stores: `ev_6cb080fbee7d3c760dcab8209dd28ef4249069c29a71cbf004c0301d0bf25ea3`; fill helper `004e0721`: `ev_44096693a5cb6ea9eaec4df7944e24572abc18e03c656feda0d26c261e6e353c0`.
- `004a6410` endpoint callback-slot installation: `ev_a7993ea2bd2d2a034086d5b0cd96eb17af9e4efbf196b6a8c46703c85844c1ba`.
- `0049eed0` status/role gates and seven-record loop: `ev_e3feb92e491c1c977cc6cae67b7c3b274520ba7b05a91c718bc5d8c7d1a5d4ac0`; `0049ecb0`: `ev_dc7077796213c65e6bf04c7af97e2ab6c59f1f03b1e2c25500bb3bc476fa8121`.
- Provider wrappers `004f4ff0`, `004f4f50`, and `004f4f90`: `ev_74048d752f4fdf08cded37dd730173a808eb41bf7dae03059fd4449b0198f0e7`, `ev_26a29732409cf84d6e3261a9d9c405e508f13ecc73400e2cf5f79c316ed25f97`, and `ev_a1d6795f93f8303f29aa8669a84141f57d757ee3a97da307496fda62990a4718`.
- `004a6500` initializes the seven endpoint records through `004a6410`: `ev_33d61c74071823fb8c31475f7ead06a04604dcaa34fc201076a79ab4869a01bb`. Dispatcher and type-5 callback behavior are retained in the linked setup audit and network roster/unpacker reports.

The negative barrier finding is bounded to these callers, reset routine, queue/list cleanup, provider wrappers, and the previously inspected socket close path. It does not resolve indirect provider implementations, callbacks running outside the executable, or concurrent runtime order. No runtime/network session was exercised.
