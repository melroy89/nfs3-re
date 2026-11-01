# Historical nGlide windowed-mode claim: component and PE-header boundary

**Confidence: verified package/header bytes. Work status: partial for MP153-007; regression mechanism unresolved.** The [audit script](scripts/audit_nglide_window_history.py) pins the author-hosted1.5.2/1.5.3 archives, reads three nGlide members into memory, and compares complete files. The [manifest](evidence/audits/nglide-window-history.json) retains both archive hashes, all six member hashes, every differing adapter-file offset and PE fields. This is a historical Modern package comparison, not retail-original correspondence.

## What changes and what stays identical

| Component |1.5.2→1.5.3 result |
|---|---|
| `drivers/nglide/thrash.ini` | Entire166-byte file identical |
| `drivers/nglide/glide3x.dll` | Entire1,425,408-byte provider identical |
| `drivers/nglide/voodoo2a.dll` | Both69,120 bytes; exactly seven changed bytes, all in PE headers |

Adapter changed file offsets are **`d8,d9,104,105,158,159,15c`**. Section headers/layout and all actual file-backed section payloads match, including code, import bytes, initialized data, exports, relocations and resources. Unbacked sections are recorded without interpreting file offset0 as their payload. Complete-file comparison also excludes hidden trailing differences outside the sections.

## Exact adapter header changes

| PE field |1.5.2 |1.5.3 |
|---|---|---|
| Optional-header checksum | `000112cf` | `0001ee97` |
| Import directory RVA | `0000e000` | Same |
| Import directory size | `000006e4` | `0000003c` |
| IAT directory RVA |0 | `0000e174` |
| IAT directory size |0 | `000000fc` |

The manifest also records independently computed PE checksums; it does not treat a checksum as a signature or authenticity proof. The directory bytes themselves lie in unchanged section payloads. Their **descriptive header ranges change**, so code-byte equality must not be promoted into identical loader behaviour. Conversely, these field changes alone do not demonstrate that Windows/Wine processes them differently in the failing scenario.

## Attribution and next action

MP153-007 advertises a fix for a1.5.2 nGlide windowed-mode regression. This comparison excludes a provider-binary update, a thrash.ini edit and an adapter code/payload rewrite in these three package members. It identifies a concrete adapter PE metadata delta but **does not establish it as the cause or fix**. The initial component pass did not compare the game EXE; the follow-up below now identifies a concrete EXE-side mode-publication change. Other package members remain outside scope.

The initial next action was to compare matched1.5.2/1.5.3 EXE windowed-mode admission/setup routes against existing [window handling](original-modern-window-handling.md) and [renderer lifecycle](original-modern-renderer-lifecycle.md) evidence. If static traces leave the header's role unresolved, a separately scoped loader/window test would be needed for a behavioural claim. Do not patch/rebuild either DLL or infer that the advertised regression never existed.

The catalog entry becomes **partial package/header evidence**, not a verified windowed-mode repair. No DLL, EXE, Windows loader, API, instruction probe or Ghidra database was executed or modified.


## EXE mode publication changes to selected-dimension centring

The extended audit extracts `nfs3.exe` from each same pinned archive, retaining executable hashes, complete mode-application bodies and three complete sizing helpers. The bodies are **1.5.2 `004beeb0..004bef9f`** (239 bytes) and **1.5.3 `004beeb0..004bef8f`** (223 bytes). This historical comparison is separate from final's later mode refactoring.

At the shared publication point, the call policy changes:

| Reached publication path |1.5.2 |1.5.3 |
|---|---|---|
| Byte`00564390` bit0 clear | Load selected record width/height, call`004cdbd0` at`004bef4c` | Same dimension inputs, call`004cdbd0` at`004bef43` |
| Bit0 set | Call`004cdc20` at`004bef53` instead | No local flag test; use the same selected-dimension call |

The old26-byte branch region `004bef3e..004bef58` becomes a10-byte load/call sequence `004bef3e..004bef48`. Both new-mode-success and already-current-mode paths can reach this publication point; this does not claim that failed mode requests or every function invocation reaches it. The selected record pointer and dimensions must remain valid.

Three helper bodies are **byte-identical across the historical pair**:

- `004cdb10..004cdbcd` (189 bytes): rectangle/style adjustment, SetWindowPos request and client-geometry publication.
- `004cdbd0..004cdc14` (68 bytes): uses screen metrics0/1 and supplied width/height to centre the requested rectangle, then calls the first helper.
- `004cdc20..004cdc4c` (44 bytes): requests origin0 and full metric width/height through the first helper.

The GetSystemMetrics import is verified for both EXEs. The [existing sizing-helper investigation](original-modern-window-geometry.md#three-complete-sizing-helpers-are-unchanged) documents formulas, integer-width/API-result limits and original/final correspondence; here the retained historical bodies verify that the difference is a **caller policy**, not a rewritten centring formula.

This is a concrete candidate mechanism for avoiding a desktop-sized request where a provider is operating in a window:1.5.3 always supplies selected-mode dimensions on this publication path. That interpretation is an **inference**, not proof that nGlide was selected, that its windowed setting was active, or that this call was the sole regression repair. The separate adapter-header changes remain recorded rather than assumed harmless.

**Resolved:** the previously missing EXE-side difference in this selected mode-publication route. **Pending:** driver/window-mode admission, complete input-pointer/state invariants, header loader effects, actual window dimensions and a reproduced1.5.2 failure/1.5.3 recovery. MP153-007 remains partial. No window, driver, API or target instruction was executed.


## Sizing flag producer, later toggle and mode-request order

The extended audit captures and asserts equality for both historical versions' `WindowedMode` reader witness `004b56e3..004b56f6`, normalized producer **`004b5bd1..004b5be3`**, and complete42-byte toggle **`00517d70..00517d9a`**.

The reader names key`WindowedMode` at`0053edd8` and stores its result at`0067900c`. The setup producer loads that value, TESTs it, SETEs AL and zero-extends AL before writing`00564390`: **WindowedMode0→flag1; nonzero→flag0**. This is a verified local value relationship, not proof that no config/load or later function overwrites it.

At its original1.5.2 publication consumer, flag0 already selected the requested-dimension centring helper; flag1 selected desktop dimensions.1.5.3 unifies both cases to requested dimensions. Therefore the local behavioural difference affects the **flag1 branch**, not every invocation configured with nonzero WindowedMode. Explaining the advertised nGlide regression may require provider window configuration or other state distinct from this game's flag. There is no nGlide-name check in this changed block, so it must not be reconstructed as a provider-specific conditional solely from the release-note wording.

The retained toggle reads the byte at`00564390`, XORs bit0, stores it, then calls`005089d0` with current width/height/depth globals. This establishes a later direct writer, without proving that the toggle is invoked or that its callee succeeds. Startup's normalized assignment is not a whole-lifetime invariant.

Both captured mode-application bodies also retain their ordering distinction: equal current/selected index jumps directly from`004beed7` to the publication point; a different admitted index calls slot`009ef958` at`004bef1b` and tests its result before publication. Thus the changed centring call is **after** a successful new-mode request in this historical path, and also reachable without a new request on the same-index path. Final's separately researched mode-preparation refactoring must not be retroactively assigned to these historical bodies.

This closes selected flag-producer and ordering questions. Full runtime driver/provider window settings, other flag writers, callback effects, selected-record lifetime, header metadata behaviour and regression reproduction remain unresolved. No setting, window, driver or target instruction was changed or executed.
