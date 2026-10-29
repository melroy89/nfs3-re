# Indexed network unpacker registration and socket-open path

## Scope and evidence

Read-only static analysis of `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, in an ephemeral REA Ghidra 12.1.4 session. No executable, runtime, or persistent Ghidra project was modified. This pass is limited to the collection at connection-record `+0x30`, its indexed dispatcher, code that appends its callback records, and the socket provider open path.

REA byte evidence: `005125b0..0051260f` (`ev_fe2f7a572bf96ca9c7f19c4a93927d9c805bf0727cde5a06c0dd89d858e81a28`); queue initialization and adjacent routines `00512660..00512766` (`ev_c633eaad9107fc50b077dbb8a2703d8dfb4580d882bd6ab7407f385865881709`); provider-open wrapper `004f7380..004f739f` (`ev_65033af4cce8c3ff1f417c393d4a4a62ba18aa8795240155f56179065e806540`); common open manager `004f5130..004f5229` (`ev_dc6a38482377b0392352f5f857419e3fc62f5a65300198796cbcdc0dd9fe676b`); socket initializer `004f6c50..004f6def` prefix (`ev_661d5d417315adb88a7a850131e104e11514a24569de9b2d421ef97af688120c`); queue initialization helper `0050dcd0` (`ev_22a0ae71a32925af63459fe318124ce9eeb537dedd69b0858060eb103b3950e0`); generic list insertion helper `0050de50` (`ev_6472cd93849e294cb05bc29db7438b794f724623dfa3cbacd7b02f5e879cb5dc`); and the socket context record at `00566e8c` (`ev_fd1f0527c14b94f32e450e4b205951b7ab52a34da6d3ce3e47a7acb764693aa7`). Raw `objdump` disassembly was checked against these original bytes.

The address `00512710` has no primary Ghidra name, and Ghidra's instruction API returned undecodable for it and its interior stores. Its code is therefore described from the complete original-byte read and independent `objdump` decode, not as a Ghidra instruction observation. REA's direct xref result for `00512710` is empty (`ev_758166e68deb0b0988bace3d7ea3b521da2ee78845b532ed054f577ab542f317`).

## Indexed dispatcher contract

`005125b0` receives context in `EAX`, requested index in `EDX`, segment count in `EBX`, descriptor array in `ECX`, and the collection as its stack DWORD argument. Parent original-byte review confirms005125b3 saves EAX toESI,005125b5 saves EBX toEDI, then005125b7 loads the stack collection intoEBX. It calls `0050e1d0` to obtain the collection count. A negative index or an index greater than or equal to that count branches to `00512470` (`00512618..0051261e`). For an in-range index it stores the index at collection `+0x1c`, calls `0050e470` to retrieve the entry, places entry `+0x0c` in `EDX`, and calls the function pointer at entry `+0x08` (`00512607..00512615`). The entry callback receives original context inEAX, entry+0xc inEDX, original segment count inEBX and retained descriptor pointer inECX, with the collection pushed as stack argument. Calling this a raw payload pointer ABI would be incorrect.

The socket reader wrapper `005126f0` obtains the collection pointer from connection `+0x30` and calls `00512650`; that helper forces `EDX=0` before calling `005125b0` (`00512650..0051265c`). Thus the receive path requests **index zero**. When the collection count is zero, index zero is out of range and the dispatcher takes `00512470`'s flatten-and-connection-callback fallback. A populated, non-null index-zero entry would instead call its `+0x08` callback with `+0x0c` context. An in-range entry lookup that returns null follows the diagnostic path at `005125d4..00512607`; it does not take the out-of-range fallback. See also the previously established [length-bearing fallback contract](detailed-analysis-notes.md#type-0x0c-participant-state-handler), which covers `00512470` and the connection `+0x20` callback.

The count/get-item helpers and dispatcher observations above are static. They do not demonstrate a callback invocation during runtime.

## Observed entry append routine

The unnamed code at `00512710` is the one observed producer of entries for the connection `+0x30` collection:

1. It preserves owner `EBP=EAX`, callback input `EDI=EBX`, and context input `ESI=EDX`.
2. It requests a `0x10`-byte entry allocation through `004e1620`.
3. It stores the context at entry `+0x04`, callback at `+0x08`, and caller-supplied `ECX` at `+0x0c` (`0051274e..00512754`).
4. It loads the collection from owner `+0x30` and passes that collection and the new entry to `0050de50` (`00512757..0051275e`), then returns 1.

`0050de50` inserts at the collection head, links the former head as the new entry's next pointer, increments the collection count, initializes the tail when the inserted entry is first, and sets the collection's nonempty flag. The initialization helper `0050dcd0`, called by `00512660`, sets count to zero and head/tail to null before setting up the collection's helper metadata. These observations are grounded by the cited complete byte reads; Ghidra did not recover the entry routine as an analyzed function.

## Socket provider initialization and admission finding

The static provider record at `00566e8c` begins with type DWORD 1 and has `004f6c50` at `+0x04` (`ev_fd1f0527c14b94f32e450e4b205951b7ab52a34da6d3ce3e47a7acb764693aa7`). The wrapper at `004f7380` selects that record and calls common manager `004f5130` (`ev_ce98861d2590250742eda16d3130858f796b3401f285cd620055a6141025cc4c`). On its successful non-null-object path, `004f5130` calls `00512660` at `004f520d` (`ev_aa01d6972775255bc59ff4ba3e233851548a02215339c8a1f63a340c2a49706e`). `00512660` allocates the collection, stores it at owner `+0x30`, and calls `0050dcd0` to initialize it empty. The socket callback `004f6c50` initializes socket state and frame limits; its observed body does not write the collection's callback-entry fields or call `00512710`.

No static, populated index-zero entry was found for this socket-open path. This is supported by the following bounded checks:

- REA direct xrefs to `00512710` returned no source references (`ev_758166e68deb0b0988bace3d7ea3b521da2ee78845b532ed054f577ab542f317`). A full byte scan of the 1,699,840-byte executable found no little-endian absolute address constant for `00512710`; a full `objdump` scan of `.code` found no direct call or jump targeting it.
- A full `.code` disassembly found 33 direct call sites to the generic insertion helper `0050de50`. Their preceding instructions and collection operands were reviewed. The only call site that passes the collection loaded from an owner `+0x30` is the insertion inside `00512710` at `0051275e`. The other 32 sites use distinct global or other record collection bases; no other one was observed to append the `+0x08` callback / `+0x0c` context entry into this per-connection collection.
- The socket open manager's observed path initializes the queue at `00512660`; neither the socket wrapper nor the decoded socket initializer directly invokes the append routine. Its loader/provider API callbacks include indirect calls, so those targets are not treated as fully resolved.

Accordingly, for the reviewed direct socket-provider path, the queue starts empty and no in-binary direct registration is shown before index-zero dispatch. The code's empty-collection branch therefore selects the fallback. This is not proof that every possible runtime socket connection remains empty: dynamically computed indirect calls, code outside the observed static references, later writers through aliases, or external provider behavior were not exhaustively resolved. No nonempty index-zero execution was observed.

## Search boundary and remaining gaps

The negative search covers Ghidra's direct references to `00512710`, full-file absolute-pointer byte search for that address, the full `.code` direct branch-target scan, and all 33 direct `0050de50` call sites in the executable. It is not a complete whole-program alias/data-flow proof that no other code can mutate a per-connection collection, and it does not resolve indirect targets. The socket opener's dynamically called provider methods, later connection lifecycle writers, registration protocol outside this executable, and actual runtime collection contents remain unknown. This report establishes no runtime reachability, network behavior, or defect.
