# Texture loading: descriptor queries and progress milestones

## Scope and evidence

[The reproducible static audit](scripts/audit_texture_loading_followup.py) pins both executable hashes and compares three complete same-address function envelopes. [The manifest](evidence/audits/texture-loading-followup.json) records span hashes and retained disassembly locations. No game, renderer, allocation or instruction probes were executed.

| Entry / saved Modern label | Envelope, exclusive end | Bytes | Difference |
|---|---|---:|---|
| `0049c5c0` SelectSupportedDriverTextureType | `0049c5c0..0049c5f9` | 57 | About-query call replaced by descriptor-cache load |
| `004d3f50` CreateTextureFromShape | `004d3f50..004d4075` | 293 | About-query call and following TEST removed |
| `004d5370` LoadSharedSfxTextureDescriptors | `004d5370..004d56a3` | 819 | Four binary32 progress immediates changed |

Names are saved analysis labels. All bytes outside the changes described below are identical in each complete envelope.

## Texture-type selector reuses the cached descriptor

At `0049c5c5`, original calls `_THRASH_about@0` through `009ef980`; Modern substitutes NOP plus `MOV EAX,[007a3a5c]`. The [renderer loader](original-modern-renderer-loading.md) verifies that export binding and cache, while the [lifecycle report](original-modern-renderer-lifecycle.md) records cache refresh. This is another consumer of the cache policy also observed in [shape conversion](original-modern-shape-conversion.md).

Both versions immediately load the pointer at descriptor `+30`, test bit 0 of byte at its `+0c`, and return type 3 if set. Otherwise they test bit 0 at `+1c`; if set, return type 7. If neither bit is set, they call `00401010` with message pointer `0053c5f0`, then have a continuation returning 7 if that call returns. The diagnostic/fatal path must not be rewritten as an ordinary successful fallback merely because a return instruction follows it.

Neither version checks descriptor or nested pointer for null in this body. Modern's descriptor comes from prior cache setup rather than a fresh query. Validity, freshness and query side effects remain separate from the retained selection logic.

## Texture creator removes a locally discarded query

Original `004d3f63..004d3f6b` calls the same about export and executes `TEST EAX,EAX`. Modern replaces that eight-byte region with `JMP 004d3f6b` and six NOPs. The next original instruction reloads EAX from its saved input; there is no branch consuming the query's zero/nonzero result. This proves removal of that direct query, not that its external side effects or incidental register changes were irrelevant in all DLLs.

The 266-byte suffix `004d3f6b..004d4075` is byte-identical. Both still call converter `004d37a0` at `004d3f97`, allocate/update through renderer slots `009ef968/009ef964`, calculate output texture-coordinate fields and release the temporary buffer. The converter itself changed, as the linked shape-conversion report documents, so this identical suffix does not establish identical texture contents.

The Modern saved body union omits the six NOP bytes and therefore reports 287 body bytes and two changed in-body bytes. The complete envelope has 293 bytes and eight changed bytes. This is a coverage-boundary distinction, not conflicting measurements.

## Shared effect textures receive lower progress milestones

Four PUSH-immediate arguments to retained progress routine `00495230` change:

| PUSH instruction | Original binary32 | Modern binary32 |
|---|---:|---:|
| `004d53a6` | 36.0 | 10.5 |
| `004d54cc` | 37.0 | 11.0 |
| `004d55cf` | 38.0 | 11.5 |
| `004d55e5` | 39.0 | 12.0 |

These four constants account for all eight changed bytes in the 819-byte loader. Its calls, asset-related instructions and output stores otherwise remain byte-identical. These are nominal progress inputs, not elapsed seconds or evidence of faster loading. The [indexed-texture progress report](original-modern-texture-progress.md) records another redistributed loading interval, and [loading timing](original-modern-loading-timing.md) explains downstream throttling/estimation; reuse those analyses before interpreting displayed progress.

## Reconstruction and limits

**Bounded work status: done; confidence: verified static comparisons.** Preserve the selected version's descriptor source, removed/retained external calls and float-bit arguments. Do not add a null fallback or treat removed queries as provably pure without qualifying the renderer interface.

Still unverified are actual texture availability/allocation, descriptor lifetime across renderer resets, all DLL implementations, visible texture output and progress timing. Those affect runtime validation and external-interface reconstruction. No executable bytes, saved Ghidra state or maintained reconstruction sources were changed.
