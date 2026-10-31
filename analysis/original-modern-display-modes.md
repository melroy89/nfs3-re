# Original versus Modern: display-mode admission and menu list

## Scope and evidence

**Static EXE comparison, not a renderer or UI test.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_display_mode_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-display-modes.json) records identities and half-open instruction spans for the matched enumerator `004bed90` and its menu-list consumer `00448210`. Original and Modern initializer calls bind those two entries directly; this establishes correspondence beyond the shared addresses. Raw assembly remains ignored under `analysis/captures/modern-differences/display-modes/`. No executable/Ghidra edits or game/probe execution.

Both use driver records of stride **0x28**, with width/height/depth DWORDs at `+0/+4/+8`, flags at `+0x10`, and fields tested at `+0x14/+0x18`. Driver descriptor `+0x3c` supplies the enumeration count and `+0x40` its array. Fields not independently established remain offsets, not invented C member meanings.

## 1. Enumerator changes

Original `004bed90..004bee71` calls the driver's about slot `[009ef980]` on each enumeration. Modern uses cached descriptor `[007a3a5c]`, accepted by its [loader](original-modern-renderer-loading.md), and calls separate eligibility helper `004bee60` for each record. Both enumerate indices 1 through the descriptor count inclusive, skipping record zero.

| Gate | Original enumerator | Official Modern eligibility helper |
|---|---|---|
| Record `+0x14` | Signed value at least 2 | Same threshold |
| Geometry | Low-32-bit `3*width == 4*height` (`004bede6..004bedfc`) | Calculated aspect value in 124..178 (`004bee78..004bee8c`) |
| Depth | 15 or 16 (`004bedfe..004bee06`) | 16 or 32 (`004bee8e..004bee99`) |
| Flags `+0x10` | Bit 0 set, bit 1 clear | Same tests |
| Extra size/budget condition | Requires signed truncating half of `[0055fed0]` to be at least low-32-bit `2*width*height` (`004bee15..004bee30`) | No corresponding test in this helper |

For ordinary positive, nonoverflowing dimensions, Modern computes `trunc(100*width/height)` and accepts 124 through 178 inclusive. This is **not an exact rational 5:4..16:9 test**: 124 is below 125, and truncation can admit values above 178%. The vendor's stated aspect range describes intended/common modes; these instructions give the actual approximate admission. At valid normal sizes, 1280×1024, 1920×1080 and 1920×1200 meet the Modern ratio gate; all three fail the original exact-4:3 geometry test. These are arithmetic deductions, not actual advertised or selected driver modes.

The old budget operand's full producer/meaning is not established here; do not silently rename it “available VRAM.” Removing this local gate does not prove the driver or later allocation accepts every larger mode. Neither helper alone establishes a 640×480 minimum; lower-resolution hiding may reside in drivers or other paths and is not verified by this comparison.

Machine caveat: Modern uses low-32-bit IMUL, clears EDX, then signed IDIV by height, without a local zero/overflow guard. The simple mathematical formula above assumes positive normal dimensions and a fitting product. Arbitrary malformed records can depart from that model or fault. Original multiplications/comparisons also use machine-width results. No malformed record was supplied or runtime fault observed.

## 2. Callback interface changes

Original enumeration invokes the callback with EAX=index, EDX=width, EBX=height, ECX=depth and one stack DWORD derived from `record+0x18 >= 2`. Original `00448210` consumes those values and ends with `RET 4`.

Modern invokes callback EAX=index and EDX=record pointer at `004bedbd..004bedc1`, with no pushed per-record argument. Modern `00448210` saves all general-purpose registers with PUSHAD/POPAD and returns with plain RET. Applying the original callback signature to Modern would lose the record pointer and misrepresent stack cleanup. This is an ABI change in an internal callback pair, not a changed Windows API signature.

## 3. Menu list: append becomes sorted insertion/deduplication

Original collector `00448210..004482b8` uses count `00559218`, fixed-stride **0x114** records at `00661220`, and dynamic-label IDs beginning at `0x7a8`. It appends in enumerated order, without a local duplicate search/sort, while signed count is below **20**. Its initializer `004482c0` resets the count and label table before enumerating.

Modern collector `00448210..0044831d` uses count `00a18260`, records at `00a18330`, and IDs beginning at `0x866`. It binary-searches the existing list ordered lexicographically by unsigned DWORD keys, inserts by shifting records with STD/REP MOVSD, clears the new record and restores CLD before normal continuation. It still uses stride 0x114. This is EXE-side sorting; driver-side sorting claims are separate.

Key comparison length depends on `Hide16bitModes` (`007a2798`):

- Zero: compare three DWORDs, **width/height/depth**, so equal dimensions at different depths remain separate keys.
- Nonzero: compare two DWORDs, **width/height**, so the depths compete for one key. At `004482db..004482e1`, an incoming lower depth is rejected; an equal or higher depth updates that record. With the eligibility gate permitting only 16/32, the retained depth for shared dimensions is therefore 32 whenever a 32-bit candidate is enumerated.

This explains the specific “hide 16-bit modes when corresponding 32-bit modes exist” mechanism. It does not globally discard every 16-bit mode or force a 32-bit driver mode when no matching candidate exists. The cached descriptor and list initialization (`00448320`) matter: it enumerates only while count is zero, rather than always rebuilding as original initializer `004482c0` does. Other count-reset paths are not excluded by this chapter.

## 4. Count boundary differs from the headline limit

At `00448263..0044826c`, Modern checks `count > 0x64` with unsigned **JA**, rather than `count >= 0x64`. A new unique candidate is admitted when count equals 100 and increments it to **101**. Duplicate/replacement processing occurs before that admission check. Original checks signed `count >= 20` before appending.

Therefore this callback alone does not prove a strict 100-entry maximum. Driver enumeration caps, available allocation/storage, all reset/admission paths and ordinary reachability must be reconciled before claiming a runtime overwrite or failure. No such failure was tested or observed. Do not silently change JA to JAE during reconstruction merely because the README says 100.

## Catalog mapping and remaining work

- **MP100-001:** EXE eligibility changes support broader aspect/depth modes, with the approximate ratio gate above. Complete projection/HUD correction and actual driver availability are independent.
- **MP150-040:** EXE-side sorted insertion is verified in the matched collector pair.
- **MP150-042:** current `Hide16bitModes` grouping/higher-depth retention is verified; final code fallback zero is in [startup settings](original-modern-startup-policy.md).
- **MP120-008/017/024:** notes about 100 modes can refer to different renderer components. This EXE's changed collector/boundary is documented, but individual DLL capacities and first-release dates are not thereby verified.
- **MP150-030:** a below-640×480 exclusion is not present in this eligibility helper; locating it elsewhere remains pending.

The [mode-selection comparison](original-modern-mode-selection.md) follows the original ID tree and Modern search/application consumers. Next: compare driver mode enumeration itself, all mode-list count resets/storage, old budget-field producer, and original/Modern projection/menu scaling. The [screenshot dimension audit](screenshot-worker-admission-audit.md) already explains why eligibility and selector fallback are not a general buffer-size proof; do not duplicate or overstate that research.
