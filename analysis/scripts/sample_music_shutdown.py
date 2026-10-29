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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pid", type=int)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seconds", type=float, default=180)
    parser.add_argument("--interval", type=float, default=0.1)
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
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", buffering=1) as output:
            def emit(row):
                output.write(json.dumps(row) + "\n")

            emit({"kind": "metadata", "pid": args.pid, "process_start": started,
                  "exe_sha256": EXPECTED_SHA256, "interval": args.interval,
                  "seconds": args.seconds, "maps": proc.joinpath("maps").read_text(),
                  "method": "O_RDONLY pread; asynchronous snapshots; no suspension or writes",
                  "limits": "No service-call tracing; handle is not assumed to be a row index; pointers are not dereferenced"})
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
                    emit({"kind": "sample", "t": time.monotonic() - begin,
                          "music_handle": struct.unpack("<I", read(0x564690, 4))[0],
                          "music_target": struct.unpack("<b", read(0x564702, 1))[0],
                          "voices": voices})
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
