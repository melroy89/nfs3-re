# Environment grid: admission policy, renderer mask and vector argument

## Evidence boundary

[The static audit](scripts/audit_environment_grid_difference.py) verifies both pinned executable hashes, three complete same-address function envelopes and the complete new Modern admission helper. [Its manifest](evidence/audits/environment-grid-difference.json) retains span hashes and disassembly locations. No environment, game or instruction probes were executed.

| Saved Modern entry / label | Complete envelope, exclusive end | Difference |
|---|---|---|
| `00479500` BuildPairedNineVectorStrips | `00479500..00479671` (369 bytes) | One binary32 argument 4.0→3.5 |
| `0047a190` DispatchGatedEnvironmentGridWithAuxiliaryPass | `0047a190..0047a1e8` (88 bytes) | Inline gate replaced by helper call |
| `0047b850` BuildEnvironmentGridQuadCommandChain | `0047b850..0047ba68` (536 bytes) | Byte TEST mask `40h`→`50h` |

The matched envelopes include internal NOP gaps. Names are saved analysis labels. Original bytes at new helper `0047b380` are retained only as a same-address witness, not asserted to be its functional counterpart.

## Dispatcher changes its exact admission predicate

Original `0047a1a4..0047a1b2` skips the grid when DWORD `006fbc2c == 1` or incoming context DWORD `[EDX] == 1`. Otherwise it calls grid builder `0047b850`, then optionally calls auxiliary routine `004946e0` when `0055d260` is nonzero.

Modern replaces that inline block with a call to `0047b380`, testing its Boolean return. The complete helper `0047b380..0047b39f` returns 1 precisely when:

`006fbc2c == 0 && (context_tag != 1 || 006fd1d8 == 0)`

Otherwise it returns 0. Consequently:

| Input class | Original | Modern |
|---|---|---|
| `006fbc2c=0`, tag other than 1 | Admit | Admit |
| `006fbc2c=0`, tag 1, `006fd1d8=0` | Skip | Admit |
| `006fbc2c=0`, tag 1, `006fd1d8!=0` | Skip | Skip |
| `006fbc2c=1` | Skip | Skip |
| Other nonzero `006fbc2c`, tag other than 1 | Admit | Skip |

The [night-lighting comparison](original-modern-night-lighting.md) and related settings research establish `006fd1d8=0` as the High rear-view-detail ordinal. The helper's exact predicate is verified independently of assigning a universal semantic meaning to context tag 1 or the other admission field. No input-range validation is added here.

Both versions retain the skipped-path tick copy `007d3684`→`0055d154`, optional auxiliary call and the `00479ed0` call placement controlled by `0055d2a4`. The first 20 dispatcher bytes and all bytes from `0047a1b2` onward are identical. Modern's saved union omits one NOP at `0047a1b1`; the full 88-byte envelope includes it.

## Grid renderer mask admits another renderer type

At `0047b8f4`, the only grid-builder edit changes `TEST BYTE [007a3a58],40h` to mask `50h`. The following zero branch still skips to `0047b91b`, and every other byte in this 536-byte function remains identical. This is the same OR-of-bits policy as the [eleven grouped effect-rendering changes](original-modern-effect-renderer-masks.md): bit `10h` alone now admits the block, while original required bit `40h`. Existing loader evidence maps configured type prefixes `d`→`40h`, `v`→`10h`; this is not validation of particular DLL output.

Other branch conditions still apply before the test. This local mask expansion does not establish that every grid command is generated or that every renderer gets identical output.

## Vector helper changes one floating-point argument

At `0047954c`, original pushes bits `40800000` (4.0); Modern pushes `40600000` (3.5). This argument reaches retained call `004e0050` at `00479559`, alongside local vector pointers and EAX=1. All other bytes in the 369-byte caller are identical.

The verified change is a numerical argument decrease of 0.5, not merely constant relocation. The parameter's complete units and effect require the callee contract and caller/resource context. It is not labelled a geometry-width, brightness or timing change on the basis of one immediate alone.

## Reconstruction and follow-up

**Bounded work status: done for the listed code differences. Confidence: verified static predicates, bytes and argument values.** Preserve zero-versus-one distinctions, all other nonzero values, skipped-path tick publication, bit-mask OR semantics and the exact binary32 argument. Do not silently normalize malformed settings to Boolean values.

**Pending:** complete context/setting producers, the vector callee's parameter semantics, all caller cadence, renderer command data and visual behavior. These affect interface/data reconstruction and runtime validation. No executable bytes, Ghidra state or maintained C were changed.
