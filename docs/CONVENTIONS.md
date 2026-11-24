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

## Switch layout: write `default:` first

For a `switch` whose cases return the callee's result, MSC 7 lays the default
block out **last** when `default:` is written last, and **directly after the
compare chain** when it is written first. The original `1f5f:0000` has the default
first, so the working source is

    switch (x) {
    default: return ((long)a << 16) | (unsigned)b;
    case 0: return h1(a, b, c);
    ...
    }

Writing `default:` at the end instead shifts the default block and every branch
distance in the function.

## Source-level rules that decide a match (round 50 summary)

Each of these was earned by a specific near-miss; applying them first saves a
compile cycle. Ordered by how often they have paid off:

| rule | example | found |
|---|---|---|
| a `register` parameter/ local stages through SI (or DI) instead of reloading from the frame | `8B 76 06` + repeated `56` instead of `FF 76 06` | r12 |
| a value moved into **AX right before** a far call is an *argument*: the callee is `__fastcall` | `B8 23 00` + call, `8B C6` + call | r20, r37, r49 |
| declare the callee `__far` when the image shows `90 0E E8`; `__near` gives a 3-byte `E8` and shifts everything | | r46 |
| accumulation and divide-plus-offset must be **separate statements**, not one expression | `t += g(...)` vs `t = a + b + c` | r46 |
| write branch conditions **negated** when the original lays the then-block out first | `if (!h(...))` emits `jnz` over the block | r45 |
| write `default:` **first** in a switch to get the original's block order | | r47 |
| an unprototyped callee makes MSC clean arguments with `mov sp,bp` instead of `add sp,N` | `8B E5` | r28 |
| a `long` local that is written but never read reserves its bytes and nothing else | `83 EC 04` | r29 |
| do not give a call result its own variable when it is only tested once (it adds a DI push) | | r45 |
| Pascal arguments push **left to right**, so the first argument sits at the highest offset | four-word far function: `a`=bp+0C ... `d`=bp+06 | r25 |
| a byte global read uses the moffs form `A0 <disp>`; caching it in a local is sometimes required | | r18, r48 |

What no source formulation reaches (older-compiler artefacts, catalogued in
`docs/BLOCKED.md`): `ENTER` frames, `2B C0` zeroing, `add reg,reg` doubling,
jump-merge booleans with `xor ax,ax`, the `or reg,ax` peephole, nop-padded jumps,
frames on functions with no locals, and reversed register-parameter assignment.

## cdecl cleanup: `add sp,N` versus `mov sp,bp`

Correction to an earlier note: MSC 7 does **not** always use `mov sp,bp` for cdecl
cleanup. A minimal check (`cd3(1,2,3)` with a prototype, no locals) produces the
expected `83 C4 06`, exactly like the original. MSC switches to `8B E5` in other
contexts - e.g. when the call sits inside a block that continues afterwards
(`2d9b:0002`, `1dfc:0116`) - while the original keeps `83 C4 <n>` there. So the
cleanup form is context dependent, and a cdecl call site inside a longer function
is a likely mismatch even when everything else lines up.

## cdecl argument order is right to left

For a `__cdecl` callee MSC pushes the **last** parameter first. When the original
pushes a far-pointer argument last (`... 1E 68 <disp> 9A`), the pointer is the
**first** parameter in the source, not the last:

    cd6(g_1bf2, g_1be8, g_1bea, g_1bec, g_1bee)   /* pushes g1bee ... g1be8, then p */

The `83 C4 0C` afterwards confirms six words of arguments, which is only reachable
with the pointer counted once.

## There is a third codegen profile: unoptimised with `55 8B EC` frames

`/Od` reproduces the original's *instruction selection* far better than `/Os` in
several units: stores become `C7 06 <g> <imm>`, comparisons become `3D <imm> 74`,
and cdecl cleanup is `83 C4 <n>` - all matching the original, where `/Os` uses AX
staging and `mov sp,bp`. The catch is the frame: `/Od` emits `C8 <n> 00 00`
(ENTER) unless `G0`, in which case it emits

    55 8B EC 81 EC <n> 00 56 57 ...

