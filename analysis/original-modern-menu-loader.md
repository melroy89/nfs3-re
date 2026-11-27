# Menu graph loader: literal path versus initialized buffer

**Verified local code delta:** the complete `LoadFrontendMenuDefinitionGraph` body at `00449510..00449891` differs in exactly three bytes, at `00449600..00449602`. These belong to the immediate operand of `MOV ESI,imm32` at `004495ff`:

| Supplied original | Official Modern v1.6.1 |
|---|---|
| `ESI = 00538f84`, literal `.\FeData\Menus` | `ESI = 007a2d34`, initialized directory buffer |

The [audit script](scripts/audit_menu_loader_difference.py) hashes both executable baselines, retains the complete disassembly/body hashes and asserts the exact changed-address set. The [manifest](evidence/audits/original-modern-menu-loader.json) also retains the unchanged filename format `%s.mnu` (`00538f94`) and open mode `rb` (`00538f9c`). Ends are exclusive. This is a real paired function comparison; no distant original region is assigned as a counterpart.

## Path construction

At `004495ff..00449676`, the loader copies the selected NUL-terminated directory string into its stack buffer, calls path separator helper `004529a0`, appends the current descriptor name using `%s.mnu` through `004df690`, then calls file-open helper `004edfe8` with mode `rb`. On zero open result it skips that descriptor's file-processing body. There is no alternative resource-open call in this local missing-file branch.

Modern's [startup path audit](original-modern-startup-paths.md#4-path-slots-and-directory-preparation) independently maps initialization of `007a2d34` to `.\fedata\menus\`, one of 22 runtime path slots. The original literal and Modern initialized default therefore name the same ordinary relative directory on a case-insensitive Windows filesystem. The change makes the loader consume initialized state rather than its own literal. It does **not** prove that this slot is a user-configurable override, that its value never changes later, or that Windows/Wine/native Linux resolve every spelling identically. Working-directory success and later changes remain separate concerns.

The separator helper makes the original and 1.2.0 defaults produce the same filename bytes for a given menu name. With DF clear, `004529a0` checks the last byte of a nonempty prefix at `004529c5`. If it is already a backslash, the helper returns without writing. Otherwise it appends the NUL-terminated backslash literal at `00539600`. Thus both original `.\FeData\Menus` and 1.2.0 `.\FeData\Menus\` become `.\FeData\Menus\setup.mnu` for the Setup descriptor. An empty prefix gets a backslash too, and a trailing forward slash is left in place with a backslash appended. These are byte transformations. The helper does not normalize case or consult the filesystem.

The 95-byte window `004529a0..004529ff`, including the complete helper and adjacent padding, matches across the hosted original and all twelve retained Modern builds (SHA-256 `cb9bd121974f17c19b2ed4399a23575367b81e1f1a03ae4eb724d542e3531d99`). The literal bytes `5c 00` match at `00539600` in all thirteen executables.

## Release boundary and first initialized prefix

The instruction at `004495ff` still loads `00538f84` in Modern 1.0.0 and 1.1.0. Every retained version from 1.2.0 through 1.6.1 loads `007a2d34`. Comparing all 897 bytes of `00449510..00449891` against the hosted original yields two groups. The original, 1.0.0 and 1.1.0 match exactly. All ten retained 1.2.0–1.6.1 releases differ from the original at the same three operand bytes and match one another across the full span. In 1.2.0 the startup call at `004a6e36` reaches the path-table initializer at `004a6f04`. Its loop copies NUL-terminated strings from `0053ec2c` into slots spaced `0x80` bytes apart beginning at `007a27b4`. The zero-based slot 11 lands at `007a2d34` and receives `.\FeData\Menus\`, from `0053ed18`. The original literal and the first replacement name the same relative directory with a different trailing separator. The capitalization changes in 1.4.0, when the initializer's source table moves to `0053eb20` and slot 11 becomes `.\fedata\menus\`. It remains lowercase through 1.6.1, including after the table moves to `0053f42c` in 1.6.0. The packaged `fedata/menus/setup.mnu` member already uses lowercase in every retained Modern archive, including 1.0.0 and 1.1.0. In those first two releases, slot 11 instead starts with the Italian speech directory, so their literal menu-loader operand is essential to interpreting that slot correctly.

To reproduce, extract `nfs3.exe` from each retained archive and compare the 897 bytes at PE RVA `0x49510`. Disassemble `004495ff..00449604` to decode the changed operand. For the prefix history, follow the startup initializer’s table pointer and read its twelfth NUL-terminated string. In 1.2.0 the copy loop is at `004a6f04..004a6f24`. Compare the archived member spelling with `7z l -slt`. The [Setup menu graph comparison](original-modern-options-postgame.md#the-display-helper-stops-overwriting-the-history-pointer-in-120) confirms that the relevant archived menu assets themselves are unchanged across this boundary. Actual file resolution and later buffer writes remain unverified.

## What is retained locally

Every byte outside that operand is identical within the complete function. Reusing the [existing loader research](detailed-analysis-notes.md), the observed body:

- Accepts definition name in EAX and reset flag in EDX; reset clears entry-type DWORDs across 2,000 `bch`-stride entry records and resets counts/arena position. It does not zero every field of every entry in that loop.
- On a non-reset duplicate name, returns early rather than rebuilding the graph.
- Initializes a zeroed `24h`-byte runtime descriptor and registers callbacks through `00442b10`.
- Parses opened menu files, discovers nonempty `nextmenu` dependencies and queues previously unknown descriptor names. The descriptor count can grow while the graph is traversed.
- Appends an entry-type-zero template sentinel after a successfully processed file, then visits descriptors through `00449990` at the end.
- Returns EAX=1 at the common exit, including normal paths where file opens failed. That return must not be promoted to an all-files-loaded success flag.

These are retained local instructions. Parser/helper implementations, callback tables, initialized fields and asset contents can differ despite identical call instructions. In particular, [the official menu inventory](original-modern-common-menu-buttons.md) finds all 52 selected official/uppercase-backup file pairs differ bytewise; identical local parsing does not imply identical menus or semantic differences in every file.

## Reconstruction requirements and unresolved work

Keep directory initialization, path joining, dependency discovery, descriptor registration and callback invocation distinct. An isolated loader test must supply the initialized directory buffer before using the Modern interface, and must reproduce missing-file/duplicate-name behaviour before any deliberate improvements. For native Linux, case-sensitive external asset lookup needs an explicit compatibility policy; a visually equivalent path spelling is not universal filesystem equivalence.

Further inspection should compare callback registration and parser helper bodies where a selected menu depends on them, qualify file/arena/queue capacity and failure contracts, and verify actual loaded files in a suitable runtime session. This bounded delta does not establish whole-frontend equivalence, historical release introduction or complete loader safety. No executable, Ghidra database, export or reconstruction source was modified; no target instructions were executed.
