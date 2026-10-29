"""Bounded read-only capture for the documented NFS3 music-stop investigation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import struct
import time


EXPECTED_SHA256 = "2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb"
SIGNATURE = bytes.fromhex("5351528d0c850000000029c1c1e105")  # 005014a0
GAMEPLAY_GLOBALS = {
    "session_mode": 0x6FD3B0, "race_mode": 0x6FD3B8,
    "track": 0x6FD4AC, "laps": 0x6FD4B4, "reverse": 0x6FD4C0,
    "opponent_choice": 0x6FD4D0, "opponent_model_choice": 0x6FD4D4,
    "traffic_disabled": 0x6FD4E8, "ai_skill": 0x6FD4F0,
    "local_index": 0x6FD4F4, "configured_vehicles": 0x6FD510,
    "configured_humans": 0x6FD514, "human_racers": 0x6FD518,
    "ai_racers": 0x6FD520, "ai_police": 0x6FD524,
    "inactive_ai": 0x56EBC0, "registry_count": 0x5F3CC8,
    "simulation_tick": 0x7D3684, "race_sequence": 0x7D36B0,
    "race_exit": 0x7D36B4,
}


def gameplay_snapshot(read):
    """Bounded asynchronous state; configured counts do not prove visibility."""
    values = {name: struct.unpack("<i", read(address, 4))[0]
              for name, address in GAMEPLAY_GLOBALS.items()}
    rows = []
    count = values["configured_vehicles"]
    if 0 <= count <= 16:
        pointers = struct.unpack("<16I", read(0x5EFAC8, 64))
        for index, pointer in enumerate(pointers[:count]):
            row = {"index": index, "pointer": pointer}
            try:
                if not pointer:
                    raise OSError("null vehicle pointer")
                raw = read(pointer, 0x654)
                integer = lambda offset: struct.unpack_from("<i", raw, offset)[0]
                row.update({"progress": integer(8), "segment": integer(0x1C),
                            "byte_88": raw[0x88], "active_89": raw[0x89],
                            "correction_timer": integer(0x174),
                            "category": integer(0x200), "wrap_counter": integer(0x204),
                            "auxiliary_wrap": integer(0x208),
                            "result_state": integer(0x2C4),
                            "activation_state": integer(0x630),
                            "activation_countdown": integer(0x650)})
            except (OSError, OverflowError) as error:
                row["read_error"] = str(error)
            rows.append(row)
    return {"globals": values, "vehicles": rows,
            "vehicle_scan_skipped": not 0 <= count <= 16}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pid", type=int)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seconds", type=float, default=180)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--gameplay-state", action="store_true",
                        help="also sample setup globals and up to16 vehicle activity records")
    args = parser.parse_args()
    if args.pid <= 0:
        parser.error("pid must be positive")
    if not math.isfinite(args.seconds) or not 1 <= args.seconds <= 600:
        parser.error("seconds must be finite and between 1 and 600")
    if not math.isfinite(args.interval) or not 0.05 <= args.interval <= 10:
        parser.error("interval must be finite and between 0.05 and 10")
    if hashlib.sha256(args.exe.read_bytes()).hexdigest() != EXPECTED_SHA256:
        parser.error("executable fingerprint does not match the documented build")
    proc = Path(f"/proc/{args.pid}")
    if proc.joinpath("comm").read_text().strip().lower() != "nfs3.exe":
        parser.error("target process is not nfs3.exe")

    def identity():
        # Start time is field22; comm can contain spaces or parentheses.
        return proc.joinpath("stat").read_text().rsplit(")", 1)[1].split()[19]

    started = identity()
    stopping = False

    def stop(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    fd = os.open(proc / "mem", os.O_RDONLY)
    try:
        def read(address, size):
            data = os.pread(fd, size, address)
            if len(data) != size:
                raise OSError(f"short read at {address:08x}")
            return data

        if read(0x400000, 2) != b"MZ" or read(0x5014A0, len(SIGNATURE)) != SIGNATURE:
            parser.error("live image signature does not match the fixed address map")
        # Verify all fixed ranges before reporting readiness or creating output.
        read(0xA09B3C, 16 * 0x60)
        read(0x564690, 4)
        read(0x564702, 1)
        if args.gameplay_state:
            for address in GAMEPLAY_GLOBALS.values():
                read(address, 4)
            read(0x5EFAC8, 64)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", buffering=1) as output:
            def emit(row):
                output.write(json.dumps(row) + "\n")

            emit({"kind": "metadata", "pid": args.pid, "process_start": started,
                  "exe_sha256": EXPECTED_SHA256, "interval": args.interval,
                  "seconds": args.seconds, "maps": proc.joinpath("maps").read_text(),
                  "method": "O_RDONLY pread; asynchronous snapshots; no suspension or writes",
                  "gameplay_addresses": GAMEPLAY_GLOBALS if args.gameplay_state else None,
                  "limits": "No service-call tracing; handle is not assumed to be a row index; optional vehicle reads are non-atomic and do not prove visibility or object lifetime"})
            print("READY: fixed ranges and read-only access verified; capture running", flush=True)
            begin = time.monotonic()
            count = 0
            while not stopping and time.monotonic() - begin < args.seconds:
                try:
                    if identity() != started:
                        raise OSError("process identity changed")
                    raw = read(0xA09B3C, 16 * 0x60)
                    voices = []
                    for index in range(16):
                        record = raw[index * 0x60:(index + 1) * 0x60]
                        signed = lambda offset: struct.unpack_from("<i", record, offset)[0]
                        unsigned = lambda offset: struct.unpack_from("<I", record, offset)[0]
                        voices.append({"row": index, "raw": record.hex(),
                                       "handle": signed(0), "state_0c": record[0x0C],
                                       "delta_18": signed(0x18), "target_1c": signed(0x1C),
                                       "current_20": signed(0x20),
                                       "effective_31": struct.unpack_from("<b", record, 0x31)[0],
                                       "response_4c": unsigned(0x4C), "modulation_58": unsigned(0x58)})
                    sample = {"kind": "sample", "t": time.monotonic() - begin,
                          "music_handle": struct.unpack("<I", read(0x564690, 4))[0],
                          "music_target": struct.unpack("<b", read(0x564702, 1))[0],
                          "voices": voices}
                    if args.gameplay_state:
                        sample["gameplay"] = gameplay_snapshot(read)
                    emit(sample)
                    count += 1
                except (OSError, ProcessLookupError) as error:
                    emit({"kind": "error", "t": time.monotonic() - begin, "message": str(error)})
                    break
                time.sleep(min(args.interval, max(0, args.seconds - (time.monotonic() - begin))))
            emit({"kind": "end", "samples": count, "elapsed": time.monotonic() - begin})
            print(f"Capture stopped: {count} samples", flush=True)
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