i.e. a classic frame that reserves all locals up front and always saves SI and
DI. The original usually has the bare `55 8B EC` form, so `/G0 /Od` is only a
match for functions whose prologue is exactly that longer form - a scan of the
whole pool finds **one** such unit (`1971:0006`), and it is a mid-routine fragment
that cannot be a ledger row.

So the three available profiles are:
- `/Os` (used for every verified row) - matches instruction selection for
  optimized code but stages through AX/SI differently and prefers `mov sp,bp`;
- `/Od` - matches unoptimised selection but frames with ENTER;
- `/G0 /Od` - correct frame shape but always reserves locals and saves SI/DI.

The original sits between them: unoptimised selection with a bare classic frame.

## Long shifts are inlined in the original, not called

For a 32-bit `v << 8` the original emits the shift inline:

    8A E0   mov ah,al        ; low word << 8
    2A C0   sub al,al
    ...
    8A F2   mov dh,dl        ; carry into the high word
    8A D4   mov dl,ah

MSC 7 emits a call to the shift helper instead (`B1 08` + `9A ...`), so every
expression built from `(long)x << 8` or `(long)x << 16` diverges at the first
shift. `20b4:0160` (_read24) is the canonical case: the original assembles a
24-bit value with inline byte shifts and no call at all, and no formulation of the
same value in MSC 7 avoids the helper. Fourteen unmatched units contain the idiom,
including six functions over 130 bytes, so this is one of the larger remaining
classes (now `inline long shift` in tools/classify.py).

## `G0` frames appear in the pool too

Not every function uses the `C9`-style frame. `13db:000c` ends `8B E5 5D C2 06 00`
- `mov sp,bp` / `pop bp` / `ret n` - which is exactly what MSC 7 emits under `G0`.
That unit also cleans a cdecl call with `8B E5` instead of `add sp,4`, another `G0`
trait. When a unit's epilogue has `8B E5 5D` (or `5D` alone), compile that source
with `G0` and expect the cdecl cleanup to match as well.

## `G0` cdecl function with locals: the frame is allocated in two steps

Under `G0`, a function that both takes parameters and has locals gets a split
prologue from MSC 7:

    B8 04 00   mov ax,4
    2B E0      sub sp,ax
    50         push ax          ; together: 6 bytes reserved for 3 locals

where the original emits a single `83 EC 06`. Every other byte of `1070:0008`
(67 B) and `103b:000c` (63 B) then matches, so this is the only thing keeping
those two units out of the ledger: they are `G0` cdecl functions with a stack
local and a `&parameter` argument, and MSC always splits the reservation there.
Declaring the function `__pascal`, dropping the `&parameter` and casting the
pointer all leave the split form in place.

## `char` arguments are pushed unpromoted in the original

The original pushes a byte argument directly out of the register it loaded into:

    8A 46 08   mov al,[bp+8]
    50         push ax            ; AH untouched
    A0 97 83   mov al,[0x8397]
    50         push ax

MSC 7 always promotes first (`98` = `cbw`, or `2A E4` = zero the high half), so a
call site like this differs by one or two bytes whatever the source casts look
like - an unprototyped callee was tried and MSC still emits `98`. The same applies
to integer promotion of `char` parameters in general, which suggests the original
compiler is pre-ANSI in this respect. Thirteen unmatched units (885 bytes) carry
the pattern and are now the `byte argument without promotion` class.

## Values live across a call: MSC spills, the original keeps them in a register

`437e:0032` keeps a scaled table pointer in SI across an intervening call
(`C1 E6 02` then `[si+0x866E]` after `h2()`), while MSC 7 allocates a frame slot
and reloads it (`89 5E FE` / `8B 5E FE`) - which also forces an `ENTER` frame that
the original does not have. Declaring the pointer or the index `register` does not
help: MSC still spills anything that must survive a call, because its register
allocator only keeps SI/DI for values with no call in between.

