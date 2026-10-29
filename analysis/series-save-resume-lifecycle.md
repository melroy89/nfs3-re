# Ordinary series save and resume lifecycle

## Scope and target

This audit traces the installed post-race save controls, the explicit tournament/Knockout profile loader, and the two series progression words. The inspected artifact is the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Static inspection only; no user profile was created or loaded, and no game, configuration, executable, live-memory, or persistent Ghidra data was changed.

## What the post-race save controls write

The installed [`postgame.mnu`](../nfs3_decomp.rep/Electronic%20Arts/Need%20For%20Speed%20III/FEDATA/MENUS/postgame.mnu) declares `Save_Tourny` and `Save_KO`. In the postgame initializer (`0044f2dc` onward), the first token is bound to callback `0044e480` for race mode `006fd3b8 == 1`; the second is bound to `0044e460` for mode `2` when the local-player selector `006fd3b0` is at most `1`. Other modes disable the respective rows. These are explicit profile-save commands, not an automatic save on every round.

The callbacks call common dialog setup `00447a30` with mode `1` for Tourny and `0` for KO. Mode 1 selects the `.trn` writer `004468c0`; mode 0 selects `.kot` writer `00446550`. Both writers allocate a `0x20f0`-byte buffer, copy that entire size from configuration base `006fbb40`, pass the copy through `00478010`, then write `0x20f0` bytes to the chosen suffixed file. The normal save path therefore serializes a whole configuration/preparation blob, rather than a small series-only record.

The mode-1 progression WORD is at `006fd40c`, blob offset `0x18cc`; the Knockout progression WORD is at `006fd3bc`, offset `0x187c`. Both lie within the copied `0x20f0` bytes. The inspected `00478010` helper resolves resource pointers in other blob fields, but does not touch either progression offset. Thus the explicit TRN/KOT save format carries the current progression WORD by full-blob copy. This establishes the bytes supplied to the file writer; it does not prove successful filesystem persistence or that a saved round was resumed through the ordinary UI. The TRN path sets its local success flag before the writer call at `00446934` and does not inspect that call's return before returning the flag.

The separate `config.dat` loader/saver (`00472980` / `00472820`) also reads or writes a whole `0x20f0`-byte blob at `006fbb40`; it is aggregate configuration persistence. The saver’s documented snapshot edit is at offset `0x1860`, not either progression offset. However, the main-menu entry (`004730d0`) clears `0x50` bytes beginning `006fd3bc` and `0x62` bytes beginning `006fd40c` (`0047319f–004731c6`). The ordinary postgame Back path returns to outer state `0x0b`, which enters this reset. Therefore `config.dat`’s incidental inclusion of the progression bytes is not a normal visible “resume series” interface, and main-menu entry clears the live progress blocks.

## Explicit profile loading

The installed [`setup.mnu`](../nfs3_decomp.rep/Electronic%20Arts/Need%20For%20Speed%20III/FEDATA/MENUS/setup.mnu) exposes a Load button with `nextmenu=loadsave`. In [`loadsave.mnu`](../nfs3_decomp.rep/Electronic%20Arts/Need%20For%20Speed%20III/FEDATA/MENUS/loadsave.mnu), the `SHOW_TOURNAMENTS` and `SHOW_KNOCKOUTS` tabs select the profile type, and the `loadnow` row invokes callback `00446c50` (installed at `004474f3`). That handler dispatches the tournament selection to `00446800` with `.trn` suffix and Knockout selection to `004465e0` with `.kot` suffix. The exact importer names and copy behavior are documented in `analysis/detailed-analysis-notes.md` at the preparation-import refinement.

On their success paths, both importers copy exactly `0x20f0` bytes into `006fbb40`. They snapshot selected runtime/preparation ranges before the copy and restore those ranges afterward. The snapshot beginning `006fbb4c` is `0x176c` bytes long and ends at `006fd2b8`; the two additional 12-byte ranges begin at `006fd2dc` and `006fd348`. None overlaps mode-one progress at `006fd40c` or Knockout progress at `006fd3bc`. Accordingly, a successful TRN/KOT import replaces the corresponding live progression word with the saved blob’s value, subject to the importer’s success path.

The normal UI sequence therefore offers a potential continuation mechanism: return to setup, choose Load, select the matching Tournament/Knockout profile, and load it. The profile importer restores the saved progress word into the live blob after the main-menu reset. The mode-one roster builder reads `006fd40c` as the sequence ordinal; the Knockout roster builder generates its list only when `006fd3bc` is zero and otherwise uses that progression value. This connects the restored fields to normal series setup logic. A loaded profile is still a setup/profile import, not a demonstrated in-race checkpoint: no car positions, race timer, or mid-race state restoration is established here.

## Findings and limits

- `.trn`/`.kot` saves copy the entire `0x20f0` configuration blob, including the relevant progression WORD.
- Explicit TRN/KOT imports copy the same full blob and preserve only selected runtime fields that do not overlap either series progression WORD.
- Main-menu entry clears both live progression regions. This distinguishes automatic aggregate `config.dat` persistence from the explicit save/load profile workflow.
- Static code supports restored progression feeding ordinary series setup. It does not establish that a particular saved file exists, is accepted, or was successfully loaded, nor that all other setup prerequisites in a profile remain compatible.
- No installed `.trn` specimen was available in the inspected prefix, and no profile files were opened or decoded for this task. No game execution or interactive resume was performed.


Address correction: the callbacks are `0044e460` and `0044e480`. Active-byte disassembly at `0044e460` is `XOR EAX,EAX; CALL 00447a30; MOV EAX,2; RET`; at `0044e480` it is `MOV EAX,1; CALL 00447a30; MOV EAX,2; RET`. Independent recheck of the writer bytes at `00446550` and `004468c0` confirms both copy `0x20f0` bytes from `006fbb40` before calling `00478010` and writing `0x20f0`. The Knockout consumer at `00473ee0` checks `WORD[006fd3bc]` and only generates a new list when it is zero; the series lifecycle audit records mode-one consumption of `WORD[006fd40c]` by `00474310`. SHA-256 remained `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

Evidence references: save/load menu resources listed above; original active-byte inspection of `0044f2dc`, corrected callbacks `0044e460` / `0044e480`, `00447a30`, `00446550`, `004468c0`, `00478010`, `00446c50`, `00446800`, `004465e0`, and `004730d0`; existing config persistence evidence in `analysis/control-binding-persistence-audit.md` and `analysis/track-eight-unlock-persistence.md`; series progression consumers and reset chain in `analysis/series-normal-terminal-lifecycle.md`; importer copy/snapshot details in `analysis/detailed-analysis-notes.md`.
