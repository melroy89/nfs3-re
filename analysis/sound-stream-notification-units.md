# Sound-stream notification units and callback

## Scope and result

Static review of the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows the top-up callback at `004e7e98`, its threshold check and remaining-count helpers, their normal chunk/end-tag producers, and the ordinary Pathfinder hook stored at `0056480c`. It reuses the existing arithmetic contracts for `004e7c58`, `004e7ce0`, and `004e7df4`; no game/audio/hardware execution or persistent Ghidra changes were made.

The “buffer-time estimate” at `004e7ce0` is a scaled remaining-chunk count divided by a byte read from the selected voice record. It is compared directly with signed integer threshold `0056476c`, but the divisor's meaning is not recovered, so neither milliseconds nor samples-per-second can be asserted. The callback's separate deadline is more interpretable: it stores `0079c1a4 + 60 * 005643d8`. The timer setup supplies `005643d8` as a requested pulse rate; the installed startup requests 128 pulses/second. This makes the deadline nominally 60 seconds if the active worker increments its clock once per requested pulse. Actual delivery cadence remains unverified.

When `004e7df4` selects its clear/notify path—on a satisfied threshold, one of its below-threshold fallback conditions, or timeout—the code clears the threshold, sets/signals the shared audio top-up event when its handle exists, and invokes the optional `0056480c` hook with zero. This is a top-up/check notification and a hook reset; it does not establish that new samples were produced or that playback finished.

## Normal data and end-tag production

`004e7f30` is the stream packet dispatcher. It routes `SCDl` data chunks (`0x6c444353`) to `004e8078`, which increments DWORD `00564698` once per submitted chunk node and adds that node's DWORD `+4` payload length into `0056469c`. The latter is the observed accumulated payload-byte quantity. `004e7ce0` does not read `0056469c`; its numerator is the count-like field `00564698`.

The matching `SCEl` end-tag (`0x6c454353`) routes to `004e82ec`. That handler increments `00564678` once per end tag. If byte `005646fe` is zero, it writes `-1` through `00564684` (the current linked-queue tail pointer), marking the tail link as terminal; it then releases/signals the end-tag node. The stream initializer writes `1` to `005646fe`; the examined direct references show no zero store, so the ordinary zero-state producer is not established. End-tag count, terminal-link insertion, and node signaling are distinct from audible playback completion.

## Remaining-count estimate and threshold

The existing helper contracts give the following chain on the active initialized-stream path (disabled/unready paths return status values):

1. `004e8078` adds one for each dispatched `SCDl` chunk. The stream consumer/refill code updates the same counter as queued nodes are processed.
2. `004e7c58` returns `00564698 + result(005017b4) - (0056470d == 2)`. The installed `005017b4` body is `XOR EAX,EAX; RET`, so its contribution is zero. The extra subtraction is conditional on the byte mode at `0056470d`; its semantic identity is not assigned here.
3. `004e7ce0` computes signed `(remainingCount * 1000) / unsignedByte(005646ff)`. The instructions at `004e7d9a..004e7db0` construct the factor 1000; `004e7db2` loads the byte divisor from offset `+0x0b` of the selected 96-byte voice record, using the index returned by `004ffc9c`, and `004e7dbd` performs signed `IDIV`. The divisor's field meaning and units remain unresolved. The factor 1000 does not by itself make the result milliseconds, and the numerator is a chunk count rather than a sample count.
4. `004e7df4` compares the signed estimate directly against signed DWORD threshold `0056476c`: `CMP` at `004e7e05` followed by signed `JL` at `004e7e0b` takes the below-threshold path. A zero threshold returns immediately at `004e7df5..004e7dff`. Therefore the threshold and estimate share a scalar comparison domain, but the domain has no defensible physical unit from the inspected producers.

Other nearby quantities have clearer but different units: `0056469c` accumulates payload bytes; `00564678` counts end-tag invocations; and byte `005646ff` is used as a divisor/scale and also in queue-trimming arithmetic. None converts the estimate into a verified sample count or playback duration.