Practical consequence: a function whose source needs a *pointer or index kept
across a call* cannot be reproduced with MSC 7, even when every instruction is
understood. `437e:0032` is fully decoded (a bitfield writer: `(old & 0x0700) |
(value << 11)`, then bit 15 via a byte OR) and still out of reach for this reason.

## Struct members are packed in the original: use `/Zp1`

`4e72:000a` reads a word at `es:[bx+7]` from a far struct, i.e. the member follows
seven `char`s with **no alignment padding**. MSC 7's default puts that member at
+8 (`/Zp2`-style alignment), and adding `/Zp1` to the flags moves it to +7 and
removes the whole difference. So when a unit's field offsets land on odd addresses,
compile it with `/Zp1` before assuming the structure is wrong.

(The same unit still differs afterwards in two swapped instructions - the original
emits `8B D8` / `8E C2` (`bx = ax`, then `es = dx`) where MSC emits the segment load
first - so packing alone is not always enough.)

## `C2`/`CA` decide the frame: near versus far

`4db8:0006` ends `C9 C2 06 00` - `leave`, then `ret 6`, i.e. a **near**-Pascal
function. Reading that byte as `CA` (far `ret imm16`) shifts every parameter offset
by two (near return address 2 bytes, far 4), which is what made the first
transcription differ at three push offsets while looking otherwise perfect. When the
parameter offsets in a unit are all two bytes lower than expected, check the return
opcode before touching the parameter list.

## cdecl: reverse the source arguments to match the push order

`1dfc:00fa` shows `push a` then `push b` for a two-argument cdecl call. Because
cdecl pushes right to left, that is `cd(b, a)` in the source - the argument order is
the *reverse* of the order the pushes appear. The same applies to four arguments
(`cd4(b, a, b, a)` produces `push a, b, a, b`), which is how the round-13
`1dfc:0116` puzzle resolves: its `83 C4 08` cleanup and register staging both fall
into place once the arguments are reversed and the second parameter is `register`.

## The original can use BX as a register variable

`11a2:000c` opens `55 8B EC 53` - it **pushes BX** before using it as the working
pointer, i.e. BX is a callee-saved register variable. MSC 7 never does this: its
register allocator only uses SI and DI and treats BX as scratch, so the surviving
copy has to be spilled to a frame slot (adding an `ENTER` frame). Eight unmatched
units (518 bytes) begin with `53` in the prologue and are unreachable for this
reason; they are now the `register variable in BX` class.

Everything else in `11a2:000c` was solved on the way: the pointer is a *near*
pointer and the callee is `__far __fastcall`, which reproduces the whole body
(`8B 07` / `8B 57 02` / `8B 4E 08` / call / `89 07` / `89 57 02`) - only the
`push bx` / `pop bx` pair around it is out of reach.

## Small constant arguments: `68 06 00` versus `6A 06`

MSC 7 pushes a small literal argument with the 80186 short form (`6A 06`), even
under `/G1`. The original sometimes uses the long form (`68 06 00`) for the same
value - `41e7:000a` passes `h(0x4827, 6, a)` and differs in exactly that one byte.
Four formulations were tried (plain, `(char)`, `6L`, `0x0006`) and all give `6A`; only
routing the value through a variable changes it, and then to `B8 06 00` / `50`
(`mov ax,6` / `push ax`), which is not the original either. Note the original does use
`6A` elsewhere in the image, so this is a per-site choice, not a compiler-wide habit.

## Register parameters: MSC assigns by first use, the original by declaration

`3ede:00a0` pins this down. Its two parameters end up as `a -> SI`, `b -> DI` in the
original (declaration order), while MSC 7 - given `register int a, register int b` -
puts **`b` in SI** because `b` is the first one the body uses (`h2(b, g)`) and `a`
only appears later. The two prologue loads (`8B 7E 08` / `8B 76 06` versus
`8B 76 08` / `8B 7E 06`) are then swapped, and that is the *only* difference in the
whole 64-byte function.

