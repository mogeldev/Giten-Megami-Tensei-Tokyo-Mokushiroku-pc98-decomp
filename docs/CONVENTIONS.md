# dds98 — conventions & parameters

Applies to the byte-match project for **Giten Megami Tensei** (game engine `DDS98.EXE`).

## Parameter block (as of: round 1, 2026-11-23)

| Parameter         | Value                                                                                                                  | Evidence |
|-------------------|-----------------------------------------------------------------------------------------------------------------------|-------|
| `<NAME>`          | `dds98`                                                                                                               | Engine binary |
| `<BINARY>`        | `giten\DDS98\DDS98.EXE` — 480 710 B, dated 10.03.1997                                                                 | Retail (the installed game) |
| `<BIN_FORMAT>`    | **MZ** (16-bit DOS EXE); load image ends at file offset 339 735; 3 562 relocations; **overlay ≈ 141 KB** (starts with NUL bytes, contents unknown) | MZ header |
| `<ARCH>`          | x86-16, **real mode**; CPU base (8086/186/386 → `/G0|/G1|/G2`) pinned down by idiom scan                            | Ghidra `x86:LE:16:Real Mode` |
| `<LOAD_BASE>`     | Ghidra mapping **`0x1000:0000`** (linear `0x10000`); entry **`0x1871:0BE5`** (header `CS:IP 0871:0BE5`)              | MZ header + `DDS98_functions.txt` ("entry") |
| `<DISASM_EXPORT>`| Ghidra 12.2 PUBLIC — project `ghidra_proj\GitenDecomp.gpr`, C export `decompiled\DDS98_decompiled.c` (1 970 functions)      | present |
| `<TOOLCHAIN>`     | **Candidate: Microsoft C 8.00x (16-bit, 1992/93)** — binary contains `MS Run-Time Library - Copyright (c) 1992, Microsoft Corp` + `run-time error` table. Exact version/linker: **phase 0 via calibration compile**, don't guess | CRT strings |
| `<CFLAGS>`        | **confirmed: `/G1 /AM /Gs /Os`** (calibration family 35ca:8090..9c, 4× RELOCS). Medium model: near data + far code; `/Gs` (no stack checks — the original carries no chkstk calls); `/Os` (bare leaf form without dead ENTER frame); `/G1` (186 idioms) | match.py, 2026-11-23 |
| `<OBJ_DUMP>`      | Object format will be **OMF** → `wdis` (Open Watcom) / `tdump` (Borland) as readers, otherwise our own `tools/omfdump.py`   | follows from toolchain |
| `<HOST>`          | Windows x64; MSC 8 only runs under DOS → **wrap the DOSBox wrapper in the build script**                                    | System |

## Addresses
- Ghidra mapping: `SSSS:OOOO`, linear = `seg*16+off`; image base `0x1000:0000` = linear `0x10000` = file offset `0x3800` (MZ header, 896 paragraphs).
- File offset = `linear − 0x10000 + 0x3800`, valid up to offset 339 735 (after that: overlay).
- MZ is relocatable at load time (3 562 relocs): always compare **image-relative against the Ghidra mapping**; which bytes are linker operands, **read from the object relocation table**, never guess.

## Codegen traits of the original compiler (consolidated; /F and /G0 corrections in rounds 90-91)

These are the **properties of the original code generator that Microsoft C 7 cannot
reproduce**. Each was established by isolating it in a function whose body otherwise
matches byte-for-byte, so each is a compiler property rather than a source mistake.
Every one was also tested against the flag matrix (`/Os`, `/Ot`, `/Od`, `/Ox`,
`/Oa`, `/Oi`, combinations) without success. Unit/byte counts come from
`tools/gap.py` and `docs/GAP.md`.

