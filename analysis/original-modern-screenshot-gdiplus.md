# Modern screenshot GDI+ initialization and cleanup

## Evidence and version boundary

The [static audit](evidence/audits/screenshot-gdiplus.json), reproduced by `python3 analysis/scripts/audit_screenshot_gdiplus.py`, captures complete Modern initializer **`004e2eb0..004e2fac` (252 bytes)** and shutdown **`004e2fac..004e2fec` (64 bytes)**, exclusive ends. Both executable hashes and original same-address witnesses are retained, but those original bytes are **not semantic counterparts**. Original TGA behaviour and Modern format selection are compared in the [screenshot overview](original-modern-screenshots.md). No DLL or target code was executed.

## Loading and success/failure

A nonzero module cell`007a2784` returns1 immediately. Otherwise the initializer calls LoadLibraryA for `gdiplus.dll`, stores its handle, and resolves seven required exports through name/function-slot pairs:

- `GdiplusStartup`, `GdiplusShutdown`.
- `GdipGetImageEncodersSize`, `GdipGetImageEncoders`.
- `GdipCreateBitmapFromGdiDib`, `GdipSaveImageToFile`, `GdipDisposeImage`.

Each missing export branches to shared cleanup and return0. GDI+ startup uses file-backed four-DWORD input`{1,0,0,1}` and token cell`007a2788`. Nonzero startup or encoder-enumeration status likewise reaches cleanup/return0. Dynamic stack storage is sized from the returned encoder-buffer byte count; no local upper bound or zero-count admission test precedes the enumeration loop.

The loop advances records by **76 bytes**, compares a UTF-16 pointer at record offset`0x30` against `image/png` and `image/jpeg`, and copies the matching record’s first16 bytes into cached GUID cells`0054d7a0` and`0054d7b0`. Those cells already have **nonzero file-backed GUIDs**, retained verbatim in the manifest. Missing MIME matches do not independently make initialization fail: the previous/initial GUID values remain. Success therefore establishes the local loading/startup/enumeration path, not proof that every selected encoder was discovered or an image can be saved.

After enumeration the initializer registers shutdown`004e2fac` through`004f7c20` and returns1. The registration facility is not revalidated here. The loop relies on coherent DLL-reported count/size/records; its decrement-and-repeat structure is preserved as observed rather than silently rewritten as a validated container iterator.

## Cleanup and shared state

Shutdown uses PUSHAD/POPAD. A nonzero token invokes the resolved `GdiplusShutdown` pointer, then clears the token. A nonzero module invokes FreeLibrary, clears the module, and zeros the seven function-pointer slots through the same name table. It does **not** clear the cached encoder GUID cells. Initialization also restores general registers while returning its status through saved EAX; neither helper saves flags or x87 state.

The module handle is published before resolution/startup finish, whereas the fast path tests only that handle. No local lock or once-only initialization protocol is present. This is a shared-state ordering limitation, not an observed concurrency failure; worker/teardown ordering is documented separately in [screenshot lifecycle](screenshot-lifecycle-contract.md). Failed DLL operations, token ownership and concurrent entry need their own runtime evidence before integration.

The bounded change is a Modern dynamic GDI+ lifecycle supporting its PNG/JPEG path, compared with the separately documented original capture path. Full SDK/driver behaviour, actual encoder success, emitted file validity and complete teardown safety remain unverified. No runtime compatibility or performance conclusion follows from these static checks.
