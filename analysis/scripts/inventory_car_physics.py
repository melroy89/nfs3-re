#!/usr/bin/env python3
"""Read installed BIGF CARP resources without running or changing the game."""

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def float32(value):
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def inventory(game_root):
    root = game_root.resolve()
    rows = []
    for path in sorted((root / "GAMEDATA/CARMODEL").rglob("*")):
        if not path.is_file() or path.suffix.lower() != ".viv":
            continue
        archive = path.read_bytes()
        if archive[:4] != b"BIGF":
            raise ValueError(f"Not BIGF: {path}")
        declared_size, count, header_size = struct.unpack_from(">III", archive, 4)
        if declared_size != len(archive):
            raise ValueError(f"Archive size mismatch: {path}")
        at = 16
        for _ in range(count):
            offset, size = struct.unpack_from(">II", archive, at)
            end = archive.index(b"\0", at + 8, header_size)
            name = archive[at + 8:end].decode("ascii")
            at = end + 1
            if offset < header_size or offset + size > len(archive):
                raise ValueError(f"Invalid member extent: {path}: {name}")
            if name.lower() != "carp.txt":
                continue
            payload = archive[offset:offset + size]
            lines = payload.decode("latin1").splitlines()
            fields = {}
            for i, line in enumerate(lines[:-1]):
                match = re.search(r"\((\d+)\)\s*$", line)
                if match:
                    key = int(match.group(1))
                    if key in fields:
                        raise ValueError(f"Duplicate CARP field {key}: {path}")
                    fields[key] = lines[i + 1].strip()
            idle, redline = int(fields[12]), int(fields[13])
            ratios = {
                kind: [float32(x) for x in fields[key].split(",")]
                for kind, key in (("manual", 7), ("automatic", 76))
            }
            if any(len(values) != 8 for values in ratios.values()):
                raise ValueError(f"Expected eight ratio entries: {path}")
            modifiers = [float32(fields[key]) for key in (52, 53, 54)]
            anti_lock_raw = fields.get(17)
            anti_lock_value = int(anti_lock_raw or "0") & 0xFF
            if not all(math.isfinite(x) for values in ratios.values() for x in values):
                raise ValueError(f"Nonfinite ratio: {path}")
            if not all(math.isfinite(x) for x in modifiers):
                raise ValueError(f"Nonfinite speed modifier: {path}")
            rows.append({
                "archive": path.relative_to(root).as_posix(),
                "archive_sha256": digest(archive),
                "archive_bytes": len(archive),
                "member": name,
                "member_sha256": digest(payload),
                "member_offset": offset,
                "member_bytes": size,
                "classification": int(fields[1]),
                "uses_anti_lock_raw": anti_lock_raw,
                "uses_anti_lock_low_byte": anti_lock_value,
                "gear_counts": {"manual": int(fields[3]), "automatic": int(fields[75])},
                "idle_rpm": idle,
                "redline_rpm": redline,
                "denominator": redline - idle,
                "velocity_to_rpm_float32": ratios,
                "corner_speed_modifiers_float32": modifiers,
            })
    if not rows:
        raise ValueError("No CARP profiles found")
    ratios = [x for row in rows for values in row["velocity_to_rpm_float32"].values() for x in values]
    modifiers = [x for row in rows for x in row["corner_speed_modifiers_float32"]]
    return {
        "method": "Read-only BIGF extraction; decimal fields converted to IEEE float32 using Python nearest-even conversion. Not execution of the game parser.",
        "scope": "All .viv files under installed GAMEDATA/CARMODEL; gamedata_org excluded. No runtime samples or tuning applied.",
        "uses_anti_lock_policy": "CARP field17 is parsed as an integer and stored as its low byte; the profile initializer defaults this byte to0 when absent. Raw absence is retained as null. Inventory does not establish which profiles are loaded at runtime.",
        "target_sha256": digest((root / "nfs3.exe").read_bytes()),
        "field_ids": {"idle": 12, "redline": 13, "manual_ratios": 7, "automatic_ratios": 76, "corner_modifiers": [52, 53, 54], "uses_anti_lock": 17},
        "summary": {
            "profiles": len(rows),
            "anti_lock_low_byte_values": sorted({r["uses_anti_lock_low_byte"] for r in rows}),
            "anti_lock_nonzero_profiles": sum(r["uses_anti_lock_low_byte"] != 0 for r in rows),
            "idle_range": [min(r["idle_rpm"] for r in rows), max(r["idle_rpm"] for r in rows)],
            "redline_range": [min(r["redline_rpm"] for r in rows), max(r["redline_rpm"] for r in rows)],
            "denominator_range": [min(r["denominator"] for r in rows), max(r["denominator"] for r in rows)],
            "all_denominators_positive": all(r["denominator"] > 0 for r in rows),
            "ratio_range_float32": [min(ratios), max(ratios)],
            "corner_modifier_range_float32": [min(modifiers), max(modifiers)],
            "all_corner_modifiers_in_zero_one": all(0 <= x <= 1 for x in modifiers),
            "conservative_abs_rpm_product_bound_speed_abs_le_255": 255 * max(abs(x) for x in ratios),
        },
        "profiles": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(inventory(args.game_root), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    else:
        print(result, end="")
