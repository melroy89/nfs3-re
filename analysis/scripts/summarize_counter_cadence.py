#!/usr/bin/env python3
"""Reproduce positive-stepping blocks from a retained gameplay JSONL capture.

Reads files only. Output rates describe sampled counter advance, not render FPS.
"""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(path, minimum_samples=10):
    blocks = []
    block = []
    previous = None
    metadata = None

    def finish():
        if len(block) >= minimum_samples:
            first, last = block[0], block[-1]
            elapsed = last['t'] - first['t']
            delta = last['simulation_tick'] - first['simulation_tick']
            blocks.append(dict(samples=len(block), first=first, last=last,
                               elapsed_seconds=elapsed, tick_delta=delta,
                               average_ticks_per_second=delta / elapsed,
                               sequence_equals_tick_all_samples=all(
                                   p['simulation_tick'] == p['race_sequence'] for p in block)))

    digest = hashlib.sha256()
    with path.open('rb') as capture:
        for raw in capture:
            digest.update(raw)
            row = json.loads(raw)
            if row.get('kind') == 'metadata':
                metadata = row
                continue
            if row.get('kind') not in ('sample', 'error'):
                continue
            state = row.get('gameplay', {})
            values = state.get('globals', {})
            vehicles = state.get('vehicles', [])
            readable = (row.get('kind') == 'sample'
                        and values.get('configured_vehicles') == 8
                        and len(vehicles) == 8
                        and all('read_error' not in v for v in vehicles))
            if not readable:
                finish()
                block, previous = [], None
                continue
            point = dict(t=row['t'], simulation_tick=values['simulation_tick'],
                         race_sequence=values['race_sequence'])
            if (previous is not None and point['t'] > previous['t']
                    and point['simulation_tick'] > previous['simulation_tick']):
                if not block:
                    block.append(previous)
                block.append(point)
            else:
                finish()
                block = []
            previous = point
    finish()
    if metadata is None:
        raise ValueError('capture has no metadata record')
    return dict(exe_sha256=metadata['exe_sha256'], raw_capture_sha256=digest.hexdigest(),
                blocks=blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.capture), indent=2))


if __name__ == '__main__':
    main()
