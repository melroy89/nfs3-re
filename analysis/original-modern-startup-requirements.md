# Original versus Modern: startup resource and desktop requirements

## Counterpart evidence

Original **`004b5f10..004b5fee`** corresponds to Modern **`004b5748..004b57c1`** by shared resource-check operations and subsystem callers, not by address. Original setup calls it at `004b6092`; Modern setup calls its counterpart at `004b5c0c`. Reproduce with `python3 analysis/scripts/audit_startup_requirement_difference.py`; the [manifest](evidence/audits/original-modern-startup-requirements.json) retains both complete bodies, caller witnesses, diagnostic helpers, imports and final messages. See [baseline](original-modern-differences.md). No API, dialog, game or instruction execution; no Ghidra edits.

## Memory arithmetic changes before the threshold

Both initialize DWORD+0 of global block `007a3ac0` to32 and pass its address to imported **GlobalMemoryStatus**, then read DWORDs at block+0ch and+14h. The report retains offsets rather than assuming a complete reconstructed structure declaration.

| Policy | Original | Modern |
|---|---|---|
| Arithmetic | Add two byte-valued DWORDs modulo2^32 | Logical-shift each DWORD right20, then add |
| Admission | Unsigned byte sum >=`01000000h` (16 MiB) | Unsigned sum of truncated MiB >=16 |
| Extra operation | Logs the shifted wrapped sum through `0042d500` | No corresponding local logging call |
| Low-resource message | Selects from six-entry tables using incoming EAX index | Fixed English text: “Your RAM resources are too low.” |

Modern’s shifted sum cannot overflow32 bits for these two32-bit inputs. Original’s byte sum can wrap: two hypothetical2-GiB fields sum to0 modulo2^32 and take the warning path, while Modern computes2048+2048. These are arithmetic examples, not injected API returns.

The change also discards fractional MiB separately. Hypothetical8.75-MiB and7.5-MiB fields total16.25MiB and pass the original threshold, but Modern floors them to8+7 and warns. Thus this is not universally equivalent admission with only overflow fixed. Preserve the demonstrated arithmetic instead of silently summing in64 bits as a reconstruction “improvement.” API errors and platform-specific field population are not tested.

## Shared disk-check request and changed diagnostics

Both pass **EAX=1 MiB** to helper `004516a0`, testing its result and entering a warning branch on zero. The Modern message explicitly says the hard drive has less than1MB free. The follow-up below now traces the free-byte arithmetic and geometry wrapper. Directory selection/failure and actual free space remain untested.

Original low-memory and disk warnings call MessageBoxA with flags31h and select text/caption pointers through the incoming index. Return2 leads to `004f2a7d`. Modern routes both through **`004b5728`**, which uses flags51031h and a shared caption, calls the same termination helper for return2, otherwise returns. The desktop-depth failure uses separate **`004b570c`**, flags51010h, followed by `004f2a7d` regardless of dialog result. The terminal ExitProcess boundary is verified in the follow-up below; pre-exit callback completion/nonlocal behavior remains unverified.

## Added desktop-depth check

After the resource checks, Modern calls **GetDesktopWindow**, **GetWindowDC** and **GetDeviceCaps** with literal index12, then uses signed comparison against8. A result below8 invokes the fatal-diagnostic path with **“Cannot run if desktop bitdepth is less than 8.”** The manifest identifies the imported APIs at the actual IAT operands. The original counterpart returns after the disk warning and has no corresponding desktop-query sequence in that body.

This branch checks the returned capability directly; it does not multiply by a second planes capability, verify a renderer-supported game mode, or prove movie decoding compatibility. The local routine contains no ReleaseDC call; ownership, other cleanup or actual resource leakage is not established by that bounded observation.

## Register and reconstruction boundaries

Modern uses PUSHAD/POPAD, preserving the incoming general registers including EAX when its ordinary path returns. It does not provide an ordinary Boolean success result. Original saves EBX/ECX/EDX/ESI/EDI/EBP, consumes incoming EAX as its diagnostic table index and leaves an operation-dependent EAX result. The two should not receive one guessed C success-return signature.

