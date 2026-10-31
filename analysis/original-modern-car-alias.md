# Original versus Modern: car-list aliases in rendering

## Evidence boundary

Modern helper **`004728f4..00472923`** and paired caller span **`00463b74..00463bc5`**. Original code at the helper’s new address is unrelated; correspondence is established through the two retargeted calls, not equal addresses. Reproduce with `python3 analysis/scripts/audit_car_alias_difference.py`; the [manifest](evidence/audits/original-modern-car-alias.json) binds both executables, strings, call targets and comparator bodies. See the [baseline](original-modern-differences.md). Static only; no game/UI or Ghidra writes.

## Matching expands from one name to three

Original calls comparator **`004e9ec0`** at **`00463b7c`** and **`00463baf`**, with the widget/list name from `[ESI+0x64]` in EAX and literal **`cars`** from `0053aa34` in EDX. Modern retargets both calls to the new helper while retaining the surrounding branches.

The helper saves the input pointer in EBX and compares it, in order, with **`cars`** (`00537e80`), **`car2`** (`00537c34`) and **`carShowcase`** (`00537e88`). It returns as soon as a comparison equals0; otherwise it returns the third comparator result. This is a zero-on-match contract, not a normalized Boolean or a stable ordering among all three names. Incoming EDX is ignored by the wrapper. It preserves EBX and uses plain RET with no stack arguments.

The complete comparator **`004e9ec0..004e9efb`** is byte-identical. It folds ASCII `A..Z` to lowercase on both sides, compares until mismatch or NUL, and returns the unsigned-byte difference in EAX. This is ASCII case-insensitive equality, not locale-aware Unicode matching. It modifies EDX; the alias wrapper’s callers must retain their actual register contracts rather than use an invented standard C ABI.

## Two affected consumer decisions

At the first call, return0 branches directly to **`00463ba2`**, admitting the shared car-list rendering path. Nonmatches continue through another name test and an item-count comparison. At the second call, the caller loads a count into ECX; nonmatch subtracts4, whereas any accepted alias retains that count before the shared call to `00439730` with EBX=4. The helper and comparator leave ECX untouched in the inspected local bodies.

Modern therefore extends the existing `cars` treatment to two additional names in this renderer. Full count meaning, asset bindings, output text/geometry, surrounding renderer changes and a unique release-note attribution remain unresolved. The finding does not establish a selection-model or gameplay change merely because the aliases contain car names.

## Official package bindings

The audit now scans all **52 `.mnu` members** directly from the hash-pinned official Modern archive, recording matching section types, exact fields/line numbers and member hashes. It finds ten bindings in nine members:

| List name | `[droplist]` members | `[cascade]` members |
|---|---|---|
| `cars` | `car1.mnu`, `cedbasic.mnu` | `main.mnu`, `mainmult.mnu`, `mainsplt.mnu` |
| `car2` | `car2.mnu` | `mainsplt.mnu` |
| `carShowcase` | `showcase.mnu`, `history.mnu`, `interior.mnu` | None in this bounded scan |

The six droplist bindings identify concrete packaged controls associated with these names. For example, `car2.mnu` binds a droplist at x101/y69 with `maxvisitem=10`; `showcase.mnu` uses the same position/count with `codelink=CAR_SELECT_P1` and `listname=carShowcase`. These fields support a menu-control association. They do not independently prove every loader callback, currently active screen or visible output.

The four cascade bindings are deliberately separate: the same list name can feed a different widget type, so their presence alone does not extend the audited droplist-renderer conclusion to cascades. Complete descriptor/loader-to-widget callback linkage remains follow-up work.

The local `fedata_org/menus` backup contains mixed uppercase/lowercase copies of several names. Its provenance is not authenticated as a clean original distribution. This scan therefore makes no original-versus-Modern asset-addition claim and does not count duplicate backup files as additional historical controls. The executable call-target comparison above remains the evidence for the code change.

## Separate adjacent helper: track-list policy alias

The neighboring Modern helper **`00472924..00472959`** concerns different names and is not part of the car-alias matcher. It returns1 exactly when **`006fd3b8==3`** and the incoming EAX string compares equal, through the same ASCII comparator, to **`tracks`** (`00537e34`) or **`rectrk`** (`005382ec`). Otherwise it returns0. It preserves EBX/EDX; ECX is untouched by its local instructions and comparator. The mode’s higher-level meaning remains outside this finding.

A paired caller witness **`00461d25..00461d51`** establishes the change: original compares only with `tracks` (`0053aa3c`), then additionally tests mode3. That conjunction selects **35** in local−`0x14`; other cases select **15**. Modern retargets the call to the new helper and selects the same two constants from its Boolean result. Thus `rectrk` receives the existing `tracks` treatment in this inspected consumer; this is an alias expansion, not evidence that mode3 itself was introduced.

Three other Modern call sites are retained in the audit: **`004628ef`**, **`004634ea`**, **`00464570`**. They likewise select15 or35 from the helper result, using different widget fields/locals. Their surrounding complete original bodies and downstream units have not been audited here. The constants must not yet be called row counts, pixel heights or selection limits. Full widget linkage and visible output remain unresolved.

## Track-policy constants feed horizontal layout

The follow-up retains Modern **`004645e3..00464609`**. It loads the helper-selected15/35 from local−4, adds15, adds that result to WORD widget+`0x1e`, and stores the low WORD back to widget+`0x1e`. The same block forms widget+`0x20` from `16 * WORD(widget+0x5a) + 2` through the observed partial-register instructions. These are separate horizontal/vertical layout calculations; the15/35 selector is not used there as a visible-row count. The coordinate interpretation is supported by the later placement reads of widget+`0x1e`, rather than inferred from its numeric magnitude alone.

In the renderer, paired spans **`00463841..00463859`**, **`00463875..00463894`** and **`004638a7..004638f4`** are byte-identical. They add the selected local−`0x48` value to the signed high WORD from widget+`0x1a` (the component beginning at+`0x1c`) before calls to drawing helpers `004d7990` and `00452190`. Two particular drawing paths additionally subtract33 or17. The alias policy changes the offset source while retaining these downstream arithmetic sequences.

For otherwise equal inputs on those paths, selecting35 instead of15 adds **20 layout units** to the offset and increases the stored extent by20 modulo the final WORD store. This is code-level support for additional horizontal room/offset for the accepted track-list alias. Full text measurement, the meaning of each indicator and coordinate-to-screen scaling are not established; “20 layout units” must not silently become a guaranteed20 physical pixels at every resolution. No menu was rendered during this comparison.

The [complete paired layout-helper follow-up](original-modern-common-menu-buttons.md#complete-layout-helper-difference-coverage) now supersedes the earlier original-body coverage limitation specifically for `00464560`: original selects35 for every mode3 list, whereas Modern restricts that choice to `tracks`/`rectrk`. Together with the separate width-add change5→15, the net local contribution changes by+10 for accepted names and−10 for other mode3 names. The other three consumers retain their own stated coverage boundaries.
