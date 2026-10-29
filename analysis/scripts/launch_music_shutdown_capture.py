"""Launch the documented NFS3 build and sample it read-only as its parent.

The Wine child owns a separate session. Ending sampling never intentionally
signals the game. This helper does not restore display modes or edit settings.
"""
import argparse
import hashlib
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

import sample_music_shutdown as sampler


def launch_independent(command, *, cwd, env, log):
    return subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                            stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--prefix", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--wine", default="wine-stable")
    parser.add_argument("--seconds", type=float, default=180)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--gameplay-state", action="store_true")
    parser.add_argument("--controller-state", action="store_true")
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or not 1 <= args.seconds <= 600:
        parser.error("seconds must be finite and between 1 and 600")
    if not math.isfinite(args.interval) or not 0.05 <= args.interval <= 10:
        parser.error("interval must be finite and between 0.05 and 10")
    if not args.exe.is_file() or hashlib.sha256(args.exe.read_bytes()).hexdigest() != sampler.EXPECTED_SHA256:
        parser.error("executable fingerprint does not match the documented build")
    if not (args.prefix / "drive_c").is_dir():
        parser.error("prefix must be an existing Wine prefix")
    wine = shutil.which(args.wine)
    if wine is None:
        parser.error("Wine executable was not found")
    for proc in Path("/proc").glob("[0-9]*/comm"):
        try:
            running = proc.read_text().strip().lower() == "nfs3.exe"
        except OSError:
            continue
        if running:
            parser.error("an NFS3 process is already running; no second instance launched")
    output = args.output.resolve()
    wine_log = output.with_suffix(output.suffix + ".wine.log")
    if output.exists() or wine_log.exists():
        parser.error("output or Wine log already exists; use a new capture path")
    output.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["WINEPREFIX"] = str(args.prefix.resolve())
    with wine_log.open("x") as log:
        child = launch_independent([wine, str(args.exe.resolve())],
                                   cwd=args.exe.resolve().parent, env=env, log=log)
    print(f"Launched Wine PID {child.pid} in its own session; log: {wine_log}", flush=True)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise SystemExit("Wine process ended before readiness; inspect its log. No relaunch attempted.")
        try:
            proc = Path(f"/proc/{child.pid}")
            if proc.joinpath("comm").read_text().strip().lower() == "nfs3.exe":
                fd = os.open(proc / "mem", os.O_RDONLY)
                try:
                    ready = (os.pread(fd, 2, 0x400000) == b"MZ" and
                             os.pread(fd, len(sampler.SIGNATURE), 0x5014A0) == sampler.SIGNATURE and
                             len(os.pread(fd, 16 * 0x60, 0xA09B3C)) == 16 * 0x60)
                finally:
                    os.close(fd)
                if ready:
                    break
        except OSError:
            pass
        time.sleep(0.2)
    else:
        raise SystemExit("Read-only ranges not ready within30seconds; no game signal or relaunch attempted.")
    argv = [str(child.pid), "--exe", str(args.exe.resolve()), "--output", str(output),
            "--seconds", str(args.seconds), "--interval", str(args.interval)]
    if args.gameplay_state:
        argv.append("--gameplay-state")
    if args.controller_state:
        argv.append("--controller-state")
    sampler.main(argv)
    status = "still running" if child.poll() is None else f"exited ({child.returncode})"
    print(f"Capture complete; game process {status}. No game signal sent.", flush=True)


if __name__ == "__main__":
    main()