| # | Trait | Evidence | Units / bytes |
|---|---|---|---|
| 1 | doubling by `add r,r` instead of `shl r,1` | `4e11:007e` matches except the final `03 C0` (`add ax,ax`); MSC emits `D1 E0`. Explains the 74×`03 DB` vs 18×`D1 E3` census that round 34 misread as hand-written assembly | 204 / 66 762 |
| 2 | *not a compiler trait*: `90 0E E8 rel16` | **CORRECTED round 91:** this is Microsoft LINK `/FARCALLTRANSLATION` (`/F`, with `/PACKC`) rewriting the compiler's `9A seg off` into `NOP; PUSH CS; CALL NEAR`. 3 507 of the 3 564 `0E E8` in the image carry that NOP; reproduced locally with `LINK 5.10 /F /PACKC`. `tools/match.py` masks the 5-byte slot, so those units are reachable; the folded 4-byte form (`0E E8` without the NOP) is handled as a one-byte shift since round 6 | 0 blocking (was 1232 / 180 177) |
| 3 | far-pointer parameters loaded as two words (`8B 5E 06` + `8E 46 08`) instead of `les bx,[bp+6]` | `1df5:0008`, `2aa3:0048` — bodies otherwise identical | 367 / 84 175 |
| 4 | stray `90` padding outside a translated far call | Most of the old 1 400-unit count was the `/F` NOP of trait 2. The rest are real: `47ef:0008` (`EB 03 90` vs `EB 02`), `2aa3:0002` (two `90` bytes, all displacements +2); `/Os` never pads, MSC 7 pads only function ends under `/Ot` | 561 / 163 630 |
| 5 | **`8B E5 5D`** (`mov sp,bp; pop bp`) instead of `C9` | **RESOLVED round 5:** `/G0` output - `mov sp,bp` is what MSC 7 emits under `/G0` for a function that *contains a call* (the 8086 has no `LEAVE`); a call-free `/G0` function gets the bare `5D`. `103a:0000` verifies byte-exactly with `/G0 /AM /Gs /Os`, including `33 C0 50` for a zero push. No longer a blocker | 0 blocking (was 144 / 24 280) |
| 6 | register-passed arguments (`mov ah,imm` then `call`) | `1cb7:0018`, `1cb9:0008`, `1cbf:0020` etc. No Microsoft C 7 construct emits `mov ah,imm` before a call — its `__fastcall` uses BX/CX/DX | 12 / 6 747 |
| 7 | absolute ESA addressing (`mov es,imm16` then `es:[disp16]`) | `2d64:0008`; MSC always addresses a far object through a base register, even with `MK_FP(const_seg, const_off)` | 6 / 17 323 |
| 8 | **`SI` as far-pointer base** (`push si` / `mov si,ax` / `es:[si+N]`) | `3a24:0006` (`clear32`), `38ad:000e` (`swap14`), `1df5:0008`, `2aa3:0048`, `37ef:000c`. MSC 7 puts the offset in **BX**. **Nuance (round 91):** `register` *does* steer a **loop counter** into SI - `4f89:0008` verifies with `register int i` - but it moves a pointer temporary to DI instead, so it does not rescue the far-pointer cases | 196 / 26 435 |
| 9 | **`mov ax,0` explicit** (`B8 00 00`) | `473f:0036` (`return 0x43A30000L;`): MSC emits `33 C0 / BA A3 43`, the binary has `B8 00 00 / BA A3 43`. **Split correction:** the `C7 06 <g> 00 00` zero *stores* are MSC 6.0 output (round 90) and no longer block; only the `mov ax,0` materialisation remains | 3 / 4 603 |

Softer variants that also block a byte-exact match but are harder to count:
**branch-block order** (which arm falls through), **operand evaluation order**, and
**register choice** (`SI` with `push`/`pop` where MSC uses `BX` with neither).

**What this means:** the practical ceiling is the `blocked by nothing` row of
`docs/GAP.md` (1 232 units / 77 022 B after the round-91 corrections). The
earlier "complete as far as this toolchain allows" conclusion was wrong twice:
`/G0` explained the `5D` epilogue and LINK `/F` explained the `90 0E E8` calls,
so two of the nine rows were not compiler traits at all.

