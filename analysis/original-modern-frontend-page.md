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

## Additional Modern consumer: logo-table model filtering

The same audit now retains complete Modern **`004a4374..004a443f`**, a separate consumer of parameterized predicate `00439cd4`. It clears output count **`007a1b90`**, returns early when BYTE `007a3a58` intersects mask6, and constructs a path from **`007a2db4`** plus literal **`logos.qfs`** at `0053cf0c`. Exact effective directory and archive loading success remain outside this local finding.

For each admitted archive entry, it obtains data through `004f24e0`, checks DWORD magic **`0x4c42544c`** (bytes `LTBL`), prepares a resource identifier through `004d6070`, reads a DWORD record count, and walks records containing a model key followed by two DWORD payloads. A zero key bypasses the presence lookup. A nonzero key is passed to **`00439cd4`**; only a nonzero result takes the ordinary output-copy route. Output at **`0066133c`** consists of the prepared identifier and the two payload DWORDs; output count increments and an unsigned comparison against30 stops further ordinary output admission.

A rejected-key route skips both payload DWORDs and executes `LOOP` at **`004a4415`**. When the decremented count remains nonzero it retries another key. **When that count becomes zero, execution falls through to `004a4417`**, the output-copy route, with the source already advanced past the rejected record. There is no intervening jump to the next archive entry. The subsequent `LOOP` at `004a442c` can then decrement zero to`0xffffffff` unless the output-count cap takes its exit. This is an observed conditional control-flow boundary, not a tested malformed-input case or an established actual asset defect. Asset record ordering, trailing storage and normal initialization must be checked before claiming a runtime failure.

The code establishes model-dependent logo admission and a30-entry stop check on the ordinary copy path. It does not identify which key denotes Ford, HSV, Lister or Spectre, prove the archive schema beyond these consumed fields, or establish complete input bounds. The original executable’s legacy logo route and Modern’s rendered animation remain separate comparisons. No release-note item is promoted solely from the archive filename or nearby manufacturer claims.

## Official logo asset: conditional trailing records exist

The audit now extracts `fedata/art/logos.qfs` directly from the hash-pinned official archive and decodes its `10fb` RefPack stream with maintained `decode_logo_refpack.py`. It checks the declared output length, back-reference bounds and final size, retaining packed/decoded SHA-256 hashes. Decoded output is524516 bytes with an `SHPI` header. A bounded magic scan finds two `LTBL` blocks:

| Decoded offset | Record count | Model-key sequence |
|---|---:|---|
| `0x40038` | 6 | `0,0,0,0,0,0` |
| `0x800a0` | 5 | `0,37,38,26,27` decimal (`0,25h,26h,1ah,1bh`) |

All record payload DWORDs are retained in the manifest. This is a decoded-asset scan, not a complete proof of how every archive-entry helper finds metadata; the consumer linkage through `004f24e0` still needs a separate field/layout audit. The two nonzero selectors used by the shared background predicate,37/38, also occur in the second block, but manufacturer identities remain unassigned.

The second block ends with conditional key27 rather than an unconditional sentinel record. Therefore the previously documented final-record rejection case is relevant to this asset’s actual ordering **if** that block reaches the loader and key27 is absent from the runtime registry. This does not establish that either condition occurs in normal play, nor that a visible failure results. It narrows the next check to metadata extraction and registry population, rather than assuming all official tables end with unconditional admission. No game/resource code was executed; decoding ran only on inert asset bytes.

## Logo metadata accessor linkage

The expanded audit retains complete Modern **`004f24e0..004f255e`**, plus indexed-entry accessor `004ea658..004ea665`. The decoded `SHPI` directory has entries `0000` at offset`0x20` and `0001` at`0x40088`. Both begin with DWORD **`0x0400107d`**: low byte type`0x7d`, upper24-bit displacement`0x40010`. The official executable’s file-backed type-validity lookup at `00566d54+0x7d` is nonzero (`0x20`).

For this positive displacement, the accessor’s `SAR8` and pointer addition lead to **`0x40030`** and **`0x80098`**, respectively. Each destination starts with type`0x6f`; that case returns destination+8, exactly **`0x40038`** / **`0x800a0`**, the two previously decoded `LTBL` locations. These exact offsets and headers are retained in the manifest. This resolves the prior uncertainty about the table locations’ correspondence to the inspected metadata accessor; they are not merely unrelated magic-string hits.

