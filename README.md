# Giten Megami Tensei: Tokyo Mokushiroku — DDS98.EXE decompilation

Byte-exact reconstruction of the game engine **DDS98.EXE** (偽典・女神転生 ～東京黙示録～,
1997) following the workflow for byte-verified decompilation:
every function is **MATCH** (byte-identical), **RELOCS** (identical except for real
OMF linker relocations), or **PENDING** with a documented cause — nothing is faked.

## Status (2026-11-23, round 40 close-out)

- **Phase 0 complete** — original toolchain: **Microsoft C/C++ 7.0** (CL 8.00, 1992),
  compiled under dosbox-x with HDPMI (HX-DOS runtime) as DPMI server.
  MSC 6.00ax was obtained but could **not** be tested: that archive.org set ships
  a Windows PE compiler driver, and the earlier "MSC 6 ruled out" result was
  invalidated by the stale-object bug (see `docs/CONVENTIONS.md`). MSC 6 codegen
  is therefore an **open question**, not a settled one.
- Base flags **`/G1 /AM /Gs /Os`** (80186, medium model, no stack checks, size
  optimization). Flags are chosen **per source file**: `/Ox` is required for
  functions whose original keeps a value in `DX`/`BX` instead of spilling it.
- **137 functions byte-verified**: **MATCH 32**, **RELOCS 105**, plus
  **22 PENDING** rows, each with the tested variants and the surviving diff.
  Ledger: `docs/MATCHING.md`. `tools/verify.py` rebuilds every source from scratch
  and re-checks every row (exit 0 = green).
- Coverage: **2067 / 293 211 own code bytes (0.705 %)** — the honest byte metric
  from `tools/coverage.py`; ~12 KB of the image are data, 963 bytes are foreign CRT.
- **How far this can go, measured**: `docs/GAP.md` counts, per codegen trait, how
  much of the binary Microsoft C 7 cannot reproduce. Only ~9.7 KB of framed code is
  reachable by this toolchain; the rest needs the original compiler generation.

## What is proven, and what is not

Proven by byte diff, not by plausibility:

- the toolchain and base flags above;
- the calling conventions (`__near`/`__far`, `__pascal`, `__fastcall`) and how
  parameter offsets follow from them;
- an idiom catalogue in `docs/IDIOMS.md` (opcode direction names the source form,
  `/Ox` register allocation, `les`/`lds` + `push ss / pop ds`, integer divide vs
  shift, jump-target alignment, and more).

**Not done:** this is a verified foundation, not a finished decompilation. 0.242 %
of the code bytes are proven. The **inventory itself is wrong**: 189 of its 1,956
entries hide 2–6 real functions each (**461 hidden units**), so the remaining work
is larger than the raw entry count suggests. A subset of the modules cannot be
reproduced from MSC 7 at any tested optimization level (`add bx,bx`,
`C7 06` zero stores, `DX`-staged 32-bit exchanges); the working assumption is
hand-written assembly there, and those rows are kept PENDING rather than forced.

## Structure

```
docs/           CONVENTIONS (parameters+evidence), MATCHING (ledger), IDIOMS, PROGRESS, STATUS, GAP,
                PENDING (open diffs with causes)
ground_truth/   functions/strings/imports + foreign_crt (foreign-code signatures) + not_code
src/calib/      reconstructed sources (8.3 names — required by MSC-CL-1992)
tools/          gt (inventory), build (dosbox-x recipe), omfdump, match, verify, coverage,
                markcrt, mine (candidate finder), sweep (family sweeper), report, disasm
```

## Building

Requires Microsoft C/C++ 7.0 (abandonware, e.g. via archive.org) and dosbox-x +
HX-DOS runtime. The complete recipe including every pitfall is in
`docs/CONVENTIONS.md`: HDPMI32 TSR before every CL call, `-nopromptfolder`,
APPDATA redirect, 8.3 source file names, `cycles=max`.

**No original material in this repo:** the binary, the toolchain, and the raw
decompiled excerpts are deliberately kept outside — this repo contains only our
own reconstructions, tools, and documentation.
