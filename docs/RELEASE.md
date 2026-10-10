# Release preparation

The intended release contains the populated Ghidra analysis databases and original documentation. It excludes the standalone game installation, personal UI state, locks, and temporary files.

## Before publication

- Confirm the intended hosting location and repository name.
- Review redistribution rights for imported program bytes and other third-party content in the databases. The Apache-2.0 license applies only to original project contributions.
- Save and close Ghidra before staging a complete database snapshot. Keep a separate backup.
- Inspect all candidate paths and any existing Git history for the external game installation, temporary files, personal paths, and unintended exports.
- Check hosting file-size limits against the largest database files.
- Commit the consistent snapshot, clone it separately, open the included `nfs3_decomp.gpr`, and verify that the project opens and saved functions, comments, types, and pseudocode are visible.
- The configured remote is `git@github.com:melroy89/nfs3-re.git`. Commit and push when ready; repository preparation has not published a release.

## Review commands

```sh
git status --short --branch
git add --dry-run .
git check-ignore -v 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe' nfs3_decomp.rep/user/ nfs3_decomp.rep/projectState
```

After saving and closing Ghidra, stage the intended snapshot and review it:

```sh
git add .
git diff --cached --check
git diff --cached --stat
git diff --cached --name-status
git ls-files
```

The file list should include `nfs3_decomp.gpr`, plus `project.prp`, the `idata/` database/index/property files, and the `versioned/` index under `nfs3_decomp.rep/`. Database deletions caused by normal storage rotation must be staged together with their replacements.

For public archives, use a reviewed Git commit with `git archive` rather than zipping the working directory. The archive includes the matching `.gpr`/`.rep` pair, ready to open after extraction.

## Validation status

The repository was reorganized after Ghidra had closed, with a checksum-verified full backup. Validation results for the moved project and a separate Git-eligible copy are recorded below. No commit, push, or public release was performed.

### Reorganization checks (2026-10-11)

- Full local backup verified with SHA-256, sizes, and permission modes before moving; project/game file hashes matched again after validation.
- Git remained on `main` with the existing GitHub `origin`; no files were staged or committed.
- Both the moved project and a separate copy of the 118 Git-eligible files opened using Ghidra 12.1.4 `analyzeHeadless`, with `-readOnly -noanalysis`.
- Both loaded `nfs3.exe` with 4,069 functions, 502 data types (including referenced types), 45,836 symbols, 2,385 user-defined symbols, and 3,022 listing comments.
- Three representative functions, including `HandleGameAbort` at `00401010`, decompiled successfully with matching names and output lengths in both copies.
- The isolated copy contained no external game installation or personal project state. This confirms that the saved analysis can be opened and decompiled without those files.
- The GUI File/Open workflow and a real Git clone were not exercised; the isolated copy used the exact Git-eligible file list because no commit exists yet. Complete GUI verification on a committed clone before claiming that release check passed.
