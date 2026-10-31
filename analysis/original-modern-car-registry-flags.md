# Car discovery: remove manufacturer-specific flag assignment

## Scope and evidence

The complete same-address registry function `00439d90..0043a4c2` (1,842 bytes, exclusive end), saved as `DiscoverAndLoadCarModelRegistry`, differs only inside `0043a20e..0043a25c`. Modern replaces that 78-byte block with `JMP 0043a25c` and 76 NOPs. [The audit](scripts/audit_car_registry_flags.py) checks both pinned executable hashes, full envelope, record-string accessor, flag writes, literals and the related copy-source getter. [The manifest](evidence/audits/car-registry-flags.json) records span hashes and disassembly locations. No cars, menus or gameplay were executed.

The Modern saved body union omits the 76-byte NOP gap and consequently lists 1,766 body bytes with two changed in-body bytes. The full-envelope comparison includes the removed original instructions.

## Removed Ferrari and Mercedes tests

Immediately before the changed region, both call `00439bd0` and retain its result in ECX. Original then performs two manufacturer tests:

1. Load the current record pointer from frame local `-4`, add 4 and call accessor `00439af0` with EDX=0.
2. Compare the returned string with file-backed `Ferrari` at `005376f0` using `004e9ec0`.
3. On equality, OR byte record `+380` with `20h`.
4. Repeat the lookup/comparison with `Mercedes` at `005376f8`, setting the same bit on equality.

The comparator's ASCII case-insensitive behavior is existing evidence in the [car-alias comparison](original-modern-car-alias.md); manufacturer matching is not a case-sensitive C `strcmp` contract. The complete accessor `00439af0..00439b14` is byte-identical in both binaries. It checks a signed WORD count and obtains the indexed string from base/offset-table fields; validity of every loaded record is not established here.

Modern skips both lookups, comparisons and conditional flag writes, retaining the following `TEST ECX,ECX` at `0043a25c` and all remaining code. This specifically removes manufacturer-based assignment of flag `20h`. It does not clear a bit already present in input records, remove every other producer, alter the record's other flags or establish every downstream consumer.

## Relationship to the Hot Pursuit claim

Release-note entry **MP120-003** says Mercedes and Ferrari cars are no longer locked in Hot Pursuit. The explicit manufacturer tests and their removal give **partial static support** for that claim. The selected originals/final Modern pair does not establish the precise introducing release, the original author's licensing motive, the meaning of flag `20h` in every mode, or successful in-game selection. Those require consumer tracing and/or controlled runtime evidence. The catalog is therefore marked Partial rather than fully verified.

## Related copy-source getter changes to an initialized buffer

The complete getter `0043ba20..0043ba2a` is ten bytes in both versions. Only its returned immediate address changes: original returns file-backed `00537720`, whose bytes are `.\fedata\plac\car.viv`; Modern returns buffer address `007a2c34`. It returns the address directly, not the DWORD contents at that address.

This removes this getter's hard-coded source string in favor of external initialization. The effective Modern path, its capacity and writers are unverified here. Address reuse across separately investigated path consumers must not be treated as proof of a single immutable semantic role. Nor does this getter alone establish a car-count expansion.

## Reconstruction and follow-up

**Bounded work status: done; confidence: verified static removal and path-address change. Claim coverage: partial.** Preserve the selected version's flag policy and address-return contract. Do not silently add back the brand restriction to Modern or assume clearing all `20h` bits is equivalent to removing these conditional ORs.

**Pending:** trace record `+380` bit `20h` consumers and other producers; qualify manufacturer metadata and existing flags; trace initialization/lifetime of `007a2c34`; test actual mode admission separately. These affect data/interface reconstruction and runtime validation. Executable bytes, saved Ghidra state and reconstruction sources remain unchanged.
