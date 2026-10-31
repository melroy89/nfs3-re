# Original versus Modern: resource-backed frontend page

## Evidence and boundaries

**Static comparison; no rendering or decompression execution.** Paired entry `00441cb0` renders a selected 16-byte page record into an intermediate raster and uploads shape tiles. Its main body `00441cb0..0044236c` differs in exactly **one byte**, at `00441d03`: unsigned dispatch maximum 4 becomes 5. Modern's additional block `00437820..004378b6` is an out-of-line switch arm, not a separate callable function; all its exits jump to shared tail `004421b8`.

Reproduce with `python3 analysis/scripts/audit_frontend_page_difference.py`. The [manifest](evidence/audits/original-modern-frontend-page.json) retains baseline hashes, both main bodies and out-of-line regions, five retained switch targets, new sixth target and selected page-record bytes. Ends are exclusive. The original bytes at the distant region are raw comparison data, not an authenticated counterpart function.

The first five switch targets remain `{00441d11,00441d11,004421e0,004422d0,00442114}`. Modern adds target `00437820` for type 5. Original values above 4 bypass the switch and join the shared tail; original bytes after the five-entry table must not be interpreted as an admitted sixth case.

## Page record 75 changes representation

At `00555c08 = 00555758 + 75*16`:

| Version | Four DWORD fields |
|---|---|
| Supplied original | `{3, 470h, 475h, 0}` |
| Official Modern | `{5, 0053f7d4, 0053f7e0, 0}` |

Original type 3 follows the localized text-range branch. Modern's pointers resolve to **`ABOUT.QFS`** and **`cred`**. The [baseline resource inventory](original-modern-differences.md) records RCDATA `ABOUT.QFS`; the executable use site now connects that named data to a page renderer. Record index 75's actual runtime selection, navigation label and historical introduction remain separate questions.

## New type-5 mechanism

The branch reads selected record+4, calls resource helper `004f1f58`, and skips to the common tail on zero result. It passes the resulting pointer to size/query helper `004f2710`, checks for zero, allocates a temporary block through `004e1620` with EBX=16, and checks allocation. It then passes source and destination to `004f2620`. Existing analysis treats this as the unpack path; this audit does not validate arbitrary compressed payloads or infer a success result where the caller does not check one.

It looks up record+8 (`cred`) in the temporary object through `004ef1e0`, then reads unsigned shape width/height WORDs at +4/+6. There is no local null check between this shape lookup and those reads. Horizontal/vertical positions are formed as **logical right shifts of wrapped `(608-width)` and `(320-height)` by one**, then supplied with the shape to `004ef3f0`. This is not general signed division toward zero for oversized dimensions. The temporary block is released through `004e1890`, and control jumps to the common tail.

The preexisting main path creates a 608×320 intermediate raster; its allocation/setup, ordinary page arms and upload/destruction instructions remain byte-identical apart from the dispatch-bound byte. Shared tail deselects raster, uploads raster+20h using the incoming argument, destroys the raster and returns the saved result, under the previously documented destructor preservation contract. Identical instructions do not prove identical assets, helper implementations or visible output.

**Verified:** one-byte main-body delta, retained five cases, discontiguous new case, text-to-resource page-record change and resource/shape names. **Unresolved:** selected-index admission, resource/unpack/shape lifetime and failure contracts, payload geometry, actual displayed page and release attribution. No claim that every frontend text page was replaced or all resource-present paths render successfully.

Existing [detailed notes](detailed-analysis-notes.md) document the main text/shape branches. Their earlier phrase “Original table” in the discontiguous-body investigation referred to the then-current analyzed Modern program, not the supplied-original executable; the paired five-versus-six-case evidence here resolves that ambiguity.
