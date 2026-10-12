# Screenshot dimensions and asynchronous ownership

Capture004c452c accepts depths15/16/24/32. With b=(depth+7)>>3 it allocates
low32(b*W*H+12), writes the12-byte header and requests the driver capture.
CreateThread is called004c45a3; successful launch immediately closes the
handle004c45b0. Failure frees the capture buffer; successful worker owns it.
Neither allocation success nor launch success validates dimensions/products.

Worker004e3078 uses output bytes/pixel c=min(b,3), row stride align4(c*W),
and allocation low32(stride*H+header), header54 except RGB565 depth16 uses66.
It reads bottom-up source rows, copies2-byte15/16-bit pixels, copies3-byte24-bit
pixels, or drops the fourth32-bit byte, then zeroes row padding. Correct
buffer extents require positive dimensions, sufficient complete capture and
nonwrapping source/output products. Current dimensions are driver records
copied by004beeb0; eligibility004bee60 checks aspect, flags and16/32 format,
without a general dimension/area bound. Other capture depths remain supported
by the lower path. No reachable arithmetic fault is established.

Worker filename counter006fd1e0 is atomic selection state, not outstanding
worker accounting. PNG/JPEG uses global GDI+ exports/encoder identifiers;
worker ignores writer status and frees its buffers before returning0.
ShutdownScreenshotGdiPlus004e2fac stops token, unloads module and clears
exports without a local wait/count check. Successful GDI+ init registers this
shutdown via004f7c20; cleanup dispatch004f7c48 is reverse registration order.

No retained worker handle, join or completion accounting is present in these
inspected bodies. This does not establish overlap at finalization, a reachable
race or use-after-free. Broader process-finalizer ordering, dimension producer
invariants, encoder availability and actual concurrency remain unresolved.
Ghidra capture arithmetic refinement is saved; no runtime screenshot test.

## Runtime finalizer ordering

Registered cleanup004f7c48 appears at priority96 in the runtime finalizer table.
Ordinary exit004dfd04 runs eligible priorities16..255 before downstream
004ff38c runs0..15 and final callback005677a0. That final callback targets
0051e934, which delegates current-thread TLS cleanup0051e8dc before ExitProcess;
it does not provide a broad worker join. Reviewed earlier app shutdown also
contains no screenshot-specific wait. This establishes cleanup's position,
not actual overlap; mutable hooks/delegated exits and backend lifetime remain
separate contracts.

## Encoder initialization admission

ProcessPendingScreenshotRequest004c4480 normalizes format before launching
capture. PNG/JPEG attempts GDI+ init; explicit init failure or unknown format
falls back toBMP. Cached nonNULL module is treated as initialized, though
initialization publishes that module before exports/startup/encoders finish;
concurrent first-use safety is not established.

004e2eb0 obtains encoder count and byte size from GDI+, subtracts byte size
fromESP without a local stack-size guard, then enumerates76-byte records.
Parent full assembly confirms the loop enters unconditionally at004e2f40,
with DECcount/JNZ at004e2f87..8a: positive count and adequate count*76 extent
are required. Zero count does not skip safely; no actual zero-count API result
was observed. Successful positive enumeration does not require findingPNG or
JPEG before returning success. CLSID cells begin with standard preset IDs;
missing matches therefore do not imply zero identifiers. Writer status is
ignored by the worker. Cleanup registration can fail at capacity32 and its
result is ignored by init. Encoder API/data validity, real availability,
stack bounds and concurrency remain unresolved.

## Display initialization does not add screenshot dimension bounds

Named InitializeRasterDisplayModeAndSurfaces00517620, verified in
assembly. It stores selector004bedcc result into current-mode0055fec0
before driver selection009ef958. On explicit driver failure it returns0
without restoring that index in this body. On success it constructs
surface records, copies their dimensions/format into configuration,
then calls ApplyDriverDisplayMode004beeb0 with the stored same index.
The latter's equal-current-index path bypasses differing-index range
validation. Selector fallback1 is not a proof of an eligible record
when no eligible mode exists. No maximum dimension/area bound is
introduced here. Driver-provided extents and caller failure recovery
remain unresolved; no malformed driver result was observed.

