# Original versus Modern: resource-backed frontend page

## Evidence and boundaries

**Static comparison; no rendering or decompression execution.** Paired entry `00441cb0` renders a selected 16-byte page record into an intermediate raster and uploads shape tiles. Its main body `00441cb0..0044236c` differs in exactly **one byte**, at `00441d03`: unsigned dispatch maximum 4 becomes 5. Modern's additional block `00437820..004378b6` is an out-of-line switch arm, not a separate callable function; all its exits jump to shared tail `004421b8`.

Reproduce with `python3 analysis/scripts/audit_frontend_page_difference.py`. The [manifest](evidence/audits/original-modern-frontend-page.json) retains baseline hashes, both main bodies and out-of-line regions, five retained switch targets, new sixth target and selected page-record bytes. Ends are exclusive. The original bytes at the distant region are raw comparison data, not an authenticated counterpart function.

The first five switch targets remain `{00441d11,00441d11,004421e0,004422d0,00442114}`. Modern adds target `00437820` for type 5. Original values above 4 bypass the switch and join the shared tail; original bytes after the five-entry table must not be interpreted as an admitted sixth case.

## Page record 75 changes representation

At `00555c08 = 00555758 + 75*16`:

| Version | Four DWORD fields |
|---|---|
| Supplied original | `{3, 470h, 475h, 0}` |
| Official Modern | `{5, 0053f7d4, 0053f7e0, 0}` |

Original type 3 follows the localized text-range branch. Modern's pointers resolve to **`ABOUT.QFS`** and **`cred`**. The [baseline resource inventory](original-modern-differences.md) records RCDATA `ABOUT.QFS`; the executable use site now connects that named data to a page renderer. Record index 75's actual runtime selection, navigation label and historical introduction remain separate questions.

## New type-5 mechanism

The branch reads selected record+4, calls resource helper `004f1f58`, and skips to the common tail on zero result. It passes the resulting pointer to size/query helper `004f2710`, checks for zero, allocates a temporary block through `004e1620` with EBX=16, and checks allocation. It then passes source and destination to `004f2620`. Existing analysis treats this as the unpack path; this audit does not validate arbitrary compressed payloads or infer a success result where the caller does not check one.

It looks up record+8 (`cred`) in the temporary object through `004ef1e0`, then reads unsigned shape width/height WORDs at +4/+6. There is no local null check between this shape lookup and those reads. Horizontal/vertical positions are formed as **logical right shifts of wrapped `(608-width)` and `(320-height)` by one**, then supplied with the shape to `004ef3f0`. This is not general signed division toward zero for oversized dimensions. The temporary block is released through `004e1890`, and control jumps to the common tail.

The preexisting main path creates a 608×320 intermediate raster; its allocation/setup, ordinary page arms and upload/destruction instructions remain byte-identical apart from the dispatch-bound byte. Shared tail deselects raster, uploads raster+20h using the incoming argument, destroys the raster and returns the saved result, under the previously documented destructor preservation contract. Identical instructions do not prove identical assets, helper implementations or visible output.

**Verified:** one-byte main-body delta, retained five cases, discontiguous new case, text-to-resource page-record change and resource/shape names. **Unresolved:** selected-index admission, resource/unpack/shape lifetime and failure contracts, payload geometry, actual displayed page and release attribution. No claim that every frontend text page was replaced or all resource-present paths render successfully.

Existing [detailed notes](detailed-analysis-notes.md) document the main text/shape branches. Their earlier phrase “Original table” in the discontiguous-body investigation referred to the then-current analyzed Modern program, not the supplied-original executable; the paired five-versus-six-case evidence here resolves that ambiguity.

## Resource lookup and declared allocation size

Modern resource loader `004f1f58..004f1f88` preserves ECX/EDX and accepts the resource name in EAX. It calls the baseline-resolved imports `FindResourceA` (`0053453c`) with literal type **10**, then `LoadResource` (`00534540`) and `LockResource` (`00534570`), using module handle global `009f3d48` for the first two APIs. Find/load failure returns zero; the lock result is returned directly. This is a verified API chain, not a DLL-name/string inference. Successful OS resource access is not exercised.

