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

## Other consumers start from different original policies

The audit now retains paired entry prefixes **`004628d0..0046291a`** and **`004634d0..00463501`**, and pins both Modern CALL targets to `00472924`. They do not begin with the same original predicate:

| Consumer | List name source | Original selects35 when | Modern selects35 when |
|---|---|---|---|
| `004628d0` | widget+`0x60` | name equals `tracks` or `rectrk`, without a mode check | mode3 and name equals `tracks` or `rectrk` |
| `004634d0` | widget+`0x64` | mode3, without a name check | mode3 and name equals `tracks` or `rectrk` |

All other cases select15 in the inspected prefixes. The first consumer already recognizes **both** names in original: literals`0053aa3c` and`0053aa9c` are `tracks`/`rectrk`, respectively. Calling that site a newly added `rectrk` alias would therefore be incorrect. Instead Modern adds the mode3 gate there, reducing the selected contribution35→15 for those names outside mode3. The second consumer gains a name gate, reducing35→15 for other names within mode3.

In `004628d0`, both versions preserve the WORD-list pointer from lookup`00442c80` in ESI before making the policy decision. Modern relocates that assignment by five bytes as part of the rewritten prefix. In `004634d0`, Modern retains the two zero-local initializations but moves them earlier to replace the original mode load; this is not evidence of removed initialization. These observations are local data-flow checks, not a complete register-liveness audit.

Together with the previously inspected `00461d25` caller and complete `00464560` helper, this establishes four caller-specific policy transitions: adding a second name, adding a mode gate, or adding a name gate depending on the site. The common final helper does not mean the original policies were uniform. Full remaining renderer/layout bodies, mode semantics and visible results remain pending. No runtime or target instruction probes were used.

## Complete `004628d0` layout helper

The paired audit now extends this consumer through both RETs at **`004629ae`** and **`004629be`**: body`004628d0..004629bf`, end exclusive, **239 bytes**. All differences fit the selector rewrite`004628ea..0046291a` and two immediate bytes at`00462972` and`00462980`. The manifest enumerates changed addresses; assertions reject changes elsewhere in the body. This supersedes the prefix-only boundary for this consumer, while `004634d0` remains a prefix comparison.

The expanded path requires WORD widget+`0x42` nonzero and a nonzero list pointer. It scans WORD IDs to a zero sentinel, starts width at40, and calls the text/width helpers`004d1850` and`00452020`. After that shared scan, original adds **selected15/35 +5** to width; Modern adds **selected15/35 +15**. With the previously established predicate change, equal incoming measured widths give these local padding contributions:

| Name and mode | Original | Modern | Change |
|---|---:|---:|---:|
| `tracks`/`rectrk`, mode3 | 40 | 50 | +10 |
| `tracks`/`rectrk`, another mode | 40 | 30 | −10 |
| Other name, any mode | 20 | 30 | +10 |

The same path computes WORD widget+`0x20` from **WORD+`0x56`**, rather than the other helper’s WORD+`0x5a`. Original stores`16 * value +5`; Modern stores`16 * value +2`, modulo65536. The shared placement then stores widget+`0x1c` from WORD+6 plus28 and widget+`0x1a` from WORD+8 plus16. The fallback path calls`00461a70` in both baselines. Its unchanged CALL operand does not prove that callee or fallback output is unchanged.

This second complete body confirms the repeated5→15 width and5→2 extent changes while preserving its distinct widget offsets and original selection predicate. It does not prove the producer/meaning of WORD+`0x56`, live list contents, text metrics, rendered dimensions or historical introduction. Preserve the WORD truncation and each widget type’s field layout in reconstruction instead of merging these helpers by superficial similarity. No game code was executed.

## Direct fallback and width dependencies checked

The audit now retains and asserts equality of two complete direct-callee bodies, rather than relying on unchanged call addresses:

| Address/body | Bytes | Paired result | Local behaviour |
|---|---:|---|---|
| `00461a70..00461a96` | 38 | Identical | Store WORD+`0x20`=27, WORD+`0x1e`=30, WORD+`0x1c`=WORD+6−10, WORD+`0x1a`=WORD+8 |
| `00452020..0045208c` | 108 | Identical | Null string returns5; otherwise selects an x87 scaling path or another width routine after calling`00452100` |

Ends are exclusive. `00461a70` has no calls, global accesses or floating-point instructions. It receives the writable widget pointer in EAX, preserves EDX via the stack, leaves EAX unchanged, and performs only those four WORD stores plus integer arithmetic/prologue/epilogue. For equal accessible input widget storage and a valid stack, this closes the previously unresolved **local fallback transformation**. Flags are affected by its subtraction; the unchanged body does not normalize them or define a portable C return convention.

The width helper saves incoming EAX as the string pointer and uses incoming EDX as input to`00452100`. For a nonnull string it tests global`00559234`. The nonzero branch calls`004d1430`, multiplies the x87 result by the binary32 value at`005395f0`, divides by the signed DWORD at`007cdac8`, calls`004dfd56`, then FISTP-stores a signed DWORD result. The zero branch calls`004da4a0` with ECX1 and EBX/EDX0. This records the local dependency and x87 conversion chain; it does not establish the complete callees, constants’ runtime values, divisor validity, resource metrics or floating-point exceptions.

Thus equal local width-helper bytes do **not** prove equal text widths across versions or configurations. The fallback is locally closed because it has no external data/callee dependency; width remains dependent on initialization, global state and additional functions. No function was executed and no runtime equivalence claim is made.

## Width dependency removes an intermediate integer conversion

Following the nonzero-renderer-flag branch reveals a substantive difference inside **`004d1430`**. Paired complete bodies are **original`004d1430..004d1471` (65 bytes)** and **Modern`004d1430..004d1450` (32 bytes)**, with exclusive ends. The audit pins their common call target`004d1000` and the original conversion instructions.

Original loads global`00561b3c` into ECX, stores1 to that global, zeroes EBX/EDX, and calls`004d1000`. It then calls`004dfd56`, FISTP-stores a signed DWORD, copies that integer through EAX, writes ECX back to the global, and FILD-loads the integer as the x87 return value. The old global value is held in ECX across the calls; full callee register preservation remains a dependency of interpreting that as an unconditional restore.

Modern instead increments the same global, zeroes EBX/EDX, calls`004d1000`, decrements the global, and returns without a local x87 conversion. It removes the original intermediate integerization. Both versions have an x87 return path; this is **not** evidence that Modern newly enables80-bit arithmetic throughout the game. The difference is the removed conversion boundary inside this particular measurement wrapper.

Consequently the identical enclosing`00452020` body can receive different numerical inputs before its multiplication/division and final integer conversion. For example, a fractional callee result need not survive the original wrapper, whereas Modern has no such local truncation step. Actual changed widths require the callee’s reachable outputs, rounding helper contract, scale/divisor values and floating-point state; none were measured here. Overflow, NaNs and x87 status/exception behaviour must not be reduced to an ordinary finite-number example.

The global-state rewrite is also not universally equivalent: original forces1 for the call; Modern supplies incoming value+1 modulo32 bits. If incoming state is0 and the callee leaves it unchanged, both expose1 and finish0; other incoming states or callee writes can differ. INC/DEC are ordinary non-LOCK operations, so this wrapper supplies no cross-thread synchronization. Reentrancy intent and global consumers remain unresolved.

The selector`00452100..0045210a` is separately byte-identical: it writes incoming EAX to global`00664650` and returns, with no font/resource lookup of its own. In the width-helper call EAX receives the incoming EDX selector first. The selector’s consumers and initialized font data must be traced before assigning full font semantics. This pass used static byte reads/disassembly only.
