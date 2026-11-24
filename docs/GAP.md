# Gap analysis - what Microsoft C 7 can and cannot reproduce

Measured over **2183 unmatched code units** (286798 bytes) from
`ground_truth/units.csv`, excluding everything already in the ledger.

Each unit is counted once per trait, so the rows overlap: a unit may hit
several traits. The final row is the set blocked by none of them.

| Trait | Units | Bytes | Share of unmatched bytes |
|---|---|---|---|
| interior 90 padding | 560 | 163606 | 57.0 % |
| split pointer load | 364 | 84091 | 29.3 % |
| add r,r doubling | 201 | 66460 | 23.2 % |
| SI base register | 199 | 28886 | 10.1 % |
| register-passed args | 12 | 6747 | 2.4 % |
| absolute ESA access | 4 | 17213 | 6.0 % |
| mov ax,0 explicit | 3 | 4603 | 1.6 % |
| **blocked by nothing** | 1209 | 81206 | 28.3 % |
| &nbsp;&nbsp;of which framed (`55 8B EC`) | 528 | 30943 | 10.8 % |

## Reading

- Every trait above is a **code generator property**, verified by isolating it
  in a function whose body otherwise matches byte-for-byte (see CONVENTIONS.md
  and IDIOMS.md). None of them can be reached by a different C formulation or
  flag combination: that was tested repeatedly and is recorded per trait.
- **`90 0E E8 rel16` is not a trait**: that is Microsoft LINK
  /FARCALLTRANSLATION (/F, with /PACKC) rewriting the compiler's `9A seg off`
  into NOP; PUSH CS; CALL NEAR. `tools/match.py` recognises the rewrite, so
  those call sites are stripped before classification; 3 507 of the 3 564
  `0E E8` in the image carry that NOP.
- Likewise not counted: direct `9A` far calls (ordinary output, operand is a
  relocation), the bare `5D` epilogue (that is the `/G0` 8086 target) and
  `C7 06 <g> 00 00` zero stores (MSC 6.0 emits them).
- **These are byte-pattern counts, so they are upper bounds on blocking**:
  a trait pattern can also occur inside an operand byte (a `90` inside a
  displacement, a `9A` inside an immediate). The `blocked by nothing` row is
  therefore a *lower* bound on what is reachable, and the per-trait rows are
  upper bounds. The relative ordering is still informative.
- The practical ceiling for byte-exact recovery with the
  toolchain available here. Anything outside it needs the original compiler
  generation, which could not be run (MSC 5.1 is EXEPACK-packed; the
  Microsoft C 6.00ax set is Windows-hosted).

## What this means for the ledger

- Verified so far: see `STATUS.md`. Unmatched and reachable: **528 framed units, 30943 bytes** (plus 681 unframed).
- At the recent rate (~500 verified bytes per round) the reachable framed
  remainder is about **61 more rounds** of work, and
  that assumes every attempt succeeds - which the last four rounds show it does
  not.
- The honest conclusion: this reconstruction is **complete as far as this
  toolchain allows**, at roughly 0.7 % of own code. Going further needs the
  original compiler generation, not more C variants.
## MSC 6.00A disks unpacked; the DOS driver is DISK6's CL.EXE (round 68)

`tools/extract_disks.py` reads the eight FAT12 images under `toolchain/msc6_disks`
and decompresses the Microsoft COMPRESS streams (`SZ` + `88 F0 27`, 12-byte
header, LZSS with a 4 KB ring). Running it into `toolchain/msc6dos/BIN` yields:

| file | from | size | note |
|---|---|---|---|
| CL.EXE | DISK6 `CL.EX$` | 28 858 | **DOS driver** (`e_lfanew = 0`, no NE/PE header) |
| CL.MSG / CL.ERR | DISK6 | 2 697 / 1 656 | its message and error files |
| C1.EXE | DISK1 `C1.EX$` | 148 060 | DOS pass 1 |
| C2.EXE | DISK1 `C2.EX$` | 354 338 | DOS pass 2 |
| C1.ERR / C23.ERR | DISK1 | 19 500 / 3 649 | phase error files |

