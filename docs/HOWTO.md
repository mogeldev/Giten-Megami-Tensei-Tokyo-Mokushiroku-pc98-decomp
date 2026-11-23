# HOWTO — reproduce, extend, and diagnose

Everything in this repository is reproducible from the retail `DDS98.EXE` with the
toolchain in `../toolchain/`. This guide covers the three things you actually do:
re-check the whole ledger, reproduce one row, and diagnose a mismatch.

## 0. Prerequisites

```
../toolchain/msc7i/           Microsoft C/C++ 7.0 (CL 8.00) — BIN, LIB, INCLUDE
../toolchain/dosboxx/         DOSBox-X
../toolchain/HDPMI32.EXE      DPMI host for the 32-bit CL driver
../giten/DDS98/DDS98.EXE     the original binary (NOT in this repo)
```

`build.py` launches DOSBox-X with `-nopromptfolder`, loads `HDPMI32`, sets
`PATH`/`INCLUDE`/`LIB` to the MSC directory, and compiles one source file. It
deletes the old OBJ, stamp and log before every build — a stale object once made a
failing compile look like a success.

## 1. Check the whole ledger

```powershell
python tools/verify.py        # rebuilds every src=/flags= group, re-matches every row
python tools/checkled.py      # bookkeeping: statuses, duplicates, missing/orphan sources
python tools/coverage.py      # the honest byte metric
python tools/report.py        # regenerates docs/STATUS.md
```

`verify.py` exits 0 only if every row still matches. It refuses rows that end
mid-instruction, include trailing padding, or duplicate an address by linear value —
those are the three ways a naive matcher silently accepts a wrong window.

## 2. Reproduce one row

Take `1f6f:000c | PICK_PTR | 44 | RELOCS | src=src/calib/cpick1.c; flags="/G1 /AM /Gs /Ox /Oa /Os"`:

```powershell
python build.py src/calib/cpick1.c --flags "/G1 /AM /Gs /Ox /Oa /Os" --force
python tools/omfdump.py build/cpick1.OBJ            # see the emitted bytes
python tools/match.py 1f6f:000c PICK_PTR --obj build/cpick1.OBJ --size 44
```

`match.py` compares the object's code against the binary at that address, masking
every byte that carries a relocation in the object (globals, call targets). It
reports `MATCH` when no byte differs, `RELOCS` when the only differences are masked,
and `DIFF` with the first differing offsets otherwise.

**The size is authoritative and must end at a return instruction.** Never take a size
from a unit that carries padding; if `verify.py` says *"real length is N"*, believe it.

## 3. Reading the binary before writing C

Four things decide the signature, and all four are visible in the bytes:

| Question | Tell |
|---|---|
| near or far function? | terminator: `C3`/`C2 imm16` = near, `CB`/`CA imm16` = far |
| where are the arguments? | near pascal → `bp+4`, far pascal → `bp+6`; cdecl near → `bp+4` but the **caller** pops |
| pascal or cdecl callee? | stack cleanup after a call: none = pascal (callee pops); `pop bx`/`add sp,n` = cdecl |
| which flags? | register staging: `8B 56 06` (DX) wants `/Ox`; `83 7E 06 00` (memory) wants `/Os` |

Two more that come up constantly:

- A far pointer argument is **two words**; a DGROUP far pointer is pushed as
  `1E 68 <offset>` (push ds; push offset), never as a single value.
- `retf imm16` is the callee's argument byte count, so `pushed_words = imm16/2`
  counts parameters **plus literals** — extra pushes are constants.

## 4. Diagnosing a DIFF

Work down this list; each item is a real case from this project:

1. **Diff at the end, value `00` vs `90`** → your window includes a padding byte.
   The real length is one or two bytes shorter.
2. **Every pushed offset off by exactly 2** → wrong frame type: `C9 C2` is near
   (arguments at `bp+4`), `C9 CA` is far (`bp+6`).
3. **`5B` (`pop bx`) right after a call** → you declared the callee cdecl; the
   original's callee is pascal and pops its own arguments.
4. **`33 C0` where the original has `B8 00 00`, or `A3` where it has `C7 06`** →
   the original materialises zero explicitly; MSC always uses the xor idiom. Not
   fixable.
5. **`D1 E0` where the original has `03 C0`** → doubling: the original uses
   `add r,r`, MSC uses `shl r,1`. Not fixable.
6. **`9A` where the original has `0E E8`** → the original calls same-segment far
   functions with `push cs; call`; MSC always emits `9A`. Not fixable.
7. **`C4 5E xx` (`les`) where the original has `8B 5E xx` + `8E 46 xx`** → split
   pointer load. Not fixable.
8. **`8E C2` / `8B D8` in the wrong order** → instruction-order trait; two
   instructions, same values. Not fixable.
9. **`push si` in the original, nothing in yours** → the original keeps a far
   pointer's offset in SI (callee-saved), MSC keeps it in BX. Not fixable.
10. **`B4 xx` (`mov ah,imm`) before a call** → register-passed arguments; no MSC
    construct produces this. Not fixable.
11. **Branch displacements off by the number of `90` bytes present** → the original
    pads jump targets even in size-optimised code. Not fixable.

If none of these explains it, the source is genuinely wrong — go back to §3.

## 5. Adding a row

1. Write the C in `src/calib/<8.3-name>.c` (DOS 8.3 — `build.py` rejects longer stems).
2. Build with the flags that fit, then `match.py` until `MATCH` or `RELOCS`.
3. Append one line to `docs/MATCHING.md`:

   `| seg:off | NAME | size | MATCH/RELOCS | src=src/calib/x.c; flags="<cflags>"; note |`

4. `python tools/verify.py` and `python tools/checkled.py` must both exit 0.
5. If a generator wrote the source, say so in the note; if a function is not a
   `units.csv` boundary, say that too.

**Do not** add a row you have not matched. `PENDING` rows are for units whose source
you believe correct but whose remaining bytes differ for a documented reason — they
carry no `src=`, are skipped by `verify.py`, and must name the surviving diff.

## 6. Existing generators

Each sweeps one mechanical family, generates `src/calib/<file>.c`, builds once and
matches every member. Re-run them after any inventory change:

```
tools/setters.py    far-pascal store setters        (55 8B EC (8B 46 xx A3 d)+ ...)
tools/wraps.py      thin call wrappers              (pushes + E8 + leave/ret)
tools/swapgen.py    swap-and-return                 (8B 16 <g> ... 8B C2 / C9 ...)
```

They refuse to overwrite a file the ledger references — that guard exists because a
generator with a colliding name once destroyed a verified source.

## 7. What is out of reach, and why

`docs/CONVENTIONS.md` lists the nine codegen traits of the original compiler with the
function that isolates each one, and `docs/GAP.md` counts the units each trait blocks.
The practical ceiling for this toolchain is the `blocked by nothing` row of that
table. Everything above it needs the original compiler generation, which could not be
made runnable here: the only DOS-hosted Microsoft C 5.1 copy is EXEPACK-packed and
this DOSBox-X build has no `LOADFIX`, and the 6.00ax set is a Windows-hosted PE.
