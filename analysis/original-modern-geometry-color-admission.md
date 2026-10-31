# Original versus Modern: geometry-color admission

## Boundaries and evidence

The paired envelope **`004ba350..004ba808`**, end exclusive, is1,208 bytes. Saved Modern analysis labels it `ApplyTrackSideAdjustedGeometryColors`; that name guides investigation but does not establish every data field or effect. Run `python3 analysis/scripts/audit_geometry_color_admission.py`. The [manifest](evidence/audits/original-modern-geometry-color-admission.json) pins both executable hashes, complete envelope and four caller setup spans. No target instructions, rendering or Ghidra writes.

All **41 differing envelope bytes** lie in `004ba382..004ba3af`. The saved Modern function inventory reports37 changed bytes in its body union because its ranges exclude `004ba3ab..004ba3af`: original contains part of an early-return epilogue there, Modern has NOPs. The envelope deliberately retains this removed original tail rather than silently calling it unchanged padding. The downstream **1,113-byte** span `004ba3af..004ba808` is byte-identical.

## Entry gate changes

Incoming EAX is retained as a context pointer in ECX; EDX is retained as another object pointer in ESI; incoming EBX is saved in a local. Both versions read object+`0x1c` and dereference global pointer`00563a90` before the gate. Early rejection does not eliminate those earlier access requirements.

| Condition | Original | Official Modern |
|---|---|---|
| Context DWORD0=1 | Return0 | Reject unless `006fd1d8==0` |
| Context DWORD0≠1 | Continue to enable test | Continue to enable test |
| Enable DWORD`006fbc24`=0 | Return0 | Return0 |
| Gates pass | Enter retained downstream body | Enter retained downstream body |

Modern compares the setting with exactly0; this is not an unsigned≤1 policy. The existing [option-binding evidence](original-modern-night-lighting.md#modern-option-binding-rear-view-detail-values02) identifies Modern`006fd1d8` as Rear View Detail: index0 High,1 Medium,2 Low. Consequently this local context1 gate admits High only, whereas the separately verified night-lighting gate admits High and Medium. Do not generalize one setting threshold to every rendering subsystem.

The first context DWORD is treated here as a tag without claiming its full producer chain. Other research establishes an optional mirror-pass context for lighting, but the four callers below still need their own context/data-flow trace before this function is assigned the same complete viewport role. No particular visible object, shadow, headlight or color effect is established solely by the analysis name or setting association.

## Retained body and callers

The unchanged tail includes track/object filtering calls, transforms, loops and color-related operations. Equal local instructions do not establish equal inputs, floating-point mode, helpers, resources or outputs. Full structure layouts, the meaning/initialization of`006fbc24`, and callback/submission contracts remain unresolved.

Paired direct calls at **`004baab3`**, **`004babe2`**, **`004bae85`** and **`004bb283`** retain target`004ba350`. The audit captures their immediate EAX/EDX/EBX setup from locals. These are call-argument witnesses, not a completed proof of the locals’ upstream producers or a universal direct-call inventory. A reconstruction should keep EAX context, EDX object and EBX input explicit until that trace is complete.

The bounded finding is an expanded context1 admission at High detail with retained downstream code, plus removed/relocated early-return instructions. It is not an arithmetic rewrite or runtime visual-equivalence claim. Historical release attribution and the affected rendered effect remain pending. No catalog status is promoted from a suggestive renderer name.
