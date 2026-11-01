# DX5 reference/final pairing and changed-byte map

## Baselines and reproduction

This comparison uses `d3da.dll` from the [author-hosted reference bundle](original-modern-original-reference-bundle.md), and `drivers/dx5/dx5a.dll` from the pinned official final Modern archive. The reference DLL hash also matches the previously inventoried local root `D3DA.DLL`; it does not match the separate setup-directory candidate. Author hosting and local equality do not authenticate pristine retail provenance.

| Role | Bytes | SHA-256 |
|---|---:|---|
| Reference `d3da.dll` | 98,641 | `ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02` |
| Final `drivers/dx5/dx5a.dll` | 72,704 | `6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42` |

Run `python3 analysis/scripts/audit_dx5_reference_final.py`. The [script](scripts/audit_dx5_reference_final.py) verifies both archive hashes before extracting members into memory, verifies member hashes, compares exports and selected whole file-backed sections, and records bounded disassembly in the [manifest](evidence/audits/dx5-reference-final.json). It never loads either DLL. Two successive successful runs produced identical manifest bytes during this increment.

## What is verified

| Area | Finding | Meaning and boundary |
|---|---|---|
| Export surface | All 34 names, ordinals, RVAs and forwarder fields match | Strong interface correspondence; not proof of identical ABI contracts or all function bodies |
| Image base | Both `60000000` | Reported VAs are preferred-image addresses, not runtime mappings |
| Whole code section | 55,296 bytes at RVA `1000`; 710 differing bytes in 25 maximal contiguous differing-byte intervals | Complete raw inventory within this section, including padding/data if present; intervals are not function or feature counts |
| Import section | All 2,048 bytes match at RVA `f000` | File-backed section equality, not equality of resolved imports or dynamic calls |
| Data section | All 7,168 bytes match at RVA `10000` | File-backed initial data equality, not equality of subsequent writes |
| `THRASH_about` | Complete 180-byte body `60001020..600010d4` differs in two immediate bytes only | Exact descriptor publication change below |
| Selection helper and `THRASH_selectdisplay` | Complete combined span `60001618..60001734`, 284 bytes, is identical | Includes the helper called by `about`, plus exported selector at `60001654`; changed subordinate callees remain possible |

All end addresses above are exclusive. The manifest records every changed interval in the code section with both byte strings and addresses, so later work can start from the remaining changes rather than rediscover their locations. This does not inventory every byte difference in the entire files: headers, relocation/export/resource sections and appended file material have separate boundaries.

## Exact descriptor publication difference

Both `about` bodies populate a descriptor at `60012010`, call helper `60001618`, then return descriptor address in EAX. At `60001090`, the five-byte instruction changes as follows:

| Reference | Modern |
|---|---|
| `ba 90 20 01 60` — `MOV EDX,60012090` | `ba 00 9e 01 60` — `MOV EDX,60019e00` |

Only bytes at `60001091..60001093` differ. Both bodies then store EDX at `600010ba` to `60012050`, descriptor offset `+40h`. The verified finding is a changed published pointer. The descriptor also retains magic `44334435h` and `+8=68h`; the latter must not be called a structure size or API version merely from this literal. See the [loader analysis](original-modern-renderer-loading.md).

The pointed-to table's initialization, element contract and consumer paths must be checked before attributing supported resolutions, bit depths or sorting changes to this relocation. The previously analysed DX7 table policy does not establish the DX5 policy.

## Storage distinction

Every section in these two DLLs has `VirtualSize=0`. Their `.bss` headers have RVA `12000`, raw-data pointer zero and nonzero raw-size fields: reference `7e00h`, Modern `8e00h`. The reference descriptor pointer falls inside the reference declared extent; the new pointer `60019e00` is exactly the reference extent's end and falls inside the expanded Modern extent, using those nonzero size fields.

This establishes a declared uninitialized-storage expansion of `1000h`. It does not establish file-backed initial values or observed loader mapping. The script does not read file offset zero as BSS contents. Actual zero filling, subsequent initialization writes and ownership of the expanded region remain distinct questions.

## Actionable follow-up and acceptance

- **Done, verified:** artifact pairing, full export inventory, whole code-section byte map, import/data section equality, complete `about` comparison and retained selection span.
- **Pending, unresolved:** follow both published pointers through initialization and executable/DLL consumers; classify the other code intervals into mechanisms before assigning release-note claims.
- **Later evidence:** authenticated retail provenance, historical introduction, full relocations/resources, runtime display enumeration and rendering acceptance.

No release-note item is promoted by this bounded pairing alone. The broader original/Modern investigation remains incomplete. Existing EXEs, saved Ghidra state, maintained C and raw exports were not edited; no target instructions, OS graphics calls or new probes were run.
