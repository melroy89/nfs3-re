# Gameplay assist menu crosswalk

## Established menu choices

The installed `level.mnu` binds the following controls by `listname`. `LookupFrontendSelectionListValues` (`00442c80`) searches 20-byte descriptors at `005563e8`, returns the WORD-ID list at descriptor+4, and returns the selection-storage pointer at descriptor+0x10. All six lists below have ordinal **0 = Off, 1 = On**. These are selectable menu values, not a live settings capture.

| List key | Installed English title | Descriptor | Selection storage | Regular-race runtime copy |
|---|---|---|---|---|
| braking | Braking | `005565f0` | `006fd474` | `006fd490` |
| collision | Collision Recovery | `00556604` | `006fd484` | `006fd4a0` |
| traction | Traction | `0055662c` | `006fd488` | `006fd4a4` |
| bestline | Best Line | `00556640` | `006fd47c` | `006fd498` |
| navigator | Navigator | `00556654` | `006fd480` | `006fd49c` |
| copassist | Pursuit | `00556668` | `006fd48c` | cleared to zero in the reviewed regular-race entry path |

Most lists point to `005561be`, containing IDs `0xe5` Off and `0xe4` On. Collision Recovery uses `005561c4`, containing `0xe7` Off and `0xe6` On. `BuildRegularRaceRoster` (`00473bf0`) copies the first five settings at `00473c36..00473c72` and clears runtime pursuit assistance at `00473c7c`. Different mode builders must be assessed separately.

## Player-facing descriptions and limits

The menu text parser (`00449328..0044933f`) searches the token-pointer array at `00561c44`, then passes the matching ordinal to localized-text lookup. Exact installed token/ordinal matches are:

- `kMenuLEVELBraking001`, ID `0x57c`: Braking. Adjacent help ID `0x57b`: Slows car for better cornering.
- `kMenuLEVELCollisio001`, ID `0x57f`: Collision Recovery. Adjacent help ID `0x57e`: Reduces negative effect of collisions.
- `kMenuLEVELTraction003`, ID `0x582`: Traction. Adjacent help ID `0x581`: Improves car handling.
- `kMenuLEVELBestLine001`, ID `0x585`: Best Line. Adjacent help ID `0x584`: Shows optimal driving path.
- `kMenuLEVELNavigato001`, ID `0x588`: Navigator. Adjacent help ID `0x587` describes audio and visual track-navigation instructions.
- `kMenuLEVELPursuit001`, ID `0x58b`: Pursuit. Adjacent help ID `0x58a`: Teleports Cop after a bust.

These are descriptions shipped with the PC installation. In particular, the Pursuit description is not instruction-level proof of the relocation writer or its timing; that remains a separate open question.

Collision Recovery has a concrete reviewed consumer: `UpdateVehicleContactRecoveryCountdown` (`00429260`) ordinarily reloads countdown700, but selects175 when vehicle flag bit04 and runtime setting006fd4a0 are both nonzero (a separate +184 branch selects512). Conditional deductions and callback scheduling mean these values are not fixed wall-clock durations. The title therefore resolves the former unknown menu wording associated with the recovery policy; it does not establish every physical consequence.

`UpdateStoredRecordsFromVehicleResult` (`00450fe0`) ORs the active assist settings into a record WORD. This is recorded metadata, not evidence that all assists disqualify a result. Braking assistance must also remain distinct from CARP `usesanti` and its conditional wheel-response clamp; the menu key alone does not establish ABS control.

## Provenance and completion boundary

Read-only extraction from the imported v1.6.2 executable and installed resources; no game/configuration edits or runtime-memory writes. Executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Installed `text.eng` SHA-256: `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`. PE section-aware address conversion was used for descriptor/token reads, and strings were resolved through the localization offset table. Ghidra review corroborated the descriptor parser, token resolver, regular-race copies, recovery consumer and record metadata consumer.

**DONE:** menu title, Off/On ordinal and regular-race setting-copy crosswalk; Collision Recovery wording.

**OPEN:** actual selected runtime settings, other mode overrides, full assist effects and live comparisons. Pursuit relocation and ABS behavior retain their independent open status.