The accessor’s more general chain traversal, signed displacements and diagnostic path are not converted into a complete validated archive parser here. These two known entries have positive in-range displacements; arbitrary files may differ. Nor does this structural linkage prove the runtime path loads this archive, that the preparation helper leaves all loop registers as expected, or which model keys are registered. Those remaining conditions still separate the observed final-record fall-through from a demonstrated game failure.

## Logo preparation boundary: cursor restored, identifier not checked

The audit retains complete Modern **`004d6070..004d6109`**, previously researched as `AllocateAndUploadConvertedShape`. Its prologue saves ESI/EDI/EBP, and the shared normal epilogue restores them. The logo loader’s ESI table cursor and EDI output cursor therefore survive this helper’s normal return, subject to its callees returning with valid stack state. ECX is not generally preserved, but the loader overwrites it with the table record count immediately afterward; its subsequent loop does not require the incoming zero to survive.

The logo caller supplies a local output cell in EAX, image-entry pointer in EDX, EBX=`0x100`, ECX=0. The helper prepares a converted shape, invokes renderer slot **`009ef968`**, stores that slot’s EAX result into the supplied output cell at **`004d60e5`**, and calls slot **`009ef964`** only when the stored result is nonzero. It then frees the temporary converted buffer and returns local−`0x14` in EAX, rather than a locally normalized upload-success Boolean.

The logo loader neither tests that returned EAX nor rejects a zero identifier in its output cell before walking/copying admitted records. This closes the normal-return cursor-preservation question, while exposing a separate unchecked renderer-result boundary. Complete conversion/allocation failure contracts, renderer callback ABI and actual identifier semantics remain unresolved. No upload or allocation was executed, and no actual failure is claimed.

## Original loader counterpart: one named image becomes metadata-driven output

Paired caller span **`00460478..0046048e`** compares a widget field with literal **`texteffects`** (`0053a970`) through `004429c0`. Its conditional call at **`00460489`** targets original **`004a4390`** versus Modern **`004a4374`**. This establishes the loader correspondence by a shared consumer, rather than by assuming equal entry addresses.

Complete original loader **`004a4390..004a440d`** formats `%s%s` using base path **`007a2db4`** and original literal **`logo.qfs`** at `0053cf0c`, loads through `004956f0`, and obtains named entry **`logo`** (`0053cf20`) through `004ef1e0`. It invokes the shared conversion/upload helper `004d6070` with destination **`007a1b94`**, EBX256 and ECX3 when BYTE `007a3a58` bit1 is set, otherwise ECX0; then frees the loaded allocation. This body has no `LTBL` record scan or model-presence filter.

Modern changes the source literal at the same data address to **`logos.qfs`**, clears a list count, gates mask6, and builds per-logo12-byte records as described above. The separate count6 assignment seen in original `004a40cd` belongs to animation/update code, not this loader’s initialization, and must not be conflated with an archive record count derived here.

Thus the evidenced change is from one named uploaded image to a metadata-driven, model-filtered output list at the paired `texteffects` call site. Complete original draw selection, final Modern rendering, manufacturer identities and historical intermediate-release transitions remain unresolved. The retained strings and both complete loader bodies make this comparison reproducible without executing either game.

## Logo output consumer: packed payload fields reach draw preparation

Modern consumer span **`004a457b..004a45bf`** reads a selected index from **`007a1b38 + 4*slot`**, multiplies it by12 and adds output base **`0066133c`**. Record DWORD0 becomes EAX, the uploaded identifier. Record+4/+6/+8/+10 are each zero-extended WORDs: +4 enters ECX, while +6/+8/+10 are pushed as stack arguments. Scale comes from **`007a1b60 + 4*slot`**; a preceding integer expression forms a high-byte colour component combined with low24 bits`0xffffff`. Placement arrives through EDX/EBX before the call to **`004d7d90`** at `004a45b9`.

