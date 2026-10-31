# Download car control: asset removal with retained binding

**MP100-053 is partially supported.** The official final `car1.mnu` contains neither `codelink=CAR_DOWNLOAD` nor `text=kMenuCAR1Download001`. Both are present in the selected uppercase local backup's tab button. This removes that authored control from the official file; no additional executable hide operation is needed for an entry that is not created from that asset.

## Executable counterpart and shared callback

The expanded [website/setup audit](scripts/audit_setup_website_difference.py) verifies complete byte identity of car-menu initializer **`00426d60..00426e1d`** between the supplied original and official Modern executables. Its retained instructions at `00426deb..00426e02`:

1. Look up token **`CAR_DOWNLOAD`**, whose string is at `00537038`.
2. If lookup returns zero, skip the callback assignment.
3. Otherwise store **`00452e60`** at item callback+64h.

Complete callback **`00452e60..00452f16`** is also byte-identical in both images, independently retained in the same audit. The [website-button report](original-modern-setup-website.md) maps the same handler's other conditional binding, diagnostic/menu-text calls and remaining boundaries. Sharing this callback is concrete instruction evidence; the presence of its token or code does not establish that the removed control remains reachable in the final menu.

The [manifest](evidence/audits/original-modern-setup-website.json) records baseline/span hashes plus both asset hashes and the selected field line numbers. The official asset is compared directly to its member in the pinned official patch archive. Ends are exclusive. No handler or target instructions were executed.

## Scope and reconstruction

The selected backup's button uses `buttontype=tab`, `mainonly=0`, `postonly=0`, and label token `kMenuCAR1Download001`. The final official file omits that entry. Backup directory naming does not authenticate retail provenance; a final v1.6.1 package also does not prove introduction in v1.0.0.

For a Modern-oriented reconstruction, preserve the official asset omission and conditional lookup rather than inventing a new unconditional disable call. For original-oriented behaviour, retain the backup control only after authenticating the desired original asset baseline and qualifying the shared callback. Do not claim the patch removes, repairs or successfully replaces the actual download service from this evidence: the retained handler's transitive effects, external service availability and alternate menu/resource paths are outside this bounded comparison.

Next: authenticate original assets and inspect an intermediate v1.0.0 package if historical attribution is needed; trace the shared callback further only when reconstructing the original feature or testing reachability warrants it. No executable, saved Ghidra, raw export or maintained C was changed.
