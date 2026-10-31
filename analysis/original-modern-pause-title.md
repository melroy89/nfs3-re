# Pause title: authored vertical adjustment

**MP100-050 is partially supported by asset evidence.** The official final `pause.mnu` moves its first `[text]` record, identified by `codelink=pstitle` / `text=kTextPause`, from backup Y14 to official Y9. The shared authored coordinates/alignment are:

| Field | Local uppercase backup | Official v1.6.1 |
|---|---:|---:|
| `x` | 320 | 320 |
| `y` | 14 | 9 |
| `align` | 2 | 2 |

The shared `priority`, `texttype`, `color`, `italic`, `scale` and `ypos` fields also match. Y is the only differing value among fields present in both title records. This is a **five-unit upward authored coordinate change**, not measured screen pixels or proof of improved alignment.

The official title record additionally omits four legacy fields present in the selected backup: `postonly=0`, `mainonly=0`, `EnableForDemo=1`, `EnableForE3Demo=1`. Their default/visibility effects are outside this coordinate comparison; the title records are not declared wholly equivalent apart from Y. Other changed records elsewhere in the menu are not attributed to this release-note item.

## Evidence and reconstruction boundary

The [inventory script](scripts/inventory_pause_title_difference.py) checks the official archive hash and compares the extracted menu byte-for-byte with `fedata/menus/pause.mnu` read directly from that archive. The [manifest](evidence/inventories/pause-title-comparison.json) retains both complete title records, their section line numbers, hashes, common-field delta and omitted fields.

- Official menu SHA-256: `b5b4849991901037b89c3f92db9f5a14f0259542ca7cb6318fa0e89673cade66`.
- Selected uppercase backup SHA-256: `691f2dbcfdb8004d216eaa58a21bfc93cc1ef47f617157985eb8ea5b0a743c8a`.

The backup is not authenticated retail provenance, and final v1.6.1 assets do not establish introduction in v1.0.0. No code or Ghidra change is justified solely by the authored coordinate witness. For C reconstruction, retain the chosen version's menu data and investigate text layout, scaling/anchor rules and omitted-field defaults before asserting a pixel-identical title. Later visual comparison should include physical resolution/aspect and pause context; none was run here.

A Luna 6 read-only review located the candidate title difference; the parent independently read the complete records and verified archive provenance through the retained script. Executables, saved Ghidra state, raw exports and maintained C remain unchanged.
