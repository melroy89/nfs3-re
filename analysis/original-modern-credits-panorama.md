# Credits panorama: two-way navigation and callback relocation

## Paired callbacks and evidence

The `credits1` row at `00556188` redirects its init callback from `00454ea0` to `00454dc8`, and its transition callback from `00454e80` to `00454da8`. The [complete registration comparison](original-modern-menu-callback-table.md) proves the pairings. The [panorama audit](scripts/audit_credits_panorama_difference.py) retains both counterpart bodies, navigation/label helpers, exact tokens, asset field locations and the distant Modern exit. [Manifest](evidence/audits/original-modern-credits-panorama.json). All ends are exclusive; no target execution.

## Restoring the pre-entry state is moved unchanged

Original `00454e80..00454e9d` and Modern `00454da8..00454dc5` are **byte-identical**. They copy saved DWORD `00664780` to both `00664794` and `00664798`, return EAX=0 and preserve EDX/EBP through their local saves. This is a relocation of retained local behaviour, not a rewritten restore policy. It does not prove the callback is invoked in every exit context or that the saved value is always valid.

Both initializers save current `00664794` to `00664780`, clear `00664794` and `00664798`, look up `ZoomSlider`, install handler `00454cf0` through `0046cac0` and submit two zero arguments through `0046c950`. Neither inspected initializer locally checks the slider lookup before those helper calls.

## Original: one next control and generated text

Original init `00454ea0..00454f02` binds `GlamNext` (`005398f4`) to `00454e40` without a local null guard on that button lookup. That handler increments `00664794`, computes signed remainder by four with IDIV, stores the remainder and calls label routine `00454d60`.

The label routine looks up `GlamSub` through the existing context/entry helpers, obtains a signed language ID from the table around `005563dc`, formats the current label using `%s` into shared buffer `00664700`, and stores that buffer pointer into the subtitle field. It also constructs the next-control label using the following index: language selector `006fbb4c == 1` copies the localized string directly; other values format `%s...` into shared buffer `00664680`. That buffer is assigned to the next-control text field. Neither destination-buffer capacity nor every entry/lookup precondition is qualified here.

Thus original navigation is one-way through the inspected control, with a label naming the next selection; this does not exclude other input routes elsewhere.

## Modern: separate next/previous and direct subtitle pointer

Modern init `00454dc8..00454e43` instead looks up `previous` and `next`, guarding each button lookup before assigning item callback+64h:

| Token | Callback | Index update |
|---|---|---|
| `previous` (`00537bc4`) | `00454d8c..00454da6` | `(index - 1) & 3` |
| `next` (`00537bbc`) | `00454d70..00454d8a` | `(index + 1) & 3` |

Both callbacks wrap in machine-width arithmetic, store to `00664794`, call `00454d40` and return zero. For indices 0..3, Next matches ordinary positive remainder progression while Previous adds the inverse route. For arbitrary corrupted index values, bit masking is not generally equivalent to original signed IDIV remainder; do not substitute a universal C `% 4` contract.

Label helper `00454d40..00454d6f` looks up `subtitle`, skips a missing entry, zero-extends the selected WORD language ID at `005563dc + index*2`, calls `004d1850`, and directly stores the returned pointer at entry+3ch. It removes the original local formatting/copy paths and their shared label buffers. The four table WORDs remain `01e1h,01e2h,01e5h,01e5h` in the inspected images. Language lookup itself differs between versions, as documented in the [language-table comparison](original-modern-language-table.md).

If Modern cannot find `next`, its initializer jumps from `00454e2d` to distant **`0045d77e`**. Here EAX is zero from the failed lookup, so `CMP EAX,1 / JNE 0045d794` selects `POPAD; XOR EAX,EAX; RET`. It therefore skips the remaining Next assignment and immediate subtitle refresh. This is a shared exit path, not a separate successful initialization body or a reason to include all intervening bytes as function code. Other entry paths to the shared region are outside this audit.

