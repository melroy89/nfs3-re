# Incremental C reconstruction readiness

**Documentation audit and fixed reference-export sample complete; first maintained leaf functionally tested.** The named first module is the **line-boundary candidate leaf**, `00485c30`. This report establishes its investigation and comparison boundaries; it does not qualify the whole game to rebuild. The later authorized [two-run reference-export check](reference-export-results.md) exported only the three selected functions. The subsequent authorized [leaf reconstruction](line-boundary-reconstruction-results.md) adds maintained C, user-local MinGW tooling and standalone differential tests; full machine-state/game integration is not qualified. Existing scratchpad investigations remain independent work.

Evidence confidence is **verified** (direct inspection/retained observation), **inferred** (interpretation/proposal), or **unresolved**. Work status is **done**, **pending**, or **blocked**. A documented unresolved contract can satisfy this audit without satisfying a later reconstruction gate.

## 1. Baseline and reference-export procedure

The audit began at repository commit `a77ab226581481ea64e110b052b0f46f240f6b6f`; checkpoints `b7c0c80` and `e395426` preserve the initial report and signature corrections. [Readback evidence](evidence/audits/recompilation-readiness-readback.md) records final saved-state identity, body hashes, instruction/flow checks, imports, resources and limitations.

| Baseline property | Observed value |
|---|---|
| Executable | `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe` |
| Executable SHA-256 | `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb` |
| File size / PE target | 1,699,840 bytes; i386 `0x14c`; little endian; image base `00400000`; entry `004f7fa0` |
| Saved project/program | `nfs3_decomp.gpr` and matching `.rep`; logical `/Electronic Arts/Need For Speed III/nfs3.exe` |
| Ghidra | 12.1.4 PUBLIC; revision `8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc` |
| Java | OpenJDK 21.0.12.1 |
| Language/compiler specification | `x86:LE:32:default` / `windows` |
| Function inventory | 4,340 total: 4,133 local, including 36 thunks; 207 external |
| Data organization | pointer/int/long/float 4 bytes; double 8; Ghidra Windows `long double` 8 |

Confidence **verified**, status **done**. This is the local modified Modern Patch executable, not an unmodified retail baseline; see [target provenance](../docs/TARGET.md).

### Address manifest and current coverage

All intervals below are half-open. Function names are labels; the primary key is executable hash + address space + original entry VA. Preserve original VAs in every future reference artifact and maintained-function traceability record.

| Entry | Body end | Purpose | Current export status |
|---|---|---|---|
| `00485c30` | `00485f1b` | Module one; fixed repeatability sample A | Reference export succeeded in both runs |
| `004abd9c` | `004ac027` | Register/x87 signature check; sample B, not module one | Reference export succeeded in both runs |
| `00518640` | `0051868d` | Register/segment helper check; sample C, not module one | Reference export succeeded in both runs |
| `00485f20` | `004860a1` | Caller context only | Deliberately excluded from first sample/module |
| `004860b0` | `004862f5` | Caller context only | Deliberately excluded from first sample/module |
| All local entries except the three selected samples | Saved function body | Outside the three-address reference sample; includes the two caller-context rows above | Deliberately excluded: 4,130 local entries in total |
| 207 external entries | External address space | Import/interface inventory, not local implementations | Deliberately excluded from body export |

Actual reference-export counts: **3 successes per run, 0 failures/timeouts/cancellations; two runs, six successful attempts covering three unique entries**. Per run, 4,130 local and 207 external entries remain excluded. [Run manifests and warnings](reference-export-results.md) account for every selected sample. Thunks must retain their inventory identity rather than silently being counted as reconstructed bodies.

### Pinned reference-export procedure (executed for the fixed sample)

