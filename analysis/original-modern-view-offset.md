# Scene view offset: new EDX mode and fixed-view dispatch

## Baselines and complete counterpart

Paired `004240c0..00424252`, currently named `UpdateSceneViewTransformOffset`, is 402 bytes in both executables. **102 bytes differ, all within `00424101..0042416b`**. The common prefix through `00424101` and entire tail `0042416b..00424252` are byte-identical. The [audit](scripts/audit_view_offset_difference.py) pins both executable hashes, retains complete bodies, dispatcher witnesses and two complete retained helpers. [Manifest](evidence/audits/original-modern-view-offset.json). Ends are exclusive; no target execution.

This is a branch-policy and interface change, not evidence of a local rewrite of the later x87 matrix arithmetic. Ambient [original/Modern x87 control differences](og-modern-x87-precision.md) remain relevant even where instruction bytes match.

## Original ignores incoming EDX; Modern consumes it

Both take a context pointer in EAX and save/restore EBX/ECX/EDX/ESI/EDI/EBP. The original overwrites EDX with raw global DWORD `007922fc` at `00424101`, before testing it. Incoming EDX therefore has no effect in this inspected body. Modern first stores the copied position DWORD, then tests **incoming EDX** at `00424104` and again at `0042413c`.

The Modern-only EDX argument is a mode/gate input. It must not be inferred as an original parameter merely from the current Ghidra signature. No stable useful scalar EAX return is established here; effects are context writes and floating-point/machine state.

Both begin with a local offset copied from context+110h/+114h/+118h, and a local base position copied from the context+4 object's +98h/+9ch/+a0h. Let `G` be the raw DWORD at `007922fc`, and `S` be the object DWORD at +9a8h:

| Inputs | Original | Modern |
|---|---|---|
| `G=0`, incoming EDX=0 | Offset X=0; context+50h=`3ca3d70ah`; offset Z=object float+11ch ×0.5, stored binary32 | Same branch policy |
| `G=0`, incoming EDX nonzero | Same as above: incoming EDX ignored | Context+50h=0; offset X=0; retain copied offset Z |
| `G!=0`, EDX=0, `S=0` | Context+50h=0; offset X binary32 approximately−0.4 | Same branch policy |
| `G!=0`, EDX=0, `S=1` | Context+50h=0; offset X approximately+0.4 | Same branch policy |
| `G!=0`, EDX=0, `S=2` | Context+50h=0; offset X=0 | Same branch policy |
| `G!=0`, EDX=0, other `S` | Context+50h=0; retain initially copied offset X | Context+50h=0; force offset X=0 |
| `G!=0`, EDX nonzero | Choose X from `S` as above; incoming EDX ignored | Context+50h=0; force offset X=0 |

`G` is an integer zero test on raw bits, not floating equality: negative-zero float bits would take the nonzero branch. `S` comparisons use unsigned branch conditions/equality. The half constant at `00536eac` remains binary64 bits `3fe0000000000000`; offsets use binary32 storage. No universal camera-view names are assigned to `G`, `S` or these physical fields from this routine alone.

## Retained transformation and outputs

The common tail scales local offset Y by the context+8 object's float+10ch and stores binary32. When indexed global `0079c4a0[context DWORD+0ch]` is nonzero, it toggles the sign bit of local offset Z. It multiplies the offset by the context+4 object's nine-float basis at +c0h using the retained x87 sequence, stores a binary32 transformed triplet and calls **`004dffb0`** to combine it with the copied base position into context+14h.