## Official menu controls and release-note scope

The hash-checked official `credits1.mnu` defines three buttons:

| Codelink | Text token | Layout type |
|---|---|---|
| `keyright next` | `kMenuCREDITSNext001` | `LL1of3` |
| `keyleft previous` | `kMenuCREDITSPrevious001` | `LL2of3` |
| `escape` | `kTextBack` | `LL3of3` |

Its subtitle entry uses `codelink=subtitle`. The selected uppercase local backup uses `GlamNext` (`LL1of2`), an Escape/`kTextBackDots` button (`LL2of2`) and `GlamSub`. Backup provenance is not authenticated retail provenance.

This supplies **partial static support for MP140-024** (common Back/Next controls for the panorama page), and **partial support for MP140-022** through authored `keyleft`/`keyright` tokens and bound direction callbacks. The conditional static arrow-dispatch route is now connected below. Actual input delivery, other contexts' callback implementations, visible output, panorama rendering and v1.4.0 introduction remain unverified. MP140-023's noticeable More button is not established by this page's controls.

## Reconstruction follow-up

Keep original and Modern navigation/label policies separate, preserve the saved state and pointer lifetimes, and explicitly model Modern's discontiguous missing-entry exit. Qualification should cover all four ordinary indices, backward wrap from zero, missing buttons/subtitle/slider, language-resource lifetime, Enter/arrow/Escape dispatch and transition restoration. Do not silently repair unchecked original lookups or treat the original shared buffers as reentrant.

These findings account for two redirected registration fields; they do not establish whole-Credits equivalence or a complete panorama implementation. Executable bytes, saved Ghidra state, raw exports and maintained C remain unchanged.

## Conditional Left/Right-to-panorama callback chain

The existing [paired menu-input investigation](original-modern-menu-input.md) already establishes that Modern adds named arrow actions after current-entry input handling. This follow-up retains the specific scanner/dispatch ranges and complete generic button handler alongside the panorama evidence, rather than treating the asset token alone as functional proof.

For ordinary admitted input:

1. `0044a315..0044a362` first offers the key to the currently selected entry's input callback at `+30h`, when present. A nonzero handled result prevents the named-arrow fallback. Earlier session/modal gates also remain relevant.
2. Left code `4b00h` uses literal `keyleft` (`0053be36`) at `0044a3cb`; Right code `4d00h` uses `keyright` (`0053be3e`) at `0044a3f2`.
3. Scanner `0044a24c..0044a2c2` searches from the context's signed starting index through `bch`-stride entries until type-zero sentinel. It selects the first type-5 entry with a non-null matching codelink and bit 0 of flags byte+4 clear, and returns its relative index. It does not apply every navigation filter used by other scanners.
4. On a match, `0044a409..0044a41e` writes that relative index to context WORDs+1ah/+1ch, sets EBX=13 (Enter), passes the context in EDX, and invokes the matched entry's `+30h` input handler. Missing named action falls back to ordinary previous/next selection instead.
5. The retained button template at `00556e40` sets `+30h=00461270` and file-backed `+58h=0`. In the simple-button branch, Enter with non-null item callback+64h invokes it at `004613cd`. The panorama initializer supplies `00454d8c` for Previous and `00454d70` for Next, connecting to the decrement/increment paths above.

This closes the **static conditional route** from authored `keyleft previous` / `keyright next` to the panorama callbacks. It requires successfully loaded/initialized entries, the named button being enabled, ordinary template state and the earlier/current-entry handlers declining the arrow. No keyboard event, current selection or rendered transition was observed.

The expanded manifest also checks the official `credits.mnu` and `slides.mnu` directly against the pinned archive. They contain `keyleft previous` / `keyright next`, and `keyleft prevslide` / `keyright nextslide`, respectively. These are relevant authored routes for MP140-022; their complete callback implementations and context-specific admission remain separate from the panorama chain verified here. Thus the catalog entry remains partial rather than promoting a three-context runtime claim from one conditional chain.