The audit retains the draw helper prefix **`004d7d90..004d7dc7`**. With its saved-register frame, stack offsets+`0x14`/+`0x18` correspond to record WORDs+8/+10. It loads them with signed32-bit `FILD` after the caller’s unsigned-WORD extension, multiplies them by the passed binary32 scale and retains binary32 copies. Their use is therefore consistent with horizontal/vertical extents; the first two WORDs are separate drawing inputs, not additional model keys. The manifest now decodes all four payload WORDs alongside the raw DWORDs.

This links the constructed12-byte list to draw preparation without claiming complete rendering. The selected-index producer, bounds, final texture-coordinate units, helper tail, renderer submission, scale/colour validity and actual visible manufacturers remain unresolved. Only the retained prefix is audited here; it is not presented as a complete function or a verified portable-C interface.

## Logo index producer and empty-list admission

Modern **`004a444c`** checks **`007a1b90==0`** at `004a4452` and jumps to its exit before the inspected slot initialization/update loops. Two direct calls to index producer `004a40c0` occur within those loops at **`004a4473`** and **`004a44be`**. This establishes an empty-list guard in that consumer; it does not prove the count cannot change concurrently or that no other indirect caller exists.

The ordinary producer path **`004a4337..004a4359`** zero-extends the byte at `00552938 + BYTE(0057126b)`, sign-extends EAX with CDQ, divides by DWORD **`007a1b90`**, and stores the remainder into **`007a1b38 + 4*slot`**. It increments the byte cursor with8-bit wrap. For a stable positive count and an unsigned-byte numerator, the stored remainder is in `[0,count-1]`. The producer itself has no zero-divisor guard; its observed caller supplies that admission check. Original’s corresponding ordinary path also divides by `007a1b90`, but its producer writes count6 at `004a40cd`; Modern removes that fixed-count write and uses the loader-populated count.

Slot9 follows a distinct sequence at **`004a40dc..004a40f7`**: it first stores the old DWORD **`0055e984`** directly as the selected index, then increments that value, uses signed IDIV by the count and stores the remainder back to `0055e984`. The modulo therefore constrains the **next** sequence value, not the index already published on this call. Valid initialization, prior nonnegative values and count changes matter; a universal selected-index bound is not established for that branch. Original uses fixed divisor6 there; Modern uses the current count.

These findings explain how the new dynamic logo list affects index selection and why an empty loaded list does not automatically imply a divide-by-zero in the inspected draw consumer. The count lifecycle, first slot9 seed, indirect callers and concurrent reloads remain unresolved. No division, animation or renderer call was executed.

## First animation state versus later reloads

The audit verifies **file-backed** initial values, including PE file offsets, in both executable baselines: sequence **`0055e984=0`** and animation sentinel **`0055e95c=-1`**. These are actual initialized bytes, not values guessed from a zero-filled virtual section. The consumer’s sentinel test at `004a445f` selects its initialization loop when the first slot remains−1.

With a stable positive loaded count and that initial counter, slot9 publishes index0 on its first producer call, then calculates the next sequence value modulo the count. This resolves the initial seed for that bounded case. It does not establish that the initial bytes remain unchanged until first use, that initialization runs exactly once, or that reloading a shorter list resets the sequence.

The decoded direct-reference search locates a load at `004a40dc` and store at `004a4114` for `0055e984`; this is a locator result, not proof that no indirect/bulk write exists. The retained logo loader clears output count but contains no explicit reset of that sequence cell. A prior index valid for a longer list can therefore require additional reset/order guarantees after list shrinkage; the preceding modulo constrains the next value only. No reload failure or out-of-range draw was observed.

## Animation producer: retained scaling, changed slot9 state constants

The audit now retains complete producer bodies: original **`004a40c0..004a4386`**, Modern **`004a40c0..004a4371`**. This avoids treating a Modern-shortened body as the original boundary. Other branches exist in these complete captures; the findings below concern the inspected slot9 and final-scale paths only.

At their corresponding final scale step, both load binary32 **`007a1b60 + 4*slot`**, multiply by the same file-backed binary64 constant **`0053cf04=0.8`**, and store binary32 to that same cell. Original additionally duplicates ST0 with `FLD ST(0)` and uses `FSTP ST(1)` before the final store; Modern performs the multiply/store directly. For ordinary finite values under equal x87 state, this retains the local arithmetic expression and final binary32 rounding. It does not establish matching status bits, exceptional behavior, full-stack preconditions or whole-animation equivalence.

