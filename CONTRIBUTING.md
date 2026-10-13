# Contributing

The completed static analysis pass and annotated Ghidra project provide a foundation for investigating and implementing game fixes and adaptations. Bug reports, feature requests, implementation work, testing, and further reverse-engineering contributions are welcome.

## Open a ticket

Search the [existing issues](https://github.com/melroy89/nfs3-re/issues), then open a ticket for a bug or proposed improvement. You do not need to understand Ghidra or assembly to contribute a useful report.

- **Bug reports:** Include the game/patch version, operating system, Wine version if applicable, relevant race settings, exact reproduction steps, and expected versus actual behavior. Screenshots, videos, or logs can help demonstrate the problem.
- **Feature requests:** Describe the desired behavior, the problem it solves, and a concrete example. Multiplayer improvements, track/lap/car limits, pursuit options, police difficulty, and traffic settings are possible areas to investigate.
- **Testing:** Report the version tested, settings used, steps performed, and results. Mention whether the behavior is consistent or intermittent.

Reverse engineering lets us trace the code behind these requests and develop targeted changes. Feasibility and scope are assessed per ticket, and proposed fixes require in-game testing before being considered validated. Opening a ticket does not require a proposed implementation.

## Contribute a change

Link your work to the relevant ticket and explain the original behavior, the change, and how you validated it. Keep each change focused. For executable or menu changes, document the original and resulting fingerprints and provide reproducible patch/build steps where possible. Preserve the target provenance and test affected game modes; static analysis alone does not prove a gameplay fix.

## Research and project files

- Record the target executable's SHA-256, Ghidra version, address, and reason for each finding. Distinguish confirmed behavior from hypotheses and automatic analysis.
- Keep original research notes under `analysis/`, project documentation under `docs/`, and original helper scripts under `scripts/`. The ignore rules allow only the documented v1.6.2 executable and setup menu from the standalone installation; personal state and temporary files remain excluded.
- Submit only material you have the right to contribute under Apache-2.0. Retain applicable attribution and identify third-party material separately.
- Keep other game files, assets, executable backups, and unreviewed exports local. Save and close Ghidra before staging shared database changes. Include database changes as a consistent snapshot, never as individual hand-picked storage files. See [sharing analysis](docs/SHARING.md).
- Before submitting, inspect `git diff --cached` and `git status --short`. Avoid force-adding ignored files.

A useful research note contains the exact target identity, observed facts, interpretation, supporting addresses, validation performed, and remaining uncertainty. Include reproduction instructions and results when adding scripts; do not claim runtime testing from static inspection alone.