## Top-up callback, threshold writer, and deadline

`004e89f8` publishes callback address `004e7e98` through `004ff660`, which stores the pointer in global slot `009f6a50`. Normal `WaitForAudioStreamTopUp` path `004ff7c0` calls `004ff670`, forwarding its incoming EAX unchanged to that callback. The direct `004ff7c0` callers are `004e0ec0` and `004f22e0`; the local code does not establish a common unit for their EAX values. It would be unjustified to label this input as bytes, chunks, samples, or milliseconds.

At `004e7e98`, only a positive incoming EAX reaches the threshold/deadline stores: `TEST`/signed `JLE` at `004e7ea6..004e7ea8` sends nonpositive input to a diagnostic-and-return path. For positive input, if optional callback pointer `0056480c` is nonnull, it receives the incoming value in EAX; its EAX return is added to that value at `004e7ebb`, and the result is stored in `0056476c` at `004e7edb`. The callback stores deadline `00564770` at `004e7ed5` after computing clock plus 60 times the requested timer rate (`004e7ec4..004e7ed3`). It runs `004e7df4` immediately only when service-state gate `004f9070` returns zero; otherwise a later ordinary stream-state callback invokes the threshold checker.

`005643d8` is written by the multimedia timer service, not by the stream packet reader. Its successful initialization stores the requested pulse-rate parameter. The startup site passes `128`; the timer worker increments `0079c1a4` once per serviced active worker iteration. `004e7e98` computes the deadline as `currentClock + 60*rate` (four shifts/one subtraction implement `64*rate - 4*rate`). Under one serviced clock increment per requested pulse, that is nominally 60 seconds. The clock producer's actual delivery rate and interruption behavior are not established, so this is a nominal bound, not a wall-clock guarantee. A signed `clock > deadline` path in `004e7df4` diagnoses timeout and then invokes the same clear/notify helper if the diagnostic handler returns.

## What clear/notify does

`004e7df4` invokes `004e7dd0` when the estimate reaches the threshold. The timeout test at `004e7e1c..004e7e22` compares the clock with the deadline and loops while signed `clock <= deadline`; it diagnoses and notifies once signed `clock > deadline`, if the diagnostic handler returns. It also notifies on the below-threshold fallback when the stream's `+0xb4`/idle/callback conditions select that branch. `004e7dd0`:

- clears DWORD `0056476c`;
- calls `004ff780`, which sets shared latch `0056785c=1` and signals event handle `00567864` if that handle is present;
- if `0056480c` is nonnull, zeroes EAX at `004e7de9` and calls it indirectly at `004e7deb`. The hook's return value is ignored by this caller.

The consumer/wait code at `004ff670` clears the shared latch before invoking the registered `009f6a50` callback. `004ff7c0` then uses the event or callback-pumping path according to its thread/handle conditions. The helper is therefore reporting that the top-up callback/check path has been serviced or its threshold/timeout condition has cleared. It does not report audio output completion.

## Optional Pathfinder callback at `0056480c`

The normal Pathfinder stream start at `004e6f0c` initializes base threshold WORD `005645c0` and current threshold WORD `005645c2` from incoming EBX, registers timer callback `004e6d68`, and stores raw callback address `004e6d94` in `0056480c`.

`004e6d94` uses one register argument: its zero case (`TEST` at `004e6d94`) copies base WORD `005645c0` to current threshold WORD `005645c2` (`004e6d98..004e6d9e`) and returns the base (`004e6da4..004e6dac`). Its nonzero case stores `base + EAX` to `005645c2` (`004e6dad..004e6db7`) and also returns the base (`004e6dbe..004e6dc6`). This explains why `004e7e98` adds the callback return to the incoming threshold. In the paired periodic check, `004e6d68` waits until end-tag count `00564678` reaches the configured start count `005645c8`, calls `004e7ce0`, and advances Pathfinder state when the estimate is below `005645c2`. The hook adjusts the Pathfinder threshold; it is not itself an audio-completion callback.