## LINK /FARCALLTRANSLATION - why the image has `90 0E E8` (round 91)
The image contains 3 564 `0E E8` and 3 507 of them are preceded by `90`. That is
not a compiler idiom: Microsoft LINK's `/FARCALLTRANSLATION` option (`/F`,
normally with `/PACKC`) rewrites a direct far call into `NOP; PUSH CS; CALL NEAR`
when the callee ends up in the caller's physical segment
(MSKB S9BJ7 / "The /FARCALL Option"). Proof on this toolchain: two objects that
call each other across modules, linked with `LINK 5.10 /F /PACKC`, produce
`90 0E E8 F3 FF` where the identical `/NOF` link keeps `9A 00 00 00 00`
(`build/CLKABF.EXE` vs `CLKABN.EXE`, round 91).

**Second form - folded to 4 bytes (round 6).** When the linker knows the callee
is in the same segment it can also drop the NOP, leaving `0E E8 rel16` (4 bytes)
where the object still has `9A seg off` (5 bytes), so the whole tail shifts one
byte left. 36 unmatched units contain such a call. `tools/match.py` detects the
shift (`shrink_sites` / `_walk`) and anchors the rest of the window on it; the
first row verified that way is `13c6:0000` (39 B).

The compiler side is ordinary: a far callee that is `extern` compiles to `9A`
plus a 4-byte fixup, exactly what our calibration objects contain. So units whose
only "trait" was the translated call are reachable, and `tools/match.py`
recognises the rewrite:

* the object byte must be `9A` and all four operand bytes must be a fixup;
* the image bytes at that offset must be exactly `90 0E E8`;
* then all five bytes count as masked (the `rel16` is link-layout dependent).

The selftest asserts the positive case, a wrong opcode, and a partial fixup. The
8-bit displacement is what the linker computed for the actual game layout, so it
is masked like every other relocated operand -- the encoding, not the distance,
is what the source determines.

## Hand-ASM evidence - `add bx,bx` (round 34, **corrected in round 64**)
The binary contains 74 occurrences of `03 DB` (`add bx,bx`, index*2) against
only 18 of `D1 E3` (`shl bx,1`). MSC 7.0 was tested with
`return g_142a[i]` under /Os, /Ox, /Ot, /Od and /O2: **every** combination emits
`D1 E3`.

**Round 64 correction:** this is not hand-written assembly. In `4e11:007e`
(`return 2*(5*(abs(a)+1) + abs(b)) + c;`) every instruction matches MSC 7 under
`/Ot /Oi` **except** the final doubling, where the original has `03 C0`
(`add ax,ax`) and MSC 7 emits `D1 E0` (`shl ax,1`). So the pattern is a
**strength-reduction choice of this compiler** ("double with add"), not evidence of
an assembler source. Units containing a doubled index remain unreachable from
MSC 7 — but by exactly two bytes and for a now-understood reason.
## Round 55 - obtaining a DOS-hosted MSC 5.1 (and why it still is not usable)
- Source that works: the **decompme compiler archive** on archive.org
  (`compiler-microsoft-microsoft-c-5.1-dos`) ships `msc-5.1.tar.gz` with
  `BIN/C1.EXE`, `C2.EXE`, `C3.EXE`, `CL.EXE` and libs - and unlike the
  Microsoft C 6.00ax set, `CL.EXE` is **not** a Windows PE binary.
- Trap: `CL.EXE` is **EXEPACK-packed**. Under DOSBox-x it fails with
  `Packed file is corrupt` on most invocations, and the failure mode is
  deceptive: the redirected log file is not created at all, so it looks like the
  shell never ran the command. `Z:\LOADFIX` does not help.
  Diagnosis is only possible by running dosbox-x with captured stderr and reading
  the `LOG: INT 21h WRITE warning` line.
- Consequence: MSC 5.1 remains **untested for codegen**. Either unpack CL.EXE or
  drive `C1 -> C2 -> C3` directly.
- **Split pointer loading** is a candidate fingerprint: some units load a far
  pointer parameter as `8B 5E 06` (offset) + `8E 46 08` (segment) instead of
  `C4 5E 06` (les). Seen in `1df5:0008` and `2aa3:0048`; MSC 7 emits `les`
  for parameter loads in every variant tried so far.
## Phase-0 evidence round 48 — epilogue styles (corrected)
Counted in the load image (byte patterns, so read as a strong pointer, not proof):

