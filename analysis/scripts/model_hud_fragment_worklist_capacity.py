#!/usr/bin/env python3
"""Model the HUD rectangle caller's fragment-list loop from reviewed assembly.

This is a model, not execution of the caller. It reuses the 16 original-byte
helper output templates retained by rectangle-fragment-mask-audit.json, then
applies the caller's replace/append/delete/restart control flow to synthetic
rectangles. It exists to test whether the caller's two 15-record local arrays
are obviously sufficient for a small exclusion count.
"""
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_REPORT = ROOT / "analysis/evidence/probes/rectangle-fragment-mask-audit.json"
DEFAULT_OUTPUT = ROOT / "analysis/evidence/probes/hud-fragment-worklist-capacity-model.json"
ARRAY_CAPACITY = 15
SOURCE = (0.0, 0.0, 100.0, 100.0)
EXCLUSIONS = [
    (16.0, 15.0, 38.0, 60.0),
    (7.0, 70.0, 75.0, 72.0),
    (79.0, 39.0, 84.0, 76.0),
    (97.0, 7.0, 99.0, 86.0),
]


def positive_overlap(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def pairwise_disjoint(rectangles):
    return all(not positive_overlap(a, b)
               for i, a in enumerate(rectangles) for b in rectangles[i + 1:])


def intersect_and_mask(source, exclusion):
    ix0 = max(source[0], exclusion[0])
    iy0 = max(source[1], exclusion[1])
    ix1 = min(source[2], exclusion[2])
    iy1 = min(source[3], exclusion[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return None
    mask = ((1 if iy1 < source[3] else 0)
            | (2 if iy0 > source[1] else 0)
            | (4 if ix1 < source[2] else 0)
            | (8 if ix0 > source[0] else 0))
    return (ix0, iy0, ix1, iy1), mask


def transform_template(rectangle, source, intersection):
    """Map canonical 0/2/8/10 coordinates to source/intersection sides."""
    ix0, iy0, ix1, iy1 = intersection
    xmap = {0.0: source[0], 2.0: ix0, 8.0: ix1, 10.0: source[2]}
    ymap = {0.0: source[1], 2.0: iy0, 8.0: iy1, 10.0: source[3]}
    return (xmap[rectangle[0]], ymap[rectangle[1]],
            xmap[rectangle[2]], ymap[rectangle[3]])


def model_fragment_list(source, exclusions, templates):
    fragments = [source]
    index = 0
    trace = []
    first_overflow = None

    while index < len(fragments):
        exclusion_index = 0
        while exclusion_index < len(exclusions):
            current = fragments[index]
            clipped = intersect_and_mask(current, exclusions[exclusion_index])
            if clipped is None:
                exclusion_index += 1
                continue

            intersection, mask = clipped
            template = templates[mask]
            pieces = [transform_template(rect, current, intersection) for rect in template]
            if len(pieces) != mask.bit_count():
                raise AssertionError(f"mask {mask:#x} template count mismatch")

            before = len(fragments)
            if not pieces:
                fragments[index] = fragments[-1]
                fragments.pop()
                trace.append({"fragment_index": index, "exclusion_index": exclusion_index,
                              "mask": mask, "action": "delete_and_swap_last",
                              "worklist_count": len(fragments)})
                if index < len(fragments):
                    exclusion_index = 0
                else:
                    exclusion_index = len(exclusions)
                continue

            fragments[index] = pieces[0]
            appended = pieces[1:]
            for append_offset, piece in enumerate(appended):
                destination_index = before + append_offset
                if first_overflow is None and destination_index >= ARRAY_CAPACITY:
                    first_overflow = {
                        "fragment_index": index,
                        "exclusion_index": exclusion_index,
                        "mask": mask,
                        "worklist_count_before": before,
                        "destination_record_index": destination_index,
                        "capacity": ARRAY_CAPACITY,
                    }
                fragments.append(piece)

            trace.append({"fragment_index": index, "exclusion_index": exclusion_index,
                          "mask": mask, "action": "replace_first_append_rest",
                          "piece_count": len(pieces), "worklist_count": len(fragments)})
            exclusion_index += 1
        index += 1

    return fragments, trace, first_overflow


def load_templates():
    report = json.loads(TEMPLATE_REPORT.read_text())
    templates = {case["mask"]: case["rectangles_xyxy"]
                 for case in report["cases"] if "mask" in case}
    if set(templates) != set(range(16)):
        raise SystemExit("retained helper report does not contain all 16 mask templates")
    canonical_source = (0.0, 0.0, 10.0, 10.0)
    for mask, actual_rectangles in templates.items():
        intersection = (2.0 if mask & 8 else 0.0,
                        2.0 if mask & 2 else 0.0,
                        8.0 if mask & 4 else 10.0,
                        8.0 if mask & 1 else 10.0)
        rebuilt = [transform_template(rect, canonical_source, intersection)
                   for rect in actual_rectangles]
        if rebuilt != [tuple(rect) for rect in actual_rectangles]:
            raise SystemExit(f"mask {mask:#x} template failed canonical self-check")
        if len(actual_rectangles) != mask.bit_count():
            raise SystemExit(f"mask {mask:#x} template has unexpected fragment count")
    return report, templates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    helper_report, templates = load_templates()
    if not pairwise_disjoint(EXCLUSIONS):
        raise AssertionError("synthetic witness exclusions must be pairwise disjoint")
    for rect in [SOURCE, *EXCLUSIONS]:
        if not (rect[0] < rect[2] and rect[1] < rect[3]):
            raise AssertionError(f"rectangle is not finite ordered positive-area: {rect}")
    if any(not (SOURCE[0] <= r[0] < r[2] <= SOURCE[2]
                and SOURCE[1] <= r[1] < r[3] <= SOURCE[3]) for r in EXCLUSIONS):
        raise AssertionError("all synthetic exclusions must lie inside source")

    fragments, trace, first_overflow = model_fragment_list(SOURCE, EXCLUSIONS, templates)
    if first_overflow is None:
        raise AssertionError("the fixed synthetic witness no longer exceeds the 15-record arrays")

    output = {
        "method": "Assembly-derived model of ClipAndSubmitHudTexturedRectangleFragments replace/append/delete/restart loop; fragment templates come from all 16 unchanged-helper cases in rectangle-fragment-mask-audit.json. The caller itself is not executed.",
        "helper_report": "analysis/evidence/probes/rectangle-fragment-mask-audit.json",
        "helper_target_sha256": helper_report["target_sha256"],
        "caller": "ClipAndSubmitHudTexturedRectangleFragments at 00487620",
        "local_arrays": {"position_records": ARRAY_CAPACITY, "paired_coordinate_records": ARRAY_CAPACITY,
                         "bytes_each": ARRAY_CAPACITY * 16},
        "source_xyxy": SOURCE,
        "synthetic_exclusions_xyxy": EXCLUSIONS,
        "exclusion_rectangles_pairwise_disjoint": True,
        "exclusion_count": len(EXCLUSIONS),
        "result": {
            "final_fragment_count": len(fragments),
            "first_out_of_bounds_append": first_overflow,
            "final_fragment_rectangles_xyxy": fragments,
            "steps": trace,
        },
        "limitations": [
            "Only synthetic finite ordered rectangles are modeled.",
            "The model follows reviewed caller control flow and retained original-helper output templates; it does not execute the caller bytes.",
            "The four-record witness does not prove that the game's HUD producers can create these coordinates or reach mode 2 with them.",
            "No live overflow, memory corruption, visual defect, or reachable game bug is established.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"output": str(args.output),
                      "final_fragment_count": len(fragments),
                      "first_out_of_bounds_append": first_overflow}, indent=2))


if __name__ == "__main__":
    main()
