# Original versus Modern: screenshot pixel representation

## Evidence boundary

Static comparison of the supplied original/backup and official Modern v1.6.1, with exact fingerprints in the [screenshot overview](original-modern-screenshots.md). The [manifest](evidence/audits/original-modern-screenshots.json) retains original TGA construction `004eafc0..004eb152`, conversion helper `005040b8..00504132` and Modern worker `004e3078..004e3247`. Reproduce with `python3 analysis/scripts/audit_screenshot_difference.py`. No target instructions, image encoder or runtime capture were executed.

The existing [worker admission audit](screenshot-worker-admission-audit.md) covers allocation/layout arithmetic and ownership. This chapter adds the original conversion comparison and release-note linkage; it does not substitute for image-output validation.

## Original 16-bit path loses one green bit

Original capture save `004eb160` constructs the TGA buffer through `004eafc0`. That routine writes the header, obtains pixel data through `004eaeb0`, and tests source depth byte `00565010` against 16 (`004eb0f9`). Exactly depth 16 calls **`005040b8`**, in-place, with source/destination pointing to the pixel buffer and EBX equal to low32(width × height).

The helper's single-pixel and two-pixel loops implement this bit transformation for each 16-bit word:

`out = ((in & 0xffc0) >> 1) | (in & 0x001f)`

Thus source bits 15..6 move to bits 14..5, bits 4..0 remain, bit 5 is discarded and output bit 15 is zero. For ordinary RGB565 input this is RGB555: red and blue retain five bits, while the low green bit is lost. For example, input `0x0020` maps to `0x0000`; `0x0040` maps to `0x0020`. These are arithmetic deductions from masks/shifts, not executed test vectors.

The conversion is conditional on depth 16. Do not describe every original screenshot format/depth as undergoing it, or claim the helper itself verifies that its input really uses RGB565. The driver capture contract and current depth supply that assumption.

## Modern 16-bit BMP intermediate retains the words

Modern worker sets a 16-bpp BMP pixel field for source depth below 24. For **exactly depth 16**, it additionally:

- Reserves **66** header bytes instead of 54 (`004e30ae..004e30bc`).
- Writes compression field **3** (`004e311d..004e3132`).
- Writes three masks at offsets 54, 58 and 62: **`0000f800`, `000007e0`, `0000001f`** (`004e3143..004e315e`).
- Copies source words through REP MOVSW without the original RGB565-to-RGB555 transformation (`004e3188..004e3197`).

These masks preserve five red, six green and five blue bits in the constructed bitmap. Microsoft documents 16-bpp BI_RGB as RGB555 and BI_BITFIELDS as allowing RGB555/RGB565 with masks; this corroborates interpretation of the observed header and masks. [BITMAPINFOHEADER documentation](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader)

Depth 15 follows the copied-word path but uses compression zero and no extra mask block. This distinction matters; the worker does not mark every two-byte source as RGB565.

This statically supports **MP140-051**'s preservation improvement for 16-bit input. For PNG/JPEG, this bitmap is passed to a separate GDI+ path; decoder acceptance, colour conversion and final image fidelity are not established by header construction alone. JPEG output must not be described as bit-exact based on this copy loop.

## Modern 32-bit source becomes 24-bit bitmap data

For depth 32, each source pixel is read with LODSD. The worker writes its low WORD, shifts right 16, writes the next byte, and omits the high byte (`004e31a0..004e31ad`). In byte order:

`[b0, b1, b2, b3] -> [b0, b1, b2]`

It sets BMP bit count to 24 and compression zero. This proves omission of the fourth byte, without proving that every driver places meaningful alpha there. Calling it “alpha removal” assumes the driver pixel contract; the code itself simply discards that byte.

Rows are visited from source height−1 down to zero, then padded with zeros to a four-byte boundary. For normal positive dimensions with fitting arithmetic, output stride is `(3*width + 3) & ~3`, so the uncompressed BMP extent is `54 + stride*height`. The captured input record still contains four bytes per source pixel; savings apply to the constructed output, not the original capture allocation.

For width divisible by four, the pixel payload falls from 4WH to 3WH bytes, a **25% reduction** against a hypothetical four-byte-per-pixel payload. At small/nonaligned widths, row padding changes that fraction. This is a layout calculation, not a measured compression ratio or a universal comparison with every original file. PNG/JPEG sizes depend on their separate encoders and content.