Verified changes include memory-sum order/units, warning selection and flags, removed local logging and the added desktop check. Historical attribution, full localization fallback, resource API failures, directory selection, pre-exit hook completion and observed startup acceptance remain unresolved. This is an independently documented code delta, not a claim that every system-requirement path in either executable has been compared.

## Disk-space follow-up: signed wrapping product becomes overflow-aware admission

The expanded audit retains complete disk check **`004516a0`** (original end `004516fa`, Modern `004516f4`) and verifies equality of geometry wrapper **`004f07d0..004f083e`**. The earlier disk-helper unknown is now narrowed to these verified local operations and the remaining directory/API boundaries.

The check keeps incoming EAX as its requested byte threshold in ECX. It calls current-directory helper `004f0730` with a stack buffer and limit250, reads the first buffer byte, subtracts64, and supplies the result as a drive number to `004f07d0`. That wrapper converts nonzero drive numbers into a three-character root such as `C:\`, otherwise passes a null root pointer, then calls imported **GetDiskFreeSpaceA** through IAT `00534514`. The related current-directory API is **GetCurrentDirectoryA**, IAT `00534500`; a full directory-helper contract is not claimed here.

The wrapper outputs four DWORDs in this order: **total clusters, free clusters, sectors per cluster, bytes per sector**. The startup check multiplies **free clusters × bytes per sector × sectors per cluster**, testing the wrapper’s return first. Nonzero wrapper return produces check result0. This ties the1-MiB request to a free-byte calculation, rather than treating the warning text as proof of the calculation.

| Case | Original | Modern |
|---|---|---|
| Product fits below2 GiB | Low32-bit IMUL product, signed threshold comparison | Unsigned MUL product, unsigned threshold comparison |
| Nonoverflowing product has bit31 set | Negative signed interpretation can reject ordinary positive threshold | Compared as unsigned bytes |
| Either multiplication exceeds32 bits | High product discarded; wrapped result compared signed | Carry/high-product indication immediately returns1 |

For a normal positive geometry product of2 GiB and the startup1-MiB threshold, original’s signed comparison rejects while Modern accepts. At exactly4 GiB the old low32 bits are0; Modern detects multiplication overflow and accepts. These are derived arithmetic examples, not injected API responses or filesystem probes.

The overflow shortcut is sound for the intended positive geometry factors and a32-bit byte threshold: a true product exceeding32 bits is larger than any such threshold. It is not a general malformed-input contract. In particular, an overflowing first product followed by a zero final factor would be accepted early by Modern; valid positive sector geometry is therefore a material assumption, not an opportunity to silently rewrite behavior.

Both routines preserve ECX/EDX and return explicit EAX0/1. The first current-directory helper’s return is not locally checked before reading its buffer, so directory failure and non-drive-prefixed paths remain unresolved. The retained wrapper’s API error conversion is delegated to `00500ff4`; error-specific behavior, actual drive selection under Wine/Linux mappings and observed large-volume acceptance are untested. This is another verified arithmetic change independent of any uniquely matched release-note bullet.

## Removed original corruption diagnostic in the large NOP span

The expanded startup audit captures original `004b5e50..004b5e9a` and proves all74 same-address bytes are NOPs in Modern. This classifies one complete original helper within the [largest outside-function NOP replacement](original-modern-outside-function-index.md). It does not imply that all corruption detection or diagnostics disappeared.

The helper consumes incoming **EAX as an unchecked index**, copies two six-DWORD tables from `004b55c8` and `004b55e0` into local storage, and uses the indexed pointers as MessageBoxA text and caption. It passes null owner and flags31h through IAT `00534764`. The first table selects the English reinstallation/corruption warning at indices0,3,4,5, German at1 and French at2. The second has six different warning-caption strings. Full pointer/text entries are retained in the [evidence manifest](evidence/audits/original-modern-startup-requirements.json); the encoded strings are decoded with Latin-1 for byte-preserving display, not a proven Windows code-page contract.

After the dialog, the return value is **not tested**: execution calls `004f2a7d` unconditionally. That seven-byte thunk clears EAX and calls `004dfd04`. The captured downstream body invokes indirect hooks and routes through `004dfd30` toward `004ff38c`. The follow-up below verifies the final ExitProcess boundary using existing research and identical original/Modern bytes. The routine has no supported ordinary returning success/failure contract; pre-exit callback behavior remains separate.

On any ordinary return from the helper, ECX, EDX, ESI, EDI and EBP are restored. EAX is call-dependent; EBX is not saved by this helper, and its preservation would require callee contracts. No index bounds check precedes either stack-table access, so a maintained interface must establish index0..5 at callers rather than treating arbitrary integers as a supported input domain.

The [registry selector](original-modern-registry.md) and [language selector](original-modern-language-table.md) already identify calls to this entry when their searches fail; [renderer initialization](original-modern-renderer-initialization.md) identifies another diagnostic route. Those call sites explain why a corruption message can reflect selector/configuration failure; its wording alone is not proof that executable or asset hashes were checked. This audit does not establish all caller reachability, a Modern counterpart for every call, or historical removal date. No dialog, API, game or instruction probe was executed.

## Removed original texture-resource log

Adjacent original helper **`004b5ea0..004b5f0b`** is another complete removed body: the audit asserts that all107 same-address Modern bytes are NOPs. The matched [subsystem setup captures](original-modern-resolution-defaults.md#menu-startup-depth-fixed-original-request-versus-optional-modern-32-bit) show original `004b60e0..004b60f8` loading selector `007a3a54`, skipping this helper when selector=1, otherwise supplying EAX=selector and EDX=`007a3a50` at CALL `004b60f3`. Modern setup `004b5c00..004b5d83` has no corresponding call. This is removal from the matched startup path, not proof no other Modern diagnostic reports low resources.

The helper saves incoming EAX/EDX in ESI/EBX, calls driver about slot `009ef980`, and reads returned descriptor DWORD `+70h`. Only when incoming selector equals6 does it add descriptor `+74h`, wrapping modulo2^32. It then compares the result **signed** against `00200000h` (2,097,152). Greater-or-equal returns without formatting; smaller values select the log path. A result with bit31 set therefore takes the log path despite being numerically large when unsigned. Descriptor units are not established solely by the threshold or warning text; do not silently rename this value available VRAM or rewrite the comparison as unsigned.

On that path, two six-entry tables at `004b55f8` and `004b5610` supply message/caption through the unchecked incoming EDX index. The fixed format at `0053fde0` is `%s: At %ld %s\n\n`; arguments are caption, the descriptor-derived value and the selected warning text. Output object is `00566f72`, passed to adapter `004f4b80`. The adapter's33 bytes are identical between the two EXEs, and its [existing formatter research](detailed-analysis-notes.md#variadic-buffered-file-formatting-adapter) establishes stack arguments stream/format/values and forwarding to `004ff014`. Thus this is a formatted-stream diagnostic, **not a MessageBox or a local startup rejection**. The destination file/console and actual write result are not established by this helper.

The helper restores EBX, ECX, ESI, EDI and EBP. EAX/EDX are operation-dependent; no Boolean success result is established. There is no local descriptor-null check or language-index bounds check, so reconstruction requires caller/driver preconditions rather than invented safe defaults. Full tables, pointer identities, original/Modern body hashes and the formatter-equality assertion are retained in the [startup manifest](evidence/audits/original-modern-startup-requirements.json). No log was generated by running the game, and no historical introduction/removal date is claimed.

## Removed DirectDraw capability probe and DirectX 5 gate

Original **`004b6590..004b67ac`** is a540-byte capability probe; the audit verifies that its entire same-address Modern region is NOPs. It captures the complete original body, its caller witness `004b5860..004b58bb`, imports, queried identifiers and six localized warning strings. The [original setup chain](original-modern-registry.md#original-selector-precedence-and-call-chain) already connects `004b5860` to subsystem startup. These are original call relationships; same-address Modern code is not assigned the original caller's role.

The probe initializes a148-byte local version-query block and calls imported **GetVersionExA**. Failure returns0. It also returns0 when block field `+10h` equals2 and unsigned field `+4` is below5. These are literal field/constant checks; interpreting every OS compatibility mode or Wine response remains outside this audit.

It then loads literal `ddraw.dll`, resolves **DirectDrawCreate**, and invokes the result with null first/third arguments and a local output pointer. Thus this dependency is established by resolver dataflow, rather than the retained name alone. Library, export or signed-negative creation failure returns0; appropriate post-load failure paths call FreeLibrary.

| Probe stage | Branch result in EAX |
|---|---:|
| First created object's slot0 call with identifier `b3a6f3e0-2b43-11cf-a2de-00aa00b93356` fails (signed-negative) | 1 |
| Subsequent original-object slot50h call fails | 0 |
| Subsequent original-object slot18h call fails | 0 |
| Created surface object's slot0 call with identifier `da044e00-69b2-11d0-a1d5-00aa00b8dfbb` fails | 3 |
| Final queried interface is obtained; success cleanup returns | 5 |

Slot0 calls have the COM query-interface argument shape, and slot8 calls have the one-object release shape. The identifiers are decoded from exact16-byte constants at `0056b928` / `0056b938`; named interface versions and complete vtable/header layouts are not inferred solely from familiar GUIDs. The method calls use signed HRESULT-style success tests. Outputs are capability-path tags, **not a complete numerical installed DirectX version**.

The helper releases intermediate queried interfaces through slot8 and unloads the library along the captured branches. It creates a108-byte local descriptor before the slot18h request. Full object ownership, implicit surface teardown and failure-side provider behavior remain unverified; visible release calls alone do not prove complete leak-free cleanup. It preserves EBX, ECX, EDX, ESI, EDI and EBP on its ordinary returns and reports the tag in EAX.

Caller `004b5872` compares the result signed against5. A lower result formats one of six language-indexed messages explicitly requiring Microsoft DirectX 5, displays MessageBoxA with flags30h, then requests termination through `004f2a7d`. Hence a method failure returning0 can trigger an installation warning even though loading DirectDraw succeeded. The diagnostic wording does not prove absence of DirectX. The complete termination-route limitation documented above still applies.

Modern removes this particular probe body and changes the setup/renderer-loading sequence documented elsewhere. That does not establish that every Modern driver is independent of DirectDraw, nor prove startup success on any OS. Intermediate-release dating, live provider results and exhaustive Modern replacement checks remain separate. No target/API execution, Ghidra change or executable modification occurred.

## Removed installation and media admission helpers

The audit now captures original **`004b62a0..004b6311`** (113 bytes) and **`004b6320..004b6400`** (224 bytes), verifies both complete regions are NOPs in Modern, and records their literal data and message tables. Original startup directly calls the admission helper at `004a3d67`, before subsystem wrapper `004a3390`. The original helper's removal is established; exhaustive replacement or media-policy coverage across Modern is not.

The small helper copies six bytes `65 58 60 62 67 58` from `0055fdc0`, adds13 to each byte modulo256 and compares the result against `007a26b4` with a length limit6. The decoded bytes are `remote`. Captured comparator `004eb390..004eb3bf` compares bytes case-sensitively and returns0 when the six-byte limit is exhausted; the caller maps that equality to EAX1, otherwise0. This is a **prefix test**, not a proved exact full-string test or a documented external user option. Inputs and later global writes remain separate contracts.

The larger helper's observed sequence is:

1. It copies the11-byte template `C:NFS3.EXE` (including its terminator), calls path helper `004f9390` with literal `install.win`, extracts a drive index through `004f93f0`, then calls drive probe `004f9410`. The CWD-based construction and its capacity limitation are traced in the follow-up below; API-failure handling remains unresolved.
2. The drive probe constructs a drive-root string, calls imported **GetDriveTypeA** via IAT `00534518`, and accepts only literal return5. If the first installation-path drive is accepted, the admission helper displays a language-indexed message saying the game must first be installed, then calls `004dfd04` with EAX0. Message tables have six entries; the global index is not locally bounds-checked.
3. If the `remote` prefix helper returns nonzero, it takes the ordinary return without scanning further drives.
4. Otherwise it scans drive indices0..25. For each accepted drive type it changes the template's first byte to `A + index` and passes it to enumeration helper `004f0330` (traced below). A nonzero result exits the scan successfully. The string is **drive-relative** (`C:NFS3.EXE`), not `C:\NFS3.EXE`; reconstructing it as a root-absolute path would change semantics.
5. Exhaustion displays the second six-entry table's message requiring the game CD in the CD-ROM drive, then calls `004dfd04` with EAX0. The terminal API is nonreturning under its ordinary contract; pre-exit callback completion remains unverified.

The drive-type wrapper is statically tied to its actual import; the diagnostic wording and scan establish an installation/media admission role. They do **not** establish what every path/resource helper verifies, authentic media identity, successful asset access or the complete original protection mechanism. The helper preserves its six saved non-EAX registers on an ordinary return, but does not provide a defined success Boolean to startup.

This closes classification of these two original entries inside the large removed startup span. The later follow-ups establish ordinary path construction and enumeration; API-failure behavior, global-source ownership, other callers and Modern replacement policy remain follow-up work. No drive was scanned and no file, CD or game API was invoked by this audit; executable bytes and saved Ghidra state remain unchanged.

## Admission path builder uses CWD and checks capacity after retrieval

The follow-up captures complete original path builder **`004f9390..004f93f0`** and directory wrapper **`004e33a0..004e3401`**. The97-byte directory wrapper is identical in original and official Modern. This does **not** pair the two EXEs' `004f9390` entries: Modern's same address is an unrelated integer-to-float adapter. The [existing directory-wrapper contract](detailed-analysis-notes.md#native-directory-and-deletion-adapters) is reused and checked against the supplied original bytes.

Original path builder takes EAX=destination, EDX=filename and EBX=capacity. It first calls `004e33a0` on the destination; that wrapper clears last error and calls **GetCurrentDirectoryA** with fixed size511. It then measures filename and destination lengths, computes `wrap32(capacity-filename_length-1)`, and returns0 if the unsigned destination length exceeds that result. Otherwise it copies the filename, including NUL, directly over the destination's existing NUL and returns1. **No separator is inserted.** For ordinary valid strings and fitting arithmetic, the later check bounds the concatenated result; subtraction underflow or retrieval failure is not repaired by that description.

Thus the admission caller forms CWD concatenated with literal `install.win`; it does not establish an executable-relative path or open that constructed file. The immediate caller uses the result only to extract a drive index before its drive-type check. This explains why missing separator insertion is not, by itself, proof that this branch fails to open an installation file: no such open occurs in the inspected path.

The capacity boundary is materially narrower than a safe generic path interface:

- Admission supplies EBX256 and destination `EBP-13ch` after reserving13ch (316) local bytes.
- The nested CWD wrapper passes511 to the API **before** the256-byte concatenation admission check. The original caller does not inspect the path builder's Boolean result before reading its drive prefix.
- A provider writing a long CWD can therefore exceed the supplied256-byte limit, and a directory string of316 or more bytes plus its terminator would extend beyond that316-byte frame-local extent if written there. This is a conditional instruction/size consequence, not a reproduced overwrite, crash or exploit claim.
- The directory wrapper's literal success test admits unsigned results1..511; other results enter its diagnostic route. If that diagnostic returns, buffer validity and returned EAX residue remain unresolved. Accepting511 in code is not proof of successful retrieval at that boundary.

Required follow-up is the actual startup CWD bounds/ownership and diagnostic failure contract if reconstructing this path. Do not silently turn its fixed511 request into a safe256 request while claiming exact original behavior. Modern removes the surrounding installation/media helper, but retains the directory wrapper for other consumers; this evidence does not establish all remaining uses are safe or equivalent. No directory API, file operation, game or new instruction probe was run.

## Media candidate test reuses retained shared file enumeration

The old admission scan's call at `004b63ab` targets **`004f0330..004f042b`**, not a dedicated disc-authentication routine. The startup audit now verifies this complete251-byte body and its **170-byte continuation `004f0280..004f032a` are byte-identical** in both EXEs. It separately asserts the IAT names **FindFirstFileA**, **FindNextFileA**, **FindClose** and **GetFileAttributesA** in both baselines. Thus removal of the media-admission caller must not be described as removal of these general file helpers.

The first helper receives the pattern pointer in EAX, closes an existing shared search handle when cell `005651d4` is not−1, copies the new pattern into shared buffer `009f09c4` and records its path-prefix length in `009f09c0`. It calls FindFirstFileA into a local result block. Invalid handle returns0; otherwise it constructs a candidate pathname in shared output buffer `009f0ac9`, combining the saved prefix with returned bytes beginning at result offset2ch.

Both the first-result and continuation paths call GetFileAttributesA on that candidate. A result of `ffffffffh`, or attribute bit10h set, skips the candidate. A retained candidate returns **EAX=`009f0ac9`**; it is not a new allocation or a Boolean1. The continuation loops with FindNextFileA and, on exhaustion, closes the handle, stores−1 to `005651d4` and returns0. The file-backed initial value of that handle cell is−1 in both baselines. Close results and error-specific filesystem behavior are not validated by these local branches.

The old admission caller only tests EAX for zero/nonzero. With its drive-relative `X:NFS3.EXE` pattern and drive-type gate, the inspected boundary therefore establishes **availability of an enumerated non-directory candidate**, not content hashing, an executable signature check, authentic media identity or completeness of game assets. Filesystem/provider semantics and any protection elsewhere remain outside this claim. A diagnostic requiring the game CD cannot strengthen this local predicate into authentication evidence.

Shared handle, pattern, prefix and output buffers make these helpers stateful: starting a new search can close the previous search, and later enumeration can overwrite the returned pathname. A C reconstruction must model that lifetime/aliasing or explicitly document a changed API. These bodies establish no local synchronization or caller-owned enumeration state; concurrent or nested use requires separate ownership analysis. Equal code and initial handle values do not prove equal directory contents, timing or runtime results.

This resolves the formerly anonymous `004f0330` boundary for the removed media scan. Remaining work concerns actual path/provider results, other callers and the broader Modern startup policy. No enumeration, file lookup, CD access, game execution or Ghidra edit was performed.

## Shared termination chain reaches ExitProcess

This follow-up reuses the established [zero-status exit-boundary research](detailed-analysis-notes.md#copy-descriptor-slots-and-zero-status-exit-boundary) and verifies it against **both** pinned EXEs. Earlier wording in this chapter left the final exit routine unresolved; that was broader than the available evidence. The audit now checks154 identical instruction bytes across these three ranges:

| Range, end exclusive | Role |
|---|---|
| `004f2a7d..004f2a84` | Clear EAX, call `004dfd04`; the meaningful zero-status entry sequence |
| `004dfd04..004dfd55` | Finalizer and downstream wrapper, with mutable hooks and conditional cleanup before tail-jumping to `004ff38c` |
| `004ff38c..004ff3ce` | Mode-dependent cleanup paths join at `004ff3c6`; push EBX and call imported ExitProcess at `004ff3c7` |

The audit asserts both binaries' IAT `005344c0` resolves to **ExitProcess**, and the final PUSH/CALL instruction bytes match. Under that API's ordinary contract the final call does not return. Provided preceding cleanup calls return normally, the inspected branch paths converge on that call; a visible epilogue after an earlier exit request is not evidence of a supported ordinary Boolean/working-value return.

This does not prove every invocation reaches the API promptly. Mutable cleanup hooks may block, terminate earlier or transfer control, and complete hook ownership/reentrancy is not validated here. The final argument is the value in EBX at the API call; preserving intended zero-status semantics through arbitrary modified callbacks requires their register/state contracts. Those limits concern pre-exit execution and status provenance, **not an unidentified final termination target**.

The seven-byte thunk range deliberately stops after its call. Existing research records that saved analysis extends the function through padding and copy-kernel jump-table data; those bytes must not be treated as executable continuation or a returning ABI. No Ghidra boundary was changed in this pass. The retained chain is shared, so the original/Modern diagnostic differences concern their admission/reporting/call sites rather than a newly introduced ExitProcess import or rewritten final exit primitive. No finalizer, callback, dialog or process-exit API was executed.

## Corruption-diagnostic callers supply zero or a language value

The audit now searches decoded direct-call instructions in the pinned original, checks all eight located targets against their raw relative CALL bytes, and asserts nine input-source instruction witnesses. This is a bounded decoded direct-call inventory, not proof that indirect calls or alternate instruction entry points do not exist.

| Callsite to `004b5e50` | Diagnostic EAX index on the inspected route |
|---|---|
| `004a3a69`, `004a3aa3` | 0: reached by TEST EAX / JNE fall-through |
| `004a3d62` | Explicit XOR EAX,EAX |
| `004a6f42` | Explicit0 after language-search exhaustion |
| `004b577c` | Explicit0 after renderer-name-search exhaustion |
| `004b5e38` | Saved incoming EDX (copied to EBX at renderer-initializer entry), then MOV EAX,EBX |
| `004b61be`, `004b61d1` | DWORD language global `007a3a50` |

Therefore the exhausted language index6 and renderer-search index11 are **not** passed directly into the six-entry diagnostic tables. Those failure routes explicitly choose0. The earlier local unchecked-index finding still matters for the three language-dependent routes, but it must not be presented as an inevitable out-of-range access just because the caller's search failed.

The [original language selector](original-modern-language-table.md#upstream-language-selection-installwin-becomes-ini-setting) compares six candidates and writes its successful index0..5 into the language global. Its exhausted route calls the verified exit chain with diagnostic index0 before the later apparent store. Under the established ordinary nonreturning exit contract, it does not proceed normally to publish6. Open failure and other writes to the global remain separate; this bounded producer does not prove the global always stays in range over the entire process.

Similarly, the original registry selector's exhausted search requests exit with index0 before the apparent store of its search result. Do not model either exit request as a normally returning diagnostic and then infer an invalid subsequent store as ordinary behavior. Pre-exit nonlocal callback behavior, all global aliases and indirect callers remain unverified. No caller or termination path was executed.

## Removed existing-window warning and embedded table

The expanded audit captures original helper **`004a38c0..004a38e2`**,34 bytes, and startup branch **`004a3a26..004a3a56`**,48 bytes. The helper passes class pointer`[005612a0]` and null window-title pointer to **FindWindowA**, resolved from original IAT`00534734`. A zero API result remains0; a nonzero result is normalized to1. The class pointer’s producer/lifetime and actual window matches are not established here.

Original startup tests that result. On nonzero it copies six DWORD pointers from **`004a3050`** into a local array, but then loads **only entry0** from`EBP-38h`. It passes that pointer, caption`0053ce54`, flags`30h` and owner value in EBX to **MessageBoxA**, resolved at`00534764`, then jumps to application tail`004a3f6c`. Entry0 reads **“Need For Speed is already running.”** The table also contains German/French existing-instance strings and three DirectX-related strings, all retained mechanically in the manifest; copying six pointers does not prove those other five strings are selected by this branch. No language index is used in the inspected selection.

Modern replaces this particular old-address48-byte startup branch with NOPs, but retains the check at a relocated caller as established below. This is replacement of the inline warning path, **not** removal of existing-window detection or permission to run multiple live instances. OS state and complete cleanup remain separate evidence.

The associated outside-body interval **`004a2ffc..004a3070`** is116 Modern NOP bytes. In original it comprises84 zero bytes, the24-byte six-pointer warning table, then eight alignment bytes. It is therefore misleading to call all116 bytes removed instructions: most were zero/data before patching. The audit asserts this partition and retains table pointers and strings. No window search, dialog, target code, Ghidra write or new instruction probe was executed.

### Modern counterpart retains detection and uses the common fatal helper

The complete34-byte FindWindow helper`004a38c0..004a38e2` is **byte-identical** in Modern. Its relocated startup call is`004a3e0c`; TEST/JZ bypasses the failure path on zero. Nonzero loads Modern text **`The game is already running.`** at`0053d02c` and calls common helper **`004b570c`**, then has a syntactic jump to application tail`004a3f6c`.

The25-byte helper`004b570c..004b5725` calls MessageBoxA with flags **`00051010h`**, caption`0053ce2c`, supplied text and owner0, then calls`004f2a7d`. The earlier retained-exit analysis establishes that target’s ordinary nonreturning path to ExitProcess; its pre-exit hooks remain unqualified. The syntactic caller jump therefore is not an ordinary continuation after that fatal helper. Original instead issues the inline MessageBox with flags30h and branches to its application tail. Message text, flag word and termination route change while the detector is retained.

The audit asserts helper equality and retains the relocated caller, text and fatal-helper bytes. This supersedes any inference that removing the old warning table or old-address branch removed duplicate-window admission. No OS detection, dialog or exit was executed; actual class-pointer state and complete shutdown remain unresolved.