The manifest now retains the exact selected PE resource `10/ABOUT.QFS/0`: RVA `00645ad0`, **47,372 bytes**, SHA-256, and its first 32 bytes. Prefix `10 fb 0a 8d 28` selects the inspected size-reader branch at `004f26a0`: it accepts the type/signature bytes and extracts a three-byte big-endian length from bytes 2..4 using BSWAP/SHR. Here that value is **`0a8d28h = 691,496`**. Wrapper `004f2710` returns this nonzero result before its alternate format path. The page arm then requests that size through `004e1620` with pool selector 16.

These observations connect resource identity, raw compressed header and requested unpacked allocation. They do not validate every compressed command, verify actual produced byte count, establish the `cred` directory entry or its dimensions, or prove allocation/decompression succeeds. The size helper takes a pointer, not an explicit resource-length argument, and this path does not call SizeofResource before parsing. The actual inspected payload is long enough for these header reads; arbitrary resource safety is not inferred.

Next: inspect the unpack/shape-directory contracts or reuse a qualified offline decoder if one becomes available. No new decoder or target execution was used for this checkpoint, and payload bytes were not modified.

## Retained unpack and shape-directory machinery

The paired audit now verifies byte identity of these complete recorded bodies/ranges:

| Entry / range | Exclusive end | Role |
|---|---|---|
| `004ef1e0` | `004ef26f` | Find shape by four-byte tag |
| `004f2620` | `004f269f` | Unpack wrapper with diagnostic/failure policy |
| `004f2560` | `004f261b` | Format dispatcher |
| `005102a4` | `005102ef` | Decoder body range 1 |
| `005102f0` | `005103ff` | Decoder body range 2 |
| `00510400` | `00510416` | Decoder body range 3 |

The last three are the existing Ghidra function inventory's ranges for `DecodePackedBackreferenceData` at `005102a4`. Gaps are not silently included as function bytes. This is a comparison of retained code, not a proof of valid decoding for every input.

For inspected payload prefix `10 fb`, the format dispatcher accepts byte1=fb and masked byte0=10, then calls `005102a4` at `004f25ee`, passing source EAX and caller-supplied destination EDX. The outer wrapper returns the dispatch result unless its zero-result diagnostic policy is activated. The page arm does not test that return before proceeding to shape lookup. Diagnostic helper `00401010` is not assumed to return or terminate universally.

Shape lookup `004ef1e0` reads a directory count from object+8, compares the requested four-byte tag against eight-byte entries beginning at object+10h, and on a match returns `object + relativeOffset` from the matched entry+4. Missing-tag handling can invoke diagnostics under `0056440c`, then returns zero on a normal returning failure path. The caller reads shape dimensions without a local zero-result guard. Directory count/offset bounds are trusted in this helper; it is not a length-checked container parser.

Thus Modern's new resource-page route reuses retained unpack/shape machinery for an added payload and record representation. This narrows the code delta but does not establish allocation bounds across the decoder, actual expanded bytes, presence of `cred`, visible output or equivalent behavior under every failure policy. Remaining next evidence is offline payload validation and runtime selection/rendering within the stated scope; neither was performed here.

## Page-table scheduling and text consolidation

The paired manifest now records the last two page records, sentinel and full table-span hash. In **both** binaries, the first record whose +4 field is zero is index **76**; indices 0..75 therefore form the observed sentinel-scanned page set. This is a file-backed table observation, not an invariant against runtime mutation.

| Record | Original | Modern |
|---:|---|---|
| 74 | Type 3, localized inclusive range `46ah..46eh` (1130..1134) | Type 3, range `46ah..475h` (1130..1141) |
| 75 | Type 3, localized inclusive range `470h..475h` (1136..1141) | Type 5, `ABOUT.QFS` / `cred` |
| 76 | Zero sentinel | Zero sentinel |

Modern thus extends the preceding text page and repurposes the last page slot; it does **not** simply append a 77th page. The new inclusive record-74 range also includes ID `46fh` (1135), which was between the two original ranges. Its actual text must be inspected before describing the visual effect of that consolidation.

Helper `0044240c` scans the +4 sentinel field from index zero and returns the last nonzero-field index. Reset `00442428` calls it, stores the result into both `00555c34` and selected index `00555c28`, clears state `005f40c0`, stores literal 63 to `00555c30` and returns. With the inspected table unchanged, this computes **75** and selects Modern's resource record. This connects data layout to a selection producer; the reset caller, subsequent state machine and displayed pixels are not exercised here.