| Epilogue | Count | Who emits it |
|---|---|---|
| `C9` + ret (leave) | **1 754** | MSC 7 with `/G1`+ |
| `5D` + ret (pop bp, SP unchanged) | **230** | MSC 5.1/6.0/7 with **`/G0`** (8086: no `LEAVE`) |
| `8B E5 5D` + ret (mov sp,bp; pop bp) | **156** | not observed from any tested compiler |

**Round 90 correction:** the first version of this table concluded "a second
compiler generation" from the `5D` rows. `1000:1364` disproves that: the same
source and the same compiler are byte-exact under `/G0`, so `5D` is a CPU-flag
fingerprint. Only the `8B E5 5D` rows still need an explanation — the `8B E5` is
redundant there (SP is already BP at the teardown), so it is an unconditional
SP restore, not a compiler needing one.

Consequence for matching: for units with a `5D` epilogue, use
`/G0 /AM /Gs /Os`; for `8B E5 5D` units the body can still be recorded as
evidence while the 2-byte teardown stays open (§ GAP).

Consequence for matching: for units with a `5D` epilogue, a body-exact C match is
still worth recording — the remaining diff is evidence about the toolchain, not a
missing source construct.

## Phase-0 finding round 25/26 — compiler generation: MSC 6.0 **NOT ACTUALLY TESTED**
Byte statistics of the original binary (load image, 294 603 code bytes):

| Pattern | Original | MSC 7.0 | Assessment |
|---|---|---|---|
| `03 DB` (add bx,bx) | **74x** | only `D1 E3` (shl) at every level tested | original uses ADD |
| `C7 06 .. 00 00` (zero immediate) | **130x** | /O2 yes, but with a frame | original: without frame |
| `33 C0 A3` (zero fold) | 32x | standard (every optimization level) | original rarely uses it |
| `55 8B EC` (frame) | 1184x | fits /Os | — |

**CORRECTION (round 46): the round-26 "MSC 6.0 disproved" result is void.**
Two independent defects invalidated it:

1. The MSC 6.00ax set fetched from archive.org ships a **Windows PE driver**:
   `MSC6I\BIN\CL.EXE` starts with an MZ header carrying the
   "This program cannot be run in DOS mode" stub, so DOSBox refuses to run it.
   Round 47 confirmed this is not a missing-DPMI problem: loading HDPMI32 first
   (the driver is described as "DOS-extended") produces the identical message.
   Only `C1`, `C1L`, `C2`, `LIB` and `QCC` in that set are real-mode DOS binaries;
   `C2L`, `C3L` and `CL` are PE. A DOS-hosted MSC 6 driver is therefore still
   missing, and the compiler passes would have to be driven manually
   (`C1` -> `C2` -> assembler) with an assembler this set does not provide.
2. `build.py` did not delete the previous OBJ before compiling, so the failing
   MSC 6 runs left the **MSC 7 objects** in `build/` and the comparison silently
   measured MSC 7 against itself. Fixed in round 45 (stale-object guard).

Consequence: **no claim about MSC 6 codegen is supported by evidence.** The
"hand-written assembly" reading of the `03 DB` / `C7 06` patterns rests on MSC 7
alone; MSC 6 remains an open question until a DOS-hosted driver is found.

**Consequence:** The remaining deviations (`C7 06` zero stores without frame,
`add bx,bx`, DX temps, jump merge) cannot be produced with either compiler
generation or any tested flag combination. This supports the
**hand/inline ASM hypothesis** for these modules (slot subsystem, clamp family,
init family, CONV). Before a `__asm` rebuild, the caller context remains
the only cross-check.

## Round 90 — MSC 6.0 **is** runnable (the round-46 blocker was the wrong disk)
`msc6\disk8\CL.EX$` decompresses with `DECOMP.EXE` to a real-mode `CL.EXE`
(81 184 B, no PE stub). Together with `C1.EXE`/`C2.EXE` (disk1/disk2) and
`C3.EXE` (disk7) it compiles under DOSBox-X without a DPMI host:

