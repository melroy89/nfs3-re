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

Original low-memory and disk warnings call MessageBoxA with flags31h and select text/caption pointers through the incoming index. Return2 leads to `004f2a7d`. Modern routes both through **`004b5728`**, which uses flags51031h and a shared caption, calls the same termination helper for return2, otherwise returns. The desktop-depth failure uses separate **`004b570c`**, flags51010h, followed by `004f2a7d` regardless of dialog result. Complete termination behavior/nonlocal exit guarantees are not established here.

## Added desktop-depth check

After the resource checks, Modern calls **GetDesktopWindow**, **GetWindowDC** and **GetDeviceCaps** with literal index12, then uses signed comparison against8. A result below8 invokes the fatal-diagnostic path with **“Cannot run if desktop bitdepth is less than 8.”** The manifest identifies the imported APIs at the actual IAT operands. The original counterpart returns after the disk warning and has no corresponding desktop-query sequence in that body.

This branch checks the returned capability directly; it does not multiply by a second planes capability, verify a renderer-supported game mode, or prove movie decoding compatibility. The local routine contains no ReleaseDC call; ownership, other cleanup or actual resource leakage is not established by that bounded observation.

## Register and reconstruction boundaries

Modern uses PUSHAD/POPAD, preserving the incoming general registers including EAX when its ordinary path returns. It does not provide an ordinary Boolean success result. Original saves EBX/ECX/EDX/ESI/EDI/EBP, consumes incoming EAX as its diagnostic table index and leaves an operation-dependent EAX result. The two should not receive one guessed C success-return signature.

Verified changes include memory-sum order/units, warning selection and flags, removed local logging and the added desktop check. Historical attribution, full localization fallback, resource API failures, directory selection, termination and observed startup acceptance remain unresolved. This is an independently documented code delta, not a claim that every system-requirement path in either executable has been compared.

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

After the dialog, the return value is **not tested**: execution calls `004f2a7d` unconditionally. That seven-byte thunk clears EAX and calls `004dfd04`. The captured downstream body invokes indirect hooks and routes through `004dfd30` toward `004ff38c`. This establishes an unconditional termination-route request after the diagnostic, but the callbacks and final exit routine remain outside the complete nonreturn proof. Do not declare an ordinary success/failure return based on the visible epilogue after the call, or mark the function nonreturning solely from intent.

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

1. It copies the11-byte template `C:NFS3.EXE` (including its terminator), calls path helper `004f9390` with literal `install.win`, extracts a drive index through `004f93f0`, then calls drive probe `004f9410`. The complete path-construction contract of `004f9390` remains unresolved.
2. The drive probe constructs a drive-root string, calls imported **GetDriveTypeA** via IAT `00534518`, and accepts only literal return5. If the first installation-path drive is accepted, the admission helper displays a language-indexed message saying the game must first be installed, then calls `004dfd04` with EAX0. Message tables have six entries; the global index is not locally bounds-checked.
3. If the `remote` prefix helper returns nonzero, it takes the ordinary return without scanning further drives.
4. Otherwise it scans drive indices0..25. For each accepted drive type it changes the template's first byte to `A + index` and passes it to resource/path helper `004f0330`. A nonzero result exits the scan successfully. The string is **drive-relative** (`C:NFS3.EXE`), not `C:\NFS3.EXE`; reconstructing it as a root-absolute path would change semantics.
5. Exhaustion displays the second six-entry table's message requiring the game CD in the CD-ROM drive, then calls `004dfd04` with EAX0. The same callback/nonreturn limitations as the earlier termination-route discussion apply.

The drive-type wrapper is statically tied to its actual import; the diagnostic wording and scan establish an installation/media admission role. They do **not** establish what every path/resource helper verifies, authentic media identity, successful asset access or the complete original protection mechanism. The helper preserves its six saved non-EAX registers on an ordinary return, but does not provide a defined success Boolean to startup.

This closes classification of these two original entries inside the large removed startup span. Precise path-helper contracts, global-source ownership, other callers and Modern replacement policy remain follow-up work. No drive was scanned and no file, CD or game API was invoked by this audit; executable bytes and saved Ghidra state remain unchanged.
