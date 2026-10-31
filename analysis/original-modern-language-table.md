# Original versus Modern: language-table marker and fallback strings

## Evidence boundary

Static supplied-original/official-Modern comparison, with exact fingerprints in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_language_table_difference.py`. The [manifest](evidence/audits/original-modern-language-table.json) retains loader/lookup/release instruction spans, six filename entries, the Modern marker and all 27 fallback entries. No language asset was loaded or rendered; no game/instruction probes were executed.

## Loader ownership and marker test

Both use filename pointers at `00563a68` for `text.eng`, `text.ger`, `text.fre`, `text.spa`, `text.ita`, `text.swe`, appended to directory buffer `007a2eb4`, and load the result through `004e0ec0`.

Original `004d1750` checks a signed upper index bound of 6, releases an existing resource before loading, then stores the new pointer at `00563a80`. That local bound alone is not a proof that every index is valid; the six inspected names and caller validation must be reconciled separately. Modern's rewritten routine indexes its table without that same local guard, relying on upstream selection, which is not re-audited here.

Modern loads first, then exchanges the pointer with `00563a80` and releases the prior nonzero pointer. It inspects the new table (`004d1788..004d17a5`):

1. Require first DWORD to be unsigned **greater than `0x1e24` (7716)**.
2. Read the relative string offset stored at byte offset `0x1e24` and compare that string with embedded **`v1.6.0`** through `004ee310`.
3. Store flag **`007a1b94=0`** on a matching marker; otherwise store **1**.

The first DWORD acts as the offset-table coverage boundary in this code. It is not independently established as the whole file length. The check locates string index **1929 (`0x789`)**; it is a language-table compatibility marker, not the running executable's exact patch release version.

No explicit null-new-resource or full payload-bound check precedes these dereferences in the inspected routine. Resource loading, allocation and validated offset/payload contracts remain dependencies. The marker comparison is not a complete parser validation.

## Lookup gains guarded fallback

Original `004d1850` routes signed IDs below `0x7a7` through direct relative-offset lookup, with no local table-coverage check; larger IDs go to dynamic lookup `004d17b0`.

Modern first compares the ID **unsigned** with **`0x7a2` (1954)**. Larger IDs go to dynamic lookup. Otherwise it computes offset `ID*4` and:

- If mismatch flag is nonzero and offset is **at least `0x1e24`**, choose embedded fallback.
- Otherwise require `[table] > offset` unsigned; if true, return `table + [table+offset]`.
- If that coverage test fails, choose embedded fallback too.

The fallback base is **`0053d310`**, with index derived from `offset - 0x1e20` when that difference is signed-positive, or zero otherwise. For ordinary handled IDs this maps **1928..1954** onto **27 entries**; lower IDs that fail coverage select entry zero (empty string). In particular, mismatch-marked tables fall back from ID 1929 onward even if their offsets appear present.

The manifest retains exact entries. Examples include empty entry zero, `v1.6.0`, `km`, `Port`, the legacy/modern port explanation, occupied-port notice, `Menu Sounds`, `Fog` and `Rear View Detail`. These are executable-embedded fallback text, not evidence that the selected external language file contains the matching translation.

The direct lookup path still trusts the stored relative offset and NUL termination. A passing table-coverage check does not prove an in-bounds string payload. Negative IDs are routed differently by the changed signed/unsigned entry condition; arbitrary invalid-ID equivalence is not claimed.

## Dynamic IDs and release helper also change

In `004d17b0`, the display-mode label range changes from original **`0x7a8..0x7bc`** to Modern **`0x866..0x8ca`**, with callback target changing from `00448400` to `00448428`. This links to the expanded [display-mode menu](original-modern-display-modes.md), rather than treating these IDs as external language-table offsets. Other car/resource dynamic-ID routes retain their surrounding structure in the inspected span; full semantic equality is not asserted here.

Original release helper begins at `004d1880`; Modern begins at `004d1890`. Modern exchanges the shared pointer with zero before conditionally freeing it; original frees first, then clears the pointer. This establishes ordering, not thread-safe language reload or successful ownership under every alias.

## Catalog conclusions and limits

**MP160-013**, checking language-file version: the marker test, compatibility flag and lookup fallback are statically supported. This routine does not visibly reject the entire file solely because the marker differs; it changes selected lookup behavior.

**MP153-008**, corrected fallback regression: final fallback logic is documented, but a regression/fix between v1.5.1 and v1.5.3 requires those binaries. Original versus final cannot establish that history.

Pending: upstream language selection, actual localized asset contents, all IDs/consumers, null/malformed input paths and rendered translations. Historical release attribution and complete format compatibility remain separate from this marker mechanism.