This sharpens the round-36 note ("the original reverses the roles"): the original's
allocation follows the declaration, MSC's follows first use. When the two happen to
agree the unit matches; when the body's first use is not the first declared parameter,
every register reference in the unit is swapped and no source reordering fixes it
without moving stack offsets.

### The two orders are independent

At `3ede:00a0` the original's prologue is `57 56 8B 7E 08 8B 76 06`: it pushes DI
before SI and loads the *second* parameter (into DI) first, even though the parameter
declared first ends up in SI. So the original separates two decisions - **which
register a parameter gets** follows the declaration (a -> SI, b -> DI), while **the
order the prologue loads them** follows first use. MSC 7 couples both to first use,
which is why an exchange in the prologue is the signature of this class.

## Branch displacements skip the padding - they are never "one byte short"

`13d5:000c` was recorded in rounds 98-99 as having a link-mangled branch displacement
(`75 1B` where `1A` looked self-consistent). That was an arithmetic error on my part,
and `tools/dis.py` settles it: the `jnz` at 0x0D targets **0x2A**, which is the start of
the following `cmp` - it simply skips the `90` padding byte at 0x29. The same unit's
`EB E0` targets 0x25 (`8B E5`), the shared epilogue, not the function's first
instruction. Both displacements are exactly right.

So there is no link-time displacement effect to account for: a branch whose target is
one byte past an apparent block boundary is the **nop-padding class**, nothing else.
Use `tools/dis.py <va> [len]` before drawing any conclusion about a displacement - two
of my earlier hypotheses were wrong in exactly this way.

## `/G0` and `/G1` couple the frame to the instruction set - use `/G0` for units with locals

Measured this round (MSC 7.0 and MSC 6.00A agree byte for byte):

    int far pascal A(int a) { int x; x = h1(a); return h2(x); }

    /G0 /AM /Gs /Os   55 8B EC 83 EC 02 FF 76 06 9A ... 8B E5 5D CA 02 00
    /G1 /AM /Gs /Os   C8 02 00 00 FF 76 06 9A ... C9 CA 02 00

So `/G0` (8086 target) uses the **classic frame** because `ENTER`/`LEAVE` do not
exist on the 8086, while `/G1` uses `ENTER`. This corrects the round-55 conclusion
"unoptimised selection + bare classic frame is unreachable with MSC 7": the frame is
reachable, via `/G0`.

The catch is that the original combines the classic frame with 80186 encodings - it
pushes small literals with `6A` (`push imm8`), which `/G0` cannot encode: it emits
`B8 01 00` / `50` instead. So:

* a unit **with locals and without `6A`** can be matched under `/G0` - the frame now
  agrees, and this is the first setting that does;
* a unit **with `6A`** cannot be matched by any MSC 6/7 flag combination: `/G0` gets
  the frame right but the push wrong, `/G1` the push right but the frame wrong.

Practical rule: compile units with locals under `/G0`, and check the image for `6A`
before expecting a match.

Scope note (round 101): of the unmatched units, only **32** have a classic frame with
locals, and **10** of those are complete, call-bearing and free of `6A`. `/G0` therefore
unlocks a few dozen units, not a few hundred - most `ENTER` usage in the image is the
original's own choice, not a flag artefact.

### Immediate pushes: the original follows the 80186 rule, MSC does not

`41e7:000a` settles it. The original pushes `0x4827` with `68 27 48` and `6` with
`68 06 00`; MSC 7 under `/G1` pushes both with `6A` (short form) and under `/G0` with
`B8 xx` / `50` (`mov` + `push`). So the original picks `6A` for small values and `68`
for large ones - the 80186 rule - and no MSC 6/7 flag reproduces that selection.

### Register-parameter assignment: four data points, still no rule
(rounds 93, 112, 113, 116)

