# Car slideshow: arrow bindings and deferred refresh

## Counterparts and evidence

The `slides` registration row at `00555f90` retains init `00453c00` and periodic callback `00453ef0`; its original intermediate callback was a return-zero stub removed in Modern, as recorded in the [registration audit](original-modern-menu-callback-table.md). The retained init prefixes identify the actual per-button counterparts:

| Control | Original callback | Modern callback |
|---|---|---|
| `nextslide` (`005397a4`) | `00453840..00453859` | `00453850..00453863` |
| `prevslide` (`005397b0`) | `00453860..0045393e` | `00453864..0045393d` |

The [audit](scripts/audit_slideshow_navigation_difference.py) pins both executable hashes, captures complete navigation/periodic bodies plus explicitly partial init/refresh witnesses, and verifies the official asset directly against the retained patch archive. [Manifest](evidence/audits/original-modern-slideshow-navigation.json). Range ends are exclusive. No target execution.

## Navigation results change from action9 to a shared update counter

Original Next increments slide index `00559588`, preserves EDX/EBP and returns **EAX=9**. Modern Next increments the same index, also increments **`0066477c`**, and returns **EAX=0**. The x86 increments wrap at machine width; no callback-local upper-bound check or wrap-to-first rule is present in Next.

Original and Modern Previous share **byte-identical core `0045386d..00453931`**. For signed index greater than1, it decrements the index. Otherwise it stores20, then repeatedly decrements and probes a constructed candidate path, starting with index19. The path depends on selected car/resource helpers and the source directories. The loop repeats while `004e0e60` returns zero; this captured core has no explicit lower-index/iteration bound. Successful probe and asset availability must not be assumed for malformed or incomplete installations.

Their wrappers and exits differ. Original Previous returns9; Modern increments `0066477c`, restores its saved register frame and returns0. Thus the change is not merely adding arrow names to unchanged callback return contracts. The full outer-loop meaning of original action9 remains a separate dependency; this report does not assume it means immediate successful redraw.

## Modern binding wrapper and periodic refresh

Original `00453c00` interleaves resource/context setup and the two button callback assignments before continuing into rendering. Modern introduces a short binding wrapper `00453c00..00453c32`: it preserves general registers, installs the new callback addresses when the named entries exist, restores registers and jumps to **`00453c33`**. That destination begins the refresh routine. These are explicit partial init/refresh captures, not a claim that the complete large rendering body is verified equivalent.

Modern periodic callback `00453ef0..00453f58` retains the existing timing/entry-flag work and adds at `00453f41`:

- If `0066477c` is zero, return through the existing zero-result path.
- Otherwise pass the menu context to `00453c33`.

The captured Modern refresh exit `00453ed7..00453eee` stores timestamp `0079c1a4` to `00559594`, clears `0066477c`, restores its stack/register frame and returns zero. The original exit lacks the counter-clear store. The inspected Modern refresh prefix also sends a null car/resource lookup to this exit, so clearing the counter must not be treated as proof that an image was successfully loaded or displayed.

These instructions establish a local deferred-update protocol: navigation marks shared state, the periodic callback notices it, and the refresh exit clears it. Counter initialization, every alias/writer, all intervening menu events and complete refresh failure paths remain unenumerated. Do not replace the counter with a boolean or assume reentrancy/thread safety without checking those uses.

## Connecting Left/Right to the slide callbacks

The official `slides.mnu` contains:

- `codelink=keyright nextslide` at line39.
- `codelink=keyleft prevslide` at line51.

The [named-action dispatch audit](original-modern-menu-input.md) and [button-handler integration](original-modern-credits-panorama.md#conditional-leftright-to-panorama-callback-chain) establish the common conditional route: after current-entry input declines an arrow, find an enabled named button, select it, invoke synthetic Enter through item+30h and then the initialized item+64h callback. The binding prefix in this report supplies those slideshow callbacks.

Together with the ordinary Credits and panorama reports, this gives conditional static routes for all three contexts named by **MP140-022**. Actual key delivery, current-entry consumption, runtime asset selection, file availability, visual output and historical introduction in v1.4.0 remain untested. The catalog remains partial for those reasons; the former missing slideshow-binding link is now resolved.

## Reconstruction follow-up

Keep version-specific callback returns and the Modern counter/periodic-refresh protocol explicit. For later comparison, include Next/Previous at indices1/2/19, missing trailing slides, no matching candidate asset, multiple inputs before periodic refresh, zero/nonzero counter and null resource state. Complete refresh/resource ownership, original action9 handling and shared global initialization must be mapped before integration or equivalence claims.

Executables, saved Ghidra state, raw exports and maintained C remain unchanged. This report documents a control-flow difference without running instruction probes or a game session.
