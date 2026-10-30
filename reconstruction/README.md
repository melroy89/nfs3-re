# First maintained module: line-boundary candidate

Only original function `00485c30..00485f1a` is reconstructed here. This is a standalone test module, not a replacement game component. Generated reference exports remain separate under ignored `analysis/captures/reference-exports/`.

| Maintained symbol | Original identity |
|---|---|
| `Nfs3LineBoundaryCandidate_00485c30` | Candidate helper at `00485c30` |
| `gLineBoundaryCandidate_00791c08[0]` | Shared binary32 component at `00791c08` |
| `gLineBoundaryCandidate_00791c08[1]` | Shared binary32 component at `00791c0c` |

The public test function uses ordinary C `cdecl`. Its input arrays have extents 2/4/4 floats; rectangle order is yMin,xMin,yMax,xMax. A zero policy returns shared storage even after a rejected candidate; nonzero policy can return null. Mask bits are ORed, not cleared. Scratch may change on rejection and persists between calls. No locks, per-call scratch or canonical-clipping corrections were added.

The implementation records original rounding points, uses binary32 volatile stores and x87 extended `long double` intermediates, and preserves the differing unrounded-versus-reloaded bound tests. It requires GCC-compatible bit copying and x87 extended long double; it is not yet a compiler-independent numerical implementation. The maintained C boundary is suitable for a later native Linux port, but that port's target/compiler/FPU behavior still needs qualification.

## Reproduce

Run from the repository root. Linux native i386 comparison (304 rows):

```sh
python3 -m unittest reconstruction.tests.test_line_boundary -v
```

Windows i686 PE comparison under Wine (40 retained rows):

```sh
MINGW_CC="$HOME/.local/opt/nfs3-mingw/usr/bin/i686-w64-mingw32-gcc-posix" \
  python3 reconstruction/tests/test_line_boundary_windows.py
```

The six required MinGW Debian/Ubuntu packages were downloaded through APT and extracted to that user-local directory. No root credentials or system package changes were needed. Native runtime dependencies already existed. Package versions/hashes are retained in local `analysis/captures/reconstruction/line-boundary/toolchain.json`; compiler version, flags and artifacts are recorded by the Windows runner.

Both builds use C11, O0, x87 arithmetic, no fast math/contraction, rounding-math awareness and standard excess-precision semantics. Windows additionally links a standalone static-runtime PE test executable, with its own CRT and test-only register adapter. All build products, extracted original instructions and Wine prefix stay under ignored analysis paths. Neither test launches or patches the game.

## Evidence boundary

[Results and follow-up gates](../analysis/line-boundary-reconstruction-results.md) distinguish functional outputs from complete machine state. Exact return-storage class, scratch bits and masks match for the tested cases; input buffers/canaries and control words remain unchanged. x87 status words do **not** fully match. This is not full register/flags/x87-tag equivalence, optimized-code qualification, native-Windows hardware validation, caller integration or gameplay proof.

The original game passes candidate/line/bounds/policy in EAX/EDX/EBX/ECX and pops one stack argument with RET4. The Windows adapter invokes only the original comparison oracle and preserves its caller's ABI; it is not a game-facing replacement adapter. Linux runs original bytes at their original VA; the Windows runner relocates only the 29 verified HIGHLOW scratch-address operands in its private instruction copy because fixed low-address allocation failed under Wine. The original executable remains unchanged.