Catalog **MP100-047**, “About slide was added to Credits,” is now **partially supported by static evidence**: the named resource, new type-5 rendering arm, repurposed last slot and reset selection are traced. The original/final pair cannot establish introduction in v1.0.0, navigation behavior, successful decoding or the displayed content. Those limits remain explicit rather than treating the catalog entry as wholly verified.

## Installed text range: blank separator and row positions

The [credits text inventory](evidence/inventories/installed-credits-text-range.json) reopens the six installed and twelve case-distinct local backup language files. It records full-file hashes and per-entry offsets, lengths and content hashes for IDs `46ah..475h`, validating NUL termination within each file. ID **46fh (1135) is empty in all 18 files**. This is installed-data evidence, not authenticated original/official patch provenance or actual language selection.

The paired main-body identity already covers the type-3 loop at `004422d0..0044236c`. It starts row coordinate at 20, visits the selected inclusive ID range, submits text/shadow calls, and advances by 20 per entry without a local empty-string skip. Therefore the inspected Modern record 74 describes **12 row positions, 20..240**, with the empty ID1135 at row **120**. The former second-page range IDs1136..1141 now occupies rows **140..240**. Original record74 described five rows20..100, and original record75 described six rows20..120 separately.

These positions follow from retained instructions and the changed record values. They establish a blank separator and regrouping for the inspected labels, not font metrics, clipping acceptance, actual glyph submissions or visible page appearance. Whether every text row contains other formatting/resource dependencies remains outside this length/hash inventory.

Reproduce with `python3 analysis/scripts/inventory_credits_text_range.py --game-dir '<installed game directory>'`. The script does not copy complete credit strings into the report, alter assets or execute target code. This closes the newly included ID1135-content question within the installed scope; About payload decoding and runtime page selection remain pending.

## Ordinary Credits Next/Previous: removed conditional text-page skip

