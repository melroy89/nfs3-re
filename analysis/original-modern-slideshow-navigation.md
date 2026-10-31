# Car slideshow: arrow bindings and deferred refresh

## Counterparts and evidence

The `slides` registration row at `00555f90` retains init `00453c00` and periodic callback `00453ef0`; its original intermediate callback was a return-zero stub removed in Modern, as recorded in the [registration audit](original-modern-menu-callback-table.md). The retained init prefixes identify the actual per-button counterparts:

| Control | Original callback | Modern callback |
|---|---|---|
| `nextslide` (`005397a4`) | `00453840..00453859` | `00453850..00453863` |
| `prevslide` (`005397b0`) | `00453860..0045393e` | `00453864..0045393d` |

The [audit](scripts/audit_slideshow_navigation_difference.py) pins both executable hashes, captures complete navigation/periodic bodies plus explicitly partial init/refresh witnesses, and verifies the official asset directly against the retained patch archive. [Manifest](evidence/audits/original-modern-slideshow-navigation.json). Range ends are exclusive. No target execution.

## Navigation results change from action9 to a shared update counter

Original Next increments slide index `00559588`, preserves EDX/EBP and returns **EAX=9**. Modern Next increments the same index, also increments **`0066477c`**, and returns **EAX=0**. The x86 increments wrap at machine width; no callback-local upper-bound check or wrap-to-first rule is present in Next.

Original and Modern Previous share **byte-identical core `0045386d..00453931`**. For signed index greater than1, it decrements the index. Otherwise it stores20, then repeatedly decrements and probes a constructed candidate path, starting with index19. The path depends on selected car/resource helpers and the source directories. The loop repeats while `004e0e60` returns zero; this captured core has no explicit lower-index/iteration bound. Successful probe and asset availability must not be assumed for malformed or incomplete installations.

Their wrappers and exits differ. Original Previous returns9; Modern increments `0066477c`, restores its saved register frame and returns0. Thus the change is not merely adding arrow names to unchanged callback return contracts. The conditional outer-loop action9 path is traced in the follow-up below; successful redraw is not implied by its completion.

## Modern binding wrapper and periodic refresh

Original `00453c00` interleaves resource/context setup and the two button callback assignments before continuing into rendering. Modern introduces a short binding wrapper `00453c00..00453c32`: it preserves general registers, installs the new callback addresses when the named entries exist, restores registers and jumps to **`00453c33`**. That destination begins the refresh routine. These are explicit partial init/refresh captures, not a claim that the complete large rendering body is verified equivalent.

Modern periodic callback `00453ef0..00453f58` retains the existing timing/entry-flag work and adds at `00453f41`:

- If `0066477c` is zero, return through the existing zero-result path.
- Otherwise pass the menu context to `00453c33`.

The captured Modern refresh exit `00453ed7..00453eee` stores timestamp `0079c1a4` to `00559594`, clears `0066477c`, restores its stack/register frame and returns zero. The original exit lacks the counter-clear store. The inspected Modern refresh prefix also sends a null car/resource lookup to this exit, so clearing the counter must not be treated as proof that an image was successfully loaded or displayed.

These instructions establish a local deferred-update protocol: navigation marks shared state, the periodic callback notices it, and the refresh exit clears it. Counter initialization, every alias/writer, all intervening menu events and complete refresh failure paths remain unenumerated. Do not replace the counter with a boolean or assume reentrancy/thread safety without checking those uses.

## Connecting Left/Right to the slide callbacks

The official `slides.mnu` contains:

- `codelink=keyright nextslide` at line39.
- `codelink=keyleft prevslide` at line51.

