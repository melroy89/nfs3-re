# Historical DX7 clip-record depth-bound change

**Confidence: verified binary value/body difference; API interpretation supported by SDK correspondence. Work status: partial candidate for MP161-003, not a reproduced visual workaround.** The [audit](scripts/audit_dx7_viewport_depth.py) verifies author-hosted1.6.0/1.6.1 archives and DX7 member hashes, export binding and complete150-byte bodies. Its [manifest](evidence/audits/dx7-viewport-depth.json) retains instruction hashes, exact values and captures. No renderer or instruction was executed.

## Exact paired difference

Both DLLs export **`_THRASH_clip@16` at`600013c0`**. Complete envelope`600013c0..60001456` differs at exactly **two bytes, `60001421` and`60001422`**. They lie in the immediate operand of the same instruction at`6000141c`, storing the last DWORD of a local six-DWORD record:

| Version | Binary32 bits | Exact value |
|---|---|---|
|1.6.0 | `3f7fff00` |0.9999847412109375 =1−1/65536 |
|1.6.1 | `3f800000` |1.0 |

The preceding fifth field remains binary32 zero. This changes a stored value, **not x87 precision-control bits**. All other local body bytes match; its external flush/submission helper can still differ, including the separately documented [texel-alignment work](original-modern-renderer-texel-alignment.md#dx7-and-dx8-historical-instruction-traces).

## Record construction and SDK interpretation

Four stack arguments are loaded into saved registers. The body computes third-minus-first and fourth-minus-second in32-bit arithmetic, publishes the rectangle values to globals, zeroes24 local bytes and constructs:

| Record offset | Observed value |
|---|---|
|+00 | First input coordinate |
|+04 | Second input coordinate |
|+08 | Wrapped third input minus first |
|+0c | Wrapped fourth input minus second |
|+10 | Binary32 zero |
|+14 | Changed binary32 value above |

After flush-related calls and restoring saved registers, `60001442..6000144b` passes the local record pointer and object from **`60058d9c`** to **vtable offset`34h`**. Microsoft's SDK defines [D3DVIEWPORT7](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3dtypes.h) as four coordinate/extent DWORDs followed by float `dvMinZ` and `dvMaxZ`; its [IDirect3DDevice7 interface](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d.h) puts SetViewport at slot13, offset34h for32-bit pointers. These match the observed layout and call.

Thus the supported interpretation is **viewport maximum depth changes to1.0**. Complete factory/object provenance, aliases and lifetime of`60058d9c` are not fully qualified here; the SDK correspondence must remain distinct from observed successful API invocation. The body discards the indirect call result and returns1 with RET16, so exported1 does not prove that the device accepted the viewport.

## Relation to the black-polygon claim

MP161-003 advertises a DX7 workaround for a black polygon near the Old Church. A viewport-depth-bound change is a concrete rendering-state candidate distinct from the display-env and mode-list changes. **No evidence here links a specific track polygon, depth value or device response to that symptom.** It must not be presented as the confirmed sole workaround, or as proof that every black polygon was caused by the old bound. Texel-alignment and other driver changes may also matter.

The catalog entry advances vendor-only→partial candidate evidence, with that attribution gap explicit. Next: verify device creation/type and viewport-call admission, then connect the affected draw/depth path or obtain separately scoped before/after rendering evidence if needed. Preserve the old constant and unchecked-result behaviour in any version-faithful reconstruction rather than silently correcting them. No executable/database bytes, viewport state or game assets were changed.
