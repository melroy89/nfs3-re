# Screenshot worker admission and ownership audit

## Scope and target

This is a static audit of the installed `nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
It follows the screenshot request latch, current display-mode fields, capture
allocation, `CreateThread` handoff, worker reads/writes/frees, shared output
format/GDI+ state, and the worker handle/teardown paths. It does not execute the
game or prove that simultaneous workers or teardown overlap occur.

## Request and mode producer chain

The processing routine at `004c4480` has exactly three decoded direct callers:
frontend input `00451969`, loading progress `00495274`, and the race loop
`004c5481` (`ev_d34fc5d12efc218cbbf0640c616cb3c2940cd5402c3aee039879407fe99c24fd`).
It returns immediately unless request latch `007a2778` is nonzero. Otherwise it
normalizes format (`004c44b8`), prepares the screenshot directory/counter
(`004c44e8`), calls the capture launcher (`004c452c`), and resets the latch at
`004c44ac`. The latch's other direct references are its two set-to-one producer
stores at `004cdc80` and `004cdcb0`; `004cdc5c` is a separately documented
zeroing path. Its xref evidence is `ev_403a11e9a26d9cf4d32dedb97595394a6f2425be74fe80243615339dfbcecff8`.
There is no compare-and-swap, lock, outstanding-worker count, or completion
poll in this request path. The latch means “request pending,” not “worker busy.”

The capture launcher reads live width, height, and depth from
`007cdae0`, `007cdae4`, and `007cdae8`. These fields are populated by
`004beeb0`, which addresses a record at
`[007a3a5c+0x40] + max(index,1)*0x28`. When the requested index differs from
the current index, it checks the index against the mode count at
`[007a3a5c+0x3c]`, requests the driver mode, and copies ten dwords from the
record to `007cdae0` after driver success (`004bef62..004bef6c`). Its
same-current-index branch skips the range check and driver call and reuses the
current record. Startup
initialization at `00517620` first selects a candidate through `004bedcc`,
passes it to the display driver, stores the successful index at `0055fec0`,
then calls `004beeb0` to publish the selected mode. Other direct callers of
`004beeb0` are `0044b1a0`, `004a33f0`, and `004a35d0`.

The candidate filter `004bee60` requires mode flag bit 0 set and bit 1 clear,
`record+0x14 > 1`, aspect ratio `width*100/height` in inclusive range
124..178, and depth 16 or 32. It does not impose a general width, height, or
area ceiling. The division has no explicit zero-height guard. The driver mode
catalog and successful driver response are therefore the upstream bounds; the
binary path reviewed here supplies no independent maximum allocation size.
The xrefs to all three live fields are bounded to the mode copy and capture
reads/job writes: `007cdae0` `ev_63bb2588f50e60b11212cc315e427068362a237f2a604ccb33b15503c8e8583f`,
`007cdae4` `ev_30fa096afe797b46f6e06152c1dd906053c49f0de72db70c8410cec3b5c4f950`,
and `007cdae8` `ev_a3ddaf472af3f9e13f9ba746fb86adb4c750ba6c6b6797f3108da683055efc5f`.

## Per-request capture record and ownership transfer

`004c452c` accepts depths 15, 16, 24, and 32, then computes `b=(depth+7)>>3`
and requests a heap block of `low32(b*W*H + 12)` bytes through
`004f1efc`/`HeapAlloc`. The first twelve bytes hold W, H, and depth; capture
pixels start at `job+12`. There is no zero/negative-dimension, multiplication
overflow, or maximum-area check in this function. The driver capture call
`[009ef920]` receives W, H, and `job+12`; only after it succeeds does the
launcher call `CreateThread` with entry `004e3078` and `lpParameter=job`.

If allocation or capture fails, or `CreateThread` returns null, the launcher
frees the job block. If thread creation succeeds, it closes the returned
thread handle immediately through `004dfc00`/`CloseHandle` and returns success
without freeing the job. The successful worker is the owner and frees that
block on its exit path. The thread ID output goes to a stack local and is not
retained. `004dfc00` only calls `CloseHandle`; closing the handle neither waits
for nor terminates the worker. Caller/launcher evidence is
`ev_5646cb068d2e265f8b6d523df9b6e2428848ad2fb2c5a90d49a9323197c2ad76`,
allocator `ev_52c31e63772ddf69b0e5495f1a84f7f4a57834610f3e3bdfb89e8f2ad0ed911f`,
free wrapper `ev_8ada03412b5bf4c617d816352a9caa3434945a0af552b3734e0324a76b4dcb75`,
handle-close wrapper `ev_36d294b12a94b42b60f2511d008b37a2f027a2c507eb024b7aadaaed5c25ab15`,
and the sole xref to worker entry `004e3078` from `004c459a`
(`ev_c22f3fe48a248d8d04c194ba7c5aaabcf79c6b909c8d12d97bfcacf6372756dd`).

Ghidra did not assign `004e3078` a procedure, so worker arithmetic is grounded
in the original executable byte range read as `ev_bd6a9e849582f81da5a373f076ad8abc442b063a28790bd2000c87b9e009cb74`
and independently disassembled with `objdump -d -Mintel` over
`004e3078..004e3245`. The worker reads W/H/depth from the job pointer, with
pixel input at `job+12`. It sets output bytes-per-pixel `c=min(b,3)`, computes
`stride=low32((c*W+3)&~3)`, and requests
`low32(stride*H + header)` where header is 54 bytes, or 66 for depth 16.
It checks the output allocation for null, writes a BMP header, copies rows
bottom-up (2-byte pixels for 15/16-bit input, 3 bytes for 24-bit input, and
three of each four source bytes for 32-bit input), and zeroes output padding.
It then calls the selected writer, frees the output buffer if allocated, frees
the capture job, and returns zero. The arithmetic is 32-bit and has no explicit
overflow or dimension validation. The output header/data extent is only
consistent when dimensions are positive and products fit without wrap, and
the supplied capture buffer contains all `b*W*H` bytes.

On the successful thread path, later display-mode changes update the live
`007cdae0..+8` configuration but do not overwrite the worker's per-request
heap record. That part of the worker input is a snapshot. There is no evidence
that the job block is reused or freed by a subsequent request; within the
decoded worker body, it is freed by that worker after output processing.

## Shared format and encoder lifetime

Format is not part of the per-request record. `007a2780` is normalized to
`bmp`, `png`, or `jpg` before launch. Direct binary references are the INI
load at `004b56a7`, normalization at `004c44b8/004c44e2`, and worker loads at
`004e31d0` and `004e31ef` (`ev_6816fdcde0d6bcd4771c38355af38f3e4a18887e20a543e84d31f38d267bf7d3`).
The worker first passes the address of this shared extension to filename
formatting, then reloads it to choose BMP versus PNG/JPEG. Thus the filename
format and encoder branch are not an immutable per-job pair; an intervening
global format change could make them disagree. Static evidence does not show
that such a concurrent change occurs.

PNG/JPEG also uses shared GDI+ state: module `007a2784`, startup token
`007a2788`, export pointers beginning `0054d750`, PNG/JPEG encoder CLSID
records at `0054d7a0/0054d7b0`, and JPEG parameters at `0054d7c0`. Init
`004e2eb0` publishes the module handle before resolving exports and starting
GDI+, then registers shutdown `004e2fac` with `004f7c20` on success. A cached
non-null module handle makes later init calls return success immediately. The
registration helper has capacity 32 and returns failure when full; init does
not inspect that return. Shutdown calls GDI+ shutdown if the token is nonzero,
then `FreeLibrary`, clears the module handle, and zeros the export slots.
Evidence: init `ev_0952d34d1a9c7b19da370d35823cf5272d09b13928a814309b9f00ea79594405`,
shutdown `ev_39a0b5238f0596ae70151972ebb0aec06aab439e11f9ae46261968a444763a26`,
and registration `ev_d57410ad47494920fab46878c96b4bf7df44a27760aabe2de277851b4915a99f`.
No worker count, retained thread handle, completion callback, or join appears in
the reviewed screenshot routines or shutdown routine. Existing
[screenshot lifecycle notes](screenshot-lifecycle-contract.md#runtime-finalizer-ordering)
place the registered callback in ordinary process finalization at priority 96;
this establishes when cleanup is eligible, not that a worker is still active.

## Bounded finding and remaining evidence gap

The per-request width/height/depth and pixel buffer are snapshotted into a
distinct allocation before thread creation, with clear failure cleanup and
worker-side release after success. The output format, encoder identifiers,
GDI+ function pointers, and GDI+ token/module remain shared globals. The
launcher closes rather than retains the worker handle, resets the request
latch after successful launch, and exposes no busy/wait/join gate. Therefore
the static code permits subsequent launches and does not itself prevent shared
format mutation or GDI+ teardown while a worker is active. It does not prove
that requests overlap, that format changes race, or that shutdown runs during
worker use. Resolving those temporal claims requires a controlled runtime trace
of CreateThread start/return, worker reads/writes, format writes, GDI+ cleanup,
and worker exit, or external proof of serialized process shutdown.

No executable or persistent Ghidra project changes were made. The active REA
session was ephemeral and is closed.

Parent live launcher review confirms failure cleanup and successful worker ownership. Preparation rereads live mode globals for allocation, job header and driver capture; the per-job snapshot is not proof those reads are atomic or consistent if another actor changes the mode mid-preparation. Stable mode state during preparation is an additional precondition. No such concurrent mode change is observed.
