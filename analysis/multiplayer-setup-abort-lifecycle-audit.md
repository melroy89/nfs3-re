# Multiplayer setup transfer and loading-abort lifecycle audit

## Scope and target

This audit follows the fixed setup transfer from its sender through the type-5 dispatcher and accumulator, then checks loading abort and session cleanup. It uses static evidence for the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`), the setup-framing notes in [detailed-analysis-notes.md](detailed-analysis-notes.md#multiplayer-setup-framing-and-music-list-ownership), the multiplayer ledger in [SCRATCHPAD.md](../SCRATCHPAD.md#partial-multiplayer-loading-synchronization-and-abort), and the type-1 unpacker report [network-unpacker-registration.md](network-unpacker-registration.md). No game execution, executable edits or persistent Ghidra changes were made.

## Sender-side framing

`004c5e80` is called by `00477f60` during race setup only when session mode `006fd3b0` is neither 0 nor 1, playback selector `006fd3a0` is 0, and the preceding loading-abort checks have not latched failure. At entry it resets accumulated offset `007d36d0` to0 and sets cursor `007d36d4` to setup buffer base `006fd39c`.

For host role (`WORD 007a22da != 0`), it takes `0x890` bytes from that buffer in chunks capped at `0xd0` (208). Integer division gives ten full 208-byte data chunks and one final 112-byte data chunk: `10*208 + 112 = 2,192 = 0x890`. For each, it writes type byte5 immediately before the data and calls `004a60e0` with helper payload length `chunk+1`. Thus the valid sender supplies eleven payloads of length209 (ten) and113 (one), carrying `0x89b` total bytes including type bytes and exactly `0x890` setup-data bytes. It advances the shared cursor through the source and ends one-past at `006fdc2c`. The send helper's outcome is not tested by this loop; exact local frame construction does not prove every payload was queued, delivered, ordered or accepted by a peer.

For client role (`007a22da == 0`), the routine instead snapshots sixteen local 108-byte records. After its marker waits it selectively restores each record's `+0x14` only when the saved signed value is 0..49, and always restores `+0x68`; other fields are left as received/modified. This is selective preservation, not whole-record rollback.

## Type-5 receive accumulator and packet gates

The network dispatcher (`004a6440`) reads type byte `packet[0]`. It invokes the registered handler only when WORD `007a22dc` is zero and the type is below `0x13`; table slot5 resolves to `AppendNetworkDataPayload` (`004c6080`). The dispatcher does not inspect `0055e88c`, the loading-abort latch, and does not pass a validated aggregate-size contract to the type-5 handler. The type-5 callback itself has no abort-state test.

At `004c6080`, the callback sets source to `EDX+1` (skipping the type byte), computes `n = EBX-1`, copies `n` bytes to `007d36d4 + 007d36d0`, then adds `n` to `007d36d0`. There is no local check that `EBX>=1`, that `offset+n <= 0x890`, that the callback is the next expected chunk, or that the resulting offset equals `0x890`. If called with a zero length, the subtraction underflows before the REP copy; upstream framing behavior and reachability decide whether that case can reach this routine. The type-7 callback `004c4190` copies a 20-byte record to `007d3650` and sets WORD `007a22a2=1`; this is a separate state update and is not a check of the type-5 accumulated byte count.

The bounded valid-producer case is precise: if the receiver starts with offset0 and cursor at `006fd39c`, and receives exactly the eleven host-produced type-5 packets once, in order, with their advertised lengths intact, the callback copies the 2,192 data bytes into `[006fd39c, 006fdc2c)` and ends with offset `0x890`. Duplicate, missing, reordered or extra packets break that conclusion. The receive handler has no cumulative bound or sequence/reset token that restores it locally. The socket framing path's exact `length+2` peek and WORD maximum apply only when that path is active; it does not supply a positive minimum or prove all transports take that path.

The sender and receiver share `007d36d4` as a cursor. On the client receive path, the sender branch does not advance it, so it remains at the buffer base. On the host send path, the loop advances it to the end of the setup data. The observed normal role split is consistent with host-send/client-receive; no local type-5 direction check in `AppendNetworkDataPayload` itself enforces that split.

## Loading abort and teardown path

`PollLoadingAbortKeyState` latches global `0055e88c`. `InitializeRaceSession` (`004a33f0`) calls setup transfer and several loading stages, polling between them. The outer track loader (`004dbbe0`) also has four tested abort checkpoints plus a final poll; early exits return without local resource/network rollback. On the common abort path, `InitializeRaceSession` calls `00494bd0` and `004df8e0`, returns failure, and `RunRaceSession` (`004a3690`) performs its session cleanup through `004a35d0`.

Two distinct state gates matter:

- The packet dispatcher checks `007a22dc`, not loading-abort latch `0055e88c`. A loading abort alone does not disable type-5 dispatch. Therefore, before session cleanup changes the network state, a received callback can still be routed to the accumulator when `007a22dc` remains zero.
- `ReleaseRaceSessionRuntimeState` (`004c4830`) reaches `004c64e0`, but that helper runs its `004c7bb0`/`004c5560` synchronization and packet-layer cleanup branch only when `0055e88c == 0` and playback selector `<2`. For a latched loading abort, this normal branch is skipped.

`RunRaceSession` has a later network-status-gated cleanup after an initialization failure: when session mode is above1 and `007a22e0 != 0`, it calls `004a65e0`. That helper sends type4 when local role flag `007a22da` is nonzero, calls `004f5280` to drain the packet-layer lists, runs network-state cleanup, then calls `004a6390`. The latter sets advertised count/state defaults, sets `007a22da=1`, clears `007a22dc` and `007a22e0`, and conditionally clears `007a22de`. These effects show an explicit teardown/reset path when the status gate selects it; they do not prove peer delivery of type4 or exclude a callback already in flight. When `007a22e0 == 0`, `RunRaceSession` skips this `004a65e0` branch, and the abort-gated `004c64e0` path has already skipped its normal cleanup; complete connection-layer lifetime for that state remains unresolved.

The transfer buffer is not cleared by the abort cleanup. Direct references to offset `007d36d0` are only the `004c5e80` reset, `004c6080` read and `004c6080` increment. The cursor pointer `007d36d4` is reinitialized by `004c5e80` and advanced by the sender; no cleanup reset or data clear was found in the reviewed direct-reference set. Thus a partial received prefix and its offset can persist after abort until the next invocation of `004c5e80`, which resets the offset and base cursor but does not clear the buffer bytes.

## Can queued data be consumed after reset?

Static evidence supports a conditional possibility, not a runtime occurrence:

1. A loading abort does not itself change dispatcher gate `007a22dc`; callbacks may continue to append before teardown.
2. The usual network cleanup path, when selected by `007a22e0 != 0`, drains packet-layer lists and resets network flags. Provider serialization, active callback completion, and late callback suppression after that drain are not established.
3. When the status gate does not select `004a65e0`, the normal cleanup branch is also suppressed by the loading-abort latch; no local type-5 callback guard prevents further accumulation if dispatcher delivery continues.
4. A later `004c5e80` invocation resets offset and cursor before its marker wait, but uses no generation/session identifier. Any old callback delivered after that reset would be accumulated into the newly selected buffer range. The local code does not distinguish old from current type-5 payloads.

Accordingly, the static path does **not** prove that queued/in-flight payload is consumed after reset, because normal teardown attempts to drain packet-layer lists and callback scheduling is unknown. It also does not establish a barrier that rules late delivery out for every status/transport path. The buffer residue and exact state gates are established; post-reset cross-session contamination remains conditional on provider/queue lifecycle and must not be presented as an observed defect.

## Evidence and remaining limits

REA function dossiers against the stated executable: setup sender `ev_33b5bd2b20703899f71f575be5029cc8aa12d1c9824a70f7d2d1249bb9726063`; setup caller `ev_2e8074c5d736c6aac80e4c7bf0ac17e540d5682a89bcfe3fd8743d7cf8c37a38`; session `ev_fc68ac5529cf04f1fdbf2fde435a11e4a25679ec42f7ca5b5c08fdee23aa6590`; race-session initializer `ev_06f730df0b98f252a00888884bcbe6f589617d7663bfa446fec702049651e645`; abort-aware track loader `ev_b9d7927c7ef08d54765d001fd329ac0bcdd7a53d6a88ddc8f5f2a8f3bf545a65`; failed-session cleanup `ev_46729d41affe25a4e332a0d4f9389d9ecbe6324a17eda3cad721e62109e79f2a`; release wrapper `ev_3da4824e826f258627c1e84142d83fd8eda33f212df7909b2ecfdf7e79c5a384`; abort-gated release helper `ev_466d96008b567a5f0df3a2f5c036f205a2e03a11fc256d77b2cc8796193e167b`; network reset `ev_ff8ac87f1709513d1548f9636fd5b9fcf1aee276722625464a38570ceee9ccc4`; network queue cleanup `ev_b00513ae55313986380ebb3eb39ffabb07ed28e090b31e0144aa5397753e6df3`.

The type-5 append routine (`004c6080`) and packet dispatcher (`004a6440`) are not FunctionManager entries in the current ephemeral Ghidra analysis. Their exact instruction sequences were checked against the selected executable bytes with bounded `objdump` ranges at `004c6080..004c60b6` and `004a6440..004a646d`; target identity/hash is stated above. The receive-slot table and socket framing limitations are retained in the linked network notes. No provider/runtime network session was exercised. The unresolved requirements are indexed receiver-count admission, exact callback/provider delivery and cancellation behavior, and proof of old-packet exclusion across abort/restart.
