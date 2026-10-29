#!/usr/bin/env python3
"""Exhaustively model two bounded exclusions through the reviewed HUD loop.

Uses original-helper output templates retained by rectangle-fragment-mask-audit.json
and the existing assembly-derived caller model. This does not execute game code.
"""
import itertools
import json
from pathlib import Path

from model_hud_fragment_worklist_capacity import (
    ARRAY_CAPACITY,
    load_templates,
    model_fragment_list,
    pairwise_disjoint,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "analysis/evidence/probes/hud-bounded-exclusion-capacity.json"
EXECUTABLE_SHA256 = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"
SOURCE = (0.0, 0.0, 5.0, 5.0)
DOMAIN = tuple(float(v) for v in range(6))


def main():
    helper_report, templates = load_templates()
    intervals = [(lo, hi) for lo in DOMAIN for hi in DOMAIN if lo <= hi]
    maximum = {"count": -1, "witness": None}
    maximum_disjoint = {"count": -1, "witness": None}
    maximum_peak = {"count": -1, "witness": None}
    maximum_disjoint_peak = {"count": -1, "witness": None}
    any_overflow = None
    any_disjoint_overflow = None
    case_count = 0
    disjoint_case_count = 0

    for x_intervals in itertools.product(intervals, repeat=2):
        for y_intervals in itertools.product(intervals, repeat=2):
            exclusions = [
                (x[0], y[0], x[1], y[1])
                for x, y in zip(x_intervals, y_intervals)
            ]
            fragments, trace, first_overflow = model_fragment_list(
                SOURCE, exclusions, templates
            )
            case_count += 1
            peak_count = max(
                [1] + [step["worklist_count"] for step in trace]
            )
            witness = {"rectangles_xyxy": exclusions,
                       "first_overflow": first_overflow,
                       "peak_worklist_count": peak_count,
                       "final_worklist_count": len(fragments)}
            if len(fragments) > maximum["count"]:
                maximum = {"count": len(fragments), "witness": witness}
            if peak_count > maximum_peak["count"]:
                maximum_peak = {"count": peak_count, "witness": witness}
            if first_overflow is not None and any_overflow is None:
                any_overflow = witness

            if pairwise_disjoint(exclusions):
                disjoint_case_count += 1
                if len(fragments) > maximum_disjoint["count"]:
                    maximum_disjoint = {
                        "count": len(fragments),
                        "witness": witness,
                    }
                if peak_count > maximum_disjoint_peak["count"]:
                    maximum_disjoint_peak = {
                        "count": peak_count,
                        "witness": witness,
                    }
                if first_overflow is not None and any_disjoint_overflow is None:
                    any_disjoint_overflow = witness

    output = {
        "method": (
            "Exhaustive axis-order model of two ordered rectangles clipped to "
            "one ordered source rectangle, using all retained original-helper "
            "templates and the assembly-derived 00487620 caller model."
        ),
        "executable_sha256": EXECUTABLE_SHA256,
        "helper_report": "analysis/evidence/probes/rectangle-fragment-mask-audit.json",
        "helper_target_sha256": helper_report["target_sha256"],
        "caller_model": "analysis/scripts/model_hud_fragment_worklist_capacity.py",
        "local_array_capacity_each": ARRAY_CAPACITY,
        "source_xyxy_representative": SOURCE,
        "endpoint_domain_representative": list(DOMAIN),
        "rectangle_interval_orderings_per_axis": len(intervals),
        "exhaustive_case_count": case_count,
        "pairwise_disjoint_case_count": disjoint_case_count,
        "maximum_all_two_rectangles": maximum,
        "maximum_pairwise_disjoint_two_rectangles": maximum_disjoint,
        "maximum_peak_all_two_rectangles": maximum_peak,
        "maximum_peak_pairwise_disjoint_two_rectangles": maximum_disjoint_peak,
        "any_overflow_witness_all_cases": any_overflow,
        "any_overflow_witness_pairwise_disjoint_cases": any_disjoint_overflow,
        "result": {
            "maximum_fragment_count": maximum["count"],
            "maximum_disjoint_fragment_count": maximum_disjoint["count"],
            "maximum_peak_worklist_count": maximum_peak["count"],
            "maximum_disjoint_peak_worklist_count": maximum_disjoint_peak["count"],
            "overflow_in_any_case": any_overflow is not None,
            "overflow_in_any_pairwise_disjoint_case": any_disjoint_overflow is not None,
        },
        "coverage_reason": (
            "For two axis-aligned rectangles, each axis has four exclusion "
            "endpoints plus the two source endpoints. Six ordered coordinate "
            "levels represent every strict ordering; tied levels represent "
            "equalities. Coordinates outside the source clip to a source edge "
            "before the helper mask and output geometry are selected, so their "
            "distances do not add cases. The grid therefore covers every "
            "finite ordered rectangle-intersection topology for two exclusions."
        ),
        "limitations": [
            "This proves only the fragment-count bound for at most two ordinary ordered exclusions through the modeled caller logic.",
            "It does not prove runtime path selection, persistent counter lifecycle across every cache transition, arbitrary nonfinite values, or renderer effects.",
            "Nondefault selector combinations may enable more than two geometry producers; their joint reachability and exact transformed rectangles are not modeled here.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT),
                      "cases": case_count,
                      "pairwise_disjoint_cases": disjoint_case_count,
                      "maximum": maximum["count"],
                      "maximum_disjoint": maximum_disjoint["count"],
                      "maximum_peak": maximum_peak["count"],
                      "maximum_disjoint_peak": maximum_disjoint_peak["count"],
                      "overflow_in_any_case": output["result"]["overflow_in_any_case"],
                      "overflow_in_any_disjoint_case": output["result"]["overflow_in_any_pairwise_disjoint_case"]},
                     indent=2))


if __name__ == "__main__":
    main()
