# Force-feedback menu: local policy and widget-layout removal

## Complete comparison

The [focused audit](scripts/audit_force_menu_layout.py) checks the complete same-address initializer `00447dd0..004481bd` (1005 bytes including RET) in the supplied original and official Modern executables. The [manifest](evidence/audits/force-menu-layout.json) pins executable/span hashes, exact replacement bytes, strings and disassembly paths. All **376 changed bytes** lie in seven replacement regions; every other function byte is identical.

This explains the changed code in the larger [outside-function interval](original-modern-outside-function-index.md) `00447b3e..00448210`. That maximal uncovered interval is not the initializer's true boundary. No menu, wheel, game or instruction probe was executed.

## Local Credits check delegates to the shared Modern policy

Original `00447e07..00447e24` looks up token `FORCE_CREDITS` through `00442a40`; if found and signed DWORD `006fd3b0 > 1`, it ORs byte bit 0 into widget `+4`. Modern replaces the block with `MOV EAX,ECX; CALL 00437614`, a jump to `00447e24`, and 20 NOPs. The Modern string at the former token address is empty, but the instruction replacement already removes this lookup from the initializer.

The [shared policy comparison](original-modern-race-now.md) maps `00437614` and its broader gates. This is another caller of that verified helper, not evidence that the old local check was copied verbatim or that every Credits entry remains reachable. The initializer still returns early for null incoming EAX; its earlier conditional call to `00451530` with float bits `3f19999a` is unchanged.

## Six per-widget layout branches are skipped

Both versions look up six named widgets into consecutive pointer cells `006611e0..006611f4`, and skip each widget's setup when its pointer is null. For a nonnull pointer, original runs one of two field-initialization paths depending on whether DWORD `00559234` is zero. Modern jumps directly over those paths, retaining the later value/callback setup.

| Widget token | Removed original region, exclusive end | Original WORD `+0x40` | Original WORD source for `+8` and `+0x66` on nonzero-state path |
|---|---|---:|---|
| `FORCE_STICKVOLUME` | `00447e94..00447ece` | 0 | `00559c94` |
| `FORCE_ROADEFFECTS` | `00447f04..00447f41` | 2 | `00559c9c` |
| `FORCE_COLLISION` | `00447f82..00447fbb` | 3 | `00559ca0` |
| `FORCE_ENGINE` | `00447ffc..00448035` | 4 | `00559ca4` |
| `FORCE_BODYROLL` | `00448076..004480af` | 6 | `00559cac` |
| `FORCE_ROADGRIP` | `004480f4..0044812d` | 7 | `00559cb0` |

On the original nonzero-state path, each block writes BYTE `+0x3d=0`, its listed WORD `+0x40`, WORD `+6=320`, WORD `+0x64=64`, and copies the listed WORD to `+8/+0x66`. On the zero-state path it writes BYTE `+0x3d=1` and the same row WORD `+0x40`, without those other writes. Modern replaces each complete block with a two-byte jump and NOP filling, so neither set of local writes occurs here. Exact semantic types of `+0x3d/+0x40/+0x64/+0x66` require their widget consumers; removed stores alone do not prove that visible controls disappeared.

After each jump, retained code converts the corresponding current setting through x87, passes its binary32 value and callback pointer to `0046c950`, and calls `0046cac0`. The six widget lookups, pointer-null checks, settings sources, callback addresses, ordering, later `+0x30` callback assignment, settings snapshot and original return sequence are byte-identical. The stick-volume conversion uses signed DWORD FILD; other shown paths build a zero-high-DWORD QWORD before FILD, retaining their unsigned-value interpretation. No x87 precision change is introduced within these seven replacements.

## Reconstruction and unresolved effects

**Work status: done for complete local byte delta. Confidence: verified static.** Modern relies on other producers or existing values for the omitted fields. A reconstruction should not reintroduce old in-race field writes merely because they appear in the original; nor should it assume those fields are unused. Changes to incidental registers/flags entering retained code remain possible, and retained callees can differ between versions.

Required follow-up for visible behavior is the packaged widget defaults/field consumers and lifecycle state `00559234`, followed by a separately authorized menu comparison if useful. Device detection, force-feedback strength and hardware compatibility are outside this local initializer finding. Existing host/VM wheel observations are not original-versus-Modern validation. Executables, Ghidra, raw exports and maintained C are unchanged.
