# Raster session: remove local cleanup registration and shorten inactive exit

## Scope and evidence

[The raster-session audit](scripts/audit_raster_session_difference.py) verifies pinned original/official Modern hashes, complete startup/shutdown envelopes, two removed callback witnesses and a shutdown tail outside the main body. [The manifest](evidence/audits/raster-session-difference.json) retains hashes and disassembly. No renderer, callback or process-exit execution was performed.

| Entry / saved Modern label | Complete envelope, exclusive end | Important boundary |
|---|---|---|
| `00524650` ShutdownRasterBackendSession | `00524650..00524693` (67 bytes) | Original inactive branch also reaches `005247ab..005247b1` |
| `005246a0` InitializeRasterBackendSession | `005246a0..005247ab` (267 bytes) | Modern saved union excludes 44 NOP bytes |

The labels are analysis names. All caller bytes outside the regions described below are identical; transitive renderer/window calls may still differ.

## Startup removes a cleanup-publication block

Both startup bodies retain width/height reads from `00564384/88`, zero-value fallbacks to 640/480, active-byte test at `0056aff0`, window/lock setup and renderer calls. The renderer-init result is tested at `00524740`; a zero result reaches the retained failure path calling `004cdaa0`. Neither local body gains a new renderer success test.

After nonzero renderer result, original's path at `0052474d`:

- Tests byte `0056aff1`; if zero, passes callback address `00524640` to `004f2a78`, then sets that byte to 1.
- Publishes callback address `00524620` to `00564418`.
- Sets active byte `0056aff0` to 1 and returns its zero-extended value.

Modern replaces `0052474d..00524787` with `XOR EAX,EAX; MOV AL,1; MOV [0056aff0],AL`, the register-pop epilogue and RET, followed by 44 NOPs. Thus this caller no longer invokes that registration helper or publishes `00564418`. It still sets active=1 and returns 1 on that path. The complete contract of `004f2a78` and ownership replacing the removed registration are not established here; no global claim that all cleanup registration is gone follows.

The branch at `00524744` checking renderer slot `009ef93c` is unchanged. Its nonzero path still calls `004e7520` with callback `005244e0` and rejoins `0052474d`. That separate setup route must not be conflated with the removed local registration block.

## Removed callbacks have concrete cleanup effects

Original `00524620..00524635` (21 bytes) preserves EDX, calls shutdown `00524650` with EAX=1, clears pointer cell `00564418`, then returns. Modern NOP-fills that span.

Original entry `00524640` loads EAX=1 and falls through padding into `00524650`; it has no standalone RET before shutdown. Modern NOP-fills its 16-byte pre-shutdown span. Recovering it as a conventional independent C function without that fall-through would omit the original cleanup call effect.

These witnesses support a removed cleanup-callback route. Actual callback registration, invocation order at exit, other pointer writers and replacement cleanup responsibility remain unresolved. The removed code is not proof of a leak or safe equivalent teardown.

## Inactive shutdown branch is shortened

Both shutdown bodies test active byte `0056aff0` after saving incoming EAX in EBX. Original's zero branch at `0052465b` goes to a second conditional jump at `005247ab`, which reaches common `XOR EAX,EAX; POP EBX; RET` at `0052468f`. No instruction between those jumps changes flags. Modern directly branches to `0052468f` and NOP-fills both the unused bytes and remote tail. The ordinary inactive path consequently retains its zero result without the extra branch.

When active is nonzero, the shutdown body remains byte-identical: optional callback removal through `004e75e0` under the renderer-slot gate, renderer shutdown call through `009ef97c`, optional `004cdaa0` when saved incoming EAX is nonzero, active-byte clear and zero return. No runtime renderer teardown or window destruction is established by observing those calls statically.

## Reconstruction and follow-up

**Bounded code-difference status: done; confidence: verified static instructions and callback effects.** Keep startup's removed publication distinct from retained secondary setup; preserve original callback fall-through and shared-tail control flow when selecting original behavior. Avoid reconstructing the saved body union alone, which omits the original remote shutdown branch and removed startup bytes.

**Pending:** the registration helper's full contract, all writers/readers of `00564418`, replacement cleanup ownership, runtime init/failure/exit ordering and driver implementations. These affect linking/startup reconstruction and runtime validation. Executable bytes, Ghidra state and maintained C remain unchanged.

## Removed dimension publisher beside the shared shutdown tail

The expanded audit captures original **`005247c0..00524814`**,84 bytes, and asserts all84 bytes are NOPs in Modern. This original helper receives EAX width, EDX height and EBX depth. Zero inputs become640/480/16 respectively; negative or other nonzero inputs are retained by these local tests. It publishes width/height/depth to`00564384/88/8c`, and stores wrapped32-bit differences `width−[0056439c]` and `height−[005643a0]` at`005643a4/a8`. It overwrites working EAX/EDX/EBX; no scalar success result or preservation of those registers should be invented.

When`00564364` is zero it tail-jumps to`00509940`; otherwise it returns directly. The follow-up below identifies that retained row-table initializer; allocator/error and ownership contracts remain unqualified. The [registered original video-mode callback](original-modern-renderer-lifecycle.md) supplies a known caller, but this does not enumerate every caller or establish complete Modern replacement ownership.

In complete outside-body interval **`005247ab..005248f0`**, all117 differences are confined to`005247ab..00524820`: the previously described remote shutdown tail, intervening alignment, this dimension publisher and following alignment. Modern NOP-fills those117 bytes; `00524820..005248f0` matches and retains subsequent raster setup code. The interval is therefore neither one deleted function nor removal of all raster setup. No renderer, tail target or instruction probe was executed.

## Tail target is a retained row-table initializer

Complete **`00509940..005099fd`**,189 bytes, is byte-identical across both EXEs. Original string witnesses identify source`cmn\row.c`, routine`initrow`, allocation label`rowtbl`, and an insufficient-space diagnostic requiring at least204. The audit retains the paired complete bodies rather than inferring behaviour solely from those strings.

It reads signed DWORD count`0056837c`; below204 it calls diagnostic`00401010`, then rejoins setup if that call returns. It therefore does not locally guarantee termination on an undersized count. With buffer pointer`00568380` null, it requests wrapped32-bit size`count<<2` through`004e1620`, using allocation label`rowtbl` and EBX from`005643f4`, then publishes the returned pointer. There is no local post-call null check before the shown header writes. Allocator and diagnostic contracts remain dependencies rather than assumed success/abort guarantees.

On the ordinary admitted valid-buffer path it writes `[buffer]=count-2`, `[buffer+4]=0`, and global`00a0a810=buffer+4*count`, all in32-bit machine arithmetic. EBX/ECX/EDX are explicitly restored; EAX retains the working buffer pointer on this ordinary path. Memory accessibility, valid size/count, aliases and allocator results remain prerequisites. Shared buffer/count/end-pointer cells do not establish reentrancy or synchronization.

Thus original dimension publisher`005247c0` could trigger row-table initialization/reset when`00564364=0`. Modern removes that publisher while retaining this initializer, so the change is at a caller/initialization route rather than deletion of the row-table facility. Other callers and full replacement ordering remain unresolved. No allocation, diagnostic or target instruction was executed.