Finally it writes the basis at context+2ch: either copies nine DWORDs or calls **`00421570`**, whose existing analysis identifies copying with first/third basis rows negated. Both complete helper bodies are byte-identical across baselines: `004dffb0..004dfff3` and `00421570..004215b7`. [Existing arithmetic/data-flow notes](detailed-analysis-notes.md#scene-view-transform-offset-update) describe this active-build contract. They apply to the Modern mode input, not the original's overwritten EDX.

Identical arithmetic bytes do not prove equal results: the new branches can supply different offsets, and x87 precision/rounding, exceptional values and helper aliasing/preconditions remain relevant. A C translation must preserve operation order and binary32 stores before considering reassociation, fused operations or a wider-precision policy.

## Dispatcher supplies both Modern modes

The paired dispatcher begins at `00426450`. Its first 24-entry table at `004263f0` changes representation:

- Original selector1 table entry points to local arm `00426482`, which calls `004240c0` with the selected context in EAX. Original dispatch uses a jump to these local arms. The follow-up below extends the capture through all original arms and resolves all24 selector targets.
- Modern selector1 table entry points directly to `004240c0`. Before its indirect CALL at `00426472`, Modern sets EAX to the selected context and **EDX=0**. The unsigned selector-minus-one range must be at most23 to reach that call.
- After the primary table call, Modern checks `006fd3b0 != 1` and `006fd1cc != 0`. If both hold, it sets **EAX=`00661220`, EDX=1**, and directly calls `004240c0` at `00426493`. This extra call occurs for every admitted table selector on that gated path, not just selector1.

This connects the new register contract to an actual producer for the separate fixed-view state. The [viewport-pose audit](original-modern-viewport-pose.md) independently maps snapshot storage at `00661220` and the related selection gate; reuse that evidence rather than naming this a particular visible camera mode without its context.

The retained table contains all24 pointer values, but this report does not recover every handler's signature or prove they all preserve the dispatcher state needed afterward. Context-array bounds, selected object lifetimes, fixed-view initialization and external/indirect callers remain unvalidated. The saved linear disassembly has one direct original call and one direct Modern call to this function; Modern's table call demonstrates why direct-call counts alone miss reachability.

## Reconstruction follow-up

Use separate original and Modern interfaces, or an explicit adapter that supplies the Modern mode. Later tests should distinguish both EDX values, raw `G=0`/nonzero/negative-zero bits, `S=0/1/2/other`, mirrored index state and ordinary/exceptional float offsets. Validate the extra fixed-view update and caller/register contracts before replacing a game-facing component. Do not silently zero the original out-of-range `S` fallback when reconstructing original behaviour.

This identifies a substantive code difference without assigning an unsupported release-note ID or date. Executables, saved Ghidra state, exports and maintained C are preserved; no instruction probes or game sessions were run.

## Complete 24-selector dispatch mapping

The audit now retains original dispatcher **`00426450..0042655a`** through its final epilogue, superseding the earlier prefix/first-arm boundary. All24 original table entries at`004263f0` resolve mechanically: ordinary local arms execute `MOV EAX,ECX; CALL callee; POP EBP/ESI/ECX/EBX; RET`; two entries instead target the shared epilogue directly. Modern’s table stores callee addresses, invoked through its already documented common CALL path.

| Raw selector | Original resolved callee | Modern callee |
|---|---|---|
| 1 | `004240c0` | Same |
| 2 | `00424260` | Same |
| 3,5 | `00424740` | Same |
| 4,6 | `004243a0` | Same |
| 7 | `00424b50` | Same |
| 8 | `00425060` | Same |
| 9 | `00425d50` | Same |
| 10 | `00425990` | Same |
| 11,12,13 | `00425ab0` | Same |
| 14 | `00425bf0` | Same |
| 15,22 | No call; shared epilogue`00426555` | `00426290` (RET-only stub) |
| 16 | `004253d0` | Same |
| 17 | `00425640` | Same |
| 18 | `004251f0` | Same |
| 19 | `004262a0` | Same |
| 20 | `00426290` | Same |
| 21 | `00424690` | Same |
| 23 | `00424ce0` | Same |
| 24 | `00424e30` | Same |

Thus22 selectors preserve their **target**, while15/22 gain a call to the RET-only stub. This is a routing statement, not proof of equal callee implementations or full machine state. Modern supplies EDX0 to its primary call and can then execute the additional gated`004240c0` call described above; original’s directly-returning local arms do not share that continuation. For15/22 the extra return address/stack traffic and caller register setup are real machine effects, even though the stub has no explicit application-memory write. Selector20 already called the original no-op at that address; original’s five-byte frame stub is shortened to a one-byte RET in Modern.

The manifest retains every selector, resolved target and unique original arm bytes, with assertions checking all CALL displacements and epilogues. The outside-body NOP interval`004264ec..00426560` consequently overlaps the end of one arm, later arms, final epilogue and alignment; it does not prove those camera/scene modes were removed. Complete per-callee contracts, raw selector meanings, all producers and runtime camera results remain unresolved. No relation to the separate unresolved dispatcher around`004b4919` is implied or required.
