# Network service selector crosswalk

## Scope

Static review of active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows the `0049f200` catalog callback, service-row fields, connect-menu selector checks, and the selected-build protocol-table registration already documented in `detailed-analysis-notes.md`. No external service, runtime, config/executable write, or persistent Ghidra edit was used. Shared initializer helpers `004f63d0` and `004f7830` were not re-investigated; their detailed provider semantics remain with the parallel review.

## What the connect menu calls selectors

Active connect-menu initializer `004405c0` calls `0049e360` with EAX values 3, 1, and 2 before applying disable bit `01` to RaceNet, IPX, and TCP items respectively. In each case, a found selector causes the corresponding item to avoid the disable write; thus the local UI treats:

| Selector | Menu item whose disabled flag is conditionally applied |
|---:|---|
| 3 | `racenet` |
| 1 | `ipx` |
| 2 | `tcp` |

This is a UI availability association, not a proven transport enum or network-provider identity. `0049e360` scans `g_nServiceCatalogRowCount` at `0055e718`, comparing each DWORD selector at `0055e734 + 0x2c*i`. If not found it invokes `0049f150`, then scans again. The catalog row base is `0055e724`; selector offset is `+0x10`, and row stride is `0x2c`.

## Catalog producer and observed row labels

`0049f030` clears the row count and calls candidate iterator `004f4c70` with callback `0049f200`. The iterator visits entries in registered candidate arrays at `009f25b0` and companion contexts at `009f25d0`, count `00566de4`. For candidates taking the supplied callback path, `004f4c70` passes the companion context's first DWORD in EDX and a pointer to its following metadata in EAX. `0049f200` uses the EDX value as the candidate-name string and copies 16 metadata bytes from EAX to row `+0x18`.

Within `0049f200`, the ordinary path (candidate name does not contain the literal `DirectPlay`, at `0053c6e4`) stores selector `1` at row `+0x10` and copies the candidate name into the row's leading 15-byte name field. On the DirectPlay path, it checks for `IPX` (`0053c6d4`) and `TCP` (`0053c6d0`) and selects the corresponding display label `DirectPlay IPX` (`0053c6f0`) or `DirectPlay TCP` (`0053c700`). This procedure itself visibly writes selector `1` on the ordinary-name path; it does not write selector `3`.

After the candidate callback enumeration, `0049f030` checks DWORD `0055e720`. When nonzero, it appends a row with selector `2` at `0049f080`, copies the fixed label `TCP` (source `0053c6d0`) into the row's leading name field at `0049f0a7–0049f0b1`, and copies a fixed 16-byte metadata block from `0055e878` into row `+0x18`. The adjacent initialization path calls `004f7830` with `TCP gather` (`0053c6d8`); parent review identifies this as the producer that sets `0055e720`. Thus selector `2` is associated with the synthesized TCP catalog row, matching the TCP menu item. Do not infer more about the gather helper's provider semantics than that reviewed producer link supports.

The selector field's only direct immediate stores in the reviewed builder are selector `1` in `0049f200` and selector `2` in `0049f030`. Parent review further connects the IPX companion name `IPX`, supplied through the `0049f150` initialization path (`004f63d0`), to the ordinary candidate callback and selector `1`. This matches the IPX item gate. I found no selector-3 store in these two functions; its RaceNet-gate producer remains unresolved outside this catalog path, not excluded everywhere. The visible active connect initializer also contains no RaceNet callback assignment, as recorded in [connect-menu-dispatch-crosswalk](connect-menu-dispatch-crosswalk.md).

## Registered provider descriptor boundary

The candidate iterator obtains provider descriptor pointers from `009f25b0` and companion-state pointers from `009f25d0`. A separate registration site at `004f6422–004f6441` registers protocol operation table `005689e8` into `009f25b0[index]`, companion table/context `00566e24` into `009f25d0[index]`, and updates candidate count `00566de4`. The operation table contains function pointers including constructor `00514650` at `+0x1c` and callback `00514f70` at `+0x40`; its `+0x40` relationship and hosted-player setup are documented in the detailed notes. This establishes a concrete registered protocol descriptor in the candidate registry.

The catalog callback classifies the companion-context name and metadata, while the registration site places an operation-table pointer in the parallel descriptor array. The inspected code does **not** establish a one-to-one mapping from the `005689e8` descriptor to selector `1`, `2`, or `3`, nor identify the external provider identity behind every candidate. The names `DirectPlay IPX` / `DirectPlay TCP` are catalog labels/literals, not proof that a Microsoft DirectPlay DLL is imported or that it is the active network backend.

## Supported conclusions and remaining questions

- Selector 1 is produced for ordinary provider-name rows. In the reviewed IPX initialization chain, companion name `IPX` reaches this ordinary-name path, matching the IPX menu gate. Other candidate identities depend on their registered context strings.
- Selector 2 is synthesized conditionally by `0049f030` with fixed catalog name `TCP`; the connect menu uses it to gate the TCP item. The adjacent `TCP gather` initializer is linked to the readiness flag that enables this row.
- Selector 3 gates the RaceNet item, but the reviewed catalog producer/callback does not create selector 3. Its producer may lie elsewhere; no identity is established here.
- The binary registers at least one concrete protocol operation table (`005689e8`) into the generic provider candidate registry. Association of that table with specific catalog rows/selectors is not proven by these local paths.
- The exact external/system implementation behind the provider candidate registration and current provider availability remain outside this static audit. The reviewed `004f63d0` IPX companion-name link and `004f7830` TCP-gather readiness link are incorporated from the parent review; their wider helper semantics are not expanded here.

## Evidence anchors

All instruction addresses above were checked with bounded `objdump -d -Mintel` ranges in the active selected PE. Relevant ranges: `004405c0–0044072e`, `0049e360–0049e3cb`, `0049f030–0049f141`, `0049f150–0049f1b7`, `0049f200–0049f376`, `004f4c70–004f4d03`, and `004f6422–004f6441`. The string literals at `0053c6d0`, `0053c6d4`, `0053c6d8`, `0053c6e4`, `0053c6f0`, and `0053c700` were decoded from the active PE's `.data` section. Exact label tests call substring helper `004e0820`; names are only accepted as producer inputs, not treated as validated OS/provider registrations.

Parent instruction/data review corroborated the selector/name chain and corrected the preliminary label transcription:0049f0a7 loads0053c6d0 (TCP), while0053c6f0 is the distinct DirectPlay IPX literal. Parent recovered AppendEnumeratedNetworkServiceRow0049f200, saved its callback/row-layout comment, and retained the special DirectPlay branch's lack of a local selector write. No live candidate list or connection was sampled.