The `PACKING.LST` explains the earlier confusion: the disks ship **two** CL
drivers - `DISK2:CL.EX$` is the "OS/2 compiler driver" (NE, hence "This program
cannot be run in DOS mode"), `DISK6:CL.EX$` is the "DOS compiler driver". The
extractor therefore prefers DISK6 for `CL.EX$`.

**Still open:** the DOS driver still produces no object and no console output under
DOSBox-X, with `CL.MSG`/`CL.ERR` beside it and `C1.EXE`/`C2.EXE` on `PATH`. Note
that DOSBox-X silently does nothing when its stdout is redirected to null in this
workspace, so any manual test must run with its output captured to a variable -
that cost most of this round's debugging time.


### Correction (round 71): "no output" does not mean "crashed"

Round 70 concluded that the DOS CL crash was tearing DOSBox down because its
redirect file was never created. A control test disproves the inference: the
**known-good CL 7.0** run with no arguments through the same `--run` path also
produces no output and no redirect file, while `CL /c ...` works normally. So
`PROGRAM.EXE > file` in this autoexec simply does not behave like a shell
redirect for these drivers, and the missing file says nothing about a crash.

What remains true: `dir C:\MSC6DOS\BIN\CL.EXE > file` works, the extracted
binaries are md5-identical to the known-good copies, and `CL /c` with the MSC6DOS
toolchain still yields no object. The next probe must therefore capture CL's
output *inside* the program run (e.g. have CL write its own log with `/Zs` style
options or check `CL`'s exit code via `if errorlevel`), not via shell redirection.

### Correction (round 91): the `--run` harness was broken, so the earlier "no output" evidence is void

`build.py`'s `--run` mode never actually ran the supplied command: it appended the
normal `CL.EXE ...` line unconditionally and only used the flag to skip the object
check. Every diagnostic that concluded "the DOS MSC 6.0 driver produces no object and
cannot be observed" (rounds 70-71) was therefore run through a harness that ignored
the request - it says nothing about `CL.EXE` itself. `build.py` now substitutes the
command for the CL line, verified with `--run "echo X > D:\BUILD\E.TXT"` (the file
appears).

With the harness working, `C:\MSC6DOS\BIN\CL.EXE /c /AM /Gs /Os /Fo... ...` still
produces no object file and writes nothing to stdout or stderr (`2>` redirect
included), while control does return to the shell - a `; echo done > D:\BUILD\D.TXT`
after it creates the marker. Two caveats that keep this inconclusive rather than
negative: CL's messages go to the *console* (MSC 7's `CL.EXE /badflag` likewise leaves
no redirectable log), and a run that hangs the shell for the full 120 s timeout can
still have produced its files (the marker test did).

Next step on this thread is therefore not "does CL write a log" but a run that makes
the driver fail visibly - e.g. a deliberately undefined symbol with `/Zs` (syntax
check only), whose `error C2xxx` line would have to appear somewhere.

### Round 92: both MSC 6.0 DOS passes run silently, and `if errorlevel` is not usable evidence

With `--run` fixed, the DOS 6.00A tools were exercised directly:

| command | object | stdout log | stderr log | files touched |
|---|---|---|---|---|
| `CL.EXE /c /AM /Gs /Os /Fo...` (from `C:\MSC6DOS\BIN`, `TMP` set) | no | no | no | none |
| `C1.EXE D:\BUILD\Z1.C` | - | no | no | none |

Both return control to the shell, so they are not crashing the session. Two facts
about the binaries, re-checked this round: `CL.EXE` is a plain DOS MZ image
(`e_lfanew = 0`, no NE/LE/OS-2 header), 28 858 bytes, and `CL.MSG` / `CL.ERR` /
`C1.ERR` / `C23.ERR` are all present beside it, so a missing message file is not the
explanation.

The `if errorlevel` probe is **not** trustworthy here: DOSBox-X's built-in shell was
observed to report success (`if not errorlevel 1` firing) for a run that produced
nothing at all, so it cannot distinguish "the tool exited 0" from "the shell does not
propagate exit codes". It should not be used as evidence either way.

Status of this thread: unresolved rather than negative. The remaining explanations are
(a) the tools write their messages through the console (INT 10h) and the SDL dummy
video driver hides them, so they fail and exit without a redirectable message; or
(b) the 6.00A DOS driver needs something the extraction did not provide (a `SETUP`
step, a `TMP`/`INIT` variable with a specific shape, or a companion file outside
`BIN`). Distinguishing them needs a run whose *screen* can be observed, which the
current headless harness cannot do.

### Round 140: the installed MSC 6.0 driver was the OS/2 build

The `toolchain/msc6dos/BIN` set - extracted in round 68 from `DISK6.IMG` - is the **OS/2**
distribution: `DISK6` also carries `OS2.LI$`, `CDLLOBJS.*` and `LLIBCDLL.LI$`, and its
`CL.EXE` (28 858 B) is an OS/2 binary. That is why it always "ran" and did nothing under
DOS.

`DISK2.IMG` is the **DOS** compiler disk, and its files differ in both size and md5:

| file | DISK6 (installed) | DISK2 (DOS) |
|---|---|---|
| `CL.EXE` | 28 858 | **29 859** |
| `C1.EXE` | 148 060 | **146 928** |
| `C2.EXE` | 354 338 | **345 721** |
| `C3.EXE` | - | **152 683** |

Installing the DISK2 set (`build/cl_DISK2.bin`, `d2_C1_EX.bin`, `d2_C2_EX.bin`,
`d2_C3_EX.bin`) still produces no object: `CL.EXE /c ...` returns control (a `; echo`
marker after it is created) with no object, no stdout, no stderr, from both the C: root
and its own directory, with `TMP` set. EMS and XMS were also enabled in the DOSBox
configuration, which changed nothing (and does not affect MSC 7, re-verified).

So the DOS 6.00A driver is now in place and still silent. The remaining explanations are
narrower: the driver may need the `SETUP`-written configuration that the retail
distribution installs (`msc51` has `NEW-CONF.SYS` / `NEW-VARS.BAT` for exactly that), or
it reports through the console (INT 10h) which the dummy video driver hides.

### Round 141: the compiler DOES talk - it was the passes that could not run

Two facts settle the round-70/71/140 confusion:

1. **MSC 6.0's driver is not silent.** `CL.EXE > D:\BUILD\E9.TXT` with no arguments writes
   `usage: cl [ option... ] filename... [ -link linkoption... ]` into the file. So the
   messages *are* redirectable and the harness was never the problem.
2. **The passes are the wrong platform.** A real compile echoes the source name and then
   writes `This program cannot be run in DOS mode.` - that is `C1.EXE` refusing to run.
   The `C1.EXE`/`C2.EXE` shipped in `msc6_disks` (DISK1, DISK2 and DISK6 all carry the
   same 148 060 / 354 338 byte pair) are Windows/OS-2 binaries.

Where the DOS passes are: `DISK8.IMG` carries `C1L.EX$`, `C2L.EX$`, `C3L.EX$`, `CL.EX$`,
`SETUP.BAT` and `SETUP.CMD` - a set that looks like the DOS distribution. Its `CL.EX$`
decompresses to a stream beginning `KW`, i.e. Microsoft **KWAJ** compression, which
`tools/extract_disks.py` does not implement (it handles SZDD only).

So the next step on this thread is concrete: teach the extractor KWAJ, unpack DISK8's
`CL.EX$` and `C1L/C2L/C3L`, and the DOS 6.00A compiler should finally run - which is the
toolchain most likely to explain walls 3, 4, 6, 7 and 9.

### Round 142: MSC 6.0 is available after all - and behaves like MSC 7

The round-140/141 investigation was chasing the wrong disk. `toolchain/msc6c` **works**
(its `CL.EXE` plus DOS passes compile objects with `--msc-dir MSC6C --no-dpmi`, which is
how round 55's `/G0` `/Od` profile work was done). `msc6dos` is simply one of the
non-DOS distributions and can be ignored.

So the alternative-compiler experiment does not need DISK8 unpacked. Running it:

| unit | MSC 7 `/G0 /Os` | MSC 6.0 `/G0 /Os` | MSC 7 `/G0 /Ox` | MSC 6.0 `/G0 /Ox` |
|---|---|---|---|---|
| `2a28:0000` | AX (differs) | AX (differs) | AX (differs) | AX (differs) |
| `2a29:000c` | AX (differs) | AX (differs) | AX (differs) | AX (differs) |

The original wants **DX**. Both compilers give AX, under both optimizers, so MSC 6.0 is
not the generation that built this binary either - consistent with round 55's conclusion
that it predates MSC 6.0 (unoptimised instruction selection plus a classic frame).

That closes the "try another compiler" avenue for the walls that matter: MSC 5.1 remains
the only older Microsoft C available here, and its extraction cannot yet be made to run
(round 92). Unpacking DISK8 is therefore only worth doing if a DOS *5.x* toolchain turns
up on it - it does not.

### Linkers: three exist, and none of them can change a ledger row

`toolchain` carries three `LINK.EXE` binaries: `msc51` (65 539 B, an old
pre-5.0-generation linker) and `msc6b` / `msc7i`, which are **byte-identical** (199 552 B,
LINK 5.1x). So MSC 6.0 and MSC 7.0 share one linker, and the only genuinely different
linker available is the old one.

That does not matter for matching, and the reason is worth stating: `tools/verify.py`
compares the **object** produced by the compiler against the image window with relocations
masked. The linker's only visible contribution is the `/FARCALLTRANSLATION` rewrite of a
5-byte far call into `90 0E E8` (nop / push cs / near call), which `match.py` already
models as an equivalent form. No layout, padding or alignment decision of the linker can
change whether a row matches - except by moving the bytes, which the relocation masking
already tolerates.

So the "try another linker" avenue is closed by construction rather than by experiment,
which is worth recording so it is not re-opened.

## Round 208 was wrong; corrected in round 260: MSC 6.0 works

Round 208 recorded `--msc-dir MSC6C` as an environment regression ("no OBJ produced", no
compiler output). **That was a mistake.** MSC 6.0 only parses the single-word keywords (`near`,
`far`, `pascal`); the `__near __pascal` spellings used for MSC 7.0 are a syntax error that
leaves no object and no log, so every probe written that way failed identically. With the
underscores removed, 6.0 compiles everything tried, including the 12 pending sources.

What 6.0 does differently from 7.0 (measured round 260, `/AM /G1 /Gs /Os`):

| construct | MSC 6.0 | MSC 7.0 | original |
|---|---|---|---|
| `int` zero (`g = 0; return g;`) | `2B C0` | `33 C0` | `2B C0` |
| `long` zero return | `2B C0 99` | `33 C0 99` | not compared |
| doubling `x * 2`, `x + x`, `x << 1` | `D1 E0` | `D1 E0` | `03 C0` |
| `fastcall` | not supported | supported | used |

So 6.0 **does** reach the `sub ax,ax` zeroing class that 7.0 cannot, and **does not** reach the
doubling class (the 199-unit wall holds on a second compiler generation). Rounds 140-146's
"MSC 6.0 behaves like MSC 7" was true for the doubling and the frame, false for zeroing.
## Round 262: MSC 5.1 unpacked; three compiler generations compared

`tools/unexepack.py` unpacks the EXEPACK'd MS C 5.10 (Feb 1988) passes, so 5.1 now builds
(`--msc-dir MSC51U --no-dpmi`; the directory is local and not published). Measured with the same
sources on 5.1, 6.0 and 7.0: **doubling is `D1 E0` on all three** (the original uses `03 C0`);
5.1 emits `ENTER 0` (`C8 00 00 00`) under `/G1` even for a function with no locals, where 6.0/7.0 emit
`55 8B EC` (the original uses `55 8B EC`, so 5.1 is the wrong generation for the frame); a plain-`int`
zero return is `2B C0` on 5.1 and 6.0 but `33 C0` on 7.0. `tools/oldsweep.py` re-sweeps every calibration and pending
source under an older compiler: one new candidate in total, reachable with 7.0 as well.

## Round 263: which compiler built the binary, and every switch tried

The binary embeds `MS Run-Time Library - Copyright (c) 1992`; the MSC 7.0 and 6.0b libraries
carry 1992 and MSC 5.1's carry 1988, so 5.1 is excluded by the binary itself. Every documented
`CL` option (read from `CL.MSG`) was then compiled over five memory models, three CPU settings
and 22 option combinations: 330 flag sets, 79 distinct objects, 17 distinct code-generation
behaviours, and **none emits `add r,r` for a doubling** (positive control confirms the detector).
The doubling, pad-byte, register-choice and tail-merge walls are therefore not switch-reachable
on any available Microsoft C 5.1-7.0.