The expanded audit retains complete original/Modern Next bodies `00442370..004423d3`, original Previous `004423e0..00442448`, Modern Previous `004423e0..0044240c`, and both initializer prefixes `00442850..00442908`. These counterpart relationships are established by the retained `next`/`previous` item callback assignments at `004428ea` and `00442901`, not by address proximity alone. The [conditional named-arrow dispatch](original-modern-credits-panorama.md#conditional-leftright-to-panorama-callback-chain) can reach these same ordinary buttons when its admission conditions hold.

Both versions only change page selection when state `005f40c0 == 4`; each callback returns zero even when that gate rejects input. Next increments selected index `00555c28`, wraps to zero when the candidate record's +4 field is zero, and sets state2. Previous decrements nonzero indices or wraps zero to the last sentinel-scanned page, then sets state3.

Original adds a special filter after Next's ordinary increment/wrap: call predicate `00439ce0`, and if it returns zero and the selected record's +4 DWORD equals **`046ah`**, increment the index again. Previous has the corresponding filter after decrementing a **nonzero** index: on the same predicate/field condition, decrement again. Its zero-to-last-page wrap branch does not apply that filter. These instructions concern record+4, not a generic test of a page type or every localized string.

Modern Next replaces the original filter at `004423a0..004423c3` with `JMP 004423c3` plus 33 NOP bytes, asserted by the script. Modern Previous is rewritten without that predicate/skip. Therefore final Modern navigation no longer uses this local conditional exclusion of record74, whose +4 field is `046ah`. This complements the established text consolidation: Modern record74 covers `046ah..0475h`, and record75 is the About resource.

The original predicate body `00439ce0..00439d12` is retained too: it obtains a value using selector `25h` through `00438ad0`, passes the stack object to `00439990`, and returns zero for result `ffffffffh`, one otherwise. Its resource/installation meaning is not assigned here; those callees and actual runtime result remain dependencies. Removing its calls from these navigation callbacks is proven without inventing that meaning.

## Initial selection differs as well

Original initializer `00442850` explicitly writes page index `00555c28=0` and cached page `00555c34=0`, clears state and stores speed63. Modern's corresponding prefix calls reset `00442428`, which scans to and selects last index75 with the inspected table. The following `next`/`previous` callback assignments remain at the same locations. Thus, with unchanged table data and ordinary admitted initialization, the initial selected record changes from page0 to Modern's About record75. This is a selection producer; later mutations, animation state, resource loading and actual displayed pixels remain unobserved.

## More button: retained route, changed authored position

The expanded manifest also hash-checks official `credits.mnu` against its pinned archive and records the selected uppercase backup's More button:

| Field | Local uppercase backup | Official final asset |
|---|---|---|
| `codelink` | `More` | `More` |
| `nextmenu` | `credits1` | `credits1` |
| `text` | `kTextMore` | `kTextMore` |
| `buttontype` | `simple` | `simple` |
| `x`, `y` | 483, 411 | 510, 456 |
| `priority` | 6 | 6 |

This supplies **partial static support for MP140-023**: a concrete repositioning of the existing More control while retaining its authored panorama destination. “Noticeable” is a visual claim requiring rendering/interaction evidence; a coordinate delta alone does not prove readability, visibility or successful activation. The selected backup is not authenticated retail provenance, and introduction in v1.4.0 remains unverified.

For C reconstruction, preserve selected-index/state gating and version-specific skip/reset rules separately from renderer and asset changes. Testing only the resource renderer would miss changed page ordering and initial selection. Future comparisons should cover state4 versus other states, indices0/73/74/75, predicate0/1 in original, missing controls and table/resource failure; this audit executes none of them.

## Presence predicate follow-up: one selector becomes two

The [model-presence audit](evidence/audits/original-modern-model-presence.json), reproduced by `python3 analysis/scripts/audit_model_presence_difference.py`, resolves part of the earlier predicate dependency. Paired direct call **`00427142`** targets original **`00439ce0`**, but Modern **`00439d00`**. Original supplies fixed selector **`0x25`** to key constructor `00438ad0`, searches through `00439990`, and normalizes result−1 to0, anything else to1.

Modern factors that operation into parameterized **`00439cd4..00439cfd`**: incoming EAX becomes the selector; a16-byte local receives the constructed key; search result−1 returns0 and other results return1. Wrapper **`00439d00..00439d19`** first tests selector`0x25`; only on success does it test`0x26`. Its result therefore requires both to be present. The new parameterized predicate is distinct from the two-selector wrapper; they must not be reconstructed as interchangeable interfaces.

Complete key-constructor **`00438ad0..00438aed`** and search **`00439990..004399e4`** bodies are byte-identical in this pair. The constructor clears16 bytes and writes the selector to the first DWORD. The search iterates entries through `00438a80`/`00438aa0`, comparing all16 key bytes with entry+`0x31c`; it returns an index on equality and−1 at list exhaustion. The lower-level list accessors, loaded records and initialization invariants are not established by these local bodies. No human-readable car/resource identities are assigned to selectors`0x25/0x26` from their numbers alone.

This is a confirmed static strengthening of the shared presence policy from one key to two. It complements, but does not reverse, the earlier finding that original navigation callbacks’ predicate filters were removed. The shared caller’s complete branch effect, other Modern consumers, actual installed model presence and historical release attribution remain follow-up work. No resource lookup or game instruction was executed.

## Shared presence consumer: background resource substitution

The audit now retains the complete paired **`004270c0..00427182`**, named `UpdateCarSelectionBackgroundResources` in the saved analysis. All byte differences in that body are confined to the call operand at **`00427143..00427147`**: original calls the one-key predicate, Modern the two-key wrapper. The surrounding resource-name mutation and assignments are retained.

At **`00427126`**, both versions load the low byte of selector **`006fd4d4`**, add ASCII`0`, and store it into character3 of the writable file-backed string **`00537090`**, initially **`opp1.qfs`**. They also compare the complete selector DWORD with3. Only for exactly3 does the predicate run; a nonzero result replaces that character with ASCII`4` at **`0042714b`**. Hence that branch chooses **`opp3.qfs`** when the predicate fails and **`opp4.qfs`** when it succeeds.

The same string pointer is then published into record+`0x40` at **`00427164`** and **`00427179`**, alongside retained WORD layout/resource fields. This establishes resource-name selection, not successful loading or what the images depict. For other selector values, low-byte addition can wrap and need not produce a decimal digit; no global range guarantee is inferred from this caller.

For otherwise equal registry contents containing key`0x25` but missing`0x26`, original therefore selects `opp4.qfs` while Modern selects `opp3.qfs` on the selector3 path. If both keys exist, both select `opp4.qfs`; if key`0x25` is absent, both retain `opp3.qfs`. This conditional consequence follows statically from the paired bodies. Actual resource availability, visual differences and the keys’ identities remain untested/unresolved.
