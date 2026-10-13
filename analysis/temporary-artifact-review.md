# Temporary NFS3 artifact decisions

Read-only review of available NFS3 artifacts in `/tmp`. Nothing was deleted. File existence and comparisons describe this review, not a durability guarantee.

| Artifact | Classification and comparison | Decision |
| --- | --- | --- |
| `/tmp/nfs3-power-parent-check.json` | Byte-identical to `evidence/probes/x87-power-probe.json` | Already retained; leave temporary copy alone |
| `/tmp/nfs3-binary64-commit-check.json` | Byte-identical to `evidence/probes/binary64-helper-probe.json` | Already retained; leave temporary copy alone |
| `/tmp/nfs3-numeric-ofg8hzu0/results.json` | Earlier 48-row result list; every complete row occurs in the final binary64 helper report's directed cases | Semantically subsumed, not byte-identical; no duplicate import |
| `/tmp/nfs3_numeric_probe.py` | Early subtraction/multiplication harness with implicit cwd binary; final helper adds explicit arguments, fingerprint validation and expanded cases | Superseded by `scripts/probe_binary64_helpers.py`; preserve temporary prototype in place |
| `/tmp/nfs3-numeric-*` | Six pre-existing generated harness directories: assembly, extracted bytes, vectors, object files and executables; prototype results assessed above | Generated/intermediate artifacts; final helpers reproduce reviewed reports. No import or deletion |
| `/tmp/nfs3-{power,exp,div,exception}.bin` | Extracted code ranges corresponding to the power helper's documented ranges | Generated inputs; original fingerprinted executable and extraction helper retained |
| `/tmp/nfs3-ghidra-resume.log` | Zero-byte log | No evidence to recover |
| `/tmp/nfs3-project-snapshot-acguezrz/project.tar` | 110 regular members: 109 byte-identical to current checkout, 0 differ, 1 absent by original name; includes older `db.2479.gbf` | Separate recovery review only if old project state is needed. Not opened in Ghidra, merged, deleted or copied into evidence |

No unique research result needed recovery from the reviewed temporary JSON files. Snapshot byte differences are not proof of unique annotations; semantic comparison would require separate Ghidra recovery work. Missing original captures cannot be recovered from these artifacts; see the [capture dependency notes](scripts/README.md#capture-dependencies-and-reproducibility).

This reorganization's reruns produced temporary outputs under `/tmp/nfs3-layout-validation-duofwehd/`. All five probe reports, controller inventory and spike reconstruction exactly match retained evidence. The binary64 helpers also create fresh `nfs3-numeric-*` harness directories on rerun; these are generated artifacts, not new findings.
