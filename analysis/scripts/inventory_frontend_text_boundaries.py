#!/usr/bin/env python3
"""Measure simple token/tab boundaries in retained FE text definitions.

This is a byte-level inventory of .MNU and .TXT files only. It does not parse
the indexed binary localization tables or prove which strings reach the game
text layout routine.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "nfs3_decomp.rep/Electronic Arts/Need For Speed III/fedata_org"
TOKEN = re.compile(rb"[^ \t\r\n\x00]+")
TABS = re.compile(rb"\t+")


def inventory(root):
    root = root.resolve()
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".mnu", ".txt"})
    if not files:
        raise FileNotFoundError(f"No .MNU/.TXT files under {root}")
    max_token = {"length": 0, "path": None, "line": None}
    max_tab_run = {"length": 0, "path": None, "line": None}
    inventory_hash = hashlib.sha256()
    total_bytes = 0
    for path in files:
        data = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(data).hexdigest()
        inventory_hash.update(rel.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\n")
        total_bytes += len(data)
        for line_number, line in enumerate(data.splitlines(), 1):
            for match in TOKEN.finditer(line):
                if len(match.group()) > max_token["length"]:
                    max_token = {"length": len(match.group()), "path": rel, "line": line_number}
            for match in TABS.finditer(line):
                if len(match.group()) > max_tab_run["length"]:
                    max_tab_run = {"length": len(match.group()), "path": rel, "line": line_number}
    return {
        "scope": "retained fedata_org .MNU and .TXT files; raw bytes split at CR/LF",
        "files_scanned": len(files),
        "total_bytes": total_bytes,
        "file_inventory_sha256": inventory_hash.hexdigest(),
        "longest_non_delimited_token": max_token,
        "longest_contiguous_tab_run": max_tab_run,
        "limitations": [
            "Does not parse indexed binary TEXT.* localization tables.",
            "Does not establish which file strings reach LayoutAndRenderWrappedFrontendText.",
            "A shorter textual scan result is not proof of safe runtime inputs or absence of dynamic strings.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory(args.asset_root)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
