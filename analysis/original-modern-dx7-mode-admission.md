# Official Modern DX7 driver: minimum resolution admission

## Artifact and boundary

This extends the [executable mode-admission comparison](original-modern-display-modes.md), which did not find a below-640×480 exclusion in the executable’s generic eligibility helper. Here the inspected artifact is **`drivers/dx7/dx7a.dll` from the retained official final package**, not the game executable and not an original-versus-Modern DLL pair. The [manifest](evidence/audits/official-dx7-mode-admission.json) records the archive/member identity, DLL size/hash, ImageBase and exact instruction spans. Reproduce with `python3 analysis/scripts/audit_dx7_mode_admission.py`. The script extracts an ignored reference copy and disassembles it; it never loads or executes the DLL.

## Enumeration callback admits only sufficiently large modes

The caller witness **`60002578..600025ec`** passes callback **`600025ec`** through an object’s vtable slot+20h. The callback reads an incoming record, calls pixel-format classifier `60003960`, and rejects a zero classifier result. It then reads width at+0ch, height at+08h and advertised depth at+54h:

| Test | Rejection |
|---|---|
| `60002613`: unsigned width <640 | Branch to callback return |
| `6000261e`: unsigned height <480 | Branch to callback return |
| `6000262a..60002644`: depth is neither16 nor32 | Branch to callback return |
| `60002644`: matching capability bit absent from `6005aaec` | Branch to callback return |

Depth16 uses capability mask400h; depth32 uses100h. For classifier result3, the output record’s depth is changed to15 at `6000265b`; the pixel classifier’s full meaning is not established here. Thus even this callback should not be summarized as “every output depth is16 or32.”

Accepted records are built with stride28h and passed to insertion helper **`600026d4..6000276d`**. The helper compares the first three DWORDs (width, height, resulting depth), inserts in sorted order or overwrites an equal entry, and caps the reviewed count at99. The callback returns1 even when it rejects a candidate; that value is not a per-mode admission result. Complete graphics-interface ABI and all API return handling remain outside this chapter.

The exported **`_THRASH_about@0` at `60001000`** writes the mode-table pointer `60017250` into descriptor+40h. The reviewed enumeration producer clears the pointed storage and builds records starting at `60017278`, matching the executable’s documented index-zero exclusion and28h stride. Export/configuration and descriptor-refresh calls may have further effects; this is not a proof of every advertised mode over the DLL’s lifetime.

## What this resolves, and what it does not

**MP150-030**, hiding modes below640×480: partial static support is now located in the supplied DX7 driver’s callback. Its unsigned width and height comparisons reject smaller ordinary candidates independently of the executable’s generic gate. This does not establish the rule in every supplied renderer, historical introduction, successful runtime enumeration or a difference from an authenticated original DX7 driver.

**MP120-019**, 640×480 always reported as16-bit for intro movies: still vendor-claimed. The reviewed callback admits dimensions equal to640×480 and has both16-bit and32-bit admission branches; it contains no exact-size branch forcing16-bit. This neither proves nor disproves a later descriptor override, other driver implementation or historical version behavior. No universal negative search is claimed. That separate depth policy requires the remaining descriptor/setup paths or the applicable release DLLs.

Next: inspect the descriptor refresh and actual menu/intro mode request path, then compare other renderer implementations only where they address a specific catalog claim. Keep movie decoder format limitations separate from enumeration policy and observed display behavior. Executable bytes and the saved Ghidra database remain unchanged.

The [menu-startup depth comparison](original-modern-resolution-defaults.md#menu-startup-depth-fixed-original-request-versus-optional-modern-32-bit) now distinguishes original’s fixed16-bit request from Modern’s optional32-bit request. This does not resolve the separate “always reported” depth claim.
