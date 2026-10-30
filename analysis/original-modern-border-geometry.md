# Original versus official Modern: textured border geometry

## Scope and binaries

Static comparison of the matched routine at `0047f650` in the supplied original and official Modern executable, with a bounded trace of Modern's border-thickness writer. No original meaning is assigned to data address `0055fed0` merely because Modern uses that address for border geometry.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

## Matched builder: old computed inset versus Modern stored inset

Both files contain a routine at `0047f650` that emits nine `0x80`-byte quad records from rectangle coordinates and atlas UV constants. Several callers are retained at the same addresses (`0048106d`, `004812cd`, `004813cb`, `00481b6d`, `00481eee`). Their instruction bodies were checked in both executables; the large routine body itself is substantially rewritten, so equal entry address alone is not treated as proof of full semantic identity.

The paired inset arithmetic at the routine entry is concrete:

- **Original `0047f650`:** for the first border coordinate, it loads DWORD `007cdac8`, multiplies by the floats at `0053b4f8` and `0053b4fc`, converts with `FISTP`, then subtracts that integer from EBX to produce the left inset (`0047f65a–0047f68e`). It repeats the same dimension-times-constant calculation for other border edges.
- **Modern `0047f650`:** it saves all four incoming coordinates, loads DWORD `0055fed0` as the thickness, then subtracts it from the left and top bounds and adds it to right/bottom bounds in its quad construction (`0047f658–0047f683`, then e.g. `0047f6af–0047f6dc`). The dimension-times-constant calculation no longer occurs in this helper.

The common binary32 float at `0053b4fc` is approximately `0.0015625` (1/640); the manifest retains its exact bits/value. The first multiplier at `0053b4f8` is `4.0` in the original file and `2.0` in Modern. Thus the original computes repeated rounded thickness terms from DWORD `007cdac8` times approximately `0.00625`; Modern uses a previously computed DWORD thickness. These are different source operands, so the multiplier change alone does not prove a factor-of-two change in rendered border size.

In Modern, updater `0047f9a4` computes and writes `0055fed0`: `FILD DWORD [007a2748]`, multiply by the Modern constants `0053b4f8` and `0053b4fc`, then `FISTP DWORD [0055fed0]` (`0047f9a4–0047f9bc`). The direct writer found is this `FISTP`. Its caller at `004be74d` invokes the updater; later code at `004be759` reads the resulting thickness. The updater applies no local range check, and `FISTP` conversion depends on the active x87 rounding mode. The [viewport comparison](original-modern-viewport-geometry.md) traces `007a2748` as the width of the centred 4:3 reference rectangle. In ordinary widescreen modes it derives from `trunc(4*H/3)`; for taller modes it remains W. This qualifies the release note’s vertical-resolution description. Its full runtime range remains unverified.

## Modern wrapper and call-site mapping

Modern adds inset wrapper `0047f98c`: it reads `0055fed0`, adds it to left/top, subtracts it from right/bottom, restores the destination register and tail-jumps to `0047f650` (`0047f98c–0047f99d`). The original has no matching wrapper body at that address; original `0047f98c` lies within the builder's remaining instruction range/data decode and does not establish an equivalent wrapper.

One visible caller changes its target: original `0047fdc2` calls `0047f650` directly, while Modern `0047fdc2` calls `0047f98c`. The other five listed caller sites still call `0047f650` directly in both builds. This proves a specific added pre-inset at that caller path, but not its final visual position, clipping outcome, or purpose.

## Do not transfer the Modern global name to the original

Modern's direct references to `0055fed0` are reads in the builder and wrapper, the write in `0047f9a4`, and a separate read at `004be759`. In the original executable, the inspected border builder does not reference `0055fed0`; the disassembly instead contains other stores to that address at `004b5aa4`, `004b5bd5`, `004b5c68`, `004b5d57`, and `004b5df6`, plus a read at `004bee1f`. Those sites have not been traced here. Accordingly, `g_nTexturedRectangleBorderThickness` is a Modern-side descriptive name only; it is not used to characterize the original DWORD.

## Retained evidence

Run `python3 analysis/scripts/audit_viewport_geometry_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-viewport-geometry.json) retains complete builder spans, the new wrapper/updater, six caller instruction witnesses and exact float constants for both executables. Raw assembly remains ignored. This does not validate every rewritten quad/UV assignment.

## Limits

- Static arithmetic and call-target changes are established from the two executable fingerprints above. Original source `007cdac8`, original uses of `0055fed0`, atlas consumers and live values remain unresolved here; Modern source `007a2748` is mapped in the viewport chapter.
- This report does not infer a final border-size ratio, viewport policy, map-scale policy, or visible rendering change from the constants alone. It does not identify all changed UV mappings or texture assets.
- No game, graphics backend, probe, or test was run; no executable or Ghidra project was modified.