1. Close writers; take an isolated copy of the complete `.gpr`/`.rep` pair, following [snapshot guidance](../docs/SHARING.md). Verify executable and saved-database hashes. Open the logical program with `analyzeHeadless`, `-process nfs3.exe -readOnly -noanalysis`; the project argument includes `/Electronic Arts/Need For Speed III` after `nfs3_decomp`. Do not import/reanalyse the executable into a new default database.
2. Use Ghidra's installed `ghidra.app.util.exporter.CppExporter` (C/C++ exporter), with a **separate invocation for each manifest entry**, explicit `AddressSet(function.getBody())`, and that entry's original-address filename. Never pass a null selection: source inspection shows it selects all program memory. Validate selected entry/body hashes and reject unexpected selection/body overlaps.
3. Instantiate `DecompileOptions` with installed defaults, set default timeout **30 seconds**, C-style comments, and warning comments on. Supply these options explicitly to `CppExporter(options, true, true, false, true, true, "")`: header on, C on, whole-program datatype emission off, referenced globals on, tag-exclusion mode on with empty tag filter. With explicit options the supplied `DecompileOptions` comment style controls output; the exporter's GUI comment preference is bypassed. Record the serialized effective options and source/JAR hashes in the run manifest. Type definitions are a separately inventoried future artifact, not silently omitted from compilation requirements.
4. Before accepting an entry, inspect a same-options `DecompInterface.decompileFunction` result: completion, timeout/cancellation, error/warning message, and presence of a real function body. Then call the exporter and inspect its result/output. `CppExporter` can emit an “Unable to decompile” comment while returning success at the file level; a nonempty `.c` or boolean success alone is insufficient. An external **120-second per-entry process deadline** catches stalls outside the decompiler timeout. Preserve logs and partial output as failed evidence, never as a successful reference.
5. Use a per-entry ledger containing baseline/program/version/options digest, VA, body ranges and hash, role, output paths and hashes, elapsed time, decompiler/exporter outcomes, warnings and exclusion reason. Terminal states: success, failure, timeout, cancellation or deliberate exclusion. Keep not-run/queued distinct. Record each retry separately; do not overwrite failures. Each of the three selected addresses must reconcile to one current state, with attempt history retained. The exclusion set is defined by the frozen inventory digest and the explicit rule “all other local addresses, plus all external entries”; this does not require exporting the rest of the game. Any larger future export scope needs a newly enumerated address manifest.
6. Use generated reference paths `analysis/captures/reference-exports/<baseline>/<options-digest>/run-{1,2}/00485c30.{c,h}` (and the other two sample addresses). Maintained C, when authorized, belongs under a separate `reconstruction/` tree with its own hand-maintained address map. The reference tree exists for the fixed sample; the later authorized maintained leaf is separate under `reconstruction/`. Generated reference text is not maintained source and must never overwrite it.
7. From two fresh read-only opens of the same isolated snapshot, export samples A/B/C in ascending entry order into two empty run directories. Pin Java, locale, LF newlines, options, selection and headers. Compare raw SHA-256 and `diff` for **all six output files per run**, plus outcome/warning ledgers. Investigate every difference; do not discard changing globals/types/comments as harmless without explanation. Repeatability of these three bodies does not establish whole-game coverage or compilability.

**Resolved scope gate:** the documentation-only phase originally prohibited C export. The subsequent explicit reference-export authorization permitted only this three-function sample. Both runs succeeded and corresponding C/header/options outputs match byte-for-byte; see the [results and cleanup report](reference-export-results.md). Inline ABI/global-layout warnings remain reconstruction work, not export failures. No maintained C or compilation/linking/probe work was authorized or started.

## 2. Interfaces and register contracts

