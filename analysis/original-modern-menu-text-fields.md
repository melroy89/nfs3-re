# Menu text fields: numeric language IDs and removed literal fallback

## Verified difference

The paired field writer `00449240` changes only within `00449342..00449371` (exclusive end). This is the **field conversion type 5** branch, distinct from menu widget type 5 (button). The seven-way type table at `00449218` maps conversion type 5 to `004492e9` in both binaries.

The [reproducible audit](scripts/audit_menu_text_field_difference.py) pins both executable hashes, retains complete comparison spans and checks 10 numeric text assignments directly against the official archive. [Evidence manifest](evidence/audits/original-modern-menu-text-field.json). No game, parser or instruction probes were executed.

## Shared prefix and changed fallback

Before the changed block, both binaries append the field value to the menu string arena through `00448f50`, retain its pointer in local `-10h`, and initialize resolved-text local `-0ch` to zero. Values beginning with `kText` or `kMenu` are searched against the symbolic string-name table at `00561c44`, up to `789h` entries. A match calls `004d1850` with the matching index and stores its result in the resolved-text local. Shared call instructions do not imply identical language lookup: [that routine changed separately](original-modern-language-table.md).

| Condition at `00449342` | Supplied original | Official Modern |
|---|---|---|
| Resolved-text local nonzero | Copy resolved pointer to destination | Store resolved pointer to destination |
| Local zero, value starts exactly `str_` | Copy original arena-string pointer to destination | Parse suffix at value+4 via `004f0430`; pass returned ID to `004d1850`; store returned pointer |
| Local zero, any other value | Copy original arena-string pointer to destination | Store zero to destination |

Modern compares the first DWORD with little-endian literal `5f727473h` (`str_`) at `0044934c`. It does not retain arbitrary literal text as the original fallback did. A failed symbolic resolution can also reach this changed branch. For values that do not begin `str_`, the inspected Modern code leaves EAX zero and stores that zero at `[EDI]`. This is a pointer-field result, not an assertion that every consumer safely handles null or necessarily renders blank text.

The direct pointer store replaces the original local four-byte-copy/return block. The other conversion branches and shared final copy/epilogue remain outside the changed-byte set. The Modern function inventory excludes padding `00449365..00449371`; the audit explicitly captures the surrounding envelope so the original return block and Modern NOP padding are accounted for.

## Where field conversion type 5 applies

The selected identical field descriptors include:

- `00557c40`: generic `help`, destination `00604ee0 + 0ch`.
- `00557e00`: button `text`, destination `00604ee0 + 3ch`.

Both rows carry conversion type 5. Other text/unit/label descriptors also use that conversion; the two selected rows are witnesses, not a complete field-schema inventory. The writer uses the selected entry index and descriptor destination offset to target an instance, as documented in the [slider field-storage trace](original-modern-slider-percentage.md).

## Official assets exercise the new notation

The final official package contains **10 `text=str_...` assignments in six menu files**:

| File | Numeric IDs in the observed assignments |
|---|---|
| `advgrph.mnu` | 1935, 1164 |
| `audio.mnu` | 1934 |
| `camera.mnu` | 1938, 1164 |
| `graphics.mnu` | 1937, 1164 |
| `pscamera.mnu` | 1938 |
| `psgraph.mnu` | 1937, 1935 |

Each line number and file hash is retained in the manifest. These are source definitions, not observed runtime reads. IDs 1934..1938 lie in the changed lookup's compatibility/fallback area; reuse the language-table report for exact coverage and fallback policy instead of assuming the external language table always supplies them.

## Retained helpers and remaining boundaries

The paired audit additionally verifies complete byte identity of:

| Range, end exclusive | Role |
|---|---|
| `00442b10..00442b5c` | Bind descriptor callbacks by name |
| `00449990..004499ad` | Invoke descriptor's one-time callback |
| `004493b0..00449504` | Read next key/value |
| `00448f50..00448fc4` | Append to parse arena |
| `004f0430..004f0487` | Signed decimal parser |

The binder scans `18h`-stride static rows from `00555c48`, compares row name with runtime descriptor+14h through `004e9ec0`, then copies five DWORDs from row+4..14h to descriptor+0..10h. The one-time helper checks descriptor WORD+20h; if zero, it calls descriptor+0 when nonnull and then writes WORD+20h=1. It marks the descriptor even when that callback was null. This preserves the distinction between the one-time callback, later descriptor callbacks and per-item callbacks. Identity of these helper bodies is not proof that every registration row or called implementation is unchanged.

For C reconstruction, explicitly choose original literal fallback or Modern numeric-ID semantics. Preserve 32-bit conversion behaviour, pointer ownership in the shared arena and language-resource lifetime. `str_` parsing has no local suffix-validation or ID-range check in the new block; decimal overflow, sign, whitespace, missing digits and language lookup must be qualified separately. The DWORD prefix read has no local string-length/alignment check; a native C translation must account for x86 unaligned reads and short-buffer accessibility rather than introducing an unsafe typed dereference or claiming validation the original lacks.

Next evidence: identify all affected field descriptors, compare relevant symbolic-name tables and registration rows, and test ordinary/malformed values against each original implementation only when runtime probing is in scope. No release-introduction date is assigned merely from this final-pair delta. This is a code-level finding independent of whether a release-note bullet explicitly mentions it.
