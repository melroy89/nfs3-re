# Race setup preset compatibility matrix

## Scope and result

This report reconciles the existing lap, opponent-count, traffic, AI-skill and
gameplay-assist findings for issue 16. The audited image is the installed
`nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
This is a research-only synthesis; it adds no setting, preset UI, configuration
format or executable behavior.

The evidence supports a **mode-specific compatibility policy**, not a
cross-mode preset tuple. Regular race controls, Tournament, Knockout and Hot
Pursuit differ in which globals they retain, replace or consume. The evidence
does not establish a shipped preset named “Classic,” nor define its values as
an authoritative combination. A fresh executable initializer's individual
values, an installed `config.dat` candidate, a loaded `.trn`/`.kot` profile,
and the live race values are separate sources.

## Control matrix

| Control | Menu domain and storage | Executable initialization evidence | Race-mode behavior established by code | Host/client and network boundary |
|---|---|---|---|---|
| **Laps** | Location `laps` list has ordinals `0/1/2` for `2/4/8` laps. Encoded selector is `006fd4b0`; ordinary reconciliation decodes into `006fd4b4`. | The default initializer sets decoded total `006fd4b4` to `2`; the final accepted selector ordinal is not independently proven by that write. | Ordinary reconciliation decodes the selector. The mode-one builder writes total `2` when signed session mode is greater than `1`, otherwise `4`; mode two writes `2`. Their Location controls are disabled by the mode menu gate. No Hot Pursuit lap override is established in the lap-writer audit. | Location assets mark both lap controls `hostonly`. Network settings carry decoded lap total in byte `+4` and encoded option in byte `+5`; the writer can publish a byte value without the frontend decoder. Transport setup also writes a supplied DWORD to the decoded total. No complete peer-ordering policy is proven. |
| **Opponent count** | Opponents page `oppnumber`: `0=None`, `1=One`, `2=Full Grid`; selected ordinal `006fd4d0`. | Default initializer sets selector `0` (None). | Ordinary local roster maps these to `0`, `1`, or enough AI racers to fill the local eight-participant target. Reconciliation forces selector `2` in Hot Pursuit and modes 1/2. The series roster builders fill remaining positions independently of this selector. Hot Pursuit uses role-specific roster budgets; selector `2` does not mean the ordinary eight-car formula there. | Menu marks the controls `hostonly`; the reviewed client gate disables input. The selector is staged as network settings byte `+0x18` and received into the DWORD. This proves a serialized field path, not end-to-end peer agreement. |
| **Traffic** | `traffic`: ordinal `0=On`, `1=Off`; inverted storage `006fd4e8` (`0` enables traffic). | Default initializer writes `0` (On). An installed `config.dat` candidate also has zero at the corresponding blob offset, but its acceptance/current use was not observed. | Ordinary race adds traffic into remaining roster slots when enabled. Modes 1/2 reconciliation writes Off. Hot Pursuit normally obeys the selector, but its special `0055eb2e & 0x20` role branch clears Off and applies separate traffic/AI budgets. Mode 0/3 track reactivation tuning is separate from initial roster allocation. | Menu marks Traffic `hostonly`. The selector is staged at settings byte `+0x19` and the receiver copies it from that byte. Static settings flow does not establish update order or final agreement. |
| **AI skill** | Opponents page `ai`: ordinal `0=Normal`, `1=Aggressive`; `006fd4f0`. | Default initializer writes `0` (Normal). | Ordinary builder retains the current global. Modes 1/2 write `1` (Aggressive). Hot Pursuit writes `1` only under `0055eb2e & 0x20`; otherwise it inherits the existing global. The downstream effects are conditional profile/timer/acceleration paths, not one universal speed multiplier. | Menu marks skill controls `hostonly`. The reviewed network-setting byte map does not assign a corresponding skill field, and the direct-reference audit does not establish a receive-side copy. That incremental-map observation does not exclude the bulk setup transfer described below; live skill-update ordering remains unresolved. |
| **Gameplay assists** | `level.mnu` exposes Off/On ordinals for Braking, Collision Recovery, Traction, Best Line, Navigator and Pursuit. Selection globals are respectively `006fd474`, `006fd484`, `006fd488`, `006fd47c`, `006fd480`, `006fd48c`. | The crosswalk establishes menu values and regular-race copies, but does not provide a complete executable-default value for every assist selector. Do not substitute candidate config values for accepted startup state. | Regular race copies the first five settings to runtime fields `006fd490`, `006fd4a0`, `006fd4a4`, `006fd498`, `006fd49c`; it clears runtime Pursuit assistance. Modes 1/2 clear a `0x1c`-byte runtime assist span at `006fd490`. Hot Pursuit explicitly clears six fields `006fd490..006fd4a4`; other assist-copy behavior is unresolved. Effects differ by control: Braking feeds a shared track-speed controller; Collision Recovery changes a conditional countdown; Traction modifies selected coefficients/response paths. | Each `level.mnu` control has a `hostonly` codelink and the client-side menu handler disables such input under its observed role check. The reviewed 40-byte network settings map does not establish the field-level serialization or receive policy for every assist. Bulk setup transfer does carry these addresses as described below; no all-assist peer agreement claim is supported. |

The session-mode predicate used by the mode-one lap builder is a separate axis
from race mode. Its signed `session > 1` branch is documented as an instruction
condition; the compatibility work does not assign that predicate a user-facing
name or assume it means “network host” or “network client.”

## Source and persistence boundaries

The executable default initializer is a code path, not proof of the values
currently loaded by a particular installation. `config.dat` load/save routines
read or write the full `0x20f0`-byte configuration blob at `006fbb40`; the
loader accepts an exact-size blob. The inspected installed candidate supplied
traffic's zero value only. No runtime file-open/read observation established
that this candidate was accepted, and its other setup values were not used as
evidence for a “Classic” tuple.

Tournament and Knockout profile save/import paths also copy the full
`0x20f0`-byte blob. Their importers snapshot and restore several selected
runtime ranges, none overlapping the two progression words. This establishes
that profile import can replace these setup selectors and series progress,
since the selectors lie within the copied blob and outside the retained
snapshots, subject to the import success path. It does not prove that a
particular profile was loaded or that its settings are compatible with every
race mode.

One ordinary Single Race capture observed session/race mode `0/0`, track 0,
forward, two laps, opponent choice None, traffic enabled, one human racer and
seven registered traffic records. The captured AI-skill global was `1`
(Aggressive), despite the executable initializer's Normal value. Its
provenance was not traced; the observation therefore demonstrates why an
initializer cannot be reported as the live selection. The capture did not
establish the six assist values or compare other modes/settings.

### Bulk race-setup transfer is separate from lobby byte settings

The [next-round transfer audit](network-series-next-round-state.md) establishes a host block spanning `[006fd39c,006fdc2c)`, length0x890, with client participant-field restoration distinct from these globals. The block includes the following fields:

| Field | Offset from block start |
| --- | ---: |
| Assist selector Braking `006fd474` | `0xd8` |
| Assist selectors Best Line/Navigator `006fd47c/480` | `0xe0/0xe4` |
| Assist selectors Collision/Traction/Pursuit `006fd484/488/48c` | `0xe8/0xec/0xf0` |
| Runtime assist span beginning `006fd490` | `0xf4` |
| AI skill `006fd4f0` | `0x154` |

Consequently the absence of a named skill/assist field in the40-byte incremental lobby map is not evidence that those values never cross peers: these globals are inside the full race-setup transfer. This establishes byte coverage for the reviewed transfer path, not successful delivery, final effective control policy, handling of a later menu edit, or live agreement in every mode. Those ordering/runtime questions remain open.

## Mode-level reading

- **Regular race, mode 0:** the menu choices have direct meanings, but the
  effective state can reflect default initialization, accepted config/profile
  bytes, network settings or other earlier setup. Traffic fill depends jointly
  on opponent choice and the inverted traffic-enable value.
- **Tournament, mode 1:** reconciliation forces Full Grid and Traffic Off;
  the builder forces Aggressive. The lap builder selects 2 or 4 total laps
  based on signed session mode. Runtime assists are cleared over the reviewed
  span. Series AI fill is not user-controlled by the ordinary opponent-count
  choice.
- **Knockout, mode 2:** the same Full Grid, Traffic Off, Aggressive and assist
  clear policies apply. The builder sets decoded lap total to 2. Later
  Knockout eligibility/progression can reduce AI rows; that is distinct from a
  user-selected ordinary opponent count.
- **Hot Pursuit, mode 3:** opponent selector is forced to Full Grid, while the
  roster is role-specific. Traffic may be enabled by the stored choice or
  forced enabled on the special `0x20` setup branch; this branch also forces
  Aggressive. Without it, skill inherits prior state. Six reviewed runtime
  assist fields are cleared. The current lap-producer audit does not establish
  a mode-3 lap policy.

No shipped preset definition named “Classic,” shared preset representation or selection handler was established by this synthesis. Calling the executable's individual initial values “Classic” would be an analyst-defined convenience label, not a proven shipped definition.
If a product-level preset is later proposed, its intended tuple and whether it
should mimic fresh defaults, the installed candidate config, or a particular
manual setup remain product questions; none is answered by these code paths.

## Evidence and limits

This synthesis links the existing detailed reports: [lap choices and mode
availability](lap-choice-gameplay-domain.md), [lap-count
writers](lap-count-producers.md), [opponent-count and traffic
behavior](traffic-density-options-behavior.md), [series opponent
policy](network-series-ai-option-semantics.md), [AI skill and profile
tuning](ai-difficulty-gameplay-controls.md), [assist menu
crosswalk](gameplay-assist-menu-crosswalk.md), [Braking](braking-assist-gameplay-behavior.md),
[Traction](traction-assist-gameplay-behavior.md), [profile save/load
lifecycle](series-save-resume-lifecycle.md), and the retained [ordinary
traffic runtime observation](evidence/runtime/ordinary-single-race-traffic-observation.json).

The completed evidence is static except for that single ordinary-race traffic
capture. It does not establish a complete multiplayer host/client application
order, a final accepted configuration/profile for the current installation,
all assist copies in modes 1/2/3, a complete cross-mode lap policy, or a
Classic preset definition. No new preset or configuration change is proposed
by this report.
