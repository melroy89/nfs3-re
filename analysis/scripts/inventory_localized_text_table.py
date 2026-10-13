#!/usr/bin/env python3
"""Inventory indexed localized strings for selected NFS3 HUD text IDs.

The table format is an offset array whose first DWORD gives the byte extent of
that array; each entry points to a NUL-terminated byte string in the same file.
This validates retained files, not the game's runtime table selection or every
possible string passed to frontend text rendering.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org/text"
LANGUAGES = ("eng", "ger", "fre", "spa", "ita", "swe")
TOKEN = re.compile(rb"[^ \t\r\n\x00]+")
TABS = re.compile(rb"\t+")
HUD_IDS = (0x156, 0x157)


def inventory_one(path):
    data = path.read_bytes()
    if len(data) < 4:
        raise ValueError(f"{path}: truncated table header")
    table_bytes = struct.unpack_from("<I", data)[0]
    if table_bytes < 4 or table_bytes % 4 or table_bytes > len(data):
        raise ValueError(f"{path}: invalid offset-table extent {table_bytes}")
    count = table_bytes // 4
    entries = []
    for index in range(count):
        offset = struct.unpack_from("<I", data, index * 4)[0]
        if offset < table_bytes or offset >= len(data):
            raise ValueError(f"{path}: entry {index} has invalid string offset {offset}")
        end = data.find(b"\0", offset)
        if end < 0:
            raise ValueError(f"{path}: entry {index} is not NUL-terminated")
        entries.append(data[offset:end])

    longest_token = {"length": 0, "id": None, "bytes_hex": None}
    longest_tab = {"length": 0, "id": None}
    longest_string = {"length": 0, "id": None}
    for index, value in enumerate(entries):
        if len(value) > longest_string["length"]:
            longest_string = {"length": len(value), "id": index}
        for match in TOKEN.finditer(value):
            if len(match.group()) > longest_token["length"]:
                longest_token = {"length": len(match.group()), "id": index, "bytes_hex": match.group().hex()}
        for match in TABS.finditer(value):
            if len(match.group()) > longest_tab["length"]:
                longest_tab = {"length": len(match.group()), "id": index}

    return {
        "file": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "file_bytes": len(data),
        "offset_table_bytes": table_bytes,
        "entry_count": count,
        "validated_entries": len(entries),
        "hud_speed_labels": {f"0x{index:03x}": entries[index].decode("latin-1") for index in HUD_IDS},
        "longest_string": longest_string,
        "longest_non_delimited_token": longest_token,
        "longest_contiguous_tab_run": longest_tab,
    }


def inventory(root):
    root = root.resolve()
    tables = [inventory_one(root / f"text.{language}") for language in LANGUAGES]
    return {
        "scope": "six lowercase indexed FEDATA localization tables selected by the game's text.<language> names",
        "root": str(root),
        "tables": tables,
        "limitations": [
            "The parser validates retained table structure and stored byte strings; it does not capture the active runtime language or table pointer.",
            "The scan does not prove which strings reach LayoutAndRenderWrappedFrontendText or cover dynamically assembled text.",
            "A clean asset inventory is not proof of safe runtime input or absence of a reachable boundary condition.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(inventory(args.text_root), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
