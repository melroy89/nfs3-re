# Car selection persistence and identity

## Finding

The player-car settings used in a race are registry **ordinals**, not persistent
model IDs: `006fd2bc` is player one’s model index and `006fd328` is player two’s
model index. `GetCarModelRecordByIndex` (`00439a50`) resolves those ordinals
through the current model registry/cache; frontend preview and race
initialization consume the same model-index fields.

The persistence format depends on which save path is used:

- The normal `config.dat` loader/saver copies the full `0x20f0` configuration
  blob. Its code does not call the series-profile ID remapper. The selected
  model ordinal is therefore copied as a number in that path; current-registry
  remapping after a changed installation order is not established for
  `config.dat`.
- Tournament (`.trn`) and Knockout (`.kot`) profiles preserve both an ordinal
  and a 16-byte model identifier. Before writing, `00478010` materializes
  identifiers from the current registry. Before importing, `00478090` resolves
  those identifiers against the current registry and replaces the saved
  ordinals. This is the explicit changed-order reconciliation path.

No save/load was executed. The report establishes transformations in the
instructions and bytes passed through the code, not successful filesystem
operations or a particular installed profile’s values.

## Current registry ordinal and stable identifier

The car-model record exposes a 16-byte identifier at `record+0x31c`.
`00439520` obtains the record by model ordinal through `00439a50`, then returns
`record+0x31c`. The player settings records begin at `006fd2bc` and `006fd328`;
their first DWORDs are the model ordinals. `ResolveFrontendCarViewModelSelection`
(`00453500`) reads these DWORDs directly for `car1`/`car2`, and the human race
participant initializer consumes the selected model index from the settings
record. These are current-registry ordinal uses, not ID-based lookup at the
point of selection.

The registry can be rebuilt and reordered. The loader appends admitted models,
then `GroupAndSortCarModelList` (`00438eb0`) partitions and relinks them using
the metadata string at record `+0x10`; discovery and race setup also rebuild
the index cache and selector groups. A model’s ordinal is therefore tied to
the resulting registry order. The existing [registry report](car-selector-gameplay-domain.md)
documents the ordering and the installed-data limits; its installed inventory
does not guarantee the same order for every modified installation.

## `.trn` / `.kot` identity round-trip

Both profile writers first copy `0x20f0` bytes from `006fbb40` to a separate
buffer. The relevant selected-model fields and identifier sidecars are:

| Selection | Ordinal field in profile blob | 16-byte identifier field | Explicit conversion |
|---|---:|---:|---|
| Player one | `+0x177c` | `+0x1780` | `00478010` writes ID; `00478090` resolves ID and overwrites ordinal |
| Player two | `+0x17e8` | `+0x17ec` | `00478010` writes ID; `00478090` resolves ID and overwrites ordinal |
| Explicit opponent model (`selection >= 4`) | selector `+0x1994` | `+0x1998` | save resolves `selection-4` and writes ID; load resolves ID and stores `ordinal+4` |

At `00478010`, the helper first requires the header DWORD to equal `0x20f0`.
For player one it loads the ordinal at `+0x177c`, calls `00439520`, and copies
four DWORDs from the returned identifier address into `+0x1780..+0x178c`
(`00478025..0047803f`). It repeats this for player two at `+0x17e8/+0x17ec`
(`00478040..0047805a`). If the opponent selector at `+0x1994` is at least 4,
it resolves `selection-4` and writes that model’s identifier bytes at `+0x1998`
(`0047805b..0047807d`). Four `MOVSD` instructions copy 16 bytes, so these sidecars
contain identifier bytes, not a pointer value. The ordinal fields remain in
the blob alongside the identifiers.

At `00478090`, the inverse helper calls `00439990` with the 16-byte sidecar
address and stores the returned current-registry ordinal at `+0x177c` and
`+0x17e8`. For an explicit opponent selection it resolves `+0x1998`, adds 4,
and stores the combined selector at `+0x1994`. Thus a valid saved ID can
recover the same car after the model’s registry ordinal changes. The helper
returns failure when one of the required ID lookups returns a negative result.
The `.trn` and `.kot` importers call `00478090` before copying the blob into
`006fbb40`; they copy only when it reports success. Missing IDs therefore
prevent that profile’s success-path global copy, subject to the callers’ other
admission conditions.

The ordinary setup/resource-preparation path also calls `00478010` and
`004781b0` on a copied configuration buffer. `004781b0` repeats the same
ordinal-to-16-byte-ID materialization for additional saved model references
within the preparation blob. This confirms the identifier sidecars are a
general serialized-reference convention in those preparation paths, but it
does not make the global model ordinal itself a stable ID.

## `config.dat` boundary

`00472820` copies exactly `0x20f0` bytes from `006fbb40` to an output buffer
and passes it to the file writer. It does not call `00478010` in its body.
`00472980` accepts a file only when the returned size is exactly `0x20f0`, then
copies the bytes to `006fbb40`. On its version branch it calls
`00472230`, which calls `0040faf0`; those instructions do not resolve model
IDs. The ordinary exact-size loader path therefore copies the ordinal fields
without the explicit `00478090`/`00439990` conversion used by series profiles.
The blob also contains the adjacent fields used as ID sidecars by the series
profile transformer, but the inspected `config.dat` loader copies these bytes
as-is rather than resolving them against the current registry.

This conclusion is bounded to the audited loader and callers. It does not
establish whether a later profile import or another indirect path changes a
selection after `config.dat` loading, nor does it show what a specific local
`config.dat` contains. In the absence of a later ID lookup, a persisted ordinal
can designate a different model if the current registry order differs.

## Network participant profiles are a separate path

For a remote participant, the sender obtains the selected model’s 16-byte ID
from the current ordinal and transmits it in the network profile. The receiver
uses `00439990` to resolve that ID in its current registry and writes the
resulting local ordinal into the setup record. This is an identity-based
network mapping, distinct from `config.dat` and from the full-blob
`.trn`/`.kot` import. Static code establishes the field conversion; matching
registries, successful peer admission and identical race behavior remain
unverified. See the [network roster report](network-roster-admission.md).

## Reproducible anchors and limits

The exact active target was the installed `nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
REA/Ghidra inspected the exact image read-only. Raw byte checks used:

```sh
EXE='nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe'
objdump -D -Mintel --start-address=0x446550 --stop-address=0x4465e0 "$EXE"
objdump -D -Mintel --start-address=0x4468c0 --stop-address=0x446950 "$EXE"
objdump -D -Mintel --start-address=0x4465e0 --stop-address=0x4466a0 "$EXE"
objdump -D -Mintel --start-address=0x446800 --stop-address=0x4468c0 "$EXE"
objdump -D -Mintel --start-address=0x478010 --stop-address=0x4780f5 "$EXE"
objdump -D -Mintel --start-address=0x439a50 --stop-address=0x439aa5 "$EXE"
objdump -D -Mintel --start-address=0x472820 --stop-address=0x4728d3 "$EXE"
objdump -D -Mintel --start-address=0x472980 --stop-address=0x472b48 "$EXE"
```

Resolved ID lookup is a current linked-registry scan that returns a matching
model ordinal (or a negative result); its exact iteration and comparison are
documented in the network and registry audits. No persistent Ghidra edits,
configuration writes, game launch or live-memory changes were made. Remaining
unknowns are successful save/load on disk, runtime registry order after a
changed installation, and any indirect post-load selection rewrite not shown
in the cited normal paths.