```
toolchain/msc6c/BIN/{CL,C1,C2,C3}.EXE   (CL from disk8, C3 from disk7)
python build.py src/calib/x.c --flags "/G1 /AM /Gs /Os" --msc-dir MSC6C --no-dpmi
```

DOSBox 0.74 works as well and is the fallback for real-mode binaries. Measured
codegen (same probe as MSC 7): `55 8B EC` frames, `C9` LEAVE under `/G1`,
`5D` under `/G0`, and three differences:

| Construct | MSC 6.0 | MSC 7.0 |
|---|---|---|
| far call to a same-segment callee | `0E E8` (`push cs; call`) | `9A` |
| zeroing a 16-bit register | `2B C0` (`sub ax,ax`) | `33 C0` (`xor ax,ax`) |
| keyword set | `far`/`pascal` only (`__pascal` = C2054 syntax error) | `__far`/`__pascal` |

Practical yield so far: none of the PENDING rows is fixed by it, and the units
whose only blocking trait is `0E E8` are startup-area fragments. It stays
available because `0E E8` is otherwise unreachable from C.

## Ledger (`docs/MATCHING.md`)
One line per address, duplicates forbidden, size ≠ 0:
`| va (seg:off) | name | size | status | note |` with status ∈ `MATCH | RELOCS | PENDING`.
Note format for verified rows (read by `tools/verify.py`):
`src=<source file>; flags="<cflags>"; <free text>` — verify rebuilds the combination
once and then compares every associated row (no trust in
existing OBJs). PENDING rows carry no `src=` and are not built.

## Build — verified recipe (2026-11-23)
`build.py` wraps: **dosbox-x** (v2026.08.31, VS/SDL1 64-bit) with `-nopromptfolder`
+ **HDPMI32** (HX-DOS runtime 2.17) as DPMI server TSR **before** every CL call
+ `cycles=max` + SDL dummy driver + APPDATA redirect to `dosboxx_home\`.

Why not DOSBox 0.74: MSC7's CL is a DOSX32 protected-mode program;
0.74 gives `run-time error R6901` (no DPMI). dosbox-x's built-in DPMI
crashes with MSC7 (GitHub issue #3844) — **HDPMI is the verified solution**.
Proof: `python build.py src/calib/triv1.c --flags "/G1 /AL"` →
480-byte OMF object (THEADR record with source file).

Decoration history: the disk files are KWAJ-compressed; `DECOMP.EXE`
(profiler disk) decompressed under DOSBox 0.74 (224/224, ~0.14 s/file).

## Open (phase 0 complete — remaining items)
1. Clarify overlay contents (≈141 KB) via the loader routines
2. LINK.EXE (DOSX16) hangs under dosbox-x in all DPMI variants (HDPMI32,
   HDPMI16, internal) — for `gen_link_stubs.py`/`build_replacement` (phase 6)
   a native OMF linker is needed (candidate: jwlink/wlink) or a
   different emulator configuration

## Rules from practice (observe on every build)
- **Name source files 8.3-compliant**: MSC-CL (1992) does not open
  long file names and otherwise dies SILENTLY (cget.c vs. calib_get.c).
- OMF objects from MSC7 carry fixups as **compact 0x9C records** (after
  COMENT class 0xA2), not as classic FIXUPP 0xF4 — omfdump.py handles both.
- PUBDEF entries from MSC7 have a type-index byte (0x00) behind the offset.
- **GitHub push (sandbox):** git HTTPS fails on schannel (SEC_E_NO_CREDENTIALS),
  credential helpers and sh prompt scripts die on the msys signal pipe.
  One-shot push with token URL: `$tok = gh auth token; git -c credential.helper=
  push https://mogeldev:$tok@github.com/....git master` (reset the remote URL
  to neutral afterwards, never persist the token).

## Foreign code (phase 1, keep separate)
Mark MS-C-CRT (evidence: runtime banner in the binary) as a library and do **not** decompile it once the CRT region is mapped via calibration compilation.

## Phase-0 evidence (ScanIdioms run, 2026-11-23, 68 452 instructions)