`004e7dd0` also calls this hook with zero after clearing the top-up threshold, restoring the Pathfinder base threshold. In `004e6be0`, the branch where the new state has no transition entries and no pending primary event unregisters `004e6d68` and clears `0056480c`. Pathfinder shutdown `004e7388` also clears the map, state callback and hook. Other indirect or alternate producers were not expanded beyond the direct normal path.

## Evidence and reproduction

Artifact identity: SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

- Count/estimate/check/notify helpers: `004e7c58` `ev_f8a568fa3b9ef69254656ac02bc4f209929e5d63a33171103ee1c5463f46a9c5`; `004e7ce0` `ev_003aa6730c562b1991466ac203d71017822fac875b393d2660675110a6ccdbc0`; `004e7df4` `ev_90faa54a4dc79f687f5b9b908bc7d1836ad308a00063f0051f7755f77cb2b532`; `004e7dd0` `ev_2f7f5aeaa17ad2924d2034a5ded4582b103d525625da0ddbd3d051673687df98`.
- Normal data/end tag producers: `004e8078` `ev_67e1de8dd42ae392df7727c010de354b504dcb6319343a57a55132722536212b`; `004e82ec` `ev_81ffa76950fe6af6be35178fa2ae4e6dbdf2a9adb33f5a97ade28b364fb4a869`; xrefs for `00564698`, `0056469c`, `00564678`, `005646fe`, and `00564684`: `ev_f0dac6a881a83704d8022ea0823e59fab69cccac2cc66b507f5b9dfdf76b3295`, `ev_d40911f06b8f8de79529ac1386217be24993908b9f80275f566eb0eb44c3506d`, `ev_48ec9f046772902b114c8b3e2d52c5acd88e2290f3446c07c8efa0bb321204e9`, `ev_2aca44ad6808bc252996fde9ee8884e2884f25ced830d54a194c22a51cbedbca`, `ev_72f038bb01c351fe33b95787bb3df3741bb8e82ab0a7a7ee2f838b5081c3e3bd`.
- Callback slot and waiter: `004ff660` `ev_14810379f1c6e6da172c2d61ff83600ea6b85a42b8afb247c30bf52ecd947655`; `004ff670` `ev_57323fe0884ef483a23a10593d22a74095d6e89e45054e1d42d53e4019c74470`; `004ff7c0` `ev_335ca70dd65c2653ec5ff2d119f1a50dc58fe75877c3af054490501e19a47658`.
- Pathfinder hook/lifecycle: `004e6f0c` `ev_08cb9a205b97e0a3ffdf45e066ad9c54abf22e641e7af33e4cee06d0d4ea801f`; `004e6be0` `ev_a8efbf94b48d785b009bc4109de59ec51354b2175d02b954321246c3ee08154b`; `004e7388` `ev_f34c6e3c001e1914cd28c107fe225d6458e76b663253d0551f7def13ccd2928b`; xrefs for `0056480c`, `0056476c`, and `00564770`: `ev_63bbde505fa623eec3e0ab39ed2315a374b1ab958bdcbd050d4de80be48786c8`, `ev_f17188f9db564953e91ee29a0a06e345b50acb0ba62be9bfa2882ab114807953`, `ev_5d3ceac3e9180a3a4704fea6667797df2f59cf78bcefe3330751d8956db47f1e`.
- Timer-rate producer: `0048eff0` `ev_18353dc7c8bc8e4407c19a82df7c94f6ad47161f6f573178693853b57473563f`; timer worker's active-iteration clock and the nominal 128-pulse startup request are documented in [the existing clock audit](frontend-dialog-contract.md#dialog-clock-producer).

The callback entries not represented as independent function entries can be inspected in the exact executable with:

```sh
objdump -d -M intel --start-address=0x004e7e98 --stop-address=0x004e7f2d '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004e6d68 --stop-address=0x004e6dc8 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004e6f0c --stop-address=0x004e7016 '<selected nfs3.exe>'
```

No audio/runtime test or executable/configuration write was performed.
