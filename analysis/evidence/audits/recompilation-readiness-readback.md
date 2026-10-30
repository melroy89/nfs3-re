# Reconstruction-readiness readback evidence

Evidence type: saved Ghidra database inspection, unchanged-file parsing and retained original-instruction probe inspection. No C export, reconstruction source generation, C compilation, gameplay or new probe execution occurred in this audit.

## Snapshot identity and inspection method

Final program database: `nfs3_decomp.rep/idata/f9/~00000f9f.db/db.3144.gbf`, SHA-256 `00b157c74363b3d10efd1138c537d7127f7bbf7cd97dfbf52dc4ccbb86fa2c5a`.

The previous storage-correction checkpoint was `db.3143.gbf`, SHA-256 `2e5078cae95f759643e258d9cf7bac932dbbf6a9e0bc63e347b75f144dbc1420`. The pre-audit `db.3141.gbf` hash was `ee64d4bae802146ef7f5957027fc7a7a48908029734f484aa11d5bdac85aa93e`. Git preserves those earlier states. An initial parameter-name collision failed before the first signature update; the successful retry and independent reopen, rather than its process exit code, establish the corrections.

Headless invocation shape used for final readback:

```sh
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
  /home/melroy/Documents/ghidra/support/analyzeHeadless \
  /home/melroy/Documents/projects/nfs3-re \
  'nfs3_decomp/Electronic Arts/Need For Speed III' \
  -process nfs3.exe -readOnly -noanalysis \
  -scriptPath /home/melroy/.local/state/nfs3-re/readiness/scripts \
  -postScript ReadinessInspect.java -postScript ReadinessInventory.java
```

The private diagnostic scripts print program language/compiler, function metadata, custom storage, plate comments, memory blocks, instructions, references, body hashes, datatype sizes and exporter defaults. They do not invoke the C exporter. A separate `ReadinessFlow.java` enumerates instructions/branch targets and reference destinations. These are investigation helpers in private state, not reconstruction sources or a published export runner. Findings and supporting excerpts are retained below; a future export runner still needs implementation under the [plan](../../recompilation-readiness.md).

For each inspected body, the check traversed `getInstructions(body,true)`, compared each instruction start to the previous maximum+1, inspected all flow targets, and enumerated reference destinations inside the body with `getReferenceDestinationIterator(body,true)` followed by `getReferencesTo`. References from outside to an interior address were counted separately from entry calls. This corrected an initial diagnostic that mistakenly iterated from-addresses; the final destination-based check is the source for the zero interior-reference counts.

Final read-only output:

```text
BASELINE 2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb
LANGUAGE x86:LE:32:default COMPILER windows FUNCTIONS 4340
INVENTORY local=4133 external=207 thunks=36
SIZES ptr=4 int=4 long=4 float=4 double=8 longdouble=8
```

Inventory identity: SHA-256 `94b4ca701df43c7106503e0b6ce40fb590c5b3d920ac62900444fed4af8716d7`, calculated over UTF-8 `entry|body|name\n` for all local functions in Ghidra's forward address iteration. This is an inventory fingerprint, not an export-completion hash.

Private durable evidence directory: `/home/melroy/.local/state/nfs3-re/readiness/`.

| Raw record | SHA-256 |
|---|---|
| `final-readback.txt` | `85341109ba8400d3fd49eea630553b911693bc87f1a7c790c88980684abfbdb2` |
| `flow-final.txt` | `ba7ddac622cc900019967fe42173f733d0c12a01c782591da0b3e219ed297669` |

These logs are local support material; this Markdown and the saved database provide the reviewable findings. The private scripts/logs are not prerequisites for opening the project.

An isolated archive of the staged Git snapshot was also opened read-only, independently of the working project. A verification script asserted all three custom parameter/return-storage maps, the executable fingerprint and both updated plate comments. Result: `READINESS_ISOLATED_CHECKPOINT_OK functions=4340`. The isolated log SHA-256 is `9fb41b687485b3fa87e14778e8dab45c9f0315326f78fade3c8d6c6611a78bce` (`isolated-readback.txt` in private state). An initial copy under a hidden `.local` path was rejected by headless project-path validation; the successful check used a temporary non-hidden project path. No database mutation was needed to resolve that path issue.


## Contracts and callers

Custom storage survived a fresh read-only reopen:

| Entry | Stored parameters | Stored return / purge |
|---|---|---|
| `00485c30` | candidate EAX:4; sourceLine EDX:4; bounds EBX:4; returnPolicy ECX:4; edgeMask Stack[4]:4 | float pointer EAX:4; purge 4 |
| `004abd9c` | vehicleInput EAX:4; tyreTuningInput EDX:4 | float10 ST0:10; purge 0 |
| `00518640` | destination EAX:4; source EDX:4; byteCount EBX:4 | void pointer EAX:4; purge 0 |

The `004abd9c` plate now says custom storage supersedes the historical MCP-only limitation. It retains the binary32-rounding and mutable tyre-field contract. The `00485c30` plate now states data extents, EBX volatility, uninitialized scratch provenance, non-reentrancy limits and bounded flow results. Independent readback found these comments in the saved database. No function-body bytes or boundaries were changed.

Selected unchanged leaf instructions support the ABI and side effects:

```text
00485c30 PUSH ESI
00485c31 PUSH EDI
00485c32 PUSH EBP
00485c33 MOV EBP,ESP
00485c35 SUB ESP,0x1c
00485c38 MOV ESI,EDX
00485c3a MOV [EBP-4],ECX
00485c3d MOV EDX,[EBP+0x10]  ; entry stack+4 after three pushes
00485c40 FLD float ptr [EAX]
00485c42 FLD float ptr [EBX+0xc]
00485d34 MOV BL,byte ptr [EDX]
00485d36 OR BL,0x2
00485d50 MOV BH,byte ptr [EDX]
00485d52 OR BH,0x4
00485f00 TEST ECX,ECX
00485f02 JNZ 00485f0a
00485f04 CMP [EBP-4],0
00485f08 JNZ 00485f11
00485f0a MOV EAX,00791c08
00485f11 XOR EAX,EAX        ; rejected policy-nonzero path
00485f13 MOV ESP,EBP
00485f15 POP EBP
00485f16 POP EDI
00485f17 POP ESI
00485f18 RET 4
```

This is a selected excerpt, not linear fall-through between every displayed line: the pointer-return path jumps from `00485f0f` to `00485f13`, bypassing the null-return XOR. Bounds and source roles are corroborated by the full saved instructions and the existing [probe register setup](../../scripts/probe_line_boundary_helper.py).

Tyre helper calls at `004ac298`, `004ac54a`, `004ac567`, `004acaa0` were revisited, including preceding loads and subsequent x87 use. At `004aca94..004acaa0`, EDX becomes `[vehicle+220]+58`, EAX becomes vehicle, and the caller consumes ST0 then stores a binary32 result at `004acaab`. At `004ac567`, the caller stores ST0 at `004ac56c`. Preserving these separate caller rounding points matters.

Byte-move calls at `0052c2c8`, `0052c3a7`, `0052e9e8`, `0052eadd` prepare EAX destination / EDX source / EBX count; subsequent code uses ECX, which the helper saves/restores. Raw bytes `8c da` at `00518658` and `8e c2` at `0051865c`, decoded independently with GNU objdump, implement reading DS then setting ES from that selector. Ghidra's printed second segment-MOV operand order is misleading. Backward path uses STD at `0051865e`, CLD at `0051866e`; forward path has no CLD.

Caller contracts and geometric caveats are reused from [detailed notes](../../detailed-analysis-notes.md), sections “Geometry-intersection helper outer contract”, “Line boundary intersection candidate” and “Isolated execution of the line-boundary helper”. No broad numerical or caller-domain proof is inferred from the signatures.

## Bodies, references and data

| Entry | Half-open body / instruction count | SHA-256 of body bytes |
|---|---|---|
| `00485c30` | `[00485c30,00485f1b)` / 255 | `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f` |
| `00485f20` | `[00485f20,004860a1)` / 157 | `ff004f6c18db46f3794e1280f1e83aee2531e13329ee4254925039daa7ce2ac9` |
| `004860b0` | `[004860b0,004862f5)` / 237 | `c9c9b53421ff34cba58ded227f81a74425a0a278c3a5c800dfac204d5d0542f8` |
| `004abd9c` | `[004abd9c,004ac027)` / 176 | `27c7ce1baedc6282855c2aadecfdbee768f25db8649f66aa9caea4e94ba9677b` |
| `00518640` | `[00518640,0051868d)` / 47 | `64b39b42ecef516f64ab5db044fa9028e0591d59af23f14583d393fbc4cd6b2c` |

