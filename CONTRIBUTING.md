# Contributing

The project is still in the decompilation phase. Small, evidence-backed research contributions are welcome.

- Record the target executable's SHA-256, Ghidra version, address, and reason for each finding. Distinguish confirmed behavior from hypotheses and automatic analysis.
- Keep original research notes under `analysis/`, project documentation under `docs/`, and original helper scripts under `scripts/`. The ignore rules exclude the standalone game installation, personal state, and temporary files.
- Submit only material you have the right to contribute under Apache-2.0. Retain applicable attribution and identify third-party material separately.
- Keep standalone game files, assets, executable patches/backups, and unreviewed exports local. Save and close Ghidra before staging shared database changes. Include database changes as a consistent snapshot, never as individual hand-picked storage files. See [sharing analysis](docs/SHARING.md).
- Before submitting, inspect `git diff --cached` and `git status --short`. Avoid force-adding ignored files.

A useful research note contains the exact target identity, observed facts, interpretation, supporting addresses, validation performed, and remaining uncertainty. Include reproduction instructions and results when adding scripts; do not claim runtime testing from static inspection alone.