This narrows the screenshot producer audit without claiming a reachable
overflow or adding checks to the binary. Ghidra name/comment saved.

## Direct screenshot request admission

The decoded direct caller set of004c4480 is frontend input00451969,
loading progress00495274 and race loop004c5481. Capture004c452c has
only004c4499 as decoded direct caller. Request007a2778 is a Boolean
latch: its direct writes are producer004cdc80/004cdcb0 setting1 and
consumer004c44ac clearing0. A processing invocation attempts at most
one launch and clears the latch on success or failure. It has no
atomic consume, lock or outstanding-worker completion gate.

This closes the bounded request representation/caller-routing question.
It does not prove universal main-thread ownership or exclude indirect
calls/reentry. Sequential requests may launch another encoder without
waiting for the previous worker; actual overlap and initialization
concurrency have not been captured. Producer004cdc50 also has unusual
repeated-zero request behaviour already documented in Ghidra; event
mapping is still partial, so it is not described as ordinary key-up.
Ghidra consumer comment saved.

## Worker output-format ownership

Capture header snapshots width/height/depth only. Worker004e31d0
passes shared extension007a2780 by pointer to filename formatting,
then004e31ef separately loads it to choose BMP or PNG/JPEG. Direct
writes found are INI loading004b56a7 and normalization004c44e2. Thus
a format snapshot is not part of the per-worker capture object.

PNG/JPEG branches select encoder CLSID pointer0054d7a0/7b0 and JPEG
parameters0054d7c0 before writer004e3014. The writer uses supplied
arguments, without another extension load. A mutation between filename
formatting and dispatch could disagree, but actual reload/concurrent
mutation is not proven. This is distinct from shared GDI+ export/token
lifetime, which remains unresolved. No mismatch was observed. Ghidra
worker comment saved; binary unchanged.

## BMP filename admission and write completion

Worker filename probe004f91ec tests GetFileAttributesA success and
non-directory bit, without reserving the path. The later BMP save
004eeae0 uses AcquireResourceWriteHandle004e2ae0 flags0x232.
OpenNativeFileHandle004e3620 translates these to write access
0x40000000, share0, disposition2 and attributes0x08000080. Disposition2
is CREATE_ALWAYS: an existing writable file is truncated, whereas
CREATE_NEW would fail if it already existed. Share0 only protects an
already-open handle lifetime. [Microsoft CreateFileA contract](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea).

This closes the bounded BMP open-policy question: the existence probe
is not an exclusive name reservation. Actual collision/overwrite is
not observed, and concurrent workers normally use distinct atomic
counter values until wrap/reset/external interference. Nonzero short
resource writes are not locally rejected by004eeae0; the screenshot
worker ignores its return and always exits0. PNG/JPEG uses its separate
GDI+ path; this CREATE_ALWAYS proof applies to the BMP branch only.
Ghidra write-helper comment saved; no executable changes.

## Filename counter initialization and wrapping

The only decoded direct counter reset006fd1e0 is004c451b: ordinary
MOV0 when directory setup succeeds and DirectoryContainsNonDotEntry
returns0. That includes empty enumeration and search failure; it does
not derive a maximum existing screenshot number. Cached-ready path
rechecks directory existence and skips reset on success. Worker
LOCK XADD then INC uses low32(old+1), with no wrap guard or lock
shared with reset. Actual concurrent reset/encoding is not captured.

File-backed prefix0053f7f4 is .\screenshots\ (14 characters);
format0053f804 is nfs3_%04d.%s. Width4 is a minimum: signed32 decimal
can occupy11 characters. With a stable normalized3-character extension,
the combined name requires at most35 bytes includingNUL, fitting the
worker260-byte local buffer. This conditional calculation does not
prove arbitrary aliased format/extension mutation safe. Existing-file
probe retries names but does not reserve them. Ghidra initializer
comment updated and saved; binary unchanged.