Original TGA construction rounds source depth upward to a multiple of eight for its header; source depth 32 therefore remains 32 in that header. Combined with Modern's three-byte output loop, this supports the mechanism behind **MP140-052**, while the complete original pixel-copy/provider contract and actual paired files remain untested.

## Limits and follow-up

Verified: original depth-16 mask/shift conversion, Modern masked RGB565 bitmap layout and word copy, Modern four-to-three-byte copy and padding. Unknown: actual driver channel order/content, full source row/pitch guarantees, end-to-end image fidelity and encoded file sizes. Existing allocation and malformed-dimension limitations remain as documented in the linked worker audit. Historical release dates require earlier patch binaries; no screenshot was taken in this phase.

## Historical150 correction initializes the full depth local

**Verified140→150 partial-write/full-read correction; XP-specific failure and live screenshots untested.** The [depth-local audit](evidence/audits/screenshot-depth-local-history.json), reproduced with `python3 analysis/scripts/audit_screenshot_depth_local_history.py`, pins author-hosted1.4.0/1.5.0 and official final EXEs. It retains complete worker bodies and every decoded access to local`EBP-8`, rather than treating same-VA changed bytes as equivalent instructions after repacking.

| Operation |1.4.0 |1.5.0/final |
|---|---|---|
|Read source depth into local |`004e3105` MOV AX,WORD[ESI+8];`004e3109` MOV WORD[EBP-8],AX |`004e3104` MOV EAX,DWORD[ESI+8];`004e3107` MOV DWORD[EBP-8],EAX |
|Calculate source-row stride |`004e3164` MOV EAX,DWORD[EBP-8] |`004e315e` same DWORD load |
|Choose24/32-bit copy branches |Compare low WORD of local |Compare full DWORD |

The worker entry saves registers, establishes EBP and reserves11ch bytes of stack without clearing the local. In140, only the low two bytes of`EBP-8` are written before the DWORD stride read; the upper two bytes retain prior stack contents on the checked ordinary path. Other recorded local stores do not initialize that upper half. This is a machine-level observation: a maintained C function must not silently model it as a defined uninitialized C integer.

For valid ordinary depth D and prior upper WORD H, the old stride input is `(H<<16)|D`, while150's full store supplies D. The following are **derived scalar examples**, not observed stack values or instruction probes:

| Width;depth;prior upper WORD |140 source bytes/row |150 source bytes/row |
|---|---:|---:|
|640;16;0 |1,280 |1,280 |
|640;16;1 |5,244,160 |1,280 |
|640;24;1 |5,244,800 |1,920 |
|640;32;1 |5,245,440 |2,560 |

The formula adds7 modulo2^32, shifts right3 and multiplies by width using low32 bits. The row loop derives source addresses from that stride and the decreasing row index, then adds capture-record base+12. In140 its subsequent low-WORD depth tests can still choose the normal16/24/32 copy branch while the source-row offset is wrong. Destination allocation earlier uses the source record's actual DWORD depth separately, so the later bad stride is not sanitized merely because allocation succeeded. Whether an incorrect address is mapped, faulting or readable remains runtime-dependent; no crash was reproduced.

The150/full-final depth and row-loop core`004e3104..004e31b8` is byte-identical. Complete workers have separate sizes/hashes (140472 bytes;150/final464 bytes), with other literal/call relocation differences outside this focused explanation. The widening also makes header-depth and local copy-condition tests consistent with the DWORD record field; it is not a proof of valid arbitrary depth inputs or complete pixel-format equivalence.

**MP150-034 advances to partial static support:** at the advertised140→150 boundary, the screenshot worker eliminates an uninitialized-upper-half dependency capable of corrupting source stride. This is consistent with a stack-content-dependent screenshot crash fix, but neither exclusive XP causation nor actual XP behaviour is established. Existing extent, allocation, driver-channel, GDI+, thread lifetime and concurrency limitations remain. Reconstruction should explicitly choose the Modern full-width contract, and document that choice as preserving a verified correction rather than quietly “fixing” the older patched machine behaviour. No screenshot, game, thread/API, instruction probe, compiler or Ghidra write was performed.
