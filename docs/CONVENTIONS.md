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

## Codegen traits of the original compiler (consolidated, round 76)

These are the **properties of the original code generator that Microsoft C 7 cannot
reproduce**. Each was established by isolating it in a function whose body otherwise
matches byte-for-byte, so each is a compiler property rather than a source mistake.
Every one was also tested against the flag matrix (`/Os`, `/Ot`, `/Od`, `/Ox`,
`/Oa`, `/Oi`, combinations) without success. Unit/byte counts come from
`tools/gap.py` and `docs/GAP.md`.

| # | Trait | Evidence | Units / bytes |
|---|---|---|---|
| 1 | doubling by `add r,r` instead of `shl r,1` | `4e11:007e` matches except the final `03 C0` (`add ax,ax`); MSC emits `D1 E0`. Explains the 74×`03 DB` vs 18×`D1 E3` census that round 34 misread as hand-written assembly | 204 / 66 762 |
| 2 | far calls to same-segment functions as `push cs; call rel16` | MSC emits `9A` for a far callee (verified with a same-file far function) and a bare `E8` for a near one; `0E E8` is unreachable | 1232 / 180 177 |
| 3 | far-pointer parameters loaded as two words (`8B 5E 06` + `8E 46 08`) instead of `les bx,[bp+6]` | `1df5:0008`, `2aa3:0048` — bodies otherwise identical | 367 / 84 175 |
| 4 | jump targets padded with `90` even in size-optimised builds | `47ef:0008` (`EB 03 90` vs `EB 02`) and `2aa3:0002` (two `90` bytes, all displacements +2); `/Os` never pads and `/Ot` restructures the returns instead | 1400 / 225 317 |
| 5 | epilogue `8B E5 5D` (`mov sp,bp; pop bp`) instead of `C9` | `11d8:000c` is 58/60 bytes identical; only the teardown differs. A bare `5D` epilogue is a milder variant of the same thing | 144 / 24 280 (+74 / 6 814) |
| 6 | register-passed arguments (`mov ah,imm` then `call`) | `1cb7:0018`, `1cb9:0008`, `1cbf:0020` etc. No Microsoft C 7 construct emits `mov ah,imm` before a call — its `__fastcall` uses BX/CX/DX | 12 / 6 747 |
| 7 | absolute ESA addressing (`mov es,imm16` then `es:[disp16]`) | `2d64:0008`; MSC always addresses a far object through a base register, even with `MK_FP(const_seg, const_off)` | 6 / 17 323 |
| 8 | **`SI` as far-pointer base** (`push si` / `mov si,ax` / `es:[si+N]`) | `3a24:0006` (`clear32`), `38ad:000e` (`swap14`), `1df5:0008`, `2aa3:0048`, `37ef:000c`. MSC 7 puts the offset in **BX**. **Nuance (round 91):** `register` *does* steer a **loop counter** into SI - `4f89:0008` verifies with `register int i` - but it moves a pointer temporary to DI instead, so it does not rescue the far-pointer cases | 196 / 26 435 |
| 9 | **explicit zero materialisation** (`B8 00 00`, `C7 06 <g> 00 00`) | `473f:0036` (`return 0x43A30000L;`): MSC emits `33 C0 / BA A3 43`, the binary has `B8 00 00 / BA A3 43`. Same style produces the `C7 06` zero stores of rounds 25/26. MSC always uses the shorter xor idiom | 106 / 32 862 |

Softer variants that also block a byte-exact match but are harder to count:
**branch-block order** (which arm falls through), **operand evaluation order**, and
**register choice** (`SI` with `push`/`pop` where MSC uses `BX` with neither).

**What this means:** the reconstruction is complete as far as this toolchain allows.
The practical ceiling is the `blocked by nothing` row of `docs/GAP.md`
(498 units / 27 144 B by byte-pattern count, i.e. an optimistic bound). Going
further needs the original compiler generation; Microsoft C 5.1 is EXEPACK-packed
in the only DOS-hosted copy available and the 6.00ax set is Windows-hosted, so
neither could be run here.

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
## Phase-0 evidence round 48 — two epilogue styles = two compiler generations
Counted in the load image (byte patterns, so read as a strong pointer, not proof):

| Epilogue | Count | Who emits it |
|---|---|---|
| `C9` + ret (leave) | **1 754** | MSC 7 at every level tested |
| `5D` + ret (pop bp, SP unchanged) | **230** | **never** by MSC 7 |
| `8B E5 5D` + ret (mov sp,bp; pop bp) | **156** | never observed from MSC 7 either |

MSC 7 emits `leave` for a frame it opened with `push bp; mov bp,sp`, including at
`/Ox /Oa /Os` and `/Oy /Os`. The 386 non-`leave` epilogues are therefore a
fingerprint of a **second compiler generation** (or of hand-written assembly) and
they explain why some units differ by exactly one byte in the epilogue while the
body matches perfectly (`1000:1364` abs is the clearest case: `99 / 33 C2 / 2B C2`
identical, only `5D` vs `C9` differs).

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
