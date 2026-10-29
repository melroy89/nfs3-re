# Dispatcher cases 40–41 at `004b4ed0` and `004b4f0c`

## Scope and evidence

Read-only static analysis of the shipped `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, using an ephemeral Ghidra 12.1.4 REA session. No executable, runtime, or persistent Ghidra project was modified. Cases 40 and 41 are entries 40 and 41 of the 80-DWORD dispatch table at `004b478c`; the original table bytes identify their destinations as `004b4ed0` and `004b4f0c` (`ev_b9ea0ff686d001bf4d1cfb774baf4a68f2b3b0069206441a9236732bba28bf14`). The dispatch at `004b4919` and destinations remain outside a recognized procedure.

REA instruction observations cover loop setup, bounds, loads, comparisons, mismatch branches, and loop increments. In particular: case 40 setup/store `ev_271c2efb2707fa4f4a1f69bb9b643ebabbb46cb4d8d20af127a43a08861152b2`, `ev_3e8df5d2003618adc7057d198448088a8b578529b595d78312fee98f20b5cfda`; bound and exit `ev_17dd79b8bbbeeda38898c665fca4c5aafd89027f8cf5f14d334cd6d757efb654`, `ev_a2b704994f804d9102b678cd79c92a7659a830a2725dba4fd3fe25da85ce305f`; its first-record load and second-record compare `ev_71a1621abab0c7d7984a86545440d733bf9bc23fa1d2639f4e5e00cdca7937aa`, `ev_a8e572d9f15e779124c0a782290b312cf76b9b728878bc5edc9783bdc6c74bc5`; equality branch and increment `ev_7bfbf755948104e7abda914a27211908178231cff5b0d3b3c41f400aefd77f3b`, `ev_58cb57a55a57be5763ec98faa7c3b91b0a9bbada824d5c9b23d0f22907d4967b`.

For case 41, the initialization and initial slot write are `ev_8a972b73d4e66623bf87a3fb5e88abff82580631eca08dff17233f8fc2024570`, `ev_63d08a34b4afd70168eec71540e748f66b2f2c55b2a9356f4b635bdc72421a0a`; bound and exit are `ev_0726d57fcae0cf404bd14991732cee86f4b2fbddafe075ada0ac35e857383c09`, `ev_23e54eb6ed7c5f1f9c8d7b100add9eb74b2c2604b6c9e61633489db0bc3a7346`; load and compare are `ev_379703e4626d430f528ea9344a3d4b6542023d37058e0bbda2f2e03f0e76bafc`, `ev_4cbc8121f8fbeb0f9202f806fd71c58866fb036620411c53e773323305a97c57`; equality branch and increment are `ev_f2ef57128da803ce8ed4e054f7273076f9231b374883e94aff361956ad32c96a`, `ev_d337503d38f3f1b6220eb8a49df4ec12cd0c394250b5c8f5aecdb423a0498a9f`.

The byte read spanning both bodies is `ev_cc4c0ef097fa786e50aafacd23b1b442e912e175921a7e44560cbeba38655a46`. Raw original-file disassembly was independently checked with `objdump`; this is decoding of the shipped bytes, not execution. Existing [dispatcher record contract](dispatcher-record-contract.md) establishes the entry null check, zero-filled 80-byte result area, common per-slot progression, and aggregate return polarity.

## Case 40 (`004b4ed0`): three DWORDs at `+0x25c`

- Exact case instruction span: `004b4ed0..004b4f0b` inclusive. Control-flow loop: `004b4ed5` zeroes EAX, `004b4ed7` jumps directly to the first body at `004b4ee2`; later iterations test at `004b4ed9`, `004b4edc` exits to `004b490a` when `EAX >= 3`, and `004b4f09..004b4f0b` increments EAX and jumps back to the test.
- Inputs are the two record pointers already held in `ECX` and `ESI` by the dispatcher setup. For each loop index `EAX`, the code compares DWORDs at `ECX + 0x25c + 4*EAX` and `ESI + 0x25c + 4*EAX`.
- It initializes the current result byte `[EBP + EDX - 0x54]` to 1 at `004b4ed0`, sets `EAX=0` at `004b4ed5`, and loops while `EAX < 3` (`CMP EAX,3` at `004b4ed9`; signed `JGE` exits to common increment `004b490a`). The compared element offsets are `+0x25c`, `+0x260`, and `+0x264`; width and stride are 4 bytes.
- A mismatch at `004b4efb` takes the non-equal path, clears `BL` at `004b4f03`, and writes zero to the current result slot at `004b4f05`. Equality skips that write. Both paths reach `INC EAX` at `004b4f09` and return to the bound check. Thus the slot is 1 only when all three DWORDs match; a mismatch does not terminate the loop.

## Case 41 (`004b4f0c`): three DWORDs at `+0x268`

- Exact case instruction span: `004b4f0c..004b4f48` inclusive. Control-flow loop: `004b4f0e` zeroes EAX, `004b4f14` jumps directly to the first body at `004b4f1f`; later iterations test at `004b4f16`, `004b4f19` exits to `004b490a` when `EAX >= 3`, and `004b4f46..004b4f48` increments EAX and jumps back to the test.
- For each loop index `EAX`, it compares DWORDs at `ECX + 0x268 + 4*EAX` and `ESI + 0x268 + 4*EAX`.
- It initializes `BH=1`, stores that byte to the current result slot, sets `EAX=0`, and loops while `EAX < 3` (`CMP EAX,3` at `004b4f16`; signed `JGE` exits to `004b490a`). The compared element offsets are `+0x268`, `+0x26c`, and `+0x270`; width and stride are 4 bytes.
- A mismatch at `004b4f38` clears `BL` at `004b4f40` and writes zero to the result slot at `004b4f42`; equality skips the clear. Both paths reach `INC EAX` at `004b4f46` and recheck the bound. The slot is 1 only when all three DWORDs match; mismatch does not stop the loop. Although `BH` seeds the slot with 1, the mismatch write uses the cleared `BL` value, so the effective mismatch result is zero.

## Result and exceptional policy

These are observed integer DWORD equality loops, not floating-point comparisons: no x87 operation or floating-point status handling appears in either case. There is no NaN/unordered comparison policy to infer for these slots. The cases themselves do not check record pointers or lengths; the enclosing entry checks only for null input pointers and returns 1 before dispatch when either is null. Otherwise, invalid or undersized non-null record pointers can fault on access; no local recovery branch is present. The loop bound is the immediate constant 3 and is independent of record contents.

Each case writes one equality byte into the dispatcher scratch slot. The enclosing aggregate later returns 1 if any slot is zero and 0 if all 80 are nonzero. Case indices are dispatcher slots; no descriptor-token or semantic record-field name is established here. These accesses support only the structural statement that both compared records are expected to expose three DWORDs at the stated byte offsets.

## Coverage limits

The table destination mapping and observed code establish these two static cases. They do not establish the upstream caller, semantic identities of the record pointers, descriptor names for the offsets, intended memory allocation sizes, or runtime reachability. Ghidra's instruction records report no containing procedure at the relevant addresses. No runtime behavior is claimed.