All five had zero instruction gaps and zero known outside-to-interior references in the final destination-based check. All jumps stayed inside their bodies; no indirect transfer was found. Only the two caller bodies make calls, all to `00485c30`. Incoming leaf call instructions: `00485ff0`, `00486071`, `004861cf`, `00486247`, `0048627e`, `004862cd`. No dispatcher dependency was observed in this boundary.

The leaf's only absolute data references are `00791c08` and `00791c0c`; their direct known references all originate inside the leaf. Example later writes: `00485cc7` to the first float and `00485cb2` to the second. A returned/aliased pointer can permit indirect references invisible to this search. The code has 29 PE HIGHLOW relocations (type 3), beginning at operand `00485cb4` and ending at `00485f0b`; these are relocatable code operands, not 29 additional data objects.

Saved memory blocks:

| Block | Inclusive range | Initialized in database |
|---|---|---|
| Headers | `00400000..004003ff` | Yes |
| `.code` | `00401000..00533fff` | Yes |
| `.idata` | `00534000..005355ff` | Yes |
| `.data` | `00536000..0056d5ff` | Yes |
| `.bss` | `0056e000..0070cfff` | No |
| `.bss.recovered` | `0070d000..00a1efff` | No |
| `.reloc` | `00a1f000..00a361ff` | Yes |
| `.rsrc` | `00a37000..00a52dff` | Yes |

PE `.bss` has `VirtualSize=0`, `SizeOfRawData=0x4b1000`, `PointerToRawData=0`, attributes `c0000080` (uninitialized/read/write). `pefile` warns that the apparent raw size exceeds the file. This is a noncanonical header, not evidence of file-backed scratch bytes; do not blindly use raw offset 0 or assume Ghidra's recovered split is an original section. Actual loader/startup initial values beyond controlled fixture seeding remain unverified.

## PE resources and imports

Read-only `pefile` 2023.2.7 parsing, retaining each descriptor rather than keying only by DLL name (KERNEL32 occurs twice):

| DLL descriptor | Lookup RVA | IAT RVA | Entries |
|---|---|---|---|
| GDI32.dll | `001340f0` | `00134458` | 2 |
| ADVAPI32.dll | `001340fc` | `00134464` | 4 |
| OLE32.dll | `00134110` | `00134478` | 1 |
| SHELL32.dll | `00134118` | `00134480` | 1 |
| KERNEL32.dll | `00134120` | `00134488` | 113 |
| WINMM.dll | `001342e8` | `00134650` | 7 |
| KERNEL32.dll | `00134308` | `00134670` | 3 |
| WSOCK32.dll | `0013431c` | `00134684` | 25 |
| USER32.dll | `00134384` | `001346ec` | 50 |
| DINPUT.dll | `00134450` | `001347b8` | 1 |

Total 207 entries. Examples corroborate existing loader/interface research: `LoadLibraryA`, `GetProcAddress`, `GetModuleHandleA`; `DirectInputCreateA`; Winsock entries include ordinals rather than all being named imports. A private initial dictionary-by-DLL draft lost the first KERNEL32 descriptor; the descriptor-preserving count above supersedes it. No incorrect import inventory was used as a linking gate.

Resource paths use **type / name-or-ID / language**; all language IDs are 0. Values below are RVAs, not absolute VAs. This is an inventory; use by the leaf is absent, and whole-game necessity has not been established.

| Type | Name/ID | Payload RVA | Size |
|---|---|---|---|
| 3 (ICON) | 100 | `006372b8` | 1,128 |
| 3 | 101 | `00637730` | 2,440 |
| 3 | 102 | `006380c8` | 4,264 |
| 3 | 103 | `00639180` | 9,640 |
| 3 | 104 | `0063b738` | 16,936 |
| 3 | 105 | `0063f970` | 24,070 |
| 3 | 200 | `006457c0` | 744 |
| 10 (RCDATA) | ABOUT.QFS | `00645ad0` | 47,372 |
| 10 | SNAP.WAV | `00651400` | 3,240 |
| 14 (GROUP_ICON) | MAIN.ICO | `0063724c` | 90 |
| 14 | ORIG.ICO | `0064579c` | 20 |
| 16 (VERSION) | 1 | `00652800` | 1,008 |
| 24 (MANIFEST) | 1 | `0065249c` | 603 |

## Exporter inspection and probe limits

