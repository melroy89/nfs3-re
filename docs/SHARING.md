# Sharing the populated Ghidra project

This repository tracks `nfs3_decomp.gpr` and the shared `project.prp`, `idata/`, and `versioned/` files under `nfs3_decomp.rep/`. These files preserve the saved analysis and imported program data needed to browse functions, comments, symbols, types, and decompiled pseudocode in Ghidra.

Only `nfs3.exe` and `FEDATA/MENUS/setup.mnu` from the local v1.6.2 preparation are tracked beneath `nfs3_decomp.rep/Electronic Arts/Need For Speed III/`; other files there are ignored. This directory is the external game installation, distinct from the logical folder with the same name inside the Ghidra project tree. Imported bytes remain in the databases. Apache-2.0 covers original contributions only; review third-party redistribution rights before making the database public.

## Save a consistent snapshot

1. Save all open programs and close the Ghidra project normally.
2. Make a separate backup of the matching `.gpr` and `.rep` pair.
3. Check `git status --short` and stage the complete shared database state, including indexes, property files, additions, and deletions. Do not select only a few `.gbf` files or edit database files by hand.
4. Review the candidate file list. Confirm that only the two documented modified game files are included from the external installation, and that user state, locks, temporary `.ps` files, and index/journal backups are excluded.
5. Commit only after the project has closed. Reopen a separate clone using the README instructions before publishing that revision.

Ghidra changes database storage files while it is running. A copy or commit taken during active writes is not a qualified project snapshot. Binary database changes are not mergeable as text; coordinate concurrent analysis and resolve database conflicts through Ghidra or separate projects rather than Git's text merge tools.

## Opening a clone

A normal clone is named `nfs3-re` and includes `nfs3_decomp.gpr` beside `nfs3_decomp.rep/`. Open the included `.gpr` through **File → Open Project**. No renaming, setup scripts, or external game directory are needed to browse the saved analysis. The personal `user/` state and `projectState` inside `.rep` are recreated locally as needed.

The databases preserve saved analysis; decompiled C-like output is generated on demand. There is no requirement to include a full decompiler export to browse functions.

## Optional research notes

Use `analysis/` for original explanations and supporting addresses. Record the target SHA-256 and distinguish observations from hypotheses. For alternate exports, inspect every output file and validate restoration separately. GZF and project archives also contain program data.

Do not use `git clean -fdx` in this workspace: it would remove the ignored game installation and other local files.
