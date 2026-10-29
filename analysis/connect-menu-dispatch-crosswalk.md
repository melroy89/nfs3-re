# Connect menu dispatch crosswalk

## Scope and finding

This re-audit uses the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Its `connect` menu initializer maps `codelink=tcp` to callback `0043fe50`. The same initializer does not install a RaceNet callback: the RaceNet assignment present in `nfs3_org.exe` is absent from active `nfs3.exe`. The RaceNet menu route therefore remains unresolved. The backup comparison is included only to explain the correction; it is not evidence for the active build.

No actual click or network session was observed.

## Descriptor and menu inputs

- Installed `FEDATA/MENUS/connect.mnu` contains button items with `codelink=tcp`, `ipx`, `modem`, `serial`, and `racenet`. TCP, modem, serial and RaceNet specify `nextmenu=mainmult`; IPX specifies `nextmenu=ipx`.
- In active `nfs3.exe`, the descriptor row at `00555f00` begins with name pointer `00537d1c` and callback slots `004405c0` at `+0x0c`, `00440730` at `+0x10`.
- The adjacent IPX descriptor begins at `00555f18`: name pointer `00537d24`, slots `00440890`, `00440960`, and `00440810` at `+0x0c/+0x10/+0x14`.
- These table values were decoded from the selected PE with `objdump -s --start-address=0x555f00 --stop-address=0x555f80`. The matching earlier REA bytes evidence is `ev_9cf63833479c34b365a96a0b83ed765a75de82c075b5c3f2ebbe9e3e79bd5d16`; prior xref interpretation of this row was incorrect and is superseded here.
- The menu parser stores `codelink` as an arena string at item `+0x10`; `nextmenu` is separate at `+0x40`. The generic button handler dispatches a non-null registered callback at `+0x64` (REA evidence `ev_041453c232137e55bbab48f7abfcfcdf6a4e7269c8107267ebce96260db587ae`).

## Active initializer `004405c0`

Active PE instructions at `004405c0–0044072e` show the initializer receiving the menu object in EAX and retaining it in ECX. It calls exact-string lookup `00442a40`, then writes callbacks into matching records:

| Codelink | Lookup | Callback written to item `+0x64` |
|---|---:|---:|
| `tcp` (`00537904`) | `004406de` | `0043fe50` at `004406ee` |
| `modem` (`00537908`) | `004406f5` | `0043ff50` at `00440705` |
| `serial` (`00537910`) | `0044070c` | `0043fee0` at `0044071c` |

The initializer also looks up `ipx` and `netw` to update enable bits. This establishes TCP registration from the active PE bytes, not from string ordering or a callback token xref. The exact TCP instruction is `mov dword ptr [eax+0x64],0x43fe50` at `004406ee`.

### RaceNet correction

In active `nfs3.exe`, the flag-controlled section at `00440682–004406c7` performs lookup/enable-bit checks for the RaceNet and modem/serial items. It then executes `jmp 004406de` at `004406c7`; bytes `004406c9–004406dd` are NOPs. Consequently, there is no RaceNet callback store in the active initializer. The separate transport-state routine `00440730` does inspect a `racenet` codelink, but that is not evidence of an item callback registration or a complete RaceNet click route.

For comparison only, `nfs3_org.exe` has SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and contains a RaceNet callback store at `004406d7`. That backup is not the selected active executable and is excluded from active-build conclusions.

## Dispatch and remaining gap

The `connect` descriptor's second callback, `00440730`, reads menu item records and sets transport selection state by codelink, including `modem`, `serial`, `ipx`, `tcp`, and `racenet`. It is distinct from the item `+0x64` callback. The TCP callback `0043fe50` builds the TCP Connection dialog and registers `0043f760` for Host Game, Join Game, and port selection. This confirms the static menu-to-TCP-dialog mapping.

RaceNet has `nextmenu=mainmult`, and active `004405c0` performs availability checks, but this review found no active per-item callback store for `racenet`. Its actual frontend click behavior and any public-service path remain open. The generic transition and item callback are separate fields, so the `nextmenu` value alone does not establish the specialized route.

An earlier direct xref query to `0043fe50` returned no direct xrefs because the callback address is written as an immediate by the initializer rather than called there. The instructions above establish the mapping despite that query result.

## Evidence boundary

Reviewed the selected PE's descriptor bytes and original instructions, installed `connect.mnu`, and the previously traced parser/button handler. No UI runtime, provider DLL, registry, network traffic, executable/configuration mutation, or persistent Ghidra edit was used. Static registration does not establish that a provider is installed, a server exists, or a connection succeeds.
