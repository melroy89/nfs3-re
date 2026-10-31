# Original DDE browser code and Modern address reuse

## Evidence and boundary

The [outside-function inventory](original-modern-outside-function-index.md) lists a 621-byte Modern NOP run at `004901c3..00490430`, containing 619 changed bytes. The [focused static audit](scripts/audit_removed_dde_region.py) identifies the original instructions beneath that run and captures complete surrounding original routines. The [manifest](evidence/audits/removed-dde-region.json) pins both executable hashes, span hashes, import bindings and strings. No game, browser or instruction probe was run.

The run starts **inside** the original six-byte conditional branch at `004901c0`, not at a function entry. Original autoanalysis having no function entry overlapping this run does not make its contents padding: an unrecognized original routine begins earlier at `00490140`, and a callback begins at `004902f0`.

## Original mechanism

| Original extent, end exclusive | Verified mechanism |
|---|---|
| `004900b0..00490106` | Tests instance DWORD `0055e358`; existing nonzero value returns 1. Otherwise passes callback `004902f0`, the instance address and two zero arguments to imported `DdeInitializeA`. Its zero-result path returns 1; failure paths clear the instance and return 0. |
| `00490110..00490133` | If instance `0055e358` is nonzero, calls imported `DdeUninitialize`; then clears the DWORD. |
| `00490140..004902ee` | Saves incoming EAX string pointer. If the instance is zero, exits returning 0. EDX=1 selects string `NETSCAPE`; other values select `IExplore`. It creates service/topic handles, with topic `WWW_OpenURL`, then calls `DdeConnect`. A nonzero connection leads to string construction and `DdeClientTransaction`; all local exit paths return EAX=0 regardless of the transaction result. |
| `004902f0..0049042c` | Callback ends with `RET 32`. It branches on several numeric transaction selectors, calls `DdeQueryStringA` with buffer limit 200 and code-page argument 1004, and compares one queried string against `NETREPORT` through `004ee310`. Exact event meanings and callback outputs need a full contract review. |

The import names are established by decoding original six-byte indirect-jump thunks `00533eb6..00533ee0` and resolving their IAT operands. This is stronger than finding DDE names in unrelated string data.

On the successful connection branch, the URL routine starts its local buffer with a quote, copies the caller-supplied bytes while prefixing each quote with a backslash, appends a quote, then appends the exact string `,,0xFFFFFFFF,0,,,NETREPORT`. The transaction call includes constants `0x20b0` and 1000. These are observed arguments; this report does not assign an independently verified timeout unit or transaction-selector name. The local buffer reserves 0x108 stack bytes in total, including saved locals; no input-length bound is apparent in the retained copy loop. This is an original behavior to preserve or deliberately address in a future port, not a newly tested failure.

## Modern difference and limits

Modern uses this address neighborhood for [overlay helpers](original-modern-view-overlay.md) and the [loading-progress estimator](original-modern-loading-timing.md). The latter ends at `004901c3`; the following 621 bytes through `00490430` are all NOPs. Consequently, same-address calls into `004900b0` in Modern must not be interpreted as calls to the old DDE initializer.

Both executables still statically import the same seven DDE functions: `DdeClientTransaction`, `DdeConnect`, `DdeCreateStringHandleA`, `DdeGetLastError`, `DdeInitializeA`, `DdeQueryStringA`, and `DdeUninitialize`. The audit explicitly verifies this. Import retention is not evidence that Modern still invokes the removed code, nor does this local removal prove that every DDE route is gone.

The separate [ShellExecute wrapper](original-modern-shell-open.md) exists in both executables with its documented owner-argument change. Thus “browser launching removed” would exceed the evidence. Original callers, callback registration reachability from actual startup, and whether this path was already inactive in the supplied original remain unresolved. No connection to multiplayer protocol, race simulation or replay precision is established.

**Bounded status: done; confidence: verified static bodies, NOP replacement, named imports and strings.** Remaining work is original caller/registration tracing and any specifically authorized runtime validation. No executable, Ghidra database, raw reference export or maintained reconstruction source was modified.
