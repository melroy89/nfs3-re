#!/usr/bin/env python3
"""Inventory FEDATA model-selector fields in installed BIGF car archives.

This read-only inventory records FEDATA members whose suffix appears in the
executable's language-code table, including the selector at offset +8 and the
16-byte identifier at +0x18. It does not execute the model loader or establish
runtime admission.
"""

import argparse
import hashlib
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGE_CODES = {"eng", "ger", "fre", "spa", "ita", "swe", "jap"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_archive(path, root):
    archive = path.read_bytes()
    if len(archive) < 16 or archive[:4] != b"BIGF":
        raise ValueError(f"Not a BIGF archive: {path}")
    declared_size, entry_count, directory_end = struct.unpack_from(">III", archive, 4)
    if declared_size != len(archive) or not 16 <= directory_end <= len(archive):
        raise ValueError(f"Invalid BIGF header extent: {path}")

    members = []
    ignored_suffixes = []
    cursor = 16
    for _ in range(entry_count):
        if cursor + 8 > directory_end:
            raise ValueError(f"Truncated BIGF directory: {path}")
        offset, size = struct.unpack_from(">II", archive, cursor)
        try:
            name_end = archive.index(b"\0", cursor + 8, directory_end)
        except ValueError as error:
            raise ValueError(f"Unterminated BIGF member name: {path}") from error
        name = archive[cursor + 8:name_end].decode("ascii")
        cursor = name_end + 1
        if offset < directory_end or offset + size > len(archive):
            raise ValueError(f"Invalid member extent: {path}:{name}")
        lowered = name.lower()
        if not lowered.startswith("fedata."):
            continue
        language = lowered.rsplit(".", 1)[1]
        if language not in LANGUAGE_CODES:
            ignored_suffixes.append(language)
            continue
        payload = archive[offset:offset + size]
        if len(payload) < 0x28:
            raise ValueError(f"Short FEDATA member: {path}:{name}")
        raw_dword = struct.unpack_from("<I", payload, 8)[0]
        signed_dword = struct.unpack_from("<i", payload, 8)[0]
        selector = signed_dword >> 16  # mirrors the loader's SAR EAX,16
        identifier = payload[0x18:0x28]
        model_root = path.parent.relative_to(root / "GAMEDATA" / "CARMODEL").as_posix()
        identifier_first_dword = struct.unpack_from("<I", identifier, 0)[0]
        flag_words = {f"+0x{offset:x}": struct.unpack_from("<H", payload, offset)[0]
                      for offset in (6, 8, 0x0e, 0x10, 0x14)}
        members.append({
            "archive": path.relative_to(root).as_posix(),
            "model_root": model_root,
            "archive_sha256": sha256(archive),
            "archive_bytes": len(archive),
            "member": name,
            "member_offset": offset,
            "member_bytes": size,
            "member_sha256": sha256(payload),
            "model_identifier_hex": identifier.hex(),
            "model_identifier_first_dword_le": identifier_first_dword,
            "model_identifier_tail_12_bytes_zero": identifier[4:] == bytes(12),
            "language": language,
            "selector_source_dword_le": raw_dword,
            "selector_source_high_word": (raw_dword >> 16) & 0xffff,
            "selector_after_signed_shift": selector,
            "metadata_flag_words": flag_words,
        })
    return members, ignored_suffixes


def inventory(game_root):
    root = game_root.resolve()
    target = root / "nfs3.exe"
    car_root = root / "GAMEDATA" / "CARMODEL"
    if not target.is_file():
        raise ValueError(f"Missing game executable: {target}")
    if not car_root.is_dir():
        raise ValueError(f"Missing installed car-model directory: {car_root}")

    archives = sorted(path for path in car_root.rglob("*")
                      if path.is_file() and path.suffix.lower() == ".viv")
    if not archives:
        raise ValueError(f"No VIV archives found under {car_root}")

    rows = []
    ignored_suffixes = Counter()
    for path in archives:
        members, ignored = read_archive(path, root)
        rows.extend(members)
        ignored_suffixes.update(ignored)
    if not rows:
        raise ValueError("No FEDATA.* members found in installed car archives")

    by_model_root = defaultdict(list)
    for row in rows:
        by_model_root[row["model_root"]].append(row)

    selector_model_counts = Counter()
    model_rows = []
    inconsistent_languages = []
    for model_root, variants in sorted(by_model_root.items()):
        values = sorted({row["selector_after_signed_shift"] for row in variants})
        for value in values:
            selector_model_counts[value] += 1
        if len(values) != 1:
            inconsistent_languages.append({
                "model_root": model_root,
                "selector_values": values,
                "members": [row["archive"] + ":" + row["member"] for row in variants],
            })
        model_rows.append({
            "model_root": model_root,
            "model_identifier_hexes": sorted({row["model_identifier_hex"] for row in variants}),
            "archive_paths": sorted({row["archive"] for row in variants}),
            "localized_member_count": len(variants),
            "languages": sorted({row["language"] for row in variants}),
            "selector_values": values,
        })

    language_counts = Counter(row["language"] for row in rows)
    return {
        "method": "Read-only BIGF directory parsing. FEDATA DWORD+8 is interpreted using the signed arithmetic shift at nfs3.exe 0043a171; no game code is executed.",
        "scope": "FEDATA members in installed GAMEDATA/CARMODEL/**/*.viv whose suffix is in the executable's seven-code language table; loose FEDATA files, other suffixes, alternate roots, custom assets and runtime model admission are excluded.",
        "target_sha256": sha256(target.read_bytes()),
        "field_basis": {
            "source_member_offset": 8,
            "source_width_bytes": 4,
            "operation": "signed little-endian DWORD arithmetic-shift-right 16",
            "destination_model_record_offset": 904,
            "language_codes_from_executable_table": sorted(LANGUAGE_CODES),
            "destination_consumer_domain": [0, 1, 2],
            "category_array_index": "selector + 1; category 0 is the combined group",
            "static_references": ["0043a171", "0043a580", "0043a6e0"],
        },
        "summary": {
            "archive_count": len(archives),
            "fedata_member_count": len(rows),
            "model_directory_count": len(by_model_root),
            "language_counts": dict(sorted(language_counts.items())),
            "ignored_fedata_suffix_counts_not_in_executable_language_table": dict(sorted(ignored_suffixes.items())),
            "selector_model_counts": {str(key): selector_model_counts[key]
                                       for key in sorted(selector_model_counts)},
            "models_with_language_selector_mismatch": len(inconsistent_languages),
        },
        "models": model_rows,
        "localized_members": rows,
        "language_mismatches": inconsistent_languages,
        "limitations": [
            "A matching installed asset does not prove that the game enumerates or successfully loads it.",
            "Static selector values and consumer indices do not prove a normal UI or race path reaches an out-of-range store.",
            "This report covers the selected installation only and does not represent modified/community car packs.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.game_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