**CPU base: 80186/80286 — no 386.** `PUSHA` 17, `POPA` 13, `ENTER` 600, `LEAVE` 1315,
`IMUL` (reg form) 100, `INSB/OUTSB` present; `0x66` prefix only 8× (noise/data),
`0x67` = 0. → calibration candidate **`/G1`** (80186); `/G2` only if a real
286 idiom shows up.

**Memory model: MEDIUM `/AM`** (corrected 2026-11-23 by calibration):
getter family 35ca:8090..9c reads globals near (`mov ax,[disp16]`, DGROUP-relative,
fixup-masked) and returns `retf` → **near data + far code = medium**.
The earlier large/huge assumption was wrong; DGROUP is presumably `0x58FC` + 64 KiB
(up to paragraph `0x68FC`), the rest up to `0x71E7` are FAR data segments.
Image layout (paragraphs): code `0–0x52B1`, stack `0x52B1–0x58FC` (`SS:SP=52B1:1000`),
DGROUP data `0x58FC–0x68FC`, FAR data `0x68FC–0x71E7`.

**crt0 = Microsoft-C-16-bit family (confirmed).** Entry `0x1871:0BE5`:
`PUSH DS/ES; MOV AX,CS; MOV DS,AX; MOV [0x5],ES; ADD AX,0x10; MOV [0x9],AX`
(saves the PSP segment and `PSP+0x10` in DGROUP), `MOV AH,30; INT 21h` (DOS ≥ 3),
`MOV ES,ES:[0x2C]` (PSP environment segment) — classic MSC-8 startup sequence.
Exact version: calibration compile first.

**Overlay (≈141 KB from offset 339 735):** dense binary payload — 74 % nonzero,
all 4-K blocks occupied, no archive/MZ signature, no ASCII strings, no
self-path reference in the binary. Assumption: data read at runtime;
clarify via the loader routines, `extract_*` tool if needed.

**Build stamp in the binary:** `DDS98 date=%s, time=%s` (linear `0x59038`).

## Comment hazard in calibration sources

MSC 7 aborts **silently** (no object, no `CL.TXT`) if a comment ends early. Do not
write a slash-prefixed flag immediately before an asterisk in a comment:
`**/G0**` contains `*/`, so the comment closes there and the rest is parsed as C.
Write flags unadorned (`G0`) or outside emphasis. This looks identical to the
known MSC 7 crash class, so check the comment first when a new source fails with
"no OBJ produced" and no log.

## The `or reg,ax` peephole

When a call result is compared, the original compiler writes
`8B F0 0B F0` (`mov si,ax; or si,ax`): it ORs the register with **AX** even
though the value was just moved out of AX. MSC 7 emits `or si,si` instead. The
two sequences are semantically identical and differ in one byte, so a unit that
is otherwise perfect and shows `0B F0` / `0B C7` / `0B C6` is blocked by this
peephole and nothing else. It is the most frequent remaining one- or two-byte
blocker in the 30-40 byte band.

## Register parameters are assigned in reverse by the original compiler

For a function with two `register` parameters, MSC 7 keeps the **first** declared
one in SI and the **second** in DI. The original does the opposite: the first
declared parameter lives in DI and the second in SI (verified on `3ae7:0000`
against a direct compile: `(register int a, register int b, ...)` gives
`8B 76 0C` / `8B 7E 0A` from MSC 7, while the original has the same values in the
other registers). Units blocked only by this are `20f9:000c`, `218f:0004`,
`2191:0008` and `3ae7:0000`; the source shapes are known and recorded, so they
need no further source searching - only the older compiler reproduces them.

## Nop padding after a short jump

The original compiler pads a short jump with a `90` before the next block:

    B8 01 00 EB 03 90 33 C0        (original)
    B8 01 00 EB 02 33 C0           (MSC 7)

The jump length already covers the `90`, so the padding is dead code - but it
shifts every *following* branch distance by one byte, which breaks an otherwise
perfect match (`4998:000c` matched 111 of 112 bytes for exactly this reason, and
`3b88:000e` misses by the same single byte at its `jz`). The padding appears with
several offsets (`EB 02 90`, `EB 03 90`, `EB 23 90`), so `tools/classify.py` only
recognises the narrow forms; treat "one byte off, at a branch distance" as this
class first.
