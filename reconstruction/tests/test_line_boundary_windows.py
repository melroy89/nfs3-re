"""Run a Windows i686 PE differential harness under an isolated Wine prefix."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CAPTURES = ROOT / "analysis/captures/line-boundary-windows"
PROBE = ROOT / "analysis/scripts/probe_line_boundary_helper.py"
DEFAULT_EXE = ROOT / "nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe"
ENTRY, END, SCRATCH = 0x485C30, 0x485F1B, 0x791C08
RECORD = struct.Struct("<10fIII")
RESULT = struct.Struct("<IIIIHHI")


def _load_probe():
    spec = importlib.util.spec_from_file_location("line_boundary_probe_fixture", PROBE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _run() -> dict:
    probe = _load_probe()
    exe = Path(os.environ.get("NFS3_BINARY", DEFAULT_EXE)).resolve()
    cc = os.environ.get("MINGW_CC", "/home/melroy/.local/opt/nfs3-mingw/usr/bin/i686-w64-mingw32-gcc-posix")
    wine = shutil.which(os.environ.get("WINE", "wine")) or shutil.which("wine-stable")
    if not exe.is_file():
        raise AssertionError(f"NFS3 executable not found: {exe}")
    if not Path(cc).is_file() or not wine:
        raise AssertionError(f"Windows harness tools unavailable: compiler={cc!r}, wine={wine!r}")
    original = exe.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    assert digest == probe.EXPECTED_SHA256, "Unexpected executable fingerprint"
    import pefile
    pe = pefile.PE(data=original)
    assert pe.FILE_HEADER.Machine == 0x14C and pe.OPTIONAL_HEADER.ImageBase == 0x400000
    code = pe.get_data(ENTRY - pe.OPTIONAL_HEADER.ImageBase, END - ENTRY)
    assert len(code) == 747 and code[-3:] == b"\xc2\x04\x00"

    inputs = bytearray()
    metadata = []
    for name, values in probe.CASES:
        values = tuple(probe.f32(v) for v in values)
        for policy in probe.POLICIES:
            inputs.extend(RECORD.pack(*(values + probe.RECTANGLE), policy,
                                      probe.INITIAL_MASK, probe.CONTROL_WORD))
            metadata.append({"case": name, "policy": policy})

    CAPTURES.mkdir(parents=True, exist_ok=True)
    prefix = CAPTURES / "wineprefix"
    binary = CAPTURES / "line_boundary_windows.exe"
    function_path = CAPTURES / "original_00485c30.bin"
    vectors_path = CAPTURES / "vectors.bin"
    raw_path = CAPTURES / "results.bin"
    function_path.write_bytes(code)
    vectors_path.write_bytes(inputs)
    flags = ["-std=c11", "-O0", "-g", "-mfpmath=387", "-fno-fast-math",
             "-ffp-contract=off", "-frounding-math", "-fexcess-precision=standard",
             "-Wall", "-Wextra", "-Werror", "-mno-sse", "-static",
             "-Wl,--image-base,0x10000000"]
    command = [cc, *flags,
               str(ROOT / "reconstruction/tests/windows_harness.c"),
               str(ROOT / "reconstruction/tests/windows_adapter.S"),
               str(ROOT / "reconstruction/line_boundary.c"),
               "-o", str(binary)]
    compiled = subprocess.run(command, capture_output=True, text=True)
    assert compiled.returncode == 0, f"MinGW compilation failed:\n{compiled.stdout}\n{compiled.stderr}"
    env = os.environ.copy()
    env.update({"WINEPREFIX": str(prefix), "WINEARCH": "win32", "WINEDEBUG": "-all"})
    wine_version = subprocess.run([wine, "--version"], env=env, capture_output=True,
                                  text=True, check=True, timeout=15).stdout.strip()
    # Wine creates this dedicated prefix on first invocation; it is never the game prefix.
    run_command = [wine, str(binary), str(function_path), str(vectors_path), str(raw_path)]
    ran = subprocess.run(run_command, env=env, capture_output=True, text=True, timeout=60)
    assert ran.returncode == 0, f"Wine harness failed ({ran.returncode}):\n{ran.stdout}\n{ran.stderr}"
    raw = raw_path.read_bytes()
    assert len(raw) == 8 + 80 * RESULT.size
    code_mapping, scratch_mapping = struct.unpack_from("<II", raw)

    observations = []
    functional_differences, status_differences = [], []
    for i, meta in enumerate(metadata):
        original_result = RESULT.unpack_from(raw, 8 + i * RESULT.size)
        maintained = RESULT.unpack_from(raw, 8 + (40 + i) * RESULT.size)
        names = ("return", "candidate0", "candidate1", "mask", "control_word", "status_word", "raw_return")
        a, b = dict(zip(names, original_result)), dict(zip(names, maintained))
        # PE address and linked C global are distinct. Compare pointer class (null/shared storage).
        functional = {
            "return_storage_class": (a["return"], b["return"]),
            "scratch_bits": ([f"0x{a['candidate0']:08x}", f"0x{a['candidate1']:08x}"],
                             [f"0x{b['candidate0']:08x}", f"0x{b['candidate1']:08x}"]),
            "mask": (a["mask"], b["mask"]),
            "control_word": (a["control_word"], b["control_word"]),
        }
        for key, (left, right) in functional.items():
            if left != right:
                functional_differences.append({**meta, "field": key, "original": left, "maintained": right})
        if a["status_word"] != b["status_word"]:
            status_differences.append({**meta, "original": f"0x{a['status_word']:04x}",
                                      "maintained": f"0x{b['status_word']:04x}"})
        observations.append({**meta,
            "original_return_storage_class": {0: "null", 1: "shared_result", 2: "unexpected"}.get(a["return"], "unexpected"),
            "maintained_return_storage_class": {0: "null", 1: "shared_result", 2: "unexpected"}.get(b["return"], "unexpected"),
            "original_raw_return": f"0x{a['raw_return']:08x}",
            "pointer_class_equal": a["return"] == b["return"],
            "original_scratch_bits": functional["scratch_bits"][0],
            "maintained_scratch_bits": functional["scratch_bits"][1],
            "original_mask": f"0x{a['mask']:02x}", "maintained_mask": f"0x{b['mask']:02x}",
            "original_cw": f"0x{a['control_word']:04x}", "maintained_cw": f"0x{b['control_word']:04x}",
            "original_sw": f"0x{a['status_word']:04x}", "maintained_sw": f"0x{b['status_word']:04x}"})

    report = {
        "source_executable": str(exe), "source_sha256": digest,
        "artifacts": {
            "original_function_path": str(function_path),
            "original_function_sha256": hashlib.sha256(code).hexdigest(),
            "input_vectors_path": str(vectors_path),
            "input_vectors_sha256": hashlib.sha256(inputs).hexdigest(),
            "windows_pe_path": str(binary),
            "windows_pe_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "raw_results_path": str(raw_path),
            "raw_results_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "method": "Windows i686 PE under Wine; unchanged original function bytes are retained as an artifact; a private copy has only its 29 verified scratch absolute operands relocated to VirtualAlloc-selected private scratch storage.",
        "function_va": f"0x{ENTRY:08x}", "function_length": len(code),
        "private_code_mapping": f"0x{code_mapping:08x}",
        "private_scratch_mapping": f"0x{scratch_mapping:08x}",
        "private_scratch_candidate_address": f"0x{scratch_mapping + 0x1c08:08x}",
        "private_copy_relocations": 29,
        "pe_image_base": "0x10000000", "wine_version": wine_version,
        "wine_prefix": str(prefix), "compiler": cc, "compile_command": command,
        "compile_stdout": compiled.stdout, "compile_stderr": compiled.stderr,
        "wine_command": run_command, "wine_stdout": ran.stdout, "wine_stderr": ran.stderr,
        "fixture_count": len(observations), "scratch_seed": "zero once per independent 40-row implementation sequence",
        "input_arrays_unchanged": True, "input_canaries_unchanged": True,
        "control_word": "FNINIT then load 0x037f before each call",
        "functional_differences": functional_differences,
        "x87_status_word_differences": status_differences,
        "functional_match": not functional_differences,
        "observations": observations,
        "limitations": ["Synthetic fixture inputs only; no game launch or gameplay.",
                        "Returned pointers are compared by null/storage class because linked C storage has its own PE address.",
                        "x87 status-word differences are recorded separately and do not by themselves fail functional comparison."],
    }
    report_path = CAPTURES / "differential.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    assert not functional_differences, f"Functional mismatch; see {report_path}"
    return report


def test_line_boundary_windows_differential():
    report = _run()
    assert report["fixture_count"] == 40
    assert report["functional_match"]


if __name__ == "__main__":
    print(json.dumps(_run(), indent=2))
