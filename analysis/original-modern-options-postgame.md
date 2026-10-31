# Options after race results: mainonly asset restriction

## Finding and scope

**MP140-019 is partially supported by a concrete asset-to-code mechanism.** The official final Options asset removes `mainonly=1` from the Race, Credits and Exit controls present in a selected uppercase local backup. Both executable versions use the same generic mainonly/postgame filtering instructions and zero-valued button defaults. Thus these official entries avoid that specific postgame suppression path, assuming normal template creation/parsing and no later overrides.

The [audit script](scripts/audit_options_postgame_difference.py) pins both executable hashes, verifies identical relevant code/data, and hash-checks the official asset directly against the retained patch archive. [Manifest](evidence/audits/original-modern-options-postgame.json). No menu rendering, input or target instructions were executed. Backup provenance is not authenticated retail provenance; the final original/Modern pair cannot date the change to v1.4.0.

## Authored fields and defaults

| Options control codelink | Local uppercase backup | Official v1.6.1 asset |
|---|---|---|
| `racenow` | `mainonly=1`, `postonly=0` | Both fields absent |
| `credits` | `mainonly=1`, `postonly=0` | Both fields absent |
| `exitprogram` | `mainonly=1`, `postonly=0` | Both fields absent |

Their official button types remain `LR1of3`, `LR2of3`, `LR3of3`, with their Race/Credits/Exit label tokens. Absence of a field is interpreted through the observed template/parser route, not assumed to mean false universally.

The button template at `00556e40` has zero WORDs at item+14h/+16h in both images and a nonzero creation callback at +24h. Existing [template installation and field-storage research](original-modern-slider-percentage.md) establishes the `bch`-byte template copy and instance-relative destination calculation. Identical 16-byte field descriptors map:

- `00557c60`: `postonly`, numeric conversion type1, destination `00604ee0 + 14h`.
- `00557c70`: `mainonly`, numeric conversion type1, destination `00604ee0 + 16h`.

The unchanged numeric writer branch stores a WORD for conversion type1. Normal omitted fields therefore retain zero; the selected backup's explicit1 overwrites the mainonly WORD. Later writers and alternate file-loading paths remain unenumerated.

## Postgame-context producer and suppression consumer

The original/Modern prefix `0044b24e..0044b271` is byte-identical. At entry to the outer frontend loop it compares the supplied context name to literal **`postgame`** at `00539048`, and stores **1** to `00662968` on equality, **0** otherwise. This describes the loop's initial context flag, not the name of every subsequently active nested menu. A nested Options descriptor can therefore still be processed under an outer postgame context. Actual entry and nesting in a particular session were not observed here.

Complete generic initializer **`0044a960..0044a9db`** is also byte-identical. It scans entries until the type-zero sentinel. When item creation callback+24h is nonnull, it invokes that callback, then applies:

| Item field / context | Flag effect |
|---|---|
| `postonly != 0`, `00662968 == 0` | OR WORD item+4 with `1001h` |
| `mainonly != 0`, `00662968 != 0` | OR WORD item+4 with `1001h` |

The code does not locally clear this mask when conditions are false. Fresh template state, preceding callbacks and other writers matter. The [flag-consumer audit](original-modern-race-now.md) separately maps bit0 to a navigation exclusion and bit1000h to suppression of the inspected entry draw callback. Those consumers support the relevance of this mask without treating it as a universal visibility invariant.

For the selected original-like asset, ordinary postgame initialization therefore applies this suppression to the three mainonly buttons. In the official asset with ordinary zero defaults, this **particular** filter does not apply it. Other policy paths can still disable or suppress a control; this is not a proof that every control is always visible/enabled.

## Separate policy and reconstruction requirements

Modern Options initializer `00442aa0` calls shared policy helper `00437614`, replacing its older local Credits gate; the [Race Now report](original-modern-race-now.md) documents that branch map. That policy is separate from generic mainonly filtering. In particular, **MP140-020** (Race hidden when Options opens from the first screen) still requires its lifecycle-state interpretation and entry-path proof; removal of mainonly fields does not prove it.

For C reconstruction, preserve the outer-context flag, zero template defaults, WORD field layout, creation-callback ordering and OR-only suppression semantics. A port that uses the current nested menu name alone to decide postgame state, or restores `mainonly=1` while adopting Modern assets, can change control behaviour even with an otherwise faithful button renderer.

Next: trace postgame-to-Options admission/return paths and all later flag writers, compare actual selected assets in a suitable runtime session, and obtain intermediate packages if historical attribution is required. Do not silently turn this bounded mechanism into whole-postgame UI equivalence. Executables, saved Ghidra state, raw exports and maintained C remain preserved.