The [named-action dispatch audit](original-modern-menu-input.md) and [button-handler integration](original-modern-credits-panorama.md#conditional-leftright-to-panorama-callback-chain) establish the common conditional route: after current-entry input declines an arrow, find an enabled named button, select it, invoke synthetic Enter through item+30h and then the initialized item+64h callback. The binding prefix in this report supplies those slideshow callbacks.

Together with the ordinary Credits and panorama reports, this gives conditional static routes for all three contexts named by **MP140-022**. Actual key delivery, current-entry consumption, runtime asset selection, file availability, visual output and historical introduction in v1.4.0 remain untested. The catalog remains partial for those reasons; the former missing slideshow-binding link is now resolved.

## Reconstruction follow-up

Keep version-specific callback returns and the Modern counter/periodic-refresh protocol explicit. For later comparison, include Next/Previous at indices1/2/19, missing trailing slides, no matching candidate asset, multiple inputs before periodic refresh, zero/nonzero counter and null resource state. Complete refresh/resource ownership, pending-menu overrides and shared global initialization must be mapped before integration or equivalence claims.

Executables, saved Ghidra state, raw exports and maintained C remain unchanged. This report documents a control-flow difference without running instruction probes or a game session.

## Original action9: descriptor transition and reinitialization path

The expanded audit retains the action table and five byte-identical original/Modern code ranges covering dispatch, transition/cleanup and reinitialization. Reused generic engine code is not itself new Modern functionality; the slideshow callback return changes whether this path is taken.

- The action switch at `0044b6c8..0044b6de` subtracts4 and indexes `0044b208`. Action9 selects table slot `0044b21c`, target **`0044b7a7`**, in both images.
- That arm passes the active descriptor and action9 to `0044aa30`. It then conditionally handles pending descriptor name `00559224`; if it resolves, active descriptor `00559230` changes and the pending pointer is cleared. It finally sets the loop-local initialization flag to1.
- At `0044b6f6`, action9 differs from continuation cases1/3, so the ordinary path returns to `0044b30b`. With the initialization flag set, that path calls **`0044ab40`** for the active descriptor. Pending-name overrides can therefore change which descriptor is initialized; “same-menu restart” is conditional on no such override.

Complete transition helper **`0044aa30..0044aac9`** first invokes descriptor+0ch if nonnull. For the original slideshow this is the verified return-zero stub `00453f50`, which preserves the EDX action value. In the nonzero `00559234` branch it then goes directly to cleanup. Otherwise, EDX=9 skips the ordinary sound/fade block, clears `00559c68` and proceeds to cleanup. This branch interpretation depends on the action surviving the descriptor callback; it is established for this original stub, not every arbitrary callback.

Cleanup **`0044a9e0..0044aa21`** scans the descriptor's entries from its signed start index to the type-zero sentinel, invoking each non-null entry callback at **+28h**. It is a callback traversal; actual allocations/resources released depend on the templates and callees. No claim that all memory is freed or every callback succeeds follows from the traversal.

Complete initializer **`0044ab40..0044ac7c`** performs generic setup, resets selection fields, calls entry-flag setup through `0044aad0`, and then invokes non-null descriptor callback **+8** at `0044ac5a`. The `slides` registration maps +8 to `00453c00` in both binaries. It subsequently calls `0044a960`, `0044a860` and `004f0650` before returning the saved initializer result. The full semantic effects of these generic callees are not revalidated here.

Thus the original slideshow's action9 normally requests a **descriptor transition/entry-cleanup/reinitialization sequence**, reaching its binding/render initialization again. Modern Next/Previous returning0 bypasses this particular action-driven sequence and instead lets periodic callback+10h inspect `0066477c` and call the separate refresh entry. Other events can still transition or reinitialize the Modern menu; this is not proof that it never rebuilds.

For C reconstruction, merging the versions under one “refresh slide” return code would hide differences in entry cleanup, selection reset, callback ordering and pending-menu overrides. Compare these effects explicitly before deciding which protocol to preserve. No runtime menu or instruction tests were added.

## Complete refresh envelope and persistent resource slots

The audit now extends the former partial capture to **`00453c00..00453eee`** in both binaries. This envelope contains original initialization/rendering versus Modern’s binding wrapper plus separate refresh entry; original post-return alignment is included explicitly. Every changed byte lies within the binding/prologue rewrite`00453c00..00453c47`, three resource call-site regions`00453e64..00453e6b`, `00453e91..00453e98`, `00453ebc..00453ec6`, or final exit`00453ee3..00453eee`. This closes byte-difference coverage of that envelope, not all external resource/render semantics.

At three sites original directly calls`004d6390` with EDX0; Modern calls new wrapper **`00451810..0045182d`**, setting DL to1,2,0 respectively. The wrapper zero-extends **DL** into ECX, reads WORD`00664770 + 2*index` into EDX, calls the same creator`004d6390`, writes AX back to that WORD slot, then restores incoming EDX/ECX and returns EAX. No wrapper-local index bound or failure check is present. The inspected slideshow callers use indices0..2. Original code at this new wrapper address is the unrelated screenshot checker, so it must not be paired as the old resource implementation.

Inside the creator, its saved EDX argument is tested at`004d6491`: nonzero selects that value into the result/index local and branches to`004d6560`; zero takes the existing record-allocation path beginning`004d649d`. This supports a prior-index/reuse mechanism at these call sites. Complete creator validation, upload/free behaviour and failure-result contracts remain unverified; storing AX without a local check does not establish successful resource reuse or a leak fix.

New helper **`00451830..0045183d`** clears **12 bytes** at`00664770` through three DWORD STOS instructions, i.e. six WORD slots. Its call at **`004daff2`** is retained in the audit as an initialization/reset witness. The wrapper’s index is an unsigned byte and is not inherently limited to those six slots; other users and global aliases must be enumerated before describing this as a universally bounded six-entry API. Active reset ordering, repeated entry and cross-menu reuse remain follow-up work.

This resource-slot change complements the already established deferred-refresh counter; it is not merely a callback-return rewrite. No allocation counts, lifetime safety, reduced memory usage or rendered refresh success were measured. Existing arrow-to-callback linkage above remains valid and should be reused rather than reinvestigated as missing. No creator, reset helper or game code was executed.

## Retained creator skips allocation for a prior index

Complete creator **`004d6390..004d66ea` (858 bytes)** is now retained and asserted byte-identical. The new wrapper therefore changes the argument supplied to retained creator logic, rather than establishing a rewritten creator algorithm.

After selecting the prior record, the creator tests its saved prior-index argument at`004d65ef`. Nonzero branches directly to`004d663a`; zero reaches the call through slot **`009ef968`** at`004d6601` and stores the returned texture handle in a12-byte record rooted at`008b5090`. The existing [THRASH export map](evidence/audits/original-modern-thrash-loader.json) identifies that slot as **`_THRASH_talloc@20`**. Both paths then reach call **`004d6654`** through slot **`009ef964`**, mapped to **`_THRASH_tupdate@12`**. Thus prior-index reuse locally skips allocation while retaining update. Neither call’s success is established by this static path inspection.

The final path frees its temporary buffers through`004e1890` and returns the selected index; detailed ownership of texture records, dimensions, allocation failure and driver handles remains unresolved. Equal body bytes do not establish equal renderer DLL behaviour. A cached nonzero index is a precondition supplied by the wrapper, not a fresh validation of that record’s lifetime or compatibility with changed image dimensions.

An every-byte E8/rel32 target scan of the official executable’s first code section finds exactly the three retained wrapper calls (`00453e66`, `00453e93`, `00453ec1`) and one reset call (`004daff2`). Their instruction locations are corroborated by retained disassembly. This bounds the direct-call inventory: **no additional direct users were found in that section**. Indirect calls, address aliases, other sections and data-driven calls are outside that search, so the helper is not declared globally slideshow-only.

This is evidence for conditional allocation avoidance at the inspected calls, not measured performance, memory savings or proof that six persistent slots are always valid. Later validation should compare first entry versus repeated refresh, resource reset between refreshes, changed image dimensions and failed update, while preserving the original/new calling protocols. No allocation or renderer call was executed.

## Counter boundaries, absolute references and periodic timing

The six-WORD slot-reset interval is **`[00664770,0066477c)`**; the deferred-refresh DWORD is the immediately following **`[0066477c,00664780)`**. The reset helper’s three DWORD stores do not touch the counter. Both lie in Modern’s `.bss` uninitialized storage with raw-data pointer0, not file-backed initial resource values. Loader initialization and subsequent refresh writes remain distinct stages.

The official code-section literal-address scan finds exactly four occurrences of address`0066477c`, each corroborated in retained instructions:

| Instruction | Effect |
|---|---|
| `00453859` | Next increments DWORD counter |
| `00453931` | Previous increments DWORD counter |
| `00453ee3` | Refresh exit stores EAX0 |
| `00453f41` | Periodic callback compares counter with0 |

The manifest records the corresponding operand-byte positions separately from instruction addresses. This is an absolute-reference inventory, not proof that no indexed alias or external callback can access the storage. For example, wrapper slot index6 would algebraically address the counter’s low WORD; inspected direct callers use0..2, and no reachable index6 call is established. Preserve the exact boundaries rather than expanding the six-slot reset to include adjacent state.

Periodic callback`00453ef0` compares current timestamp`0079c1a4` with saved`00559594` plus200 using signed integer arithmetic. Its `JLE` at`00453f0d` targets **the counter test itself** at`00453f41`; the other path toggles two entry flag bits and updates the saved timestamp before reaching the same test. Consequently the200-unit interval gates that flag/timestamp work, **not the pending refresh call**. A pending nonzero counter can request refresh on a periodic invocation even when the interval has not elapsed. Timestamp units, wrap behaviour in actual sessions and callback frequency are not measured here.

Multiple increments before refresh are coalesced by the nonzero test and exit clear; the code does not process one refresh per increment. It remains a wrapping DWORD, not a normalized Boolean: wrap to0 would suppress the test until another write, and a refresh exit clears pending state even on the previously documented null-resource path. These are machine-level implications, not observed failure scenarios. The instructions supply no synchronization or atomic read-and-clear protocol; actual concurrency/reentrancy reachability is unresolved. No periodic tick or game code was run.

## Slot invalidation follows the existing texture reset chain

Complete reset counterparts **original`004daf80..004daff7` (119 bytes)** and **Modern`004daf80..004daffc` (124 bytes)** retain an identical114-byte prefix through`004daff2`. Modern inserts exactly the five-byte CALL to`00451830`, then uses the same five-byte POP/RET epilogue shifted forward. This is an added slot invalidation at an existing reset boundary, not a replacement of the original reset algorithm.

The shared prefix calls`00431bc0`, **`004d5c40`** and`004d93a0`; iterates100 records of20 bytes each writing WORD`ffff` at record offset+12 and zero byte at+16; resets global indices`008b7628`=1 and`008b762c`=0; then calls state setter`00431900` with EAX2/EDX0. These observed field writes do not establish the meaning or complete ownership of every record field.

Complete **`004d5c40..004d5c8b` (75 bytes)** is byte-identical and calls pointer slot **`009ef918`** at`004d5c48`, mapped by the [THRASH export evidence](evidence/audits/original-modern-thrash-loader.json) to **`_THRASH_treset@0`**. Thus the Modern slot clear occurs after that driver reset request and the shared local bookkeeping in the observed normal-return order. No success/rollback check is added by the five-byte insertion; a driver request is not evidence that every resource was actually released.

The previously retained generic initializer`0044ab40` supplies a concrete upstream route: when global`00559234` is0 it reaches CALL`0044ab71` to`004daf80` before its later menu descriptor callback. Its other branch skips this path. Therefore the slots are not merely cleared at an unconnected helper, but neither are they guaranteed to clear on every menu initialization. Other reset callers and renderer modes retain their own admission questions.

For reconstruction, preserve driver/local reset followed by cached-slot invalidation. Clearing only the small slot array would not reproduce the rest of the routine; preserving cached indices across the observed reset could reference reset resource records. Actual stale-handle reachability, driver failure and cross-menu lifetime require later validation. The refresh counter remains outside this slot clear, as established above. No reset or driver call was executed.
