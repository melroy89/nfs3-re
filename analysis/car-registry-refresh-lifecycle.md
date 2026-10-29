# Car registry refresh and selector lifecycle

## Scope and artifact

This audit follows ordinary registry discovery, transferred-car completion, marked-car cleanup, and the subsequent index-cache and selector-group refreshes. It does not revisit the registry, cache, or group capacity questions.

The inspected executable is the installed active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Analysis was read-only and the REA binary session was closed after inspection. No executable, configuration, runtime, or persistent Ghidra project was changed.

## Refresh contract

`ClearCarModelIndexCache` (`004399f0`) is a thin wrapper around the memory-fill helper. Its body sets `EAX=005f3c00`, `EBX=0xc8`, and `EDX=0` before calling `004e0640`; this clears exactly 200 bytes, or 50 DWORD pointer slots. Evidence: `ev_fb7ebb025ee6356900f00227935095bce51225298c9a49ca679d1699cd6570e3`.

`DiscoverAndLoadCarModelRegistry` (`00439d90`) calls this reset at `00439d9e`, then recounts and scans installed model sources. It appends accepted records to the linked list. At the end, it calls `RebuildEligibleCarModelGroups` (`0043a580`) at loader callsite `0043a49c` and then performs its final uniqueness/setup helpers. Thus a successful complete discovery pass invalidates the ordinal-to-record cache before population and rebuilds selector groups after population. The direct loader instruction evidence is `ev_0b87d8f0b2f0b9ea93f8a81bb01aad702a46c94d6e8956ebfa5b1ba3ed4f081c`; the existing same-artifact loader dossier is `ev_d839de47b9f466a5fb4d8c17222972c3b5d2871735a13217dd6a704ff23d590c`.

Before selector repopulation, `RebuildEligibleCarModelGroups` zeroes the 800-byte block at `005552d8` and the 16-byte count block at `005555f8`. It then filters the current registry and sorts the four groups. The relevant bounds and writes are visible at `0043a595–0043a5b1` and the group appends at `0043a5b6–0043a62c`; no group-cache state is carried across this rebuild. Evidence: `ev_3dd5f4e2b00e7f36caa65e8bb815e1ee85faabeb6ca8433c5c6432c89d9de943`.

The separate list-order helper `GroupAndSortCarModelList` (`00438eb0`) first resets the same index cache, partitions/relinks the existing list, and publishes the rebuilt head at `00554f70`. It does not itself call the selector-group builder. In the normal discovery sequence this is followed by the loader's later call to `0043a580`, so the group arrays reflect the post-ordering list. Evidence: `ev_354d82b6ec35f6249087572f41d6cef931bb757bf2b7204e4efc803c51c9b7f9`; the existing helper analysis is recorded in `detailed-analysis-notes.md` under “Car registry cleanup and ordering helpers.”

## Append, completion, and removal paths

- **Ordinary discovery:** Initialization routine `004b5c00` calls the loader at `004b5cfb`, checks its result, and then reads the registry count. The loader owns both cache invalidation and selector-group rebuild; the initialization caller does not need a second explicit group rebuild. Evidence: `ev_0b87d8f0b2f0b9ea93f8a81bb01aad702a46c94d6e8956ebfa5b1ba3ed4f081c` and `ev_eeb8cf8fcbe27d46571a4ef0390692cc94f11ca8c4e8e7fe7811411ae91a3783`.
- **Received-car completion:** The active control-handler table at `0055ecbc` maps types17/18 to `0049b470`/`0049b520` (slots `0055ed00`/`0055ed04`). Type18 wrapper `0049b52a` calls `AppendCarResourceTransferData` (`0049b5f0`) with shared state `0055e5bc`. Its completed memory-stage branch performs file/Carp metadata work, reloads the registry at `0049b7c7`, calls identifier/display/flag setters `0043bc00/40/70/90`, then reloads again at `0049b7ef`. Those reloads reach the same cache/group rebuild contract. Discovery returns are not checked before the setters, so actual success and the intended last-discovered target remain qualified. This is the established active static receive route; the older `UpdateCarVivArchiveAndRefreshRegistry` body (`0043ae60..0043b29c`) still has no established ingress and is not required to explain these calls. No live transfer or filesystem mutation was executed.

- **Marked-car cleanup:** `0043b390`, called by `004730d0`, walks the linked list. For records whose flag byte at `+0x380` has bit `0x08`, it unlinks the record and passes it through the record cleanup/release calls; otherwise it advances. After traversal it calls `0043bcf0` and then `DiscoverAndLoadCarModelRegistry` (`0043b3dd–0043b3e2`). Consequently the cleanup path also reaches the cache reset and selector rebuild by reloading the registry after removals. Direct instruction evidence: `ev_40560edb31a8df9def193dabb68de5e45bd4da632b47692035bfe2aed6184c83`; caller/ordinary setup context: `ev_141481d6381e21d6ada2ea280ff4ef2798e28021b78a73a2b827716fbefa9fcc`.

The received-car completion branch and marked-car removal helper are not established as a single transaction. Static code shows their effects and refresh calls, but not how higher-level event dispatch orders them against the selector UI or any in-progress race setup.

## Race setup and re-entry

The normal race-setup entry `00474ca0` calls `RebuildEligibleCarModelGroups` at its entry, before `BuildRegularRaceRoster` or the other mode-specific roster builders. `004a3690` calls this setup entry when its guards allow the setup path. Thus re-entering this race-setup path rebuilds selector groups from the current registry, even when no discovery occurred between entries. Evidence: `ev_de3e65f7d404ded9bd5dea65d0935cec7442a7750494e475b475aa8a05cb053b` for `00474ca0`, and `ev_f449098573c10470c3841299fb90065da465460befcd98a861aa6580f7d91b24` for its caller.

This establishes refresh on initial discovery, on the observed transfer/cleanup reload paths, and on race-setup entry. It does not establish that every generic frontend screen return re-enters `00474ca0`, or that the selector is redrawn synchronously after a transfer callback. Those caller-order details require the indirect event/dispatch path or a controlled UI trace.

## Remaining evidence gaps

1. The active received-car handler chain is established statically, but ordered delivery, successful phase completion and file operations have not been observed. The separate older updater at0043ae60 still has no established ingress.
2. The exact ordering between a completion callback, menu redraw/re-entry, and a concurrently active setup path is unknown.
3. No runtime observation was made of cache contents, group counts, or visible selector updates after add/remove operations.

These gaps limit caller-order and visible-UI claims; they do not alter the statically observed reset/reload/rebuild sequence.

Parent instruction review corroborated discovery cache-reset call00439d9e, ordering0043a34a, group rebuild0043a49c, cleanup reload0043b3e2 and race-setup rebuild00474cb3. Current name004399f0 is ClearCarModelIndexCache. The active receive/completion route was subsequently corroborated via the packet table, wrapper and exact reload callsites above; no runtime selector refresh was observed.
