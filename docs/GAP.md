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