Installed source inspected: `Ghidra/Features/Decompiler/lib/Decompiler-src.zip`, member `ghidra/app/util/exporter/CppExporter.java`. Source archive SHA-256 `cc15e14c15ad9eda7abefde73c757112e88307c81b2088b7d9ce670e258fee92`; `Decompiler.jar` SHA-256 `8fcbca197aee63507607f66512a64756b0ad77545964257b2048477b5faea3f4`.

Instantiated defaults were read without calling export: C file on, header off, C++ comments on, datatype definitions on, referenced globals on, empty tag filter, excluded-tag mode on. `DecompileOptions` default timeout is 30 seconds. The [future procedure](../../recompilation-readiness.md#pinned-future-procedure-not-executed) deliberately overrides header/type/comment choices and pins options.

Source inspection confirms null address selection falls back to program memory; selected functions are decompiled; diagnostics can produce an “Unable to decompile” comment rather than a function body, while file-level export returns true. This is why the per-entry procedure needs a separate completion/error ledger. None of this establishes that an export succeeded or is repeatable.

Retained original-byte oracle inspected, not rerun:

- [Script](../../scripts/probe_line_boundary_helper.py) SHA-256 `dcd7caa31b8a6e72ffc2706184b3e72e4754d1d881fb8d28f76427c6b5c6ea4e`.
- [40-row result](../probes/line-boundary-helper-probe.json) SHA-256 `efab8ccdfc856300459593afa7a0955d799e99331e443b736267436ea64148d0`.
- Twenty source vectors × two policy values, mask seeded `a0`, FNINIT/CW `037f` every row, scratch zero-seeded only once. It captures EAX return, two raw float words, mask, CW and SW. Preserved GPRs, EFLAGS, caller execution, populated x87 stack, concurrent calls and reconstructed C are not covered.

Final scope: verified saved metadata/contracts and bounded original instruction/data facts; inferred future toolchain/interface choices; unresolved export repeatability, complete machine equivalence, arbitrary aliasing/initialization and game integration.

## Follow-up handoff review

Reviewed from commit `828a1ce71ac7f975b01b62aac7413323e722ca49`. Section 6's proposed 32-bit Windows model is **ILP32**, not LLP64. Its pointer/int/long widths were already correct and remain 4 bytes. This corrects a terminology defect in the proposal; it changes neither the saved compiler specification nor any executable/database bytes.

An independent read-only report review checked all eight handoff areas and the installed `CppExporter.java` constructor, selection and failure-output handling. It found no additional actionable contract/evidence inconsistency. Parent inspection also checked the retained probe source/results and source-backed exporter behavior. The exclusion rule is now worded explicitly to include the two caller-context entries, avoiding any suggestion that their rows add to the 4,130 exclusions. The acceptance table now has one row per handoff item, and the next-phase sequence separates sample export, type/expression/toolchain preparation, standalone implementation/linking and comparison, removing the earlier circular wording about completing priorities 1–4 before their own work.

Current file SHA-256 checks matched the values above for the executable, `db.3144.gbf`, probe script and retained probe result. Read-only PE parsing again counted 207 imports; the retained fixture still has 40 rows. The user separately reported a successful independent read-only reopen verifying the three custom register signatures, saved comments and 4,340 entries, with matching executable/database/probe hashes. This follow-up did not repeat that reopen or mutate Ghidra: the existing saved corrections remain appropriate, and the model-label correction belongs in Markdown. No new save/readback cycle is necessary when no Ghidra change is made.

Remaining unknowns retain their stage and follow-up in report §8:

- **Reference export:** no output/re-export equivalence has been observed; execute the three-address two-run procedure only after authorization.
- **Module compilation:** C types, any emitted unsupported constructs and the explicit x87/store model remain unimplemented; inventory actual reference output and pin/qualify the ILP32 toolchain in the next phase.
- **Linking:** the standalone symbols/CRT/adapter are specified as proposals, not linked artifacts; inspect real helpers/imports and prove ABI when those objects exist.
- **Runtime validation:** no C-versus-original comparison exists; extend register/FPU capture and execute the stated fixture on both implementations. Actual loader/startup, alias/reentrancy and caller/game integration require separate evidence before expanding that scope.

No C export or reconstruction source, toolchain installation, compilation/linking, new instruction probe or unrelated scratchpad investigation was performed during this follow-up. The completed deliverable is the bounded readiness audit and actionable next-phase plan, with later engineering gates explicitly unqualified.