Slot9 retains initial scale bits **`0x3fcccccd`** (binary32 approximately1.6), but changes the DWORD written to **`007a1ac0 + 4*slot`** from **60 to0**, and the DWORD written to **`0055e95c + 4*slot`** from **410 (`0x19a`) to390 (`0x186`)**. Its other inspected state writes remain0 at `007a1ae8 + 4*slot` and3 at `007a1b10 + 4*slot`. These cells participate in animation/update state, but no physical time units or visible smoothing effect are assigned here.

This provides bounded evidence of changed slot state alongside retained final scaling. It does not yet verify the release-note claim about smoother logo disappearance: the draw/update consumer and time-to-state conversion must be compared before making that attribution.

## Position-dependent logo fade replaces hard admission cutoffs

Paired retained consumer span **`004a44c3..004a45c7`** establishes a direct display-policy change. Both compute a base intensity in ECX (initially150; slot9’s first pass uses255). After centring the first pass horizontally, original admits the draw only for signed **`150 < x < 640`** and **`0 < y < 450`**. Those tests simply skip the draw outside the interval; they do not locally reduce its colour intensity near those bounds.

Modern replaces that admission sequence with four conditional negative additions. For ordinary non-overflowing integers, the inspected arithmetic is:

`adjusted = base + min(x-200,0) + min(440-x,0) + min(y-100,0) + min(380-y,0)`

It skips drawing when the resulting signed value is negative. Zero still reaches draw preparation. The subsequent shift by24 packs its low byte into the high byte of the colour DWORD, with low24 bits white. This establishes a position-dependent opacity/intensity reduction in the caller; complete renderer interpretation of that byte and visible smoothness remain separate evidence. This is not an arbitrary-input C formula: the actual x86 SUB/ADD operations wrap32 bits and use sign-bit branches, so signed-overflow-free integer invariants must be established before translating it literally.

The first-pass centring expression also changes. Original halves a signed DWORD extent with truncation-toward-zero correction, applies scale through x87, then calls **`004dfd56`** to round toward zero before integer storage. That helper temporarily loads control WORD`0x0c3f`, executes `FRNDINT`, then restores the previous control word. Modern zero-extends the selected record’s WORD extent, halves it with SAR1, computes the adjusted position using `FISUBR`, and directly executes `FISTP`. Its final conversion therefore follows the active x87 rounding mode, rather than explicitly forcing truncation. Exceptional values and status flags are not proved equivalent.

This gives bounded static support for **MP150-023**, the smoother-disappearance claim, while also identifying a numeric conversion difference relevant to C reconstruction. No logo frame or timing sequence was rendered; the complete animation update cadence and physical coordinate scaling remain unresolved.

## Retained update cadence and twelve local draw passes

Paired **`004a45c7..004a46e1`**,282 bytes, is byte-identical; the audit asserts its complete equality. This separates Modern’s changed fade/centering/resource inputs from a retained local movement/update tail.

At **`004a4697..004a46c4`**, each visited slot advances horizontal state **`0055e95c[slot]`** by **`007a1ae8[slot]`**, and vertical state **`007a1ac0[slot]`** by **`007a1b10[slot]`**, through32-bit ADD. Signed horizontal values outside150..640 or vertical values outside0..450 route to producer reinitialization. Endpoints remain admitted by these reset comparisons even though original draw admission used strict interior comparisons. This state advance is per visit to this routine, with no clock read or elapsed-time multiplier in the retained tail. The caller’s scheduling rate remains outside the evidence; values such as3 cannot yet be described as pixels per second.

For each admitted slot, EDI starts0 and increments until12. These are **twelve local rendering passes within one visit**, not twelve game frames. The first pass uses the special base intensity/centering path already described. Later passes compute their base intensity through the retained integer sequence based on `(12-EDI)*150`, signed division by12, then signed division by2 with truncation correction. They also adjust local drawing positions; those transient locals do not replace the stored base position cells updated once per slot.

Consequently the changed position-dependent fade applies over an existing multi-pass drawing pattern, while the local update-tail instructions remain unchanged. Equal instructions do not prove equal trajectories or cadence: Modern changes producer constants, list-derived extents and centering conversion before this tail. The x87/helper status, complete caller scheduling and actual frame output remain unresolved. No animation was executed.