| unit | register params (declaration order) | MSC put in SI | original put in SI |
|---|---|---|---|
| `3ede:00a0` | `a` (08), `b` (06), body uses `b` first | `b` (06) | `a` (08) |
| `3874:000a` | `b` (08), `c` (06), body uses `c` first | `b` (08) | `c` (06) |
| `4e58:0004` | `e` (06), `g` (04) | `g` (04) | `e` (06) |
| `218f:0004` | `a` (08), `b` (06) | `a` (08) | `b` (06) |

No ordering rule explains all four: declaration order fails on `3ede` and `4e58`,
first use fails on `3874`, and "lowest offset" fails on `3874` and `218f`. MSC's
allocator is doing something demand-driven that this project has not reverse-engineered.
Treat any unit whose prologue loads **two** register parameters as test-me-not-predict,
and bracket it with `register` on one parameter at a time.

## MSC hoists a later call's constant pushes; the original keeps them in order

`3e34:000a` is `h1(8); s = h2(0x0F, 0x4000); h3(1, 0, a, b, s); h4(s); g = 0;`.
The original emits the calls strictly in statement order. MSC 7 pushes `h3`'s two
constant arguments *before* calling `h2`:

    original   B8 08 00 call  6A 0F 68 00 40 call  8B F0 50 FF 76 08 FF 76 06 6A 00 6A 01 call
    MSC 7      B8 08 00 call  6A 01 6A 00 FF 76 08 FF 76 06 6A 0F 68 00 40 call  8B F0 56 call

because the constants do not depend on `h2`'s result. Any unit where one call's
arguments precede a preceding call's invocation is this effect, not a source-order
mistake - and no flag turns it off.

Also from the same unit: the first call is `__fastcall` - the value arrives in AX
(`B8 08 00`) with no push at all, which is the tell recorded in round 45.

## No frame means no locals - rewrite the expression, do not introduce a variable

Two rounds produced the same mistake (round 122's `438c:0004`, round 123's
`3e48:000a`): a unit whose prologue is only `55 8B EC 56` was first transcribed with a
temporary variable for a call result or a computed value, which makes MSC allocate a
frame and adds `83 EC nn`. The original has **no locals at all** - the value is consumed
inside the expression that produces it:

    /* wrong: forces a frame */
    r = h3(x); if (r == 9) return x - g;
    /* right: matches */
    if (h3(x) == 9) return x - g;

So on any unit whose frame is just `55 8B EC` plus a register save, assume **zero**
locals and restructure until nothing needs storing. The same applies to a parameter that
is modified and used again (`a -= 0x119; ... while (a > 0) ...`), which the original
keeps in a scratch register rather than writing back to the frame slot.

## `/Ox` resolves register reuse and allocation - try it before declaring a unit blocked

Round 133 found that `/Ox` (rather than `/Os`) matches units that `/Os` misses on
register grounds, in two different ways:

- `50ff:000e` (138 B): under `/Os` MSC takes a fresh CX for the second pointer of a
  call's argument list; under `/Ox` it **reuses AX**, as the original does (the value is
  already pushed and `push ss` does not clobber AX);
- `218f:0004` / `2191:0008` (36 B each): under `/Os` MSC assigns the two register
  parameters to SI/DI in the opposite order to the original; under `/Ox` the allocation
  matches exactly.

So the "register assignment" wall recorded in rounds 93/112/113/116 is at least partly a
*flag* artefact, not a compiler-generation difference. Compile a unit whose only
difference is a register name under `/Ox` (`/G1` for the frame and 80186 encodings,
`/G0` when it has locals) before concluding anything about the allocator.

`/Ox` is not a blanket fix: on `322c:002c` it *reverses* the SI/DI assignment against
the original instead of aligning it, and on `13db:000c` it hoists a register save the
original does not have. Use it when the diff is "the same register under a different
name", and fall back to `/Os` when the original is the one doing *less* optimisation
(no value kept across statements, no register for a dead temporary).