Saved custom storage now replaces misleading prototypes for the three requested/sample functions. It was independently read back after saving. See [contract evidence](evidence/audits/recompilation-readiness-readback.md#contracts-and-callers), the existing [geometry investigation](detailed-analysis-notes.md) and [original-byte probe](scripts/probe_line_boundary_helper.py).

| Address | Verified inputs and outputs | Preserved/hidden state and limits |
|---|---|---|
| `00485c30` | EAX candidate float2; EDX source line float4; EBX rectangle `[yMin,xMin,yMax,xMax]`; ECX zero/nonzero return policy; entry stack+4 points to BYTE mask. EAX returns shared float2 pointer or null; `RET 4`. Writes scratch and ORs mask bits, including possible writes before rejection. | ESI/EDI/EBP restored; EBX is volatile (BL/BH are changed on some paths), as are EAX/ECX/EDX. No documented flag result; EFLAGS are not preserved. x87 status/exceptions are observable but complete stack/status behavior outside the fixture's initialized FPU is unresolved. |
| `004abd9c` | EAX opaque vehicle; EDX mutable tyre-tuning float. No stack inputs; ST0 returns a binary32-rounded scale. Some session/race gates first write `1.0f` through EDX. | EBX/ECX/ESI/EDI/EBP restored; EDX unchanged locally; EAX contains incidental result bits, not a verified integer status. x87 status/EFLAGS not preserved. Saved `float10` ST0 models physical storage, not an original C `long double` declaration. |
| `00518640` | EAX destination; EDX source; EBX unsigned byte count. EAX returns original destination; plain RET. Overlap paths choose forward or backward copy. | ECX/ESI/EDI restored, EBX/EBP unchanged; ES temporarily receives DS and is restored. EDX's segment-selector result is not source preservation. Forward path assumes clear DF; backward path does STD then CLD. Exact arithmetic flags and all processor-dependent upper EDX bits are not a promised C result. |

All four tyre callsites (`004ac298`, `004ac54a`, `004ac567`, `004acaa0`) were revisited: EAX is vehicle, EDX is `[vehicle+220]+58`; consumers use ST0 directly or store it to binary32. The byte-move callers (`0052c2c8`, `0052c3a7`, `0052e9e8`, `0052eadd`) prepare EAX/EDX/EBX and use preserved ECX after return. These helpers are audit samples, **not dependencies of module one**.

Relevant leaf callers have explicit assembly-backed contracts, although their saved prototypes remain incomplete:

- `00485f20`: EAX input float4, EDX bounds float4, EBX output float4, ECX DWORD-mask pointer; no stack arguments; ESI/EDI/EBP restored. Clears the DWORD mask, passes its address to the leaf's BYTE-mask argument, and sets leaf policy 1 at `00485ff0`/`00486071`. Returns EAX 0 for acceptance, 1 for rejection. Output can be partly written before failure.
- `004860b0`: EAX input float4, EDX bounds float4, EBX DWORD-count pointer, ECX output capacity up to eight floats; no stack arguments; ESI/EDI/EBP restored. Returns EAX 1 for accepted processing, 0 for rejection; count 0/1/2 only on accepted paths. Calls at `004861cf`, `00486247`, `0048627e`, `004862cd` mix checked policy 1 and unchecked policy 0. Its local mask is uninitialized and unread by this caller; preserve this observation without copying an indeterminate C automatic read into a new implementation.

**Proposed maintained C interface:** a normal `__cdecl` test interface accepting three explicit float-array pointers, a `uint32_t` policy and a `uint8_t *` mask, returning the module's shared float-pair pointer or null. Retain the original shared storage identity and operation order. Do not add `restrict`, transactional writes, automatic mask clearing or a supposedly safer clipping policy. An original-register adapter is a separate later ABI artifact; `fastcall` and GCC `regparm(3)` do not express EAX/EDX/**EBX**/ECX plus callee-pop stack argument. Contracts are **verified / done** within the stated static/fixture scope; complete flags, alias and x87 admission remain **unresolved / pending**.

## 3. Function boundaries and control flow

Fresh saved-database inspection found the following contiguous instruction coverage. Branch targets stayed within each body except the listed direct calls; no indirect call/jump, external tail jump, jump table or cross-function tail sharing was found in these five bodies. No known incoming reference enters a body's middle from outside it. These are bounded database/instruction observations, not a promise that all possible indirect callers have been discovered.

| Entry | Bytes / decoded instructions | Direct callees | Observation |
|---|---|---|---|
| `00485c30` | 747 / 255 | None | All decoded blocks/branches accounted for; local merges at `00485f00`/`00485f13`; RET4 |
| `00485f20` | 385 / 157 | `00485c30` only | Two leaf calls; two local returns |
| `004860b0` | 581 / 237 | `00485c30` only | Four leaf calls; multiple local returns |
| `004abd9c` | 651 / 176 | None | Local branches and plain RET |
| `00518640` | 77 / 47 | None | REP copy loops and local returns |

The dispatcher around `004b4919` is **excluded and unresolved**. No dependency from this leaf or its two direct callers was found; dispatcher recovery is not a gate for this module or the three-address reference sample. Callback-target recovery is not applicable inside this leaf because it makes no calls. Larger HUD callers and rendering callbacks remain later integration work.

## 4. Data, layout and initialization

| Required object | Verified layout | Initialization/provenance and limits |
|---|---|---|
| Candidate input | Two binary32 values, offsets 0/4, extent 8 | Caller supplied; no local pointer/extent/alignment validation |
| Source line | Four binary32 values, offsets 0/4/8/12, extent 16 | Caller supplied; retain independent pointer identity even when it aliases an endpoint |
| Bounds | Four binary32 values in yMin,xMin,yMax,xMax order, extent 16 | Caller supplied; ordered/sorted/finite bounds are fixture assumptions, not enforced universally |
| Mask | BYTE read/OR/write, extent 1 | Leaf does not initialize it. Clipper caller clears a DWORD; fragment caller does not initialize its local byte |
| Shared result | `00791c08` and `00791c0c`, adjacent binary32, total 8 bytes | Ghidra `.bss.recovered`, uninitialized. No file-backed initial float values. Direct scratch references in the saved DB occur only in the leaf; indirect writes/aliases and whole-game startup initialization are not proved absent |
| Locals | Prologue reserves `0x1c` bytes; local binary32 stores impose rounding points | Stack lifetime, not persistent game state; preserve store/operation order |

These are arrays/scalars, not a recovered aggregate structure: no compiler packing pragma is needed for the first module. Unknown game structures remain opaque; the tyre sample's vehicle `+160`, nested pointer `+220`, and tyre value `+58` are offsets, **not a verified full vehicle/participant struct**.

Storage classes must remain separate:

- **File backed:** code, `.idata`, `.data`, `.reloc`, `.rsrc` in this snapshot; tyre constants at `0053dd4c..0053ddb0` are file-backed floats. No absolute file-backed constant table is referenced by the leaf.
- **Loader zero-filled:** PE `.bss` has uninitialized-data attributes `c0000080`, raw offset 0 and noncanonical size fields; Ghidra splits it into `.bss` and `.bss.recovered`. Zero initialization is the expected loader contract, **inferred**, not a fresh Windows-loader measurement. Do not read PE offset 0 as scratch initial bytes or claim that startup leaves the region zero. The retained ELF oracle explicitly seeds its scratch section with zero; that is a different verified initialization boundary.
- **Relocatable:** 29 PE `HIGHLOW` relocation records lie within the leaf body, covering its absolute scratch address operands. Original-instruction harnesses must preserve those VAs or apply/document relocation to a private copy; a future C global uses linker relocation instead. Do not import the raw original pointer immediates as arbitrary C addresses. No data/function-pointer table or callback is required by this leaf. Other game pointers remain out of module scope.
- **Startup/later writes:** leaf writes at e.g. `00485cb2`/`00485cc7` establish later scratch updates; callers initialize masks as described above. No separate startup writer was found through direct scratch xrefs, but indirect clears/copies are not excluded. Functional comparison must seed both implementations identically, preserve fixture order and compare rejected-call writes. The existing harness initializes scratch once, not before each row.
- **PE resources:** none is required by this leaf or its standalone test boundary. The game inventory contains icon IDs 100–105/200, icon groups `MAIN.ICO`/`ORIG.ICO`, RCDATA `ABOUT.QFS`/`SNAP.WAV`, version ID 1 and manifest ID 1, all language 0. [Resource table](evidence/audits/recompilation-readiness-readback.md#pe-resources-and-imports) records numeric types and names. These are inventoried resources, not proof that all are required at startup or by a later replacement component; preserve their IDs if that boundary is selected.

Confidence **verified** for sizes, database block state, direct references, PE attributes and relocation/resource records; **inferred/unresolved** for loader/startup/reentrancy generalizations. Layout documentation status **done** for this module; full game-data reconstruction remains **pending**.

## 5. Machine behavior needing explicit treatment

- x87 uses extended intermediates, binary32 spill/reload boundaries and `FNSTSW AX`/`SAHF` branches. The tested control word is `037f` (masked exceptions, extended precision, round to nearest). Do not replace branch-specific unordered predicates with a single mathematical comparison, erase stores, enable fast-math, substitute SSE arithmetic, or assume C `long double` matches the saved Windows data organization. Complete x87 stack occupancy/status and alternate precision/rounding/exception modes remain unresolved.
- Denominator magnitude bits are tested as a 32-bit integer (`& 7fffffff`), treating both signed zeros as zero and choosing a +0 slope. Preserve bits through defined byte-copy/bit conversion; pointer-punning a float through `uint32_t *` can violate C effective-type/alignment rules. Integer widths are explicit: 32-bit policy/address arithmetic, 8-bit OR mask. Do not allow integer promotions/sign extension to change masks or flags. No general signed wrapping arithmetic or variable shift algorithm occurs in this leaf; generated p-code's flag/parity operations are machine models, not recovered C source.
- x86 accepts unaligned scalar accesses; typed C dereferences require valid alignment and object representation. Either state aligned/nonoverlapping buffers as a bounded first test domain, or use byte-safe loads/stores and compare aliases before admitting them. Do not add `restrict` or reorder reads around scratch/mask writes without evidence. Float division by zero and signaling NaNs require a target/FPU contract; ordinary ISO C syntax alone does not promise original exceptions/status.
- Shared global scratch makes nested/concurrent calls potentially interfere. The original leaf contains no lock, atomic operation, save/restore of scratch or ownership protocol. A single-threaded serialized test preserves that boundary; per-thread/per-call scratch would change storage semantics. No in-game scheduler exclusion has been proved.
- `00518640` is a runtime/assembly sample: REP MOVS, carry propagation (`SHR`/`ADC`), DS/ES, and DF need an adapter/model, not unresolved decompiler pseudo-operations. Source+count is 32-bit wrapping; relational comparisons between unrelated C pointers and out-of-object pointer arithmetic cannot directly reproduce that. Standard `memmove` equivalence is bounded to clear DF, valid flat-address ranges and nonwrapping arithmetic. Do not silently repair wrapping behavior. GNU disassembly of raw bytes corroborated ES=DS; Ghidra's text operand ordering for segment MOVs is misleading here.
- `004abd9c` needs separately rounded reciprocal/multiply stages and exposes a write to tyre tuning. The x87 returned value is not evidence that the caller never observes EAX residue or flags; those dependencies remain unqualified outside the reviewed callsites.

No suspect original behavior was corrected. Policies, write-before-rejection, corner tie choices and invalid candidate witnesses remain original-compatibility questions. [Existing probes](scripts/README.md) establish only their tested original-instruction behavior.

## 6. First module, toolchain and dependency boundary

**First artifact (now built/tested):** a standalone 32-bit Windows console **test executable** containing the C leaf plus a comparison harness. It is not a DLL replacement, patched executable or running-game component. First acceptance scope: the ordered, finite fixture witnesses under CW `037f`, followed by the full retained 40-row fixture as separately reported exceptional coverage.

**Selected first toolchain:** GCC/MinGW-w64 targeting `i686-w64-mingw32`, C11, PE32, Windows **ILP32** data model (32-bit pointer/int/long, 8-bit bytes, binary32 float). Candidate baseline flags: `-std=c11 -O0 -g -m32 -march=i686 -mfpmath=387 -fno-fast-math -ffp-contract=off -frounding-math -fexcess-precision=standard`, no LTO. These are a proposal, not a sufficient equivalence recipe: explicit extended intermediates and binary32 stores must follow the instruction contract. Globally adding `-ffloat-store` can introduce extra rounding and is not a solution. GCC documents excess precision and rounding limits; see [x86 options](https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html), [optimization options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html), and [x86 calling attributes](https://gcc.gnu.org/onlinedocs/gcc/x86-Attributes.html).

At readiness audit time the cross compiler was absent. It has since been installed user-locally as the Ubuntu MinGW i686 POSIX compiler, package `13.2.0-6ubuntu1+26.1`; native GCC is 13.3.0. [The leaf results](line-boundary-reconstruction-results.md) record the selected flags/packages and actual standalone builds. Other toolchains/build modes remain unqualified. Assert type sizes, floating representation and selected long-double behavior in that future harness; MinGW long-double layout must not be inferred from Ghidra's 8-byte Windows `long double` setting.

Use an ordinary test `main` and the toolchain CRT for the standalone executable, with explicit FPU setup/restoration per comparison. Keep the C test ABI `__cdecl`; an assembly adapter must preserve harness ABI registers while deliberately loading the original EAX/EDX/EBX/ECX, pushing the mask pointer, and accounting for RET4. A test-only original-register adapter now exists for the Windows oracle. It is not a game-facing replacement adapter. Replacing a live game function would additionally require exact caller-visible preserved/clobbered state and flags, resources/startup/lifetime checks; that stage is not authorized here.

Maintained/test symbol map (implemented for this standalone slice): `Nfs3LineBoundaryCandidate_00485c30` is the maintained test function; `gLineBoundaryCandidate_00791c08` is a two-element binary32 global, with element 1 tracing to `00791c0c`; `CallOriginalLineBoundary_00485c30` is the future oracle adapter; `main` is new test startup with no original-game address. Keep the alias between both scratch elements. Link through the MinGW compiler driver's default CRT/Windows import libraries, with no leaf-specific libraries or resources. Basic arithmetic needs no game allocator, DirectX, WinMM or Winsock dependency; any actual compiler helper/libc emission must be recorded from the later object/import inspection rather than assumed absent.

| Dependency class | Module-one requirements | Later integration/context |
|---|---|---|
| Internal calls | None | Leaf's two callers, then HUD line/triangle emission and track map: `00485f20`, `004860b0`, `004873e0`, `00487a30`, `0048d4c0` |
| Data | Three caller arrays, BYTE mask, one shared 8-byte result | Caller count/output buffers and larger HUD/render state |
| Static imports | None in the leaf | Game PE: 207 imports across 10 descriptors/9 unique DLL names; standalone harness gets its own toolchain/CRT imports |
| Dynamic interfaces | None in the leaf | Existing static loader evidence: Thrash `004f84a8`; Glide loader `005043f0` resolves 58 names into `00a0a270..00a0a354`; resolver `004f1ebc` forwards module/export names |
| Callbacks | None in the leaf | Renderer submission/driver callback tables are outside scope |
| Assets/resources | None in the leaf; fixture JSON is test data | Game assets/PE resources must be preserved and selected by the later component boundary |

Dependency confidence: leaf requirements **verified**; proposed harness/toolchain **inferred**. Existing loader call/slot evidence establishes dynamically resolved interfaces, not universal live availability. A DLL filename found only in a string/configuration is **not** a confirmed dependency; do not automatically link every driver name. See the linked [detailed investigation](detailed-analysis-notes.md), [loaded renderer evidence](installed-renderer-capability-inventory.md) and [host/VM baseline](network-host-vm-runtime-baseline.md) for their distinct scopes.

**Proposed test stubs: none for module one.** Synthetic buffers, seeded storage and FPU setup are test inputs, not substitutions for game callees. Omitting the callers/game prevents validation of caller reachability, real buffer lifetimes, rendering, scheduling and gameplay. If later UI/allocator/driver stubs are introduced, list each by address and do not use stubbed runs to claim those omitted behaviors.

## 7. Behavioral comparison plan

Reuse the [40-case original-byte report](evidence/probes/line-boundary-helper-probe.json) and its [harness](scripts/probe_line_boundary_helper.py). It fingerprints 747 unchanged bytes, runs them at original VAs in a native Linux i386 ELF, and captures return pointer, scratch raw bits, mask, CW and SW. It uses no callee stubs. It does **not** capture preserved GPRs/EFLAGS or run either caller. The JSON field `accepted_pointer` means nonnull return, not geometric acceptance under policy zero.

The documentation-only phase inspected the retained harness without executing it. The subsequent [maintained-leaf tests](line-boundary-reconstruction-results.md) now execute both original and C: 304 native i386 rows and 40 Windows/Wine rows with exact functional matches. The Windows oracle uses a private, explicitly relocated instruction copy; both original runners reproduce all 40 retained rows including CW/SW. Status words differ from C, so complete FPU/ABI equivalence and game-facing replacement remain unqualified.

| Comparison group | Inputs/state | Required comparison / limitation |
|---|---|---|
| Existing ordinary witnesses | Horizontal/vertical/diagonal crossings; both policies; seeded mask `a0` | Exact null/storage identity, both binary32 result words, mask; no tolerance justified |
| Boundaries and degeneracy | Existing exact-edge, corner, signed-zero delta, zero-length, parallel and line-extension vectors; later all side/corner permutations | Preserve original branch/tie behavior and writes on rejection; direct leaf behavior does not establish wrapper reachability |
| Exceptional fixture rows | Existing NaN candidate coordinates and invalid/infinite result witnesses under masked CW `037f` | Compare raw NaN/zero bits, mask, return and relevant status; no generic epsilon or NaN-payload waiver without a justified reduced claim |
| Globals/output buffers | Scratch seeded once as original fixture; row order unchanged; mask reset each row; later add nonzero scratch seeds, sentinels and rejected-call sequences | Compare scratch even on null returns; verify caller arrays remain unchanged for nonalias inputs and no writes outside admitted buffers |
| Register/stack ABI | Sentinel ESI/EDI/EBP, plus ESP before/after RET4; record volatile GPRs and arithmetic flags | Extend harness before ABI claim; do not demand preservation of EBX. Record EFLAGS dependencies explicitly rather than treating C call flags as stable |
| Floating-point state | `FNINIT`, CW `037f` for baseline; snapshot CW/SW/TOP/tags and exceptions; later populated x87 stack and alternate precision/rounding modes | Existing report captures CW/SW only. Compare intended exception/status effects at the same observation point; exact stack/state claim remains pending |
| Aliasing/alignment | Future directed candidate/line/bounds/mask/scratch overlaps and unaligned valid storage | Excluded from initial aligned, nonoverlapping test scope; preserve ordering and byte access before extending scope |
| Reentrancy/integration | Later nested/concurrent calls, wrappers and actual HUD path | No concurrency or game/render claim from a serialized leaf harness; requires separate admission and integration evidence |

The first C harness should report every row, not just the selected finite assertions in the old script. Distinguish a finite functional pass, full fixture pass, machine-state pass and in-game integration pass. Compiler transformations may change x87 condition bits/status even when output floats match: either reproduce the required state or narrow and justify the claim based on caller use. Do not hide discrepancies behind a tolerance.

## 8. Staged readiness and prioritized blockers

The documentation deliverables, fixed-sample export and standalone leaf compilation/linking are **done**. Functional differential validation passed within its stated scope; complete machine-state and game integration qualification are not done. Priority is dependency order for this module, not a severity rating for the game.

| Priority / address | Evidence and required action | Confidence | Work status | Affected stage |
|---|---|---|---|---|
| 1 — sample `00485c30`, `004abd9c`, `00518640` | Two same-baseline runs succeeded; all six C/header files and three options files match. Coverage, inline warnings and cleanup are recorded in the [results](reference-export-results.md) | Verified for this sample/configuration | Done; all other entries remain excluded | Reference export |
| 2 — `00485c30`, `00791c08/0c` | Maintained C uses explicit types, shared scratch, binary32 stores and extended intermediates; scoped functional cases pass. Alias/FPU-state expansion needs separate evidence | Verified scoped implementation/test evidence | Done for first O0 leaf; broader semantics pending | Module compilation / expanded runtime validation |
| 3 — `00485c30` test boundary | User-local MinGW packages/flags recorded; ILP32 static assertions and standalone Windows/i386 compilation pass | Verified selected build | Done for the recorded configuration | Module compilation |
| 4 — `00485c30` adapter / `004f7fa0` game entry | Standalone PE main/CRT, scratch and original-register oracle adapter linked and executed; game startup/replacement ABI remains outside this artifact | Verified standalone link/execution | Done for test executable; game integration pending | Linking |
| 5 — `00485c30` fixture | 304 native and40 Windows/Wine rows match return/scratch/mask/input/CW checks. SW condition bits differ; resolve caller-required flags/tags/state before replacement | Verified functional scope, unresolved full machine equivalence | Functional pass; full state/integration pending | Runtime validation |
| 6 — `00485f20`, `004860b0` | Contracts known, prototypes still incomplete; retain uninitialized unused-mask and nontransactional-write caveats. Recover complete caller domains/alias/state before expanding module | Verified bounded static evidence; full domains unresolved | Pending, not a leaf compilation prerequisite | Module compilation / runtime validation of caller module |
| 7 — `00791c08/0c`, PE `.bss` | Inspect actual Windows loader/startup and indirect writes if global initial state matters beyond controlled tests; establish serialization/lifetime before game integration | Inferred zero-fill; unresolved indirect initialization/concurrency | Pending, not a controlled-fixture prerequisite | Linking / runtime validation of game integration |
| 8 — `004abd9c`, `00518640` | Custom storage fixed and read back; preserve x87 rounding/writeback and segment/DF/wrapping contracts if later chosen as modules; add dedicated comparisons then | Verified static contracts; full machine behavior unresolved | Done for signature audit; pending for reconstruction | Their future module compilation / runtime validation |
| Deferred — `004b4919` | Separate dispatcher recovery; no leaf dependency found | Unresolved | Pending outside this module | Only a later stage that proves a dependency |

| Stage | Current evidence | Gate decision |
|---|---|---|
| Reference export | Two successful three-address runs, matching source/header/options hashes, pinned baseline/configuration and accounted omissions/warnings | **Passed for the fixed sample only:** no whole-program or compilability claim |
| Module compilation | Maintained leaf and selected GCC x87 types/flags compiled in native and Windows i686 test builds | **Passed for recorded O0 configurations only** |
| Linking | Standalone Windows PE and native i386 harness linked with separate original/C storage and oracle adapters | **Passed for tests:** no game-link compatibility claim |
| Runtime validation | C and original executed on both targets; exact functional checks and explicit SW differences | **Functional scope passed; complete state/game integration not qualified** |

### Documentation-phase acceptance check

| Handoff item | Acceptance | Later-phase limit |
|---|---|---|
| 1. Baseline and export procedure | **Complete:** exact target/snapshot, exporter/options, address manifest, omissions and repeatability procedure recorded | Two-run check passed for only the three selected references; no whole-program export claim |
| 2. Signatures and register contracts | **Complete:** three custom signatures saved/read back; relevant callers and hidden-state caveats recorded | Complete flags/x87/alias domains and caller prototype recovery remain scoped follow-ups |
| 3. Boundaries and control flow | **Complete:** five contiguous bodies, direct calls and known references inspected | Unrelated dispatcher and broader indirect-call discovery remain outside this module |
| 4. Data, layouts and initialization | **Complete:** required arrays/scratch/mask, storage classes, relocations and resources distinguished | Actual loader/startup indirect writes and game resource necessity remain unresolved |
| 5. Machine behavior | **Complete:** x87 rounding/status, widths, masking, alias/alignment/UB and shared-state risks identified | A supported C expression/type model and expanded machine-state comparisons remain pending |
| 6. Module and build boundary | **Complete:** leaf00485c30, dependency/symbol map, standalone test artifact and ILP32/ABI proposal defined | Recorded MinGW O0 standalone configuration now passes; other configurations and game ABI remain pending |
| 7. Original-versus-C comparison | **Complete:** retained 40-row oracle, exactness policy, additional cases and stub limits documented | Scoped C/original differential execution now passes; complete state and integration remain pending |
| 8. Staged readiness report | **Complete:** blockers have evidence, action, confidence, work status and affected stage; saved Ghidra readback recorded | Reference export, compilation, linking and runtime qualification are separate future gates |

The follow-up review corrected the ILP32 label without changing the already-correct pointer/int/long sizes. Independent report/source review found no additional contract or evidence inconsistency. The separately reported read-only Ghidra review confirmed all three custom signatures, saved comments and 4,340 entries; current file hashes also match the retained evidence. No additional Ghidra mutation was justified. See the [follow-up evidence record](evidence/audits/recompilation-readiness-readback.md#follow-up-handoff-review).

### Current implementation follow-up

The three-reference export and first standalone leaf implementation/testing steps have been carried out; see [the leaf results](line-boundary-reconstruction-results.md). The [static caller audit](line-boundary-x87-callers.md) found no direct use of the differing C0/C2/C3 bits at six known callsites, but proved return-state propagation and stopped at identified render/transform boundaries. The next gate is to follow those specific boundaries before clearing caller-required machine-state/ABI behavior; flags/tags, admitted aliases/FPU modes and actual game integration remain unqualified. No unrelated dispatcher, multiplayer or controller investigation is a prerequisite for this bounded module.

Only `00485c30` is maintained C. `004abd9c` and `00518640` remain reference samples. The original executable remains unchanged. Current Ghidra type/comment checkpoint is documented separately from the immutable pre-export `db.3144` baseline in the leaf evidence; do not substitute its hash when reproducing the old export runs.

The later [three-baseline sample audit](original-modern-reconstruction-baselines.md) verifies that all three selected instruction bodies also match the supplied original and official Modern files, including the leaf relocation sites and selected tyre constants. It does not broaden the existing test or integration claims.
